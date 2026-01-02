#!/usr/bin/env python3
# @self-expose: {"id": "test_agents_api", "name": "Test Agents Api", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agents Api功能"]}}
"""
测试聊天室智能体获取API
验证 /api/agents 端点是否正常工作
"""

import requests
import json

def test_agents_api():
    """测试智能体获取API"""
    print("=== 测试聊天室智能体获取API ===")
    
    # API基础URL
    base_url = "http://localhost:10808"
    
    try:
        # 测试健康检查端点
        print("1. 检查服务器状态...")
        health_response = requests.get(f"{base_url}/api/health")
        print(f"   健康检查状态码: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print("   ✓ 服务器运行正常")
        else:
            print("   ✗ 服务器可能未正常运行")
            return False
        
        # 测试智能体获取端点
        print("\n2. 测试智能体获取端点...")
        agents_response = requests.get(f"{base_url}/api/agents")
        print(f"   智能体API状态码: {agents_response.status_code}")
        
        if agents_response.status_code == 200:
            data = agents_response.json()
            print(f"   ✓ API调用成功")
            print(f"   成功状态: {data.get('success', False)}")
            print(f"   消息: {data.get('message', 'N/A')}")
            print(f"   智能体数量: {data.get('count', 0)}")
            
            # 显示智能体列表
            agents = data.get('agents', [])
            if agents:
                print("\n   获取到的智能体列表:")
                for i, agent in enumerate(agents, 1):
                    print(f"   {i}. {agent.get('name', '未知')} (ID: {agent.get('id', '未知')})")
                    print(f"      描述: {agent.get('description', '无描述')}")
                    print(f"      状态: {agent.get('status', '未知')}")
                    print(f"      颜色: {agent.get('color', '默认')}")
            else:
                print("   ⚠ 未获取到智能体列表")
                
            return True
        else:
            print(f"   ✗ API调用失败，状态码: {agents_response.status_code}")
            if agents_response.text:
                print(f"   错误信息: {agents_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"   ✗ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("开始测试聊天室智能体获取功能...")
    success = test_agents_api()
    
    if success:
        print("\n🎉 智能体获取API测试完成！")
    else:
        print("\n❌ 智能体获取API测试失败！")
    
    print("\n提示: 如果测试失败，请检查:")
    print("1. 服务器是否正在运行 (python stable_start_server.py)")
    print("2. 端口10808是否被占用")
    print("3. API端点路径是否正确")