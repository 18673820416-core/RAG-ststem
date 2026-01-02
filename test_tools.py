#!/usr/bin/env python
# @self-expose: {"id": "test_tools", "name": "Test Tools", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Tools功能"]}}
# -*- coding: utf-8 -*-
"""
测试工具功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent

def test_agent_tools():
    """测试智能体工具功能"""
    print("=== 测试智能体工具功能 ===")
    
    # 创建智能体实例
    agent = BaseAgent(
        agent_id="test_agent",
        agent_type="test",
        prompt_file="test_prompt.md"
    )
    
    print("智能体创建成功")
    
    # 测试工具注册
    print("\n1. 测试工具注册:")
    # 调用process_message方法，该方法会获取工具状态
    response = agent.process_message("你好，测试一下工具功能")
    print("process_message调用成功")
    
    print("\n2. 测试工具调用:")
    # 测试command_line工具
    command_test_response = agent.process_message("请执行命令：echo 'Hello, World!'")
    print(f"命令行工具测试响应: {command_test_response}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_agent_tools()
