#!/usr/bin/env python
# @self-expose: {"id": "test_all_tools", "name": "Test All Tools", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test All Tools功能"]}}
# -*- coding: utf-8 -*-
"""
测试基类智能体注册的所有工具
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent

def test_all_tools():
    """测试所有注册的工具"""
    print("=== 测试基类智能体所有工具 ===")
    
    # 创建智能体实例
    agent = BaseAgent(
        agent_id="test_agent",
        agent_type="test",
        prompt_file="test_prompt.md"
    )
    
    print("\n1. 智能体创建成功")
    print(f"   可用工具数量: {len(agent.available_tools)}")
    print(f"   工具列表: {agent.available_tools}")
    
    # 测试工具状态
    print("\n2. 工具状态:")
    for tool_name, status in agent.tool_status.items():
        print(f"   {tool_name}: {'可用' if status['available'] else '不可用'} - {status['type']}")
    
    # 测试command_line工具
    print("\n3. 测试command_line工具:")
    try:
        # 使用智能体的process_message方法测试
        response = agent.process_message("请执行命令：echo '测试command_line工具'")
        print(f"   响应: {response}")
        if "成功" in response:
            print("   ✓ command_line工具测试通过")
        else:
            print("   ✗ command_line工具测试失败")
    except Exception as e:
        print(f"   ✗ command_line工具测试失败: {e}")
    
    # 测试file_writing工具
    print("\n4. 测试file_writing工具:")
    try:
        response = agent.process_message("请创建一个测试文件，内容为'测试file_writing工具'")
        print(f"   响应: {response}")
        
        # 检查文件是否创建成功
        test_file = "test_output.txt"
        if os.path.exists(test_file):
            print("   ✓ 文件创建成功")
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   文件内容: {content}")
            
            # 测试file_reading工具
            print("\n5. 测试file_reading工具:")
            response = agent.process_message(f"请读取文件 {test_file}")
            print(f"   响应: {response}")
            if "测试file_writing工具" in response:
                print("   ✓ file_reading工具测试通过")
            else:
                print("   ✗ file_reading工具测试失败")
            
            # 清理测试文件
            os.remove(test_file)
            print("   测试文件已清理")
        else:
            print("   ✗ 文件创建失败")
    except Exception as e:
        print(f"   ✗ file_writing工具测试失败: {e}")
    
    # 测试统一记忆系统工具
    print("\n6. 测试统一记忆系统工具:")
    try:
        # 测试memory_creation工具
        memory_id = agent.create_memory(
            content="测试记忆内容",
            memory_type="test",
            priority="high",
            tags=["test", "memory"]
        )
        print(f"   ✓ memory_creation工具测试通过，记忆ID: {memory_id}")
        
        # 测试get_memories工具
        memories = agent.get_memories({"type": "test"})
        print(f"   ✓ get_memories工具测试通过，找到记忆: {len(memories)} 条")
        
        # 测试delete_memory工具
        if memories:
            delete_result = agent.delete_memory(memory_id)
            print(f"   ✓ delete_memory工具测试通过，删除结果: {delete_result}")
    except Exception as e:
        print(f"   ✗ 统一记忆系统工具测试失败: {e}")
    
    # 测试工具调用失败处理
    print("\n7. 测试工具调用失败处理:")
    try:
        # 测试不存在的命令
        response = agent.process_message("请执行命令：nonexistent_command_123")
        print(f"   响应: {response}")
        if "失败" in response and "重试" in response:
            print("   ✓ 工具调用失败处理测试通过")
        else:
            print("   ✗ 工具调用失败处理测试失败")
    except Exception as e:
        print(f"   ✗ 工具调用失败处理测试失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_all_tools()
