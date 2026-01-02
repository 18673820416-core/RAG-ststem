#!/usr/bin/env python
# @self-expose: {"id": "test_simple", "name": "Test Simple", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Simple功能"]}}
# -*- coding: utf-8 -*-
"""
简单测试脚本，测试工具使用奖励机制的核心功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath("."))

# 简单测试反馈收集功能
def test_feedback_collector():
    """测试反馈收集功能"""
    print("\n=== 测试1: 反馈收集功能 ===")
    
    try:
        from src.agent_feedback_collector import AgentFeedbackCollector
        collector = AgentFeedbackCollector()
        
        # 收集反馈
        feedback_result = collector.collect_feedback(
            agent_id="test_agent_001",
            agent_type="test_agent",
            tool_name="test_tool",
            feedback_type="功能优化",
            content="这个工具的响应速度有点慢，建议优化算法提高性能。",
            priority="high"
        )
        
        print(f"反馈收集结果: {json.dumps(feedback_result, ensure_ascii=False)}")
        
        return feedback_result.get("feedback_id")
        
    except Exception as e:
        print(f"反馈收集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# 简单测试反馈评估功能
def test_feedback_evaluator(feedback_id):
    """测试反馈评估功能"""
    print("\n=== 测试2: 反馈评估功能 ===")
    
    try:
        from src.feedback_evaluator import FeedbackEvaluator
        evaluator = FeedbackEvaluator()
        
        # 评估反馈
        evaluation_result = evaluator.evaluate_feedback(feedback_id)
        print(f"反馈评估结果: {json.dumps(evaluation_result, ensure_ascii=False, indent=2)}")
        
        # 获取评估结果
        evaluation = evaluator.get_evaluation_result(feedback_id)
        print(f"获取评估结果: {json.dumps(evaluation, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"反馈评估测试失败: {e}")
        import traceback
        traceback.print_exc()

# 简单测试智能体行为评估功能
def test_agent_behavior_evaluator():
    """测试智能体行为评估功能"""
    print("\n=== 测试3: 智能体行为评估功能 ===")
    
    try:
        from src.agent_behavior_evaluator import AgentBehaviorEvaluator
        evaluator = AgentBehaviorEvaluator()
        
        # 评估智能体行为
        evaluation_result = evaluator.evaluate_agent_behavior("test_agent_001", 24)
        print(f"智能体行为评估结果: {json.dumps(evaluation_result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"智能体行为评估测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试工具使用奖励机制核心功能...")
    
    # 测试反馈收集
    feedback_id = test_feedback_collector()
    
    if feedback_id:
        # 测试反馈评估
        test_feedback_evaluator(feedback_id)
    
    # 测试智能体行为评估
    test_agent_behavior_evaluator()
    
    print("\n=== 核心功能测试完成 ===")
