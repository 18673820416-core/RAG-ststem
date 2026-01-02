from src.vector_database import VectorDatabase
from collections import Counter

vdb = VectorDatabase()
all_mem = vdb.get_all_memories()

# 统计状态分布
status_dist = Counter([m.get('status', 'active') for m in all_mem])

print(f"📊 向量数据库统计:")
print(f"  总记忆数: {len(all_mem)}")
print(f"\n状态分布:")
for status, count in status_dist.items():
    print(f"  {status}: {count}")

# 主库记忆
active_mem = [m for m in all_mem if m.get('status', 'active') == 'active']
print(f"\n✅ 主库(active)记忆: {len(active_mem)}")

# 显示几个示例
if active_mem:
    print(f"\n前3个主库记忆示例:")
    for i, m in enumerate(active_mem[:3], 1):
        content = m.get('content', '')[:50]
        print(f"  {i}. {content}...")
