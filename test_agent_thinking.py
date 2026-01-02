#!/usr/bin/env python3
# @self-expose: {"id": "test_agent_thinking", "name": "Test Agent Thinking", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agent Thinking功能"]}}
# -*- coding: utf-8 -*-
"""
测试智能体思维过程记录功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent

def test_agent_thinking():
    """测试智能体思维过程记录"""
    print("=== 智能体思维过程测试 ===")
    
    try:
        # 创建智能体实例
        agent = BaseAgent(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_file="test_prompt.txt"
        )
        
        print("智能体创建成功")
        
        # 测试消息
        test_message = "再次测试你的基本工具是否正常，报告给我。"
        print(f"\n发送测试消息: {test_message}")
        
        # 处理消息
        response = agent.process_message(test_message)
        
        print(f"\n智能体响应: {response}")
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_thinking()