#!/usr/bin/env python3
# @self-expose: {"id": "solo_main", "name": "Solo Main", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Solo Main功能"]}}
"""
RAG系统 - SOLO模式主入口
简化架构，专注核心功能
保持与原系统设计意图的兼容性
"""

import argparse
import json
import logging
import re
import uuid
from pathlib import Path
from datetime import datetime
import sqlite3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 保持与原系统兼容的向量维度设计
VECTOR_DIMENSION = 1024  # 与原系统配置一致

class SoloVectorDatabase:
    """简化版向量数据库 - SOLO模式
    保持与原系统设计意图的兼容性
    """
    
    def __init__(self, db_path="data/rag_memory.db"):
        self.db_path = Path(db_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建主记忆表（保持与原系统设计意图兼容）
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
        
        # 创建索引，支持多维度查询
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON memory_units(topic)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_units(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_units(importance)")
        
        conn.commit()
        conn.close()
    
    def add_memory(self, memory_data):
        """添加记忆单元，保持与原系统设计兼容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 生成唯一ID
        memory_id = f"mem_{uuid.uuid4()}"
        
        # 准备数据
        topic = memory_data.get('topic', '未分类')
        content = memory_data.get('content', '')
        source_type = memory_data.get('source_type', 'unknown')
        timestamp = memory_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        importance = memory_data.get('importance', 0.5)
        confidence = memory_data.get('confidence', 0.8)
        tags = json.dumps(memory_data.get('tags', []), ensure_ascii=False)
        
        # 处理向量（保持与原系统兼容）
        vector_blob = None
        if 'vector' in memory_data and memory_data['vector']:
            vector = memory_data['vector']
            # 确保向量是1024维
            if len(vector) != VECTOR_DIMENSION:
                # 调整向量维度
                if len(vector) > VECTOR_DIMENSION:
                    vector = vector[:VECTOR_DIMENSION]
                else:
                    # 补零到1024维
                    vector = vector + [0.0] * (VECTOR_DIMENSION - len(vector))
            # 使用JSON存储向量（简化实现，保持兼容性）
            vector_blob = json.dumps(vector).encode('utf-8')
        
        # 插入数据（使用INSERT OR IGNORE避免重复）
        cursor.execute("""
            INSERT OR IGNORE INTO memory_units 
            (id, topic, content, source_type, timestamp, importance, confidence, tags, vector, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id, topic, content, source_type, timestamp, importance, 
            confidence, tags, vector_blob, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return memory_id
    
    def search_memories(self, query=None, topic=None, min_importance=0.3, limit=10):
        """搜索记忆单元，支持多维度查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询条件，支持多维度过滤
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
            # 解析向量
            vector = None
            if row[8]:
                try:
                    vector = json.loads(row[8].decode('utf-8'))
                except Exception as e:
                    logger.warning(f"解析向量失败: {e}")
            
            memory = {
                'id': row[0],
                'topic': row[1],
                'content': row[2],
                'source_type': row[3],
                'timestamp': row[4],
                'importance': row[5],
                'confidence': row[6],
                'tags': json.loads(row[7]) if row[7] else [],
                'vector': vector
            }
            results.append(memory)
        
        conn.close()
        return results
    
    def get_memory_count(self):
        """获取记忆单元总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_units")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_topics(self):
        """获取所有主题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT topic FROM memory_units ORDER BY topic")
        topics = [row[0] for row in cursor.fetchall()]
        conn.close()
        return topics
    
    def close(self):
        """关闭数据库连接"""
        pass

class SoloDataCollector:
    """简化版数据收集器 - SOLO模式
    保持与原系统设计意图的兼容性
    """
    
    def __init__(self):
        self.processed_files = set()
    
    def collect_from_file(self, file_path):
        """从单个文件收集数据"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return []
        
        if file_path in self.processed_files:
            return []
            
        self.processed_files.add(file_path)
        
        try:
            # 根据文件类型处理
            if file_path.suffix.lower() in ['.txt', '.md', '.json']:
                return self._process_text_file(file_path)
            elif file_path.suffix.lower() in ['.log']:
                return self._process_log_file(file_path)
            else:
                logger.debug(f"跳过不支持的文件类型: {file_path}")
                return []
                
        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {e}")
            return []
    
    def _process_text_file(self, file_path):
        """处理文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 基础文本数据记录
            data_item = {
                "source": "file_system",
                "file_path": str(file_path),
                "content": content,
                "file_type": file_path.suffix,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "collected_at": datetime.now().isoformat()
            }
            
            return [data_item]
            
        except Exception as e:
            logger.error(f"读取文本文件失败 {file_path}: {e}")
            return []
    
    def _process_log_file(self, file_path):
        """处理日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            log_entries = []
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    log_entry = {
                        "source": "log_file",
                        "file_path": str(file_path),
                        "line_number": line_num,
                        "content": line.strip(),
                        "collected_at": datetime.now().isoformat()
                    }
                    log_entries.append(log_entry)
                    
            return log_entries
            
        except Exception as e:
            logger.error(f"读取日志文件失败 {file_path}: {e}")
            return []
    
    def collect_from_directory(self, dir_path, recursive=True):
        """从目录收集数据"""
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            logger.warning(f"目录不存在: {dir_path}")
            return []
        
        all_data = []
        
        if recursive:
            # 递归遍历文件夹
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    data = self.collect_from_file(file_path)
                    all_data.extend(data)
        else:
            # 只遍历当前文件夹
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    data = self.collect_from_file(file_path)
                    all_data.extend(data)
        
        logger.info(f"从目录 {dir_path} 收集到 {len(all_data)} 条数据")
        return all_data
    
    def collect_all(self, paths, recursive=True):
        """从所有路径收集数据"""
        all_data = []
        
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                data = self.collect_from_file(path)
                all_data.extend(data)
            elif path_obj.is_dir():
                data = self.collect_from_directory(path, recursive)
                all_data.extend(data)
        
        logger.info(f"总共收集到 {len(all_data)} 条数据")
        return all_data

class SoloRAGSystem:
    """SOLO模式RAG系统
    保持与原系统设计意图的兼容性
    """
    
    def __init__(self, db_path="data/rag_memory.db"):
        self.db = SoloVectorDatabase(db_path)
        self.collector = SoloDataCollector()
    
    def build_database(self, data):
        """构建记忆数据库，保持与原系统设计兼容"""
        logger.info("开始构建记忆数据库...")
        
        memory_count = 0
        filtered_count = 0
        
        for item in data:
            content = item.get('content', '')
            
            # 数据质量过滤
            if not content.strip():
                filtered_count += 1
                continue
                
            if len(content.strip()) < 20:
                filtered_count += 1
                continue
                
            # 检查是否只包含特殊字符或数字
            if re.match(r'^[\s\d\W]+$', content.strip()):
                filtered_count += 1
                continue
                
            # 构建记忆数据，保持与原系统设计兼容
            memory_data = {
                'topic': self._extract_topic(item),
                'content': content,
                'source_type': item.get('source', 'unknown'),
                'timestamp': item.get('collected_at', item.get('last_modified', datetime.now().isoformat())),
                'importance': self._calculate_importance(item),
                'confidence': 0.8,
                'tags': self._extract_tags(item)
            }
            
            # 添加记忆单元
            self.db.add_memory(memory_data)
            memory_count += 1
        
        logger.info(f"记忆数据库构建完成，添加了 {memory_count} 条记忆，过滤掉了 {filtered_count} 条低质量数据")
        
        return {
            'added_memories': memory_count,
            'filtered_memories': filtered_count,
            'total_memories': self.db.get_memory_count()
        }
    
    def _extract_topic(self, item):
        """提取主题"""
        # 从文件路径提取主题
        file_path = item.get('file_path', '')
        if 'docs' in file_path.lower():
            return '文档'
        elif 'logs' in file_path.lower():
            return '日志'
        elif 'chat' in file_path.lower() or 'conversation' in file_path.lower():
            return '聊天记录'
        else:
            return item.get('topic', '未分类')
    
    def _calculate_importance(self, item):
        """计算重要性"""
        content = item.get('content', '')
        # 基于内容长度和质量计算重要性
        length_score = min(len(content) / 1000, 1.0) * 0.5
        # 简单的关键词加权
        keywords = ['AI', '技术', '架构', '设计', '实现', '算法', '模型']
        keyword_score = sum(1 for keyword in keywords if keyword in content) / len(keywords) * 0.5
        return round(length_score + keyword_score, 2)
    
    def _extract_tags(self, item):
        """提取标签"""
        tags = []
        file_path = item.get('file_path', '')
        if file_path:
            suffix = Path(file_path).suffix.lower()
            if suffix:
                tags.append(suffix[1:])  # 去掉点号
        return tags
    
    def search(self, query, limit=10):
        """搜索记忆，保持与原系统设计兼容"""
        logger.info(f"搜索记忆: {query}")
        return self.db.search_memories(query=query, limit=limit)
    
    def show_statistics(self):
        """显示系统统计信息"""
        total_memories = self.db.get_memory_count()
        topics = self.db.get_topics()
        
        return {
            'total_memories': total_memories,
            'topics_count': len(topics),
            'topics': topics[:10],
            'vector_dimension': VECTOR_DIMENSION,
            'design': '保持与原系统设计兼容，支持多维度查询'
        }
    
    def close(self):
        """关闭系统资源"""
        self.db.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='RAG系统 - SOLO模式')
    parser.add_argument('--build', action='store_true', help='构建记忆数据库')
    parser.add_argument('--search', type=str, help='搜索记忆内容')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--collect', nargs='+', help='收集指定路径的数据')
    parser.add_argument('--limit', type=int, default=10, help='搜索结果数量限制')
    parser.add_argument('--db', type=str, default='data/rag_memory.db', help='数据库路径')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG系统 - SOLO模式")
    print(f"保持与原系统设计兼容，向量维度: {VECTOR_DIMENSION}")
    print("=" * 60)
    
    # 创建SOLO RAG系统实例
    rag_system = SoloRAGSystem(args.db)
    
    try:
        if args.collect:
            # 收集数据
            data = rag_system.collector.collect_all(args.collect)
            print(f"✅ 数据收集完成，共 {len(data)} 条记录")
            
        if args.build:
            # 构建数据库
            # 加载现有数据（如果有）
            data_files = list(Path('data').glob('collected_data_*.json'))
            if data_files:
                # 按时间戳排序，取最新的文件
                data_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_file = data_files[0]
                
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"✅ 加载数据文件: {latest_file.name}")
                except Exception as e:
                    print(f"❌ 加载数据失败: {e}")
                    return
            else:
                # 如果没有现有数据，从默认路径收集
                default_paths = [
                    'docs',
                    'logs'
                ]
                data = rag_system.collector.collect_all(default_paths)
            
            # 构建数据库
            result = rag_system.build_database(data)
            print(f"✅ 数据库构建完成")
            print(f"   添加记忆: {result['added_memories']} 条")
            print(f"   过滤数据: {result['filtered_memories']} 条")
            print(f"   总记忆数: {result['total_memories']} 条")
        
        if args.search:
            # 搜索记忆
            results = rag_system.search(args.search, args.limit)
            print(f"\n搜索 '{args.search}' 的结果 ({len(results)} 条):")
            print("=" * 50)
            
            for i, memory in enumerate(results, 1):
                print(f"\n{i}. [{memory['source_type']}] {memory['topic']}")
                print(f"   重要性: {memory['importance']} | 置信度: {memory['confidence']}")
                print(f"   时间: {memory['timestamp']}")
                print(f"   内容: {memory['content'][:100]}...")
                if memory.get('tags'):
                    print(f"   标签: {', '.join(memory['tags'])}")
        
        if args.stats:
            # 显示统计信息
            stats = rag_system.show_statistics()
            print(f"\nRAG系统统计信息:")
            print("=" * 30)
            print(f"记忆单元总数: {stats['total_memories']}")
            print(f"主题分类数: {stats['topics_count']}")
            print(f"向量维度: {stats['vector_dimension']}")
            print(f"设计理念: {stats['design']}")
            print(f"主题列表: {', '.join(stats['topics'])}{'...' if len(stats['topics']) > 10 else ''}")
        
        # 如果没有指定任何操作，显示帮助信息
        if not any([args.build, args.search, args.stats, args.collect]):
            parser.print_help()
            print("\n示例:")
            print("  python solo_main.py --collect docs logs --build --stats")
            print("  python solo_main.py --search \"AI技术\" --limit 5")
            print("  python solo_main.py --stats")
    
    finally:
        rag_system.close()

if __name__ == "__main__":
    main()
