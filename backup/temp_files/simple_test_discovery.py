#!/usr/bin/env python
# @self-expose: {"id": "simple_test_discovery", "name": "Simple Test Discovery", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Test Discovery功能"]}}
# -*- coding: utf-8 -*-
"""
简单测试自动发现机制
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, 'src')

def simple_test():
    """简单测试"""
    print("=== 简单测试自动发现机制 ===\n")
    
    try:
        # 测试发现引擎
        print("1. 测试自动发现引擎")
        from agent_discovery_engine import discover_all_components
        
        result = discover_all_components()
        
        agents = result.get("agents", {})
        tools = result.get("tools", {})
        
        print(f"发现的智能体数量: {len(agents)}")
        print(f"发现的工具数量: {len(tools)}")
        
        if agents:
            print("\n发现的智能体:")
            for agent_id, info in agents.items():
                print(f"  - {agent_id}")
                print(f"    模块: {info.get('module_name', '未知')}")
                print(f"    类型: {info.get('type', '未知')}")
                if 'function_name' in info:
                    print(f"    函数: {info.get('function_name')}")
                if 'class_name' in info:
                    print(f"    类: {info.get('class_name')}")
        
        print("\n2. 测试智能体管理器")
        from agent_manager import AgentManager
        
        manager = AgentManager(enable_auto_discovery=True)
        
        discovery_info = manager.get_discovery_info()
        print(f"自动发现启用: {discovery_info['auto_discovery_enabled']}")
        print(f"智能体总数: {discovery_info['total_agents']}")
        print(f"智能体类型: {discovery_info['agent_types']}")
        
        print("\n3. 测试路由功能")
        test_query = "收集数据信息"
        result = manager.route_request(test_query)
        print(f"查询: '{test_query}'")
        print(f"路由到: {result.get('agent_type', '未知')}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()