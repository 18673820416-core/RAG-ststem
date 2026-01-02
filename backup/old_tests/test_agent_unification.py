#!/usr/bin/env python
# @self-expose: {"id": "test_agent_unification", "name": "Test Agent Unification", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agent Unification功能"]}}
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证统一智能体模板
开发提示词来源：用户建议统一智能体模板，实现智能体统一管理
"""

import sys
import os
import logging
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_manager import get_agent_manager, route_user_query

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_agent_manager_initialization():
    """测试智能体管理器初始化"""
    print("=== 测试智能体管理器初始化 ===")
    
    manager = get_agent_manager()
    
    # 检查智能体状态
    status = manager.get_agent_status()
    print(f"智能体状态: {status}")
    
    # 验证所有智能体都已初始化
    expected_agents = ["system_architect", "scheme_evaluator", "code_implementer"]
    for agent_type in expected_agents:
        if agent_type in status:
            print(f"✓ {agent_type} 智能体初始化成功")
        else:
            print(f"✗ {agent_type} 智能体初始化失败")
    
    return len(status) == len(expected_agents)

def test_specific_agent_queries():
    """测试特定智能体查询"""
    print("\n=== 测试特定智能体查询 ===")
    
    test_cases = [
        {
            "agent_type": "system_architect",
            "query": "请设计一个微服务架构",
            "description": "系统架构师查询"
        },
        {
            "agent_type": "scheme_evaluator",
            "query": "请评估这个技术选型",
            "description": "方案评估师查询"
        },
        {
            "agent_type": "code_implementer", 
            "query": "请生成一个简单的Python类",
            "description": "代码实现师查询"
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['description']}")
        print(f"指定智能体: {test_case['agent_type']}")
        print(f"查询: {test_case['query']}")
        
        result = route_user_query(test_case["query"], test_case["agent_type"])
        
        if "error" not in result:
            print(f"✓ 查询处理成功")
            print(f"  智能体类型: {result.get('agent_type', '未知')}")
            print(f"  响应时间: {result.get('timestamp', '未知')}")
            success_count += 1
        else:
            print(f"✗ 查询处理失败: {result.get('error')}")
    
    return success_count == len(test_cases)

def test_agent_diaries():
    """测试智能体日记功能"""
    print("\n=== 测试智能体日记功能 ===")
    
    manager = get_agent_manager()
    
    # 获取所有智能体的日记摘要
    diaries = manager.get_agent_diaries(limit=3)
    
    print(f"获取到 {len(diaries)} 个智能体的日记")
    
    for agent_type, diary_summary in diaries.items():
        print(f"\n{agent_type} 智能体日记摘要:")
        print(f"  总条目数: {diary_summary.get('total_entries', 0)}")
        print(f"  最近活动: {diary_summary.get('last_activity', '无')}")
        print(f"  日记类型统计: {diary_summary.get('type_statistics', {})}")
    
    return len(diaries) > 0

def main():
    """主测试函数"""
    print("开始统一智能体模板测试")
    print("=" * 60)
    
    test_results = {}
    
    # 执行各项测试
    test_results["manager_initialization"] = test_agent_manager_initialization()
    test_results["specific_agent_queries"] = test_specific_agent_queries()
    test_results["agent_diaries"] = test_agent_diaries()
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！统一智能体模板工作正常")
    else:
        print("⚠️ 部分测试失败，需要检查智能体实现")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)