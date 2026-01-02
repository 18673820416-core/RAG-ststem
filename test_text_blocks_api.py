import requests
import json

try:
    response = requests.get('http://localhost:5000/api/text-blocks')
    print(f"✅ API响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 数据统计:")
        print(f"  - 总文本块数: {data.get('count', 0)}")
        print(f"  - 思维节点数: {data.get('thought_nodes_count', 0)}")
        print(f"  - 总关联数: {data.get('total_connections', 0)}")
        print(f"  - 返回块数: {len(data.get('blocks', []))}")
        
        if data.get('blocks'):
            print(f"\n第一个文本块示例:")
            first = data['blocks'][0]
            print(f"  - ID: {first.get('id')}")
            print(f"  - 标题: {first.get('title')}")
            print(f"  - 重要性: {first.get('importance')}")
    else:
        print(f"❌ 请求失败: {response.text}")
except Exception as e:
    print(f"❌ 错误: {e}")
