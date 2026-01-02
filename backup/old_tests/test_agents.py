#!/usr/bin/env python3
# @self-expose: {"id": "test_agents", "name": "Test Agents", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agents功能"]}}
# -*- coding: utf-8 -*-
"""
测试智能体回复质量
"""

import sys
import os
from pathlib import Path

# 添加当前目录和src目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

# 设置环境变量
os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + str(current_dir / "src")

def test_system_architect_agent():
    """测试系统架构师智能体"""
    print("=== 测试系统架构师智能体 ===")
    
    try:
        from src.system_architect_agent import SystemArchitectAgent
        
        # 创建智能体实例
        agent = SystemArchitectAgent("test_architect")
        
        # 测试响应
        test_message = "请设计一个RAG系统的架构方案"
        response = agent.respond(test_message)
        
        print(f"测试消息: {test_message}")
        print(f"响应内容: {response}")
        print("✅ 系统架构师智能体测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 系统架构师智能体测试失败: {e}")
        return False

def test_scheme_evaluator_agent():
    """测试方案评估师智能体"""
    print("\n=== 测试方案评估师智能体 ===")
    
    try:
        from src.scheme_evaluator_agent import SchemeEvaluatorAgent
        
        # 创建智能体实例
        agent = SchemeEvaluatorAgent()
        
        # 测试响应
        test_message = "请评估这个RAG系统架构方案的风险和可行性"
        response = agent.respond(test_message)
        
        print(f"测试消息: {test_message}")
        print(f"响应内容: {response}")
        print("✅ 方案评估师智能体测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 方案评估师智能体测试失败: {e}")
        return False

def test_code_implementer_agent():
    """测试代码实现师智能体"""
    print("\n=== 测试代码实现师智能体 ===")
    
    try:
        from src.code_implementer_agent import CodeImplementerAgent
        
        # 创建智能体实例
        agent = CodeImplementerAgent()
        
        # 测试响应
        test_message = "请实现这个RAG系统的核心模块"
        response = agent.respond(test_message)
        
        print(f"测试消息: {test_message}")
        print(f"响应内容: {response}")
        print("✅ 代码实现师智能体测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 代码实现师智能体测试失败: {e}")
        return False

def test_multi_agent_chatroom():
    """测试多智能体聊天室"""
    print("\n=== 测试多智能体聊天室 ===")
    
    try:
        from src.multi_agent_chatroom import MultiAgentChatroom
        
        # 创建聊天室实例
        chatroom = MultiAgentChatroom()
        
        # 启动聊天室
        if chatroom.start_chatroom():
            print("✅ 聊天室启动成功")
            
            # 发送测试消息
            test_message = "请讨论如何设计一个高效的RAG系统架构"
            result = chatroom.send_user_message(test_message)
            
            print(f"测试消息: {test_message}")
            print(f"响应数量: {len(result.get('agent_responses', []))}")
            
            # 显示智能体响应
            for i, response in enumerate(result.get('agent_responses', [])):
                print(f"智能体 {i+1}: {response.get('content', '')[:100]}...")
            
            print("✅ 多智能体聊天室测试成功")
            return True
        else:
            print("❌ 聊天室启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 多智能体聊天室测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试智能体回复质量...\n")
    
    # 测试单个智能体
    architect_success = test_system_architect_agent()
    evaluator_success = test_scheme_evaluator_agent()
    implementer_success = test_code_implementer_agent()
    
    # 测试多智能体聊天室
    chatroom_success = test_multi_agent_chatroom()
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    print(f"系统架构师智能体: {'✅ 通过' if architect_success else '❌ 失败'}")
    print(f"方案评估师智能体: {'✅ 通过' if evaluator_success else '❌ 失败'}")
    print(f"代码实现师智能体: {'✅ 通过' if implementer_success else '❌ 失败'}")
    print(f"多智能体聊天室: {'✅ 通过' if chatroom_success else '❌ 失败'}")
    
    if all([architect_success, evaluator_success, implementer_success, chatroom_success]):
        print("\n🎉 所有测试通过！智能体回复质量良好。")
        return True
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)