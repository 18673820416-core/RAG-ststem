#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能体和工具发现"""

import sys
sys.path.insert(0, 'src')

from agent_discovery_engine import AgentDiscoveryEngine

print("="*60)
print("测试智能体和工具发现机制")
print("="*60)

engine = AgentDiscoveryEngine()

print("\n1. 开始发现智能体...")
print("-"*60)
agents = engine.discover_agents()

if "error" in agents:
    print(f"❌ 发现失败: {agents['error']}")
else:
    agent_count = len([k for k in agents.keys() if not k.startswith("error")])
    print(f"✅ 成功发现 {agent_count} 个智能体")
    
    # 显示前5个智能体
    for i, (agent_id, info) in enumerate(list(agents.items())[:5], 1):
        print(f"\n  智能体 #{i}:")
        print(f"    ID: {agent_id}")
        print(f"    名称: {info.get('agent_name')}")
        print(f"    发现方法: {info.get('discovery_method')}")
        print(f"    版本: {info.get('version')}")

print("\n\n2. 开始发现工具...")
print("-"*60)
tools = engine.discover_tools(auto_submit_review=False)

if "error" in tools:
    print(f"❌ 发现失败: {tools['error']}")
else:
    tool_count = len([k for k in tools.keys() if not k.startswith("error")])
    print(f"✅ 成功发现 {tool_count} 个工具")
    
    # 显示前5个工具
    for i, (tool_id, info) in enumerate(list(tools.items())[:5], 1):
        print(f"\n  工具 #{i}:")
        print(f"    ID: {tool_id}")
        print(f"    名称: {info.get('tool_name')}")
        print(f"    发现方法: {info.get('discovery_method')}")
        print(f"    版本: {info.get('version')}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
