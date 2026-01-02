#!/usr/bin/env python
# @self-expose: {"id": "test_thinking_transparency", "name": "Test Thinking Transparency", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Thinking Transparency功能"]}}
# -*- coding: utf-8 -*-
"""
测试思维透明化功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent

# 创建一个简单的测试智能体
test_agent = BaseAgent(
    agent_id="test_agent",
    agent_type="test_type",
    prompt_file="test_prompt.md"
)

# 测试思维透明化功能
print("=== 测试思维透明化功能 ===")
response = test_agent.respond("你好，测试一下你的思维透明化功能")
print("\n智能体响应：")
print(response)
print("\n=== 测试完成 ===")
