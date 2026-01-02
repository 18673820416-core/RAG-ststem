# -*- coding: utf-8 -*-
"""测试基础智能体文本写入权限"""
import datetime
from src.base_agent import BaseAgent

print("="*60)
print("测试基础智能体文本写入权限")
print("="*60)

# 创建基础智能体
agent = BaseAgent('test_agent_write', 'base')
print(f"✅ 创建基础智能体: {agent.agent_id}, 类型: {agent.agent_type}")

# 测试1: 写入logs目录(应该成功)
test_file = f"logs/base_agent_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
test_content = f"""✅ 基础智能体文本写入成功!

测试信息:
- 智能体ID: {agent.agent_id}
- 智能体类型: {agent.agent_type}
- 测试时间: {datetime.datetime.now().isoformat()}
- 文件路径: {test_file}

这证明:所有智能体都有写文本的权限,只是不能写代码!
"""

print(f"\n📝 测试1: 写入logs目录")
print(f"   文件路径: {test_file}")
result = agent.call_tool('file_writing', {
    'file_path': test_file,
    'content': test_content
})

if result.get('success'):
    print(f"   ✅ 写入成功!")
    print(f"   📄 消息: {result.get('data', {}).get('message', 'N/A')}")
else:
    print(f"   ❌ 写入失败: {result.get('error')}")

# 测试2: 尝试写入代码文件(应该失败)
print(f"\n📝 测试2: 尝试写入代码文件(应该被拒绝)")
result2 = agent.call_tool('file_writing', {
    'file_path': 'src/test_code.py',
    'content': '# 测试代码'
})

if result2.get('success'):
    print(f"   ⚠️  意外成功! 权限控制失效!")
else:
    print(f"   ✅ 正确拒绝: {result2.get('error')}")

# 测试3: 尝试写入非允许目录(应该失败)
print(f"\n📝 测试3: 尝试写入非允许目录(应该被拒绝)")
result3 = agent.call_tool('file_writing', {
    'file_path': 'test_random_file.txt',
    'content': '随机内容'
})

if result3.get('success'):
    print(f"   ⚠️  意外成功! 目录限制失效!")
else:
    print(f"   ✅ 正确拒绝: {result3.get('error')}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
