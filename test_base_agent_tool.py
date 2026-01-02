#!/usr/bin/env python3
# @self-expose: {"id": "test_base_agent_tool", "name": "Test Base Agent Tool", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Base Agent Tool功能"]}}
# -*- coding: utf-8 -*-
"""
测试base_agent.py中的工具调用逻辑
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.base_agent import BaseAgent

# 创建BaseAgent实例
base_agent = BaseAgent(agent_id="test_agent", agent_type="test_agent", prompt_file="src/agent_prompts/base_agent_prompt.md")

# 测试消息：直接发送工具调用JSON
# 这里我们使用命令行工具的调用格式
test_message = "请执行命令 'ls -la' 查看当前目录下的文件"

print("发送测试消息：")
print(test_message)
print("\n等待响应...")

# 调用respond方法，测试工具调用逻辑
response = base_agent.respond(test_message)

print("\n响应结果：")
print(response)
