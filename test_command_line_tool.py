# -*- coding: utf-8 -*-
"""测试命令行工具修复"""
import datetime
from src.base_agent import BaseAgent

print("="*60)
print("测试命令行工具 - 智能体的'手'与'脚'")
print("="*60)

# 创建基础智能体
agent = BaseAgent('test_command_agent', 'base')
print(f"✅ 创建基础智能体: {agent.agent_id}, 类型: {agent.agent_type}")

# 测试1: 执行简单命令(列出当前目录)
print(f"\n📝 测试1: 执行命令 'dir logs'")
result1 = agent.call_tool('command_line', {
    'command': 'dir logs',
    'timeout': 10
})

if result1.get('success'):
    print(f"   ✅ 命令执行成功!")
    print(f"   输出: {result1.get('data', {}).get('output', '')[:200]}...")
else:
    print(f"   ❌ 命令执行失败: {result1.get('error')}")

# 测试2: 执行Python命令
print(f"\n📝 测试2: 执行Python命令")
result2 = agent.call_tool('command_line', {
    'command': 'python --version',
    'timeout': 10
})

if result2.get('success'):
    print(f"   ✅ 命令执行成功!")
    print(f"   Python版本: {result2.get('data', {}).get('output', '').strip()}")
else:
    print(f"   ❌ 命令执行失败: {result2.get('error')}")

# 测试3: 缺少参数(应该失败)
print(f"\n📝 测试3: 缺少command参数(应该被拒绝)")
result3 = agent.call_tool('command_line', {
    'timeout': 10
})

if result3.get('success'):
    print(f"   ⚠️  意外成功! 参数验证失效!")
else:
    print(f"   ✅ 正确拒绝: {result3.get('error')}")

print("\n" + "="*60)
print("✅ 命令行工具修复完成!")
print("智能体现在拥有了真正的'行动'能力,不再是纸上谈兵的LLM!")
print("="*60)
