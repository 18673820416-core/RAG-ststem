#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mesh_database_interface import MeshDatabaseInterface
from src.memory_vector_db import MemoryVectorDB

# 初始化向量数据库
vector_db = MemoryVectorDB()
all_memories_data = vector_db.get_all_memories(limit=100)
all_memories = [{'id': m[0], 'content': m[3]} for m in all_memories_data]

print(f"测试记忆数: {len(all_memories)}")

# 初始化数据库接口
db = MeshDatabaseInterface()

# 生成归纳摘要
results = db.generate_summaries_with_induction(all_memories[:50])

print(f"归纳结果数: {len(results)}")

# 质量验证
quality_counts = {'excellent': 0, 'good': 0, 'poor': 0}

for result in results[:10]:
    memory_id = result['id']
    summary = result['topic_summary']
    
    # 简化评分
    score = 0
    if len(summary) > 0:
        score += 1
   
    # 压缩率检查
    orig_len = len(all_memories[0]['content']) if all_memories else 100
    if 0.1 <= len(summary)/orig_len <= 0.5:
        score += 1
    
    # 关键点检查
    if result.get('key_points'):
        score += 1
    
    # 评级
    if score >= 2:
        quality_counts['excellent'] += 1
        level = "优秀"
    elif score >= 1:
        quality_counts['good'] += 1
        level = "良好"
    else:
        quality_counts['poor'] += 1
        level = "需改进"
    
    print(f"[{len([k for k in quality_counts.values() if k > 0])}] {level} (分数: {score}/3)")

# 输出报告
total = sum(quality_counts.values())
excellent_rate = quality_counts['excellent'] / total * 100 if total > 0 else 0

print(f"\n=== v1.5质量报告 ===")
print(f"优秀: {quality_counts['excellent']}/{total} ({excellent_rate:.0f}%)")
print(f"良好: {quality_counts['good']}/{total}")
print(f"需改进: {quality_counts['poor']}/{total}")

if excellent_rate >= 90:
    print(f"\n✅ 达到90%优秀率目标！")
elif excellent_rate >= 80:
    print(f"\n⚠️ 接近目标，当前{excellent_rate:.0f}%")
else:
    print(f"\n❌ 未达标，需继续优化")
