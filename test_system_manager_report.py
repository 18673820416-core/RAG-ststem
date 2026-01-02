#!/usr/bin/env python
# @self-expose: {"id": "test_system_manager_report", "name": "Test System Manager Report", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test System Manager Report功能"]}}
# -*- coding: utf-8 -*-
"""
测试系统管家智能体的问题汇总和汇报功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.system_architect_agent import get_system_manager
from src.base_agent import BaseAgent
import time

def test_system_manager_report():
    """测试系统管家智能体的汇总和汇报功能"""
    
    print("=" * 80)
    print("系统管家智能体 - 问题汇总与汇报测试")
    print("=" * 80)
    
    # 1. 创建几个测试智能体，让它们记录泡泡
    print("\n第一步：创建测试智能体并记录问题...")
    
    agent1 = BaseAgent(agent_id="data_processor_001", agent_type="data_processor")
    agent2 = BaseAgent(agent_id="api_server_001", agent_type="api_server")
    agent3 = BaseAgent(agent_id="ml_trainer_001", agent_type="ml_trainer")
    
    # 记录一些问题
    agent1.note_bubble("工具问题", "file_reading工具处理大文件时很慢", 
                      context={"tool": "file_reading", "file_size": "100MB"}, priority="high")
    time.sleep(0.1)
    
    agent1.note_bubble("理解困难", "检索到的文本块'mem_789'语义不清", 
                      context={"memory_id": "mem_789"}, priority="urgent")
    time.sleep(0.1)
    
    agent2.note_bubble("工具问题", "file_reading工具经常超时", 
                      context={"tool": "file_reading"}, priority="high")
    time.sleep(0.1)
    
    agent2.note_bubble("优化建议", "建议增加API缓存机制", priority="normal")
    time.sleep(0.1)
    
    agent3.note_bubble("工具问题", "file_reading读取模型文件失败", 
                      context={"tool": "file_reading"}, priority="high")
    time.sleep(0.1)
    
    agent3.note_bubble("构思", "计划实现模型版本管理系统", priority="normal")
    
    print("✅ 已记录 6 个泡泡（3个智能体）")
    
    # 2. 获取系统管家智能体
    print("\n第二步：获取系统管家智能体...")
    manager = get_system_manager()
    print(f"✅ 系统管家: {manager.agent_id}")
    
    # 3. 汇总所有智能体的问题
    print("\n第三步：汇总所有智能体的未解决问题...")
    summary = manager.collect_all_agent_issues(days=7)
    
    print(f"活跃智能体数: {summary['total_agents']}")
    print(f"未解决问题总数: {summary['total_issues']}")
    print(f"共性问题数量: {len(summary['common_issues'])}")
    print(f"\n问题分类统计:")
    for category, count in summary['issues_by_category'].items():
        print(f"  - {category}: {count} 个")
    
    print(f"\n共性问题（多个智能体都遇到的）:")
    for issue in summary['common_issues']:
        print(f"  - [{issue['priority']}] {issue['category']}: {issue['summary'][:60]}...")
        print(f"    出现次数: {issue['occurrence_count']}, 影响智能体: {', '.join(issue['affected_agents'])}")
    
    # 4. 生成系统进化报告
    print("\n第四步：生成系统进化报告...")
    report = manager.generate_system_evolution_report(days=7)
    
    # 5. 向用户汇报
    print("\n第五步：向用户（主脑）汇报...")
    manager.report_to_user(report)
    
    print("\n" + "=" * 80)
    print("✅ 系统管家智能体测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_system_manager_report()
