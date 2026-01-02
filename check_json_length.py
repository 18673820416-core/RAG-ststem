import json

with open('logs/startup_status.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"total_logs字段: {data['startup_logs']['total_logs']}")
print(f"实际logs列表长度: {len(data['startup_logs']['logs'])}")
print(f"duplicate_count字段: {data['startup_logs']['duplicate_count']}")
print(f"实际duplicates列表长度: {len(data['startup_logs']['duplicates_detected'])}")
