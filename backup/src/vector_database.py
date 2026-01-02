# @self-expose: {"id": "vector_database", "name": "Vector Database", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Vector Database功能"]}}
# 向量数据库模块

import sqlite3
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.system_config import DATABASE_PATH, VECTOR_DIMENSION

class VectorDatabase:
    """基于SQLite的向量数据库"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # 创建主记忆表（简化版，基于12维设计思想）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_units (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                importance FLOAT DEFAULT 0.5,
                confidence FLOAT DEFAULT 0.8,
                tags TEXT,
                vector BLOB,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON memory_units(topic)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_units(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_units(importance)")
        
        self.conn.commit()
    
    def add_memory(self, memory_data: Dict[str, Any], vector: Optional[List[float]] = None) -> str:
        """添加记忆单元"""
        cursor = self.conn.cursor()
        
        # 生成唯一ID
        memory_id = f"mem_{hash(str(memory_data) + str(datetime.now()))}"
        
        # 准备数据
        topic = memory_data.get('topic', '未分类')
        content = memory_data.get('content', '')
        source_type = memory_data.get('source_type', 'unknown')
        timestamp = memory_data.get('timestamp', datetime.now().isoformat())
        importance = memory_data.get('importance', 0.5)
        confidence = memory_data.get('confidence', 0.8)
        tags = json.dumps(memory_data.get('tags', []), ensure_ascii=False)
        
        # 处理向量（如果提供）
        vector_blob = None
        if vector:
            vector_array = np.array(vector, dtype=np.float32)
            vector_blob = vector_array.tobytes()
        
        # 插入数据
        cursor.execute("""
            INSERT INTO memory_units 
            (id, topic, content, source_type, timestamp, importance, confidence, tags, vector, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id, topic, content, source_type, timestamp, importance, 
            confidence, tags, vector_blob, datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return memory_id
    
    def search_memories(self, 
                       query: str = None, 
                       vector: List[float] = None,
                       topic: str = None,
                       min_importance: float = 0.3,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆单元"""
        cursor = self.conn.cursor()
        
        # 构建查询条件
        conditions = ["importance >= ?"]
        params = [min_importance]
        
        if topic:
            conditions.append("topic LIKE ?")
            params.append(f"%{topic}%")
        
        if query:
            conditions.append("(topic LIKE ? OR content LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 执行查询
        sql = f"""
            SELECT id, topic, content, source_type, timestamp, importance, confidence, tags, vector
            FROM memory_units
            WHERE {where_clause}
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """
        
        params.append(limit)
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            memory = {
                'id': row[0],
                'topic': row[1],
                'content': row[2],
                'source_type': row[3],
                'timestamp': row[4],
                'importance': row[5],
                'confidence': row[6],
                'tags': json.loads(row[7]) if row[7] else [],
                'vector': np.frombuffer(row[8], dtype=np.float32).tolist() if row[8] else None
            }
            results.append(memory)
        
        # 如果有向量，进行相似度排序（简化版）
        if vector and results:
            results = self._sort_by_similarity(results, vector)
        
        return results
    
    def _sort_by_similarity(self, memories: List[Dict[str, Any]], query_vector: List[float]) -> List[Dict[str, Any]]:
        """基于向量相似度排序（简化实现）"""
        def calculate_similarity(vec1, vec2):
            if not vec1 or not vec2:
                return 0.0
            
            # 简单的余弦相似度计算
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 * norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        
        # 计算每个记忆的相似度
        scored_memories = []
        for memory in memories:
            memory_vector = memory.get('vector')
            similarity = calculate_similarity(query_vector, memory_vector) if memory_vector else 0.0
            
            # 结合重要性和相似度
            combined_score = memory['importance'] * 0.6 + similarity * 0.4
            
            scored_memories.append((memory, combined_score))
        
        # 按综合分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        return [memory for memory, score in scored_memories]
    
    def get_memory_count(self) -> int:
        """获取记忆单元总数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_units")
        return cursor.fetchone()[0]
    
    def get_topics(self) -> List[str]:
        """获取所有主题"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT topic FROM memory_units ORDER BY topic")
        return [row[0] for row in cursor.fetchall()]
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

def main():
    """测试向量数据库功能"""
    # 创建数据库实例
    db = VectorDatabase()
    
    try:
        # 添加测试数据
        test_memory = {
            'topic': 'RAG系统设计',
            'content': '基于意识=认知=记忆=意义的循环等式，建立个人知识记忆系统',
            'source_type': 'conversation',
            'timestamp': datetime.now().isoformat(),
            'importance': 0.8,
            'confidence': 0.9,
            'tags': ['RAG', '记忆系统', '知识管理']
        }
        
        memory_id = db.add_memory(test_memory)
        print(f"添加记忆成功，ID: {memory_id}")
        
        # 搜索测试
        results = db.search_memories(query='RAG系统', min_importance=0.3)
        print(f"\n搜索到 {len(results)} 条结果:")
        
        for i, memory in enumerate(results, 1):
            print(f"\n{i}. 主题: {memory['topic']}")
            print(f"   内容: {memory['content'][:50]}...")
            print(f"   重要性: {memory['importance']}")
        
        # 统计信息
        print(f"\n数据库统计:")
        print(f"记忆总数: {db.get_memory_count()}")
        print(f"主题列表: {db.get_topics()}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()