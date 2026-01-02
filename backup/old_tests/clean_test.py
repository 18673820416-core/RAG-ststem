#!/usr/bin/env python3
# @self-expose: {"id": "clean_test", "name": "Clean Test", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Clean Test功能"]}}
# -*- coding: utf-8 -*-
"""
清晰测试智能体respond方法
"""

import sys
import os
from pathlib import Path

# 添加当前目录和src目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

# 设置环境变量
os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + str(current_dir / "src")

def test_architect():
    """测试系统架构师智能体"""
    print("=== 测试系统架构师智能体 ===")
    try:
        from src.system_architect_agent import SystemArchitectAgent
        agent = SystemArchitectAgent("test_architect")
        response = agent.respond("请设计一个RAG系统的架构方案")
        print(f"✅ 测试成功")
        print(f"响应长度: {len(response)} 字符")
        print(f"响应内容: {response}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_evaluator():
    """测试方案评估师智能体"""
    print("\n=== 测试方案评估师智能体 ===")
    try:
        from src.scheme_evaluator_agent import SchemeEvaluatorAgent
        agent = SchemeEvaluatorAgent()
        response = agent.respond("请评估这个RAG系统架构方案的风险和可行性")
        print(f"✅ 测试成功")
        print(f"响应长度: {len(response)} 字符")
        print(f"响应内容: {response}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_implementer():
    """测试代码实现师智能体"""
    print("\n=== 测试代码实现师智能体 ===")
    try:
        from src.code_implementer_agent import CodeImplementerAgent
        agent = CodeImplementerAgent()
        response = agent.respond("请实现这个RAG系统的核心模块")
        print(f"✅ 测试成功")
        print(f"响应长度: {len(response)} 字符")
        print(f"响应内容: {response}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始清晰测试智能体respond方法...\n")
    
    # 分别测试每个智能体
    print("\n" + "="*50)
    architect_success = test_architect()
    
    print("\n" + "="*50)
    evaluator_success = test_evaluator()
    
    print("\n" + "="*50)
    implementer_success = test_implementer()
    
    # 汇总结果
    print("\n" + "="*50)
    print("=== 测试结果汇总 ===")
    print(f"系统架构师智能体: {'✅ 通过' if architect_success else '❌ 失败'}")
    print(f"方案评估师智能体: {'✅ 通过' if evaluator_success else '❌ 失败'}")
    print(f"代码实现师智能体: {'✅ 通过' if implementer_success else '❌ 失败'}")
    
    if all([architect_success, evaluator_success, implementer_success]):
        print("\n🎉 所有智能体respond方法测试通过！")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")