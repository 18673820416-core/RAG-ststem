import json

with open('logs/startup_status.json', encoding='utf-8') as f:
    data = json.load(f)

logs = data['startup_logs']['logs']

print("=" * 60)
print("启动日志完整性验证")
print("=" * 60)

print("\n【JSON文件前10条日志】")
for i, log in enumerate(logs[:10]):
    print(f"  {i+1}. [{log['logger']}] {log['message'][:80]}")

print("\n【导入阶段日志】")
for log in logs:
    if '导入' in log['message'] or '加载' in log['message'] or '开始启动' in log['message']:
        print(f"  [{log['logger']}] {log['message']}")

print("\n【引擎初始化日志（前5条）】")
engine_logs = [log for log in logs if '引擎' in log['message'] or '人脸识别' in log['message']]
for log in engine_logs[:5]:
    print(f"  [{log['logger']}] {log['message']}")

print("\n【统计信息】")
print(f"  总日志数: {len(logs)}")
print(f"  stdout日志数: {sum(1 for log in logs if log['logger'] == 'stdout')}")
print(f"  logging日志数: {sum(1 for log in logs if log['logger'] != 'stdout')}")
print(f"  重复日志数: {data['startup_logs']['duplicate_count']}")

print("\n【重复日志前3条】")
for i, dup in enumerate(data['startup_logs']['duplicates_detected'][:3]):
    print(f"  {i+1}. [{dup['logger']}] {dup['message'][:50]}... (重复{dup['count']}次)")
