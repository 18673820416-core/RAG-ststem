#!/usr/bin/env python
# @self-expose: {"id": "test_base_agent_simple", "name": "Test Base Agent Simple", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Base Agent Simple功能"]}}
# -*- coding: utf-8 -*-
"""
简单测试BaseAgent的基本功能
"""

import sys
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

# 使用绝对导入
from src.base_agent import BaseAgent

def test_base_agent_initialization():
    """测试BaseAgent初始化"""
    print("=== 测试BaseAgent初始化 ===")
    
    try:
        # 创建测试智能体
        agent = BaseAgent('test_agent', 'test_type', 'test_prompt.txt')
        print("✓ 智能体初始化成功")
        print(f"  智能体ID: {agent.agent_id}")
        print(f"  智能体类型: {agent.agent_type}")
        print(f"  完整系统提示词已获取: {'是' if hasattr(agent, 'full_system_prompt') else '否'}")
        print(f"  核心系统提示词已获取: {'是' if hasattr(agent, 'core_system_prompt') else '否'}")
        print(f"  扩展系统提示词已获取: {'是' if hasattr(agent, 'extended_system_prompt') else '否'}")
        
        return True
    except Exception as e:
        print(f"✗ 智能体初始化失败: {e}")
        return False

def test_system_prompt_refresh():
    """测试系统提示词刷新"""
    print("\n=== 测试系统提示词刷新 ===")
    
    try:
        agent = BaseAgent('test_agent', 'test_type', 'test_prompt.txt')
        
        # 保存初始系统提示词
        initial_prompt = agent.full_system_prompt
        
        # 刷新系统提示词
        agent.full_system_prompt = agent.get_system_prompt()
        agent._split_system_prompt()
        
        print("✓ 系统提示词刷新成功")
        print(f"  初始提示词长度: {len(initial_prompt)}")
        print(f"  刷新后完整提示词长度: {len(agent.full_system_prompt)}")
        print(f"  核心提示词长度: {len(agent.core_system_prompt)}")
        print(f"  扩展提示词长度: {len(agent.extended_system_prompt)}")
        
        return True
    except Exception as e:
        print(f"✗ 系统提示词刷新失败: {e}")
        return False

def test_temporary_agent_detection():
    """测试临时智能体检测"""
    print("\n=== 测试临时智能体检测 ===")
    
    try:
        # 创建临时智能体
        temp_agent = BaseAgent('temp_test_agent', 'temporary_test_type', 'test_prompt.txt')
        
        # 检测是否为临时智能体
        is_temporary = temp_agent.agent_id.startswith("temp_") or "temporary_" in temp_agent.agent_type
        
        print("✓ 临时智能体检测成功")
        print(f"  智能体ID: {temp_agent.agent_id}")
        print(f"  智能体类型: {temp_agent.agent_type}")
        print(f"  是临时智能体: {'是' if is_temporary else '否'}")
        
        return True
    except Exception as e:
        print(f"✗ 临时智能体检测失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试BaseAgent基本功能...\n")
    
    # 运行所有测试
    tests = [
        test_base_agent_initialization,
        test_system_prompt_refresh,
        test_temporary_agent_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败！")
        sys.exit(1)
