#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试系统维护师智能体集成
"""

import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 80)
print("测试系统维护师智能体集成")
print("=" * 80)

# 测试1: 智能体发现
print("\n【测试1】智能体发现机制")
print("-" * 80)
try:
    from src.agent_discovery_engine import get_discovery_engine
    engine = get_discovery_engine()
    agents = engine.discover_agents()
    
    print(f"✅ 发现 {len(agents)} 个智能体:")
    for agent_id in agents.keys():
        print(f"  - {agent_id}")
    
    if "system_maintenance_agent" in agents:
        print("\n✅ 系统维护师智能体已被发现机制识别")
    else:
        print("\n❌ 系统维护师智能体未被发现")
        
except Exception as e:
    print(f"❌ 智能体发现测试失败: {e}")

# 测试2: 直接加载智能体
print("\n【测试2】直接加载系统维护师智能体")
print("-" * 80)
try:
    from src.system_maintenance_agent import get_system_maintenance
    
    agent = get_system_maintenance()
    print(f"✅ 系统维护师智能体加载成功")
    print(f"  智能体ID: {agent.agent_id}")
    print(f"  智能体类型: {agent.agent_type}")
    print(f"  目的: {agent.purpose}")
    
    # 测试基本功能
    print("\n【测试3】系统维护师核心功能")
    print("-" * 80)
    
    # 测试健康巡检
    health_result = agent.monitor_system_health()
    print(f"✅ 健康巡检完成")
    print(f"  总体状态: {health_result.get('overall_status', 'unknown')}")
    print(f"  发现问题数: {len(health_result.get('issues_found', []))}")
    
    # 测试配置校验
    config_result = agent.validate_configuration()
    print(f"\n✅ 配置校验完成")
    print(f"  配置有效: {config_result.get('is_valid', False)}")
    
except Exception as e:
    print(f"❌ 智能体加载测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 聊天室集成
print("\n【测试4】多智能体聊天室集成")
print("-" * 80)
try:
    from src.multi_agent_chatroom import AgentRole
    
    # 检查角色枚举
    print("✅ AgentRole枚举成员:")
    for role in AgentRole:
        print(f"  - {role.value}")
    
    if any(role.value == "系统维护师" for role in AgentRole):
        print("\n✅ 系统维护师已添加到AgentRole枚举")
    else:
        print("\n❌ 系统维护师未添加到AgentRole枚举")
        
except Exception as e:
    print(f"❌ 聊天室集成测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
