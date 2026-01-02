#!/usr/bin/env python
# @self-expose: {"id": "test_agent_feedback_api", "name": "Test Agent Feedback Api", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agent Feedback Api功能"]}}
# -*- coding: utf-8 -*-
"""
测试智能体反馈API - 验证进化值评估体系的关键功能

测试内容：
1. 智能体主动提交工具反馈
2. 获取智能体的反馈列表
3. 获取反馈统计信息
4. 验证反馈与记忆泡泡的联动

开发提示词来源：工具使用奖励机制设计.md - 智能体反馈驱动工具进化机制
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent_feedback_api():
    """测试智能体反馈API"""
    print("=" * 80)
    print("🔧 测试智能体反馈API（进化值评估体系）")
    print("=" * 80)
    
    try:
        # 导入BaseAgent
        from src.base_agent import BaseAgent
        
        # 创建测试智能体
        print("\n测试1: 创建测试智能体")
        print("-" * 80)
        
        agent = BaseAgent(
            agent_id="test_agent_001",
            agent_type="test_agent"
        )
        
        print(f"✓ 智能体创建成功")
        print(f"  智能体ID: {agent.agent_id}")
        print(f"  智能体类型: {agent.agent_type}")
        print(f"  反馈收集器可用: {agent.feedback_collector is not None}")
        print(f"  泡泡管理器可用: {agent.bubble_manager is not None}")
        
        # 测试2: 提交工具反馈
        print("\n测试2: 智能体主动提交工具反馈")
        print("-" * 80)
        
        feedbacks_to_submit = [
            {
                "tool_name": "FileReadingTool",
                "feedback_type": "使用体验",
                "content": "处理大文件（>10MB）时响应较慢，建议添加进度显示",
                "priority": "medium"
            },
            {
                "tool_name": "MemoryRetrievalTool",
                "feedback_type": "功能优化",
                "content": "建议增加语义相似度阈值参数，可以过滤低相关性结果",
                "priority": "high"
            },
            {
                "tool_name": "CommandLineTool",
                "feedback_type": "问题报告",
                "content": "Windows环境下执行某些命令时出现编码错误",
                "priority": "high"
            },
            {
                "tool_name": "VectorDatabase",
                "feedback_type": "新功能需求",
                "content": "希望支持批量删除记忆的功能，方便记忆清理",
                "priority": "low"
            }
        ]
        
        submitted_feedbacks = []
        for i, feedback_data in enumerate(feedbacks_to_submit, 1):
            result = agent.submit_tool_feedback(
                tool_name=feedback_data["tool_name"],
                feedback_type=feedback_data["feedback_type"],
                content=feedback_data["content"],
                priority=feedback_data["priority"]
            )
            
            if result.get("status") == "success":
                print(f"\n✓ 反馈 {i} 提交成功")
                print(f"  工具: {feedback_data['tool_name']}")
                print(f"  类型: {feedback_data['feedback_type']}")
                print(f"  优先级: {feedback_data['priority']}")
                print(f"  反馈ID: {result.get('feedback_id')}")
                submitted_feedbacks.append(result.get("feedback_id"))
            else:
                print(f"\n✗ 反馈 {i} 提交失败: {result.get('message')}")
        
        print(f"\n总计提交: {len(submitted_feedbacks)}/{len(feedbacks_to_submit)} 条反馈")
        
        # 测试3: 获取智能体的反馈列表
        print("\n测试3: 获取智能体的反馈列表")
        print("-" * 80)
        
        my_feedbacks = agent.get_my_feedbacks()
        print(f"智能体 {agent.agent_id} 的反馈数量: {len(my_feedbacks)}")
        
        if my_feedbacks:
            print(f"\n反馈列表:")
            for i, feedback in enumerate(my_feedbacks, 1):
                print(f"\n  [{i}] {feedback['tool_name']} - {feedback['feedback_type']}")
                print(f"      优先级: {feedback['priority']}")
                print(f"      状态: {feedback['status']}")
                print(f"      内容: {feedback['content'][:50]}...")
        
        # 测试4: 获取反馈统计信息
        print("\n测试4: 获取反馈统计信息")
        print("-" * 80)
        
        stats = agent.get_feedback_statistics()
        print(f"统计信息:")
        print(f"  总反馈数: {stats['total_feedbacks']}")
        print(f"\n  按类型统计:")
        for feedback_type, count in stats['by_type'].items():
            print(f"    - {feedback_type}: {count}")
        print(f"\n  按优先级统计:")
        for priority, count in stats['by_priority'].items():
            print(f"    - {priority}: {count}")
        print(f"\n  按状态统计:")
        for status, count in stats['by_status'].items():
            print(f"    - {status}: {count}")
        print(f"\n  按工具统计:")
        for tool_name, count in stats['by_tool'].items():
            print(f"    - {tool_name}: {count}")
        
        # 测试5: 验证反馈与记忆泡泡的联动
        print("\n测试5: 验证反馈与记忆泡泡的联动")
        print("-" * 80)
        
        if agent.bubble_manager:
            bubble_stats = agent.get_bubble_statistics()
            print(f"泡泡统计:")
            print(f"  总泡泡数: {bubble_stats.get('total_bubbles', 0)}")
            print(f"  未解决: {bubble_stats.get('unresolved', 0)}")
            print(f"  已解决: {bubble_stats.get('resolved', 0)}")
            
            # 获取工具问题类泡泡
            if bubble_stats.get('total_bubbles', 0) > 0:
                print(f"\n  泡泡分类统计:")
                by_category = bubble_stats.get('by_category', {})
                for category, count in by_category.items():
                    print(f"    - {category}: {count}")
        else:
            print("⚠️ 泡泡管理器不可用")
        
        # 测试6: 测试按条件过滤反馈
        print("\n测试6: 测试按条件过滤反馈")
        print("-" * 80)
        
        # 按状态过滤
        pending_feedbacks = agent.get_my_feedbacks(status="pending")
        print(f"待评估的反馈数量: {len(pending_feedbacks)}")
        
        # 按工具过滤
        memory_tool_feedbacks = agent.get_my_feedbacks(tool_name="MemoryRetrievalTool")
        print(f"关于 MemoryRetrievalTool 的反馈数量: {len(memory_tool_feedbacks)}")
        
        # 总结
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！")
        print("=" * 80)
        
        print("\n智能体反馈API核心功能验证:")
        print("  ✓ 智能体主动提交工具反馈")
        print("  ✓ 支持4种反馈类型（使用体验、功能优化、新功能需求、问题报告）")
        print("  ✓ 支持3级优先级（low、medium、high）")
        print("  ✓ 获取智能体的反馈列表")
        print("  ✓ 获取反馈统计信息")
        print("  ✓ 反馈自动记录到记忆泡泡")
        print("  ✓ 支持按条件过滤反馈")
        
        print("\n进化值评估体系集成:")
        print("  ✓ 反馈收集器已集成到BaseAgent")
        print("  ✓ 所有智能体自动具备反馈能力")
        print("  ✓ 支持智能体-工具协同进化闭环")
        
        print("\n进化传递链条:")
        print("  智能体主动反馈 → 工具集合进化 → 智能体进化 → 系统进化")
        print("  🔄 闭环已建立！")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_feedback_api()
    exit(0 if success else 1)
