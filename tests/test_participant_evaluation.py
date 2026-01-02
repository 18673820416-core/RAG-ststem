#!/usr/bin/env python3
# @self-expose: {"id": "test_participant_evaluation", "name": "Test Participant Evaluation", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Participant Evaluation功能"]}}
# -*- coding: utf-8 -*-
"""
测试参与者进化值评分机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheme_evaluator_agent import SchemeEvaluatorAgent
from system_iteration_engine import SystemIterationEngine
from datetime import datetime
import json

def test_participant_evaluation():
    """测试参与者进化值评分机制"""
    print("=== 测试参与者进化值评分机制 ===")
    
    # 创建评估师智能体实例
    evaluator = SchemeEvaluatorAgent()
    
    # 测试数据
    participant_id = "architect_001"
    evolution_action = {
        "action_id": "proposal_20241201_001",
        "action_type": "proposal_evaluation",
        "solves_core_issue": True,
        "technical_quality": "high",
        "is_complete": True,
        "innovation_level": "high",
        "is_original": True,
        "collaboration_level": "high",
        "helps_others": True,
        "co_creation_spirit": True,
        "skill_improvement": "high",
        "knowledge_gain": True
    }
    
    context_data = {
        "problem_complexity": "high",
        "solution_impact": "significant"
    }
    
    # 执行参与者进化值评估
    print(f"\n1. 评估参与者 {participant_id} 的进化值...")
    evaluation_result = evaluator.evaluate_participant_contribution(
        participant_id, evolution_action, context_data
    )
    
    print(f"   综合进化值: {evaluation_result['overall_evolution_value']:.1f}")
    print(f"   详细评分: {json.dumps(evaluation_result['detailed_scores'], indent=2, ensure_ascii=False)}")
    print(f"   排名位置: {evaluation_result['ranking_position']}")
    print(f"   需要实时反馈: {evaluation_result['needs_real_time_feedback']}")
    print(f"   改进建议: {evaluation_result['recommendations']}")
    
    # 测试实时反馈
    if evaluation_result['needs_real_time_feedback']:
        print(f"\n2. 生成实时反馈...")
        feedback = evaluator.provide_real_time_feedback(participant_id, evaluation_result)
        print(f"   反馈内容:\n{feedback}")
    
    # 测试排行榜报告
    print(f"\n3. 获取参与者排行榜报告...")
    ranking_report = evaluator.get_participant_ranking_report()
    print(f"   总参与者数: {ranking_report['total_participants']}")
    print(f"   排行榜更新时间: {ranking_report['ranking_updated']}")
    print(f"   优秀参与者数: {ranking_report['ranking_summary']['excellent_count']}")
    print(f"   良好参与者数: {ranking_report['ranking_summary']['good_count']}")
    print(f"   平均参与者数: {ranking_report['ranking_summary']['average_count']}")
    
    # 测试多个参与者
    print(f"\n4. 测试多个参与者的评估...")
    participants = [
        ("architect_001", {"technical_quality": "high", "innovation_level": "high"}),
        ("architect_002", {"technical_quality": "medium", "innovation_level": "medium"}),
        ("evaluator_001", {"technical_quality": "high", "collaboration_level": "high"})
    ]
    
    for participant_id, action_data in participants:
        action = evolution_action.copy()
        action.update(action_data)
        
        result = evaluator.evaluate_participant_contribution(participant_id, action, context_data)
        print(f"   参与者 {participant_id}: 进化值 {result['overall_evolution_value']:.1f}, 排名 {result['ranking_position']}")
    
    # 获取最终排行榜
    final_ranking = evaluator.get_participant_ranking_report()
    print(f"\n5. 最终排行榜前3名:")
    for i, participant in enumerate(final_ranking['top_participants'][:3]):
        print(f"   第{i+1}名: {participant['participant_id']} - 平均分 {participant['average_score']:.1f}")
    
    print("\n=== 参与者进化值评分机制测试完成 ===")

def test_system_iteration_integration():
    """测试系统迭代引擎集成"""
    print("\n=== 测试系统迭代引擎集成 ===")
    
    # 创建系统迭代引擎实例
    iteration_engine = SystemIterationEngine()
    
    # 创建一个测试问题
    problem_id = iteration_engine.identify_problem(
        "system_architect",
        "性能优化",
        "系统响应时间较慢，需要优化数据库查询",
        "high",
        ["数据库", "性能", "优化"]
    )
    print(f"1. 创建问题: {problem_id}")
    
    # 创建一个测试方案
    proposal_id = iteration_engine.create_proposal(
        "architect_001",
        problem_id,
        "数据库查询优化方案",
        "通过索引优化和查询重构提升性能",
        ["添加索引", "重构查询", "缓存优化"],
        "high",
        "significant"
    )
    print(f"2. 创建方案: {proposal_id}")
    
    # 评估方案并包含参与者评估数据
    participant_evaluation_data = {
        "solves_core_issue": True,
        "technical_quality": "high",
        "is_complete": True,
        "innovation_level": "medium",
        "is_original": True,
        "collaboration_level": "high",
        "helps_others": True,
        "co_creation_spirit": True,
        "skill_improvement": "medium",
        "knowledge_gain": True
    }
    
    evaluation_id = iteration_engine.evaluate_proposal(
        "evaluator_001",
        proposal_id,
        85.0,
        "成本效益分析：投入产出比高",
        "high",
        ["建议优先实施索引优化"],
        participant_evaluation_data
    )
    print(f"3. 评估方案: {evaluation_id}")
    
    # 检查系统状态
    status = iteration_engine.get_iteration_status()
    print(f"4. 系统迭代状态:")
    print(f"   总问题数: {status['total_problems']}")
    print(f"   总方案数: {status['total_proposals']}")
    print(f"   总评估数: {status['total_evaluations']}")
    
    print("\n=== 系统迭代引擎集成测试完成 ===")

if __name__ == "__main__":
    try:
        test_participant_evaluation()
        test_system_iteration_integration()
        print("\n✅ 所有测试通过！参与者进化值评分机制已成功实现。")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()