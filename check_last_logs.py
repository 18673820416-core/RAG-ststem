import json

with open('logs/startup_status.json', encoding='utf-8') as f:
    data = json.load(f)

logs = data['startup_logs']['logs']

print("检查最后10条JSON日志:")
for i, log in enumerate(logs[-10:], len(logs)-9):
    print(f"{i}. [{log['logger']}] {log['message'][:80]}")

print("\n检查是否有'系统初始化完成':")
for log in logs:
    if '系统初始化完成' in log['message']:
        print(f"  找到: {log['message']}")

print("\n检查是否有'知识图谱异步':")
for log in logs:
    if '知识图谱异步' in log['message'] or '知识图谱持久化' in log['message']:
        print(f"  找到: {log['message']}")
