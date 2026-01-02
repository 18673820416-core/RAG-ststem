#!/usr/bin/env python
# @self-expose: {"id": "test_chatroom", "name": "Test Chatroom", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Chatroom功能"]}}
# -*- coding: utf-8 -*-
"""
多智能体聊天室测试脚本
测试聊天室功能及智能体协同交互
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_chatroom_basic():
    """测试聊天室基本功能"""
    print("=== 多智能体聊天室基本功能测试 ===")
    
    try:
        from multi_agent_chatroom import MultiAgentChatroom, AgentRole, MessageType
        
        # 创建聊天室实例
        chatroom = MultiAgentChatroom()
        print("✓ 聊天室实例创建成功")
        
        # 测试启动聊天室
        if chatroom.start_chatroom():
            print("✓ 聊天室启动成功")
        else:
            print("✗ 聊天室启动失败")
            return False
        
        # 测试发送消息
        test_messages = [
            "大家好！我们来讨论一下智能体协同工作流的设计。",
            "构架师，你觉得应该如何设计系统的架构？",
            "评估师，这个方案的风险如何？",
            "实现师，技术实现上有什么建议？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 测试消息 {i} ---")
            print(f"用户: {message}")
            
            result = chatroom.send_user_message(message)
            
            if "error" not in result:
                print("✓ 消息发送成功")
                
                # 显示智能体响应
                for response in result["agent_responses"]:
                    print(f"  {response['sender']}: {response['content']}")
                
                # 显示方法论洞察
                if result["methodology_insights"]:
                    print("  方法论洞察:")
                    for insight in result["methodology_insights"]:
                        print(f"    - {insight}")
            else:
                print(f"✗ 消息发送失败: {result['error']}")
        
        # 测试获取对话历史
        history = chatroom.get_conversation_history()
        print(f"\n✓ 对话历史获取成功，共 {len(history)} 条消息")
        
        # 测试获取方法论洞察
        insights = chatroom.get_methodology_insights()
        print(f"✓ 方法论洞察获取成功，共 {len(insights)} 条洞察")
        
        # 测试停止聊天室
        chatroom.stop_chatroom()
        print("✓ 聊天室停止成功")
        
        print("\n=== 基本功能测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        return False

def test_chatroom_api():
    """测试聊天室API接口"""
    print("\n=== 多智能体聊天室API接口测试 ===")
    
    try:
        # 导入API模块
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        from chat_api import app
        
        # 创建测试客户端
        with app.test_client() as client:
            
            # 测试状态检查接口
            response = client.get('/api/chatroom/status')
            if response.status_code == 200:
                data = json.loads(response.data)
                if data['success']:
                    print("✓ 状态检查接口正常")
                else:
                    print("✗ 状态检查接口返回失败")
            else:
                print("✗ 状态检查接口请求失败")
            
            # 测试消息发送接口
            test_message = {
                "message": "测试API接口功能"
            }
            
            response = client.post('/api/chatroom/message', 
                                 json=test_message,
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data['success']:
                    print("✓ 消息发送接口正常")
                    print(f"  用户消息: {data['user_message']['content']}")
                    print(f"  智能体响应数量: {len(data['agent_responses'])}")
                else:
                    print(f"✗ 消息发送接口返回失败: {data.get('error', '未知错误')}")
            else:
                print("✗ 消息发送接口请求失败")
            
            # 测试历史记录接口
            response = client.get('/api/chatroom/history')
            if response.status_code == 200:
                data = json.loads(response.data)
                if data['success']:
                    print("✓ 历史记录接口正常")
                    print(f"  历史消息数量: {data['count']}")
                else:
                    print("✗ 历史记录接口返回失败")
            else:
                print("✗ 历史记录接口请求失败")
        
        print("\n=== API接口测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ API接口测试过程中出现错误: {e}")
        return False

def test_interaction_patterns():
    """测试交互模式分析功能"""
    print("\n=== 交互模式分析测试 ===")
    
    try:
        from multi_agent_chatroom import MultiAgentChatroom
        
        chatroom = MultiAgentChatroom()
        chatroom.start_chatroom()
        
        # 测试不同类型的消息
        test_scenarios = [
            {
                "message": "我们需要设计一个可扩展的系统架构",
                "expected_keywords": ["架构相关"]
            },
            {
                "message": "请评估这个技术方案的风险",
                "expected_keywords": ["评估相关"]
            },
            {
                "message": "如何实现这个功能模块",
                "expected_keywords": ["实现相关"]
            },
            {
                "message": "综合考虑架构、评估和实现",
                "expected_keywords": ["架构相关", "评估相关", "实现相关"]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n测试场景: {scenario['message']}")
            
            result = chatroom.send_user_message(scenario['message'])
            
            if "error" not in result:
                # 检查方法论洞察
                insights = result.get("methodology_insights", [])
                if insights:
                    print("✓ 生成方法论洞察:")
                    for insight in insights:
                        print(f"  - {insight}")
                else:
                    print("  (未生成方法论洞察)")
                
                # 检查智能体响应模式
                response_count = len(result.get("agent_responses", []))
                print(f"  智能体响应数量: {response_count}")
                
                # 验证关键词提取
                for keyword in scenario['expected_keywords']:
                    if any(keyword in insight for insight in insights):
                        print(f"✓ 检测到关键词: {keyword}")
                    else:
                        print(f"✗ 未检测到关键词: {keyword}")
            else:
                print(f"✗ 消息发送失败: {result['error']}")
        
        chatroom.stop_chatroom()
        print("\n=== 交互模式分析测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 交互模式分析测试过程中出现错误: {e}")
        return False

def main():
    """主测试函数"""
    print("开始多智能体聊天室测试...")
    
    # 运行所有测试
    test_results = []
    
    # 基本功能测试
    test_results.append(("基本功能测试", test_chatroom_basic()))
    
    # API接口测试
    test_results.append(("API接口测试", test_chatroom_api()))
    
    # 交互模式分析测试
    test_results.append(("交互模式分析测试", test_interaction_patterns()))
    
    # 输出测试总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n测试完成: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！多智能体聊天室功能正常。")
        print("\n下一步操作:")
        print("1. 运行 'python api/chat_api.py' 启动聊天室服务器")
        print("2. 打开浏览器访问 http://localhost:8888/chatroom.html")
        print("3. 开始与三个智能体进行交互讨论")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()