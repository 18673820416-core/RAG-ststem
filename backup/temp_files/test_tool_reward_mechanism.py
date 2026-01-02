#!/usr/bin/env python
# @self-expose: {"id": "test_tool_reward_mechanism", "name": "Test Tool Reward Mechanism", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Tool Reward Mechanism功能"]}}
# -*- coding: utf-8 -*-
"""
工具使用奖励机制测试脚本
测试整个工具使用奖励机制的功能
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath("e:\\RAG系统"))

# 使用绝对导入
import src.agent_feedback_collector
import src.feedback_evaluator
import src.agent_behavior_evaluator
import src.self_evolution_controller

# 创建实例
collector = src.agent_feedback_collector.AgentFeedbackCollector()
evaluator = src.feedback_evaluator.FeedbackEvaluator()
behavior_evaluator = src.agent_behavior_evaluator.AgentBehaviorEvaluator()
evolution_controller = src.self_evolution_controller.SelfEvolutionController()

class ToolRewardMechanismTester:
    """工具使用奖励机制测试器"""
    
    def __init__(self):
        self.collector = collector
        self.evaluator = evaluator
        self.behavior_evaluator = behavior_evaluator
        self.evolution_controller = evolution_controller
        
        self.test_agent_id = "test_agent_001"
        self.test_agent_type = "test_agent"
        self.test_tool_name = "test_tool"
    
    def test_feedback_collection(self):
        """测试反馈收集功能"""
        print("\n=== 测试1: 反馈收集功能 ===")
        
        try:
            # 收集反馈
            feedback_result = self.collector.collect_feedback(
                agent_id=self.test_agent_id,
                agent_type=self.test_agent_type,
                tool_name=self.test_tool_name,
                feedback_type="功能优化",
                content="这个工具的响应速度有点慢，建议优化算法提高性能。同时，希望能增加批量处理功能，提高工作效率。",
                priority="high"
            )
            
            print(f"反馈收集结果: {json.dumps(feedback_result, ensure_ascii=False)}")
            
            # 获取反馈
            feedback_id = feedback_result.get("feedback_id")
            if feedback_id:
                feedback = self.collector.get_feedback(feedback_id)
                print(f"获取反馈结果: {json.dumps(feedback, ensure_ascii=False, indent=2)}")
                return feedback_id
            
            return None
            
        except Exception as e:
            print(f"反馈收集测试失败: {e}")
            return None
    
    def test_feedback_evaluation(self, feedback_id):
        """测试反馈评估功能"""
        print("\n=== 测试2: 反馈评估功能 ===")
        
        try:
            # 评估单个反馈
            evaluation_result = self.evaluator.evaluate_feedback(feedback_id)
            print(f"单个反馈评估结果: {json.dumps(evaluation_result, ensure_ascii=False, indent=2)}")
            
            # 获取评估结果
            evaluation = self.evaluator.get_evaluation_result(feedback_id)
            print(f"获取评估结果: {json.dumps(evaluation, ensure_ascii=False, indent=2)}")
            
            # 获取所有评估结果
            all_evaluations = self.evaluator.get_all_evaluations()
            print(f"所有评估结果数量: {len(all_evaluations)}")
            
            # 生成优化任务
            optimization_tasks = self.evaluator.generate_optimization_tasks(3)
            print(f"生成优化任务数量: {len(optimization_tasks)}")
            
            return evaluation
            
        except Exception as e:
            print(f"反馈评估测试失败: {e}")
            return None
    
    def test_agent_behavior_evaluation(self):
        """测试智能体行为评估功能"""
        print("\n=== 测试3: 智能体行为评估功能 ===")
        
        try:
            # 评估智能体行为
            evaluation_result = self.behavior_evaluator.evaluate_agent_behavior(
                agent_id=self.test_agent_id,
                time_window_hours=24
            )
            print(f"智能体行为评估结果: {json.dumps(evaluation_result, ensure_ascii=False, indent=2)}")
            
            # 获取评估统计信息
            stats = self.behavior_evaluator.get_evaluation_statistics()
            print(f"评估统计信息: {json.dumps(stats, ensure_ascii=False, indent=2)}")
            
            return evaluation_result
            
        except Exception as e:
            print(f"智能体行为评估测试失败: {e}")
            return None
    
    def test_tool_evolution(self):
        """测试工具进化执行功能"""
        print("\n=== 测试4: 工具进化执行功能 ===")
        
        try:
            # 处理工具进化
            evolution_result = self.evolution_controller.process_tool_evolution(top_n=2)
            print(f"工具进化处理结果: {json.dumps(evolution_result, ensure_ascii=False, indent=2)}")
            
            # 获取进化统计信息
            evolution_stats = self.evolution_controller.get_evolution_statistics()
            print(f"进化统计信息: {json.dumps(evolution_stats, ensure_ascii=False, indent=2)}")
            
            return evolution_result
            
        except Exception as e:
            print(f"工具进化测试失败: {e}")
            return None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试工具使用奖励机制...")
        
        # 测试反馈收集
        feedback_id = self.test_feedback_collection()
        
        if feedback_id:
            # 测试反馈评估
            self.test_feedback_evaluation(feedback_id)
        
        # 测试智能体行为评估
        self.test_agent_behavior_evaluation()
        
        # 测试工具进化执行
        self.test_tool_evolution()
        
        print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    tester = ToolRewardMechanismTester()
    tester.run_all_tests()
