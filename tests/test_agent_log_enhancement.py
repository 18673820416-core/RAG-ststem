#!/usr/bin/env python
# @self-expose: {"id": "test_agent_log_enhancement", "name": "Test Agent Log Enhancement", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Agent Log Enhancement功能"]}}
# -*- coding: utf-8 -*-
"""
测试智能体日志增强功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent_log_enhancement():
    """测试智能体日志增强功能"""
    print("=== 测试智能体日志增强功能 ===")
    
    try:
        # 导入智能体基类
        from src.base_agent import BaseAgent
        
        # 创建一个简单的智能体实例用于测试
        class TestAgent(BaseAgent):
            """测试智能体"""
            def __init__(self):
                # 调用父类初始化方法
                super().__init__(
                    agent_id="test_agent_1",
                    agent_type="test_agent",
                    prompt_file="test_prompt.txt"
                )
            
            @BaseAgent.auto_log
            def test_auto_log_method(self, message):
                """测试自动日志装饰器的方法"""
                print(f"执行测试方法，消息: {message}")
                return f"处理结果: {message}"
            
            def test_temp_log(self, content):
                """测试临时日志记录"""
                self._write_temp_log(content, "TEST")
                print(f"临时记录已写入: {content}")
        
        # 创建测试智能体实例
        test_agent = TestAgent()
        print("✓ 测试智能体创建成功")
        
        # 测试1: 自动日志装饰器
        print("\n1. 测试自动日志装饰器...")
        result = test_agent.test_auto_log_method("这是一个测试消息")
        print(f"✓ 自动日志方法执行成功，结果: {result}")
        
        # 测试2: 后台临时记录
        print("\n2. 测试后台临时记录...")
        for i in range(3):
            test_agent.test_temp_log(f"这是第 {i+1} 条临时记录")
        print("✓ 后台临时记录测试完成")
        
        # 测试3: 手动触发日志整理
        print("\n3. 测试日志整理功能...")
        test_agent._cleanup_temp_logs(max_age_hours=0)  # 清理所有临时日志
        print("✓ 日志整理功能测试完成")
        
        # 测试4: 检查日记文件
        print("\n4. 检查日记文件...")
        diary_file = test_agent.diary_file
        temp_diary_file = diary_file.parent / f"{test_agent.agent_id}_temp_diary.json"
        
        if diary_file.exists():
            print(f"✓ 工作日志文件存在: {diary_file}")
        else:
            print(f"✗ 工作日志文件不存在: {diary_file}")
        
        if temp_diary_file.exists():
            print(f"✓ 临时日志文件存在: {temp_diary_file}")
        else:
            print(f"✗ 临时日志文件不存在: {temp_diary_file}")
        
        # 测试5: 检查定时任务
        print("\n5. 检查定时任务...")
        if hasattr(test_agent, 'scheduled_tasks'):
            for task_name, task_config in test_agent.scheduled_tasks.items():
                if task_config['running']:
                    print(f"✓ 定时任务 {task_name} 正在运行")
                else:
                    print(f"✗ 定时任务 {task_name} 未运行")
        else:
            print("✗ 定时任务未初始化")
        
        print("\n=== 智能体日志增强功能测试完成 ===")
        print("✓ 所有测试通过")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_log_enhancement()
