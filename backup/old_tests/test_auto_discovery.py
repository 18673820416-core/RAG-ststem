#!/usr/bin/env python
# @self-expose: {"id": "test_auto_discovery", "name": "Test Auto Discovery", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Auto Discovery功能"]}}
# -*- coding: utf-8 -*-
"""
测试自动发现机制
开发提示词来源：用户希望实现智能体和工具的自动发现机制
"""

import sys
import os
import logging

# 添加src目录到路径
sys.path.insert(0, 'src')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_auto_discovery():
    """测试自动发现机制"""
    print("=== 测试自动发现机制 ===")
    
    try:
        # 导入智能体管理器
        from agent_manager import AgentManager
        
        print("\n1. 测试启用自动发现的智能体管理器")
        manager_with_discovery = AgentManager(enable_auto_discovery=True)
        
        # 获取发现信息
        discovery_info = manager_with_discovery.get_discovery_info()
        print(f"自动发现启用状态: {discovery_info['auto_discovery_enabled']}")
        print(f"智能体总数: {discovery_info['total_agents']}")
        print(f"智能体类型: {discovery_info['agent_types']}")
        print(f"发现来源: {discovery_info['discovery_sources']}")
        
        print("\n2. 测试禁用自动发现的智能体管理器")
        manager_manual = AgentManager(enable_auto_discovery=False)
        
        discovery_info_manual = manager_manual.get_discovery_info()
        print(f"自动发现启用状态: {discovery_info_manual['auto_discovery_enabled']}")
        print(f"智能体总数: {discovery_info_manual['total_agents']}")
        print(f"智能体类型: {discovery_info_manual['agent_types']}")
        
        print("\n3. 测试刷新功能")
        if discovery_info['auto_discovery_enabled']:
            print("刷新智能体列表...")
            refreshed_agents = manager_with_discovery.refresh_agents()
            print(f"刷新后智能体数量: {len(refreshed_agents)}")
            print(f"刷新后智能体类型: {list(refreshed_agents.keys())}")
        
        print("\n4. 测试路由功能")
        test_queries = [
            "设计一个系统架构",
            "评估这个方案",
            "实现代码功能",
            "收集数据信息"
        ]
        
        for query in test_queries:
            result = manager_with_discovery.route_request(query)
            print(f"查询: '{query}' -> 路由到: {result.get('agent_type', '未知')}")
        
        print("\n=== 自动发现机制测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_discovery_engine():
    """测试自动发现引擎"""
    print("\n=== 测试自动发现引擎 ===")
    
    try:
        from agent_discovery_engine import discover_all_components, get_discovery_engine
        
        print("1. 获取发现引擎实例")
        engine = get_discovery_engine()
        print(f"发现引擎类型: {type(engine).__name__}")
        
        print("\n2. 发现所有组件")
        result = discover_all_components()
        
        agents = result.get("agents", {})
        tools = result.get("tools", {})
        
        print(f"发现的智能体数量: {len(agents)}")
        print(f"发现的工具数量: {len(tools)}")
        
        if agents:
            print("\n发现的智能体:")
            for agent_id, info in agents.items():
                print(f"  - {agent_id}: {info.get('module_name', '未知')}")
        
        if tools:
            print("\n发现的工具:")
            for tool_id, info in tools.items():
                print(f"  - {tool_id}: {info.get('module_name', '未知')}")
        
        print("\n=== 自动发现引擎测试完成 ===")
        
    except Exception as e:
        print(f"发现引擎测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试自动发现机制...")
    
    # 测试发现引擎
    test_discovery_engine()
    
    # 测试智能体管理器
    test_auto_discovery()
    
    print("\n所有测试完成！")