from src.system_statistics_service import get_system_statistics_service

stats_service = get_system_statistics_service()
system_stats = stats_service.get_system_statistics()

print("📊 系统统计服务数据:")
print(f"\n向量数据库统计:")
vdb_stats = system_stats['vector_database']
for key, value in vdb_stats.items():
    print(f"  {key}: {value}")

print(f"\n知识图谱统计:")
kg_stats = system_stats['knowledge_graph']
for key, value in kg_stats.items():
    print(f"  {key}: {value}")

print(f"\n思维引擎统计:")
te_stats = system_stats['thought_engine']
for key, value in kg_stats.items():
    print(f"  {key}: {value}")
