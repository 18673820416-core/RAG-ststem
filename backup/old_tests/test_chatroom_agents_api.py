#!/usr/bin/env python3
# @self-expose: {"id": "test_chatroom_agents_api", "name": "Test Chatroom Agents Api", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Chatroom Agents Api功能"]}}
# -*- coding: utf-8 -*-
"""
测试聊天室智能体获取API
验证BaseAgent基类过滤功能
"""

import requests
import json

def test_chatroom_agents_api():
    """测试聊天室智能体获取API"""
    print("=== 测试聊天室智能体获取API ===")
    
    try:
        # 获取智能体列表
        response = requests.get('http://localhost:10808/api/chatroom/agents')
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            agents = response.json()
            print(f'获取到的智能体数量: {len(agents)}')
            print('智能体列表:')
            
            agent_names = []
            for agent in agents:
                name = agent.get('name', '未知')
                desc = agent.get('description', '无描述')
                agent_type = agent.get('type', '未知类型')
                print(f'  - {name} ({agent_type}): {desc}')
                agent_names.append(name)
                
            # 验证是否包含BaseAgent
            if 'BaseAgent' in agent_names:
                print('❌ 错误: 仍然包含BaseAgent基类智能体')
                print('智能体发现引擎的过滤逻辑可能未生效')
                return False
            else:
                print('✅ 成功: BaseAgent基类智能体已被正确过滤')
                
            # 验证是否包含正确的智能体
            expected_agents = ['SystemArchitectAgent', 'SchemeEvaluatorAgent', 'CodeImplementerAgent', 'DataCollectorAgent']
            found_expected = [agent for agent in expected_agents if agent in agent_names]
            
            print(f'期望的智能体: {expected_agents}')
            print(f'找到的期望智能体: {found_expected}')
            
            if len(found_expected) == len(expected_agents):
                print('✅ 成功: 所有期望的智能体都已正确发现')
            else:
                missing = set(expected_agents) - set(found_expected)
                print(f'⚠️ 警告: 缺少以下智能体: {list(missing)}')
                
            return True
            
        else:
            print(f'响应内容: {response.text}')
            return False
            
    except Exception as e:
        print(f'错误: {str(e)}')
        return False

def test_agent_discovery_engine():
    """直接测试智能体发现引擎"""
    print("\n=== 直接测试智能体发现引擎 ===")
    
    try:
        import sys
        from pathlib import Path
        
        # 添加路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        sys.path.insert(0, str(current_dir / "src"))
        
        from src.agent_discovery_engine import AgentDiscoveryEngine
        
        # 创建发现引擎实例
        discovery_engine = AgentDiscoveryEngine()
        
        # 发现智能体
        agents_info = discovery_engine.discover_agents()
        print(f'智能体发现引擎发现的智能体数量: {len(agents_info)}')
        
        agent_names = []
        for agent_info in agents_info:
            name = agent_info.get('class_name', '未知')
            agent_names.append(name)
            print(f'  - {name}')
            
        # 验证是否包含BaseAgent
        if 'BaseAgent' in agent_names:
            print('❌ 错误: 智能体发现引擎仍然发现BaseAgent')
            return False
        else:
            print('✅ 成功: 智能体发现引擎已正确过滤BaseAgent')
            return True
            
    except Exception as e:
        print(f'错误: {str(e)}')
        return False

def main():
    """主测试函数"""
    print("开始测试聊天室智能体获取功能...\n")
    
    # 测试API
    api_success = test_chatroom_agents_api()
    
    # 测试发现引擎
    engine_success = test_agent_discovery_engine()
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    print(f"聊天室API测试: {'✅ 通过' if api_success else '❌ 失败'}")
    print(f"发现引擎测试: {'✅ 通过' if engine_success else '❌ 失败'}")
    
    if api_success and engine_success:
        print("\n🎉 所有测试通过！BaseAgent过滤功能正常工作。")
        print("聊天室现在能正确动态获取可用的智能体。")
        return True
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)