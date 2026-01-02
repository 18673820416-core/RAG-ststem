"""
安全链路测试脚本

测试内容：
1. 主服务器注册
2. 查询占用端口
3. 模拟前哨击穿
4. 验证系统维护师日记记录

使用方法：
1. 确保静态服务器（10808端口）已启动
2. 运行此脚本：python test_security_chain.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:10808"

def test_register_server():
    """测试服务器注册"""
    print("\n=== 测试1：注册主服务器实例 ===")
    
    response = requests.post(
        f"{BASE_URL}/api/server/register",
        json={"port": 5000, "pid": 12345}
    )
    
    result = response.json()
    print(f"✅ 注册结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result.get("success", False)

def test_query_ports():
    """测试查询占用端口"""
    print("\n=== 测试2：查询占用端口 ===")
    
    response = requests.post(
        f"{BASE_URL}/api/server/occupied-ports",
        json={}
    )
    
    result = response.json()
    print(f"✅ 查询结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result.get("success", False)

def test_outpost_breach():
    """测试前哨击穿模拟"""
    print("\n=== 测试3：模拟前哨击穿（安全链路） ===")
    
    response = requests.post(
        f"{BASE_URL}/api/security/outpost-breach-test",
        json={}
    )
    
    result = response.json()
    print(f"✅ 击穿结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 检查关键步骤
    if result.get("success"):
        print("\n安全链路验证：")
        print(f"  1️⃣ 端口数据自毁: {result['self_destruct']['total_instances']} 个实例已销毁")
        print(f"  2️⃣ 主服务器警报: {len(result['alerted_servers'])} 个服务器已通知")
        
        if result['maintenance']['reported_to_maintenance']:
            print(f"  3️⃣ 维护师记录: ✅ {result['maintenance']['maintenance_response']['message']}")
        else:
            print(f"  3️⃣ 维护师记录: ⚠️ 未启动（{result['maintenance']['reason']}）")
    
    return result.get("success", False)

def main():
    """主测试流程"""
    print("=" * 60)
    print("🔐 安全链路测试（前哨-主堡-主脑）")
    print("=" * 60)
    
    try:
        # 测试1：注册服务器
        if not test_register_server():
            print("❌ 服务器注册失败，终止测试")
            return
        
        # 测试2：查询端口
        if not test_query_ports():
            print("❌ 查询端口失败，终止测试")
            return
        
        # 测试3：前哨击穿
        if not test_outpost_breach():
            print("❌ 前哨击穿测试失败")
            return
        
        print("\n" + "=" * 60)
        print("✅ 安全链路测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：请确保静态服务器（10808端口）已启动")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
