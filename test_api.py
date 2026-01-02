import requests
import json

# 测试端口9437的API
port = 9437

print(f"测试端口 {port} 的API...")

# 1. 测试健康检查
try:
    r = requests.get(f'http://localhost:{port}/api/health')
    print(f"\n1. /api/health:")
    print(f"   状态码: {r.status_code}")
    data = r.json()
    print(f"   backend_status: {data.get('backend_status')}")
    print(f"   message: {data.get('message')}")
except Exception as e:
    print(f"   错误: {e}")

# 2. 测试文本块API
try:
    r = requests.get(f'http://localhost:{port}/api/text-blocks')
    print(f"\n2. /api/text-blocks:")
    print(f"   状态码: {r.status_code}")
    data = r.json()
    print(f"   success: {data.get('success')}")
    print(f"   count: {data.get('count')}")
    print(f"   thought_nodes_count: {data.get('thought_nodes_count')}")
    print(f"   total_connections: {data.get('total_connections')}")
    if not data.get('success'):
        print(f"   error: {data.get('error')}")
except Exception as e:
    print(f"   错误: {e}")

# 3. 测试聊天室历史API
try:
    r = requests.get(f'http://localhost:{port}/api/chatroom/history')
    print(f"\n3. /api/chatroom/history:")
    print(f"   状态码: {r.status_code}")
    data = r.json()
    print(f"   success: {data.get('success')}")
    print(f"   count: {data.get('count', 0)}")
    if not data.get('success'):
        print(f"   error: {data.get('error')}")
except Exception as e:
    print(f"   错误: {e}")
