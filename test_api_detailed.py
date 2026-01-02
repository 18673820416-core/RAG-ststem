import requests
import json
import time

print("🔍 开始详细测试 /api/text-blocks 接口...")
print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

try:
    start_time = time.time()
    response = requests.get('http://localhost:5000/api/text-blocks', timeout=30)
    elapsed = time.time() - start_time
    
    print(f"✅ API响应状态码: {response.status_code}")
    print(f"⏱️  响应时间: {elapsed:.2f}秒\n")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("📦 完整响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应: {response.text[:500]}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"响应内容: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时（30秒）")
except requests.exceptions.ConnectionError:
    print("❌ 连接失败 - 服务器可能未运行")
except Exception as e:
    print(f"❌ 未知错误: {e}")
    import traceback
    traceback.print_exc()
