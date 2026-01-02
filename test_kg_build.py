#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试知识图谱首次构建"""

import time
from src.system_statistics_service import get_system_statistics_service

print("=" * 60)
print("测试知识图谱首次构建流程")
print("=" * 60)

# 初始化服务
print("\n⏳ 步骤1: 初始化SystemStatisticsService...")
start = time.time()
svc = get_system_statistics_service()
print(f"✅ 服务初始化完成，耗时: {time.time()-start:.2f}秒")

# 强制构建知识图谱
print("\n⏳ 步骤2: 强制构建知识图谱（force_rebuild_kg=True）...")
start2 = time.time()
try:
    stats = svc.get_system_statistics(force_refresh=True, force_rebuild_kg=True)
    elapsed = time.time() - start2
    
    print(f"✅ 知识图谱构建完成，耗时: {elapsed:.2f}秒")
    print(f"\n📊 构建结果:")
    print(f"  - 节点数: {stats['knowledge_graph']['total_nodes']}")
    print(f"  - 边数: {stats['knowledge_graph']['total_edges']}")
    print(f"  - 覆盖率: {stats['knowledge_graph']['coverage_rate']:.1f}%")
    print(f"  - 总记忆数: {stats['vector_database']['total_memories']}")
    
except Exception as e:
    print(f"❌ 构建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
