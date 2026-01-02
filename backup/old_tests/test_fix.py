#!/usr/bin/env python3
# @self-expose: {"id": "test_fix", "name": "Test Fix", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Fix功能"]}}
# -*- coding: utf-8 -*-
"""
测试数据收集者智能体修复结果
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_manager():
    """测试智能体管理器"""
    print("=== 测试智能体管理器 ===")
    
    try:
        from agent_manager import AgentManager
        
        # 初始化智能体管理器
        manager = AgentManager()
        print("✓ 智能体管理器初始化成功")
        
        # 检查智能体列表
        agents = list(manager.agents.keys())
        print(f"✓ 当前管理的智能体: {agents}")
        
        # 检查是否包含数据收集者智能体
        if 'data_collector' in agents:
            print("✓ 数据收集者智能体已成功集成到智能体管理器")
        else:
            print("✗ 数据收集者智能体未集成到智能体管理器")
            return False
            
        # 测试路由功能
        print("\\n=== 测试路由功能 ===")
        test_cases = [
            ("收集数据", "data_collector"),
            ("数据采集", "data_collector"),
            ("吃饭时间", "data_collector"),
            ("系统架构", "system_architect"),
            ("代码实现", "code_implementer")
        ]
        
        for query, expected_agent in test_cases:
            result = manager.route_request(query)
            status = "✓" if result == expected_agent else "✗"
            print(f"{status} 查询: '{query}' -> 路由到: {result} (期望: {expected_agent})")
            
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_multi_agent_chatroom():
    """测试多智能体聊天室"""
    print("\\n=== 测试多智能体聊天室 ===")
    
    try:
        from multi_agent_chatroom import MultiAgentChatroom
        
        # 初始化聊天室
        chatroom = MultiAgentChatroom()
        print("✓ 多智能体聊天室初始化成功")
        
        # 检查智能体列表
        agents = list(chatroom.agents.keys())
        print(f"✓ 聊天室智能体: {agents}")
        
        # 检查是否包含数据收集者智能体
        from multi_agent_chatroom import AgentRole
        if AgentRole.DATA_COLLECTOR in agents:
            print("✓ 数据收集者智能体已成功集成到聊天室")
        else:
            print("✗ 数据收集者智能体未集成到聊天室")
            return False
            
        # 测试路由功能
        print("\\n=== 测试聊天室路由功能 ===")
        test_cases = [
            ("收集数据", AgentRole.DATA_COLLECTOR),
            ("数据采集", AgentRole.DATA_COLLECTOR),
            ("吃饭", AgentRole.DATA_COLLECTOR),
            ("系统设计", AgentRole.ARCHITECT),
            ("代码", AgentRole.IMPLEMENTER)
        ]
        
        for query, expected_role in test_cases:
            result = chatroom.route_request(query)
            status = "✓" if result == expected_role else "✗"
            print(f"{status} 查询: '{query}' -> 路由到: {result} (期望: {expected_role})")
            
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试数据收集者智能体修复...")
    print("=" * 50)
    
    # 运行测试
    manager_success = test_agent_manager()
    chatroom_success = test_multi_agent_chatroom()
    
    print("\\n" + "=" * 50)
    if manager_success and chatroom_success:
        print("🎉 所有测试通过！数据收集者智能体修复成功！")
    else:
        print("❌ 部分测试失败，请检查修复情况。")