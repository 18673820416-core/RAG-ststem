#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试修复后的智能体发现机制"""

import sys
sys.path.insert(0, 'src')

from agent_discovery_engine import discover_all_components

print("="*60)
print("测试智能体发现机制")
print("="*60)

result = discover_all_components()

agents = result["agents"]
tools = result["tools"]
summary = result["summary"]

print(f"\n✅ 发现 {summary['total_agents']} 个智能体")
print(f"✅ 发现 {summary['total_tools']} 个工具")
print(f"发现时间: {summary['discovery_time']}")

print("\n智能体列表:")
print("-"*60)
for i, (agent_id, info) in enumerate(agents.items(), 1):
    print(f"{i}. {agent_id}")
    print(f"   名称: {info.get('agent_name')}")
    print(f"   文件: {info.get('file_path')}")
    print(f"   版本: {info.get('version')}")
    print(f"   发现方法: {info.get('discovery_method')}")
    print()

if tools:
    print("\n工具列表:")
    print("-"*60)
    for i, (tool_id, info) in enumerate(list(tools.items())[:5], 1):
        print(f"{i}. {tool_id}")
        print(f"   名称: {info.get('tool_name')}")
        print()

print("="*60)
print("测试完成")
print("="*60)
