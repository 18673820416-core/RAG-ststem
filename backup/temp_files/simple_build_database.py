#!/usr/bin/env python3
# @self-expose: {"id": "simple_build_database", "name": "Simple Build Database", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Build Database功能"]}}
# -*- coding: utf-8 -*-
"""
简化版数据库构建脚本
绕过NumPy兼容性问题，直接构建记忆数据库
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

def load_collected_data():
    """加载数据收集器生成的数据"""
    # 查找最新的收集数据文件
    data_dir = Path("data")
    collected_files = list(data_dir.glob("collected_data_*.json"))
    
    if not collected_files:
        print("❌ 未发现数据收集器生成的数据文件")
        return []
    
    # 按时间戳排序，取最新的文件
    collected_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = collected_files[0]
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 加载收集数据成功: {latest_file.name}")
        print(f"   记录数量: {len(data)} 条")
        return data
        
    except Exception as e:
        print(f"❌ 加载收集数据失败: {e}")
        return []

def build_memory_database(data: list):
    """构建记忆数据库"""
    print("🔨 开始构建记忆数据库...")
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect('data/rag_memory.db')
    cursor = conn.cursor()
    
    # 创建记忆表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            source_type TEXT,
            timestamp TEXT,
            importance REAL DEFAULT 0.5,
            confidence REAL DEFAULT 0.8,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
        import re
        if re.match(r'^[\s\d\W]+$', content.strip()):
            filtered_count += 1
            continue
        
        # 处理数据格式
        if 'metadata' in item and 'file_path' in item['metadata']:
            file_path = item['metadata']['file_path']
            
            # 根据文件路径确定主题
            if 'docs' in file_path.lower():
                topic = 'DOCS聊天记录'
            elif 'logs' in file_path.lower():
                topic = '系统日志'
            else:
                topic = '其他数据'
                
            importance = item.get('semantic_quality', 0.5)
            
            memory_data = {
                'topic': topic,
                'content': content,
                'source_type': 'collected_data',
                'timestamp': item['metadata'].get('collected_at', ''),
                'importance': importance,
                'confidence': 0.8,
                'tags': json.dumps(['collected', 'sliced'])
            }
        else:
            memory_data = {
                'topic': item.get('source', '未分类'),
                'content': content,
                'source_type': item.get('source', 'unknown'),
                'timestamp': item.get('collected_at', item.get('last_modified', '')),
                'importance': 0.5,
                'confidence': 0.8,
                'tags': json.dumps([item.get('file_type', 'unknown')])
            }
        
        # 插入记忆数据（使用INSERT OR IGNORE避免唯一性约束错误）
        cursor.execute('''
            INSERT OR IGNORE INTO memory_units (topic, content, source_type, timestamp, importance, confidence, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_data['topic'],
            memory_data['content'],
            memory_data['source_type'],
            memory_data['timestamp'],
            memory_data['importance'],
            memory_data['confidence'],
            memory_data['tags']
        ))
        
        memory_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ 记忆数据库构建完成")
    print(f"   添加记忆: {memory_count} 条")
    print(f"   过滤数据: {filtered_count} 条")
    
    return memory_count

def show_statistics():
    """显示数据库统计信息"""
    conn = sqlite3.connect('data/rag_memory.db')
    cursor = conn.cursor()
    
    # 获取记忆总数
    cursor.execute('SELECT COUNT(*) FROM memory_units')
    memory_count = cursor.fetchone()[0]
    
    # 获取主题分类
    cursor.execute('SELECT DISTINCT topic FROM memory_units')
    topics = [row[0] for row in cursor.fetchall()]
    
    print("\n📊 数据库统计信息:")
    print("=" * 30)
    print(f"记忆单元总数: {memory_count}")
    print(f"主题分类数: {len(topics)}")
    print(f"主题列表: {', '.join(topics[:10])}{'...' if len(topics) > 10 else ''}")
    
    # 显示各主题的记忆数量
    print("\n各主题记忆数量:")
    cursor.execute('SELECT topic, COUNT(*) FROM memory_units GROUP BY topic ORDER BY COUNT(*) DESC')
    for topic, count in cursor.fetchall():
        print(f"  {topic}: {count} 条")
    
    conn.close()

def main():
    """主函数"""
    print("=" * 50)
    print("简化版记忆数据库构建工具")
    print("=" * 50)
    
    # 1. 加载收集的数据
    data = load_collected_data()
    if not data:
        return
    
    # 2. 构建记忆数据库
    memory_count = build_memory_database(data)
    
    if memory_count > 0:
        # 3. 显示统计信息
        show_statistics()
        
        print(f"\n🎉 数据库构建成功！现在可以运行知识图谱重建了。")
        print(f"   运行命令: python rebuild_knowledge_graph.py")
    else:
        print("❌ 数据库构建失败，没有有效数据")

if __name__ == "__main__":
    main()