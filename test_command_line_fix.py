#!/usr/bin/env python3
# @self-expose: {"id": "test_command_line_fix", "name": "Test Command Line Fix", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Command Line Fix功能"]}}
# -*- coding: utf-8 -*-
"""
测试RAG系统命令行工具功能修复

这个脚本用于测试修复后的命令行工具功能是否正常工作。
它将直接调用BaseAgent的respond方法，并检查它是否能够正确处理工具调用。
"""

import sys
import os

# 添加正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.base_agent import BaseAgent

# 创建BaseAgent实例
base_agent = BaseAgent(agent_id="test_agent", agent_type="test_agent", prompt_file="src/agent_prompts/base_agent_prompt.md")

# 测试消息：直接请求执行命令行工具
# 这里我们使用一个简单的命令，查看当前目录下的文件
test_message = "请执行命令 'ls -la' 查看当前目录下的文件"

print("发送测试消息：")
print(test_message)
print("\n等待响应...")

# 调用respond方法，测试工具调用逻辑
response = base_agent.respond(test_message)

print("\n响应结果：")
print(response)

# 检查响应是否包含工具调用
if "tool_call" in response:
    print("\n✅ 测试通过：响应中包含工具调用")
    print("\n现在，让我们手动测试工具调用执行逻辑...")
    
    # 模拟工具调用执行逻辑
    import json
    import re
    
    try:
        # 打印原始响应，查看实际内容
        print(f"\n原始响应：")
        print(repr(response))
        
        # 直接使用响应作为JSON字符串，因为它已经是一个完整的JSON格式了
        tool_call_json = response
        print(f"\n使用的JSON：")
        print(repr(tool_call_json))
        
        # 解析工具调用信息
        tool_call = json.loads(tool_call_json)['tool_call']
        tool_name = tool_call['name']
        parameters = tool_call['parameters']
        
        print(f"\n✅ 成功提取工具调用信息：")
        print(f"   工具名称：{tool_name}")
        print(f"   参数：{parameters}")
        
        # 执行工具调用
        print(f"\n✅ 准备执行工具调用：")
        print(f"   调用工具：{tool_name}")
        print(f"   参数：{parameters}")
        
        # 调用工具集成器执行工具调用
        tool_result = base_agent.tool_integrator.call_tool(
            tool_name=tool_name,
            parameters=parameters,
            caller_info={"agent_id": base_agent.agent_id, "agent_type": base_agent.agent_type},
            usage_intention="测试工具调用"
        )
        
        print(f"\n✅ 工具调用执行成功！")
        print(f"\n工具调用结果：")
        print(json.dumps(tool_result, ensure_ascii=False, indent=2))
        
        print("\n🎉 所有测试通过！RAG系统命令行工具功能修复成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ 测试失败：响应中不包含工具调用")
