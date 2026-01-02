#!/usr/bin/env python
# @self-expose: {"id": "test_memory_bubble", "name": "Test Memory Bubble", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Memory Bubble功能"]}}
# -*- coding: utf-8 -*-
"""
测试记忆泡泡功能
验证智能体的随手记能力
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.base_agent import BaseAgent
import time

def test_memory_bubble():
    """测试记忆泡泡完整流程"""
    
    print("=" * 70)
    print("记忆泡泡功能测试")
    print("=" * 70)
    
    # 1. 创建测试智能体
    print("\n1. 创建测试智能体...")
    agent = BaseAgent(
        agent_id="test_agent_001",
        agent_type="test"
    )
    print("✅ 智能体创建成功")
    
    # 2. 记录各种类型的泡泡
    print("\n2. 记录各种类型的泡泡...")
    
    # 工具问题
    bubble1 = agent.note_bubble(
        category="工具问题",
        content="file_reading工具处理大文件时响应很慢",
        context={"tool": "file_reading", "file_size": "50MB"},
        priority="high"
    )
    print(f"✅ 工具问题泡泡: {bubble1}")
    time.sleep(0.1)  # 确保时间戳不同
    
    # 优化构思
    bubble2 = agent.note_bubble(
        category="构思",
        content="计划实现记忆泡泡自动汇总功能",
        context={"module": "memory_bubble_manager"}
    )
    print(f"✅ 构思泡泡: {bubble2}")
    time.sleep(0.1)
    
    # 理解困难
    bubble3 = agent.note_bubble(
        category="理解困难",
        content="检索到的文本块'mem_12345'语义模糊，难以理解",
        context={"memory_id": "mem_12345", "similarity": 0.65},
        priority="urgent"
    )
    print(f"✅ 理解困难泡泡: {bubble3}")
    time.sleep(0.1)
    
    # 待办事项
    bubble4 = agent.note_bubble(
        category="待办",
        content="优化向量检索算法，提升召回率"
    )
    print(f"✅ 待办泡泡: {bubble4}")
    
    # 3. 解决一个问题
    print("\n3. 标记泡泡已解决...")
    success = agent.resolve_bubble(
        bubble1, 
        resolution_note="已优化file_reading工具，增加了分块读取功能"
    )
    print(f"✅ 泡泡 {bubble1} 已标记为解决" if success else "❌ 标记失败")
    
    # 4. 查看泡泡统计
    print("\n4. 查看泡泡统计...")
    stats = agent.get_bubble_statistics()
    print(f"总泡泡数: {stats['total']}")
    print(f"已解决: {stats['resolved']}")
    print(f"未解决: {stats['unresolved']}")
    print(f"按类别统计: {stats['by_category']}")
    print(f"按优先级统计: {stats['by_priority']}")
    
    # 5. 获取未解决的问题
    print("\n5. 获取未解决的问题...")
    unresolved = agent.get_unresolved_issues()
    print(f"未解决问题数: {len(unresolved)}")
    for issue in unresolved:
        print(f"  - [{issue['priority']}] {issue['category']}: {issue['content']}")
    
    # 6. 写日记
    print("\n6. 写每日工作日记...")
    diary_path = agent.write_daily_diary(cleanup_resolved=True)
    print(f"✅ 日记已保存: {diary_path}")
    
    # 7. 查看日记内容
    print("\n7. 日记内容预览...")
    if diary_path and Path(diary_path).exists():
        with open(diary_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("=" * 70)
        print(content)
        print("=" * 70)
    
    # 8. 验证已解决的泡泡被清理
    print("\n8. 验证泡泡清理...")
    stats_after = agent.get_bubble_statistics()
    print(f"清理后总泡泡数: {stats_after['total']}")
    print(f"清理后未解决: {stats_after['unresolved']}")
    
    print("\n" + "=" * 70)
    print("✅ 记忆泡泡功能测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    test_memory_bubble()
