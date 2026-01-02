# @self-expose: {"id": "vector_database", "name": "Vector Database", "type": "component", "version": "1.2.1", "needs": {"deps": ["database_manager"], "resources": []}, "provides": {"capabilities": ["Vector Database功能", "存储和检索记忆单元", "向量相似性搜索", "记忆管理", "记忆删除", "数据库迁移支持"], "data_formats": [{"name": "memory_unit", "id_pattern": "mem_*", "fields": ["id", "topic", "content", "source_type", "timestamp", "importance", "confidence", "tags", "status", "worldview_version", "retire_reason", "vector"]}]} }
# 向量数据库模块

import logging
import sqlite3
import json
import os
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.system_config import DATABASE_PATH, VECTOR_DIMENSION, EMBEDDING_MODEL, MODEL_CACHE_DIR
from src.database_manager import get_database_manager
from src.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

class VectorDatabase:
    """基于SQLite的向量数据库"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_manager = get_database_manager()
        # 使用统一Embedding服务
        self.embedding_service = get_embedding_service()
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
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
                status TEXT DEFAULT 'active',
                worldview_version TEXT,
                retire_reason TEXT,
                vector BLOB,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 数据库迁移：检查并添加新字段（兼容旧数据库）
        self._migrate_database(cursor)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON memory_units(topic)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_units(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_units(importance)")
        
        conn.commit()
    
    def _migrate_database(self, cursor):
        """数据库迁移：添加缺失的字段"""
        try:
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_units'")
            if not cursor.fetchone():
                return  # 表不存在，无需迁移
            
            # 获取当前表结构
            cursor.execute("PRAGMA table_info(memory_units)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # 需要添加的新字段
            new_columns = [
                ('status', 'TEXT DEFAULT \'active\''),
                ('worldview_version', 'TEXT'),
                ('retire_reason', 'TEXT')
            ]
            
            # 添加缺失的字段
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE memory_units ADD COLUMN {col_name} {col_type}")
                        print(f"✅ 数据库迁移：已添加字段 '{col_name}'")
                    except sqlite3.OperationalError as e:
                        print(f"⚠️ 添加字段 '{col_name}' 失败（可能已存在）: {e}")
            
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")
    
    def add_memory(self, memory_data: Dict[str, Any], vector: Optional[List[float]] = None) -> str:
        """添加记忆单元"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 生成唯一ID
        memory_id = f"mem_{hash(str(memory_data) + str(datetime.now()))}"
        
        # 准备数据
        topic = memory_data.get('topic', '未分类')
        content = memory_data.get('content', '')
        source_type = memory_data.get('source_type', 'unknown')
        # 统一使用年月日时分秒格式，避免同维记忆切片问题
        timestamp = memory_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        importance = memory_data.get('importance', 0.5)
        confidence = memory_data.get('confidence', 0.8)
        tags = json.dumps(memory_data.get('tags', []), ensure_ascii=False)
        
        # 处理向量（如果提供）
        vector_blob = None
        if vector:
            vector_array = np.array(vector, dtype=np.float32)
            vector_blob = vector_array.tobytes()
        
        # 插入数据（使用INSERT OR IGNORE避免重复）
        cursor.execute("""
            INSERT OR IGNORE INTO memory_units 
            (id, topic, content, source_type, timestamp, importance, confidence, tags, status, worldview_version, retire_reason, vector, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id, topic, content, source_type, timestamp, importance, 
            confidence, tags, 
            memory_data.get('status', 'active'),
            memory_data.get('worldview_version'),
            memory_data.get('retire_reason'),
            vector_blob, datetime.now().isoformat()
        ))
        
        conn.commit()
        return memory_id
    
    def search_memories(self, 
                       query: str = None, 
                       vector: List[float] = None,
                       topic: str = None,
                       min_importance: float = 0.3,
                       start_time: str = None,
                       end_time: str = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索记忆单元，支持本地embedding检索
        
        Args:
            query: 搜索查询文本
            vector: 查询向量（如果未提供，将自动生成）
            topic: 主题筛选
            min_importance: 最小重要性
            start_time: 开始时间（格式：%Y%m%d_%H%M%S）
            end_time: 结束时间（格式：%Y%m%d_%H%M%S）
            limit: 返回结果数量
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = ["importance >= ?"]
        params = [min_importance]
        
        if topic:
            conditions.append("topic LIKE ?")
            params.append(f"%{topic}%")
        
        if query:
            conditions.append("(topic LIKE ? OR content LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # 时间范围查询条件
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 执行查询
        sql = f"""
            SELECT id, topic, content, source_type, timestamp, importance, confidence, tags, status, worldview_version, retire_reason, vector
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
                'status': row[8] or 'active',
                'worldview_version': row[9],
                'retire_reason': row[10],
                'vector': np.frombuffer(row[11], dtype=np.float32).tolist() if row[11] else None
            }
            results.append(memory)
        
        # 如果没有提供向量，但有查询文本，自动生成查询向量
        if not vector and query:
            vector = self._generate_query_vector(query)
        
        # 如果有向量，进行相似度排序
        if vector and results:
            results = self._sort_by_similarity(results, vector)
        
        return results
    
    def _generate_query_vector(self, query: str) -> List[float]:
        """生成查询文本的向量表示，使用统一Embedding服务"""
        if not query:
            dimension = self.embedding_service.get_dimension()
            return [0.0] * dimension
        try:
            vector = self.embedding_service.encode(query)
            return vector
        except Exception as e:
            print(f"生成查询向量失败: {e}")
            dimension = self.embedding_service.get_dimension()
            return [0.0] * dimension
    
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
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_units")
        return cursor.fetchone()[0]
    
    def get_topics(self) -> List[str]:
        """获取所有主题"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT topic FROM memory_units ORDER BY topic")
        return [row[0] for row in cursor.fetchall()]
    
    def search_by_time_range(self, 
                           start_time: str, 
                           end_time: str,
                           min_importance: float = 0.3,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """按时间范围搜索记忆单元
        
        Args:
            start_time: 开始时间（格式：%Y%m%d_%H%M%S）
            end_time: 结束时间（格式：%Y%m%d_%H%M%S）
        """
        return self.search_memories(
            start_time=start_time,
            end_time=end_time,
            min_importance=min_importance,
            limit=limit
        )
    
    def get_timeline_statistics(self) -> Dict[str, Any]:
        """获取时间线统计信息"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 获取最早和最晚时间
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM memory_units")
        min_time, max_time = cursor.fetchone()
        
        # 获取按时间分组的记忆数量
        cursor.execute("""
            SELECT SUBSTR(timestamp, 1, 8) as date, COUNT(*) as count 
            FROM memory_units 
            GROUP BY date 
            ORDER BY date
        """)
        daily_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'earliest_time': min_time,
            'latest_time': max_time,
            'total_memories': self.get_memory_count(),
            'daily_statistics': daily_stats
        }
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """获取所有记忆单元"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, topic, content, source_type, timestamp, importance, confidence, tags, status, worldview_version, retire_reason, vector
            FROM memory_units
            ORDER BY timestamp DESC
        """)
        
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
                'status': row[8] or 'active',
                'worldview_version': row[9],
                'retire_reason': row[10],
                'vector': np.frombuffer(row[11], dtype=np.float32).tolist() if row[11] else None
            }
            results.append(memory)
        
        return results
    
    def update_memory(self, memory_id: str, new_content: str):
        """更新记忆单元的内容"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE memory_units
            SET content = ?, updated_at = ?
            WHERE id = ?
        """, (new_content, datetime.now().isoformat(), memory_id))
        
        conn.commit()
    
    def update_memory_status(self, memory_id: str, status: str,
                             worldview_version: Optional[str] = None,
                             retire_reason: Optional[str] = None) -> bool:
        """更新记忆单元的状态信息（active/archived/retired 等）"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE memory_units
            SET status = ?,
                worldview_version = COALESCE(?, worldview_version),
                retire_reason = COALESCE(?, retire_reason),
                updated_at = ?
            WHERE id = ?
        """, (status, worldview_version, retire_reason, datetime.now().isoformat(), memory_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆单元
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM memory_units
                WHERE id = ?
            """, (memory_id,))
            
            conn.commit()
            deleted_count = cursor.rowcount
            
            if deleted_count > 0:
                logger.info(f"成功从向量库删除记忆: {memory_id}")
                return True
            else:
                logger.warning(f"向量库中未找到记忆: {memory_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除记忆 {memory_id} 失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close_connection()

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
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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