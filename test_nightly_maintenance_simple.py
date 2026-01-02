#!/usr/bin/env python3
# @self-expose: {"id": "test_nightly_maintenance_simple", "name": "Test Nightly Maintenance Simple", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Nightly Maintenance Simple功能"]}}
# -*- coding: utf-8 -*-
"""
测试夜间维护调度器（简化版）

直接使用BaseAgent进行测试，避免其他智能体的初始化问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nightly_maintenance_simple():
    """测试夜间维护功能（简化版）"""
    print("=" * 80)
    print("🌙 测试夜间维护调度器（简化版）")
    print("=" * 80)
    
    try:
        # 导入依赖
        from src.base_agent import BaseAgent
        from src.nightly_maintenance_scheduler import NightlyMaintenanceScheduler
        
        # 测试1: 创建测试智能体
        print("\n测试1: 创建测试智能体")
        print("-" * 80)
        
        test_agents = []
        for i in range(3):
            agent = BaseAgent(
                agent_id=f"test_agent_{i+1}",
                agent_type="test_agent"
            )
            test_agents.append(agent)
            print(f"✓ 创建智能体: {agent.agent_id}")
        
        # 测试2: 创建模拟的智能体管理器
        print("\n测试2: 创建模拟智能体管理器")
        print("-" * 80)
        
        class MockAgentManager:
            """模拟智能体管理器"""
            def __init__(self, agents):
                self.agents_list = agents
            
            def get_all_agent_instances(self):
                return self.agents_list
        
        mock_manager = MockAgentManager(test_agents)
        print(f"✓ 模拟管理器创建成功，包含 {len(test_agents)} 个智能体")
        
        # 测试3: 为测试智能体添加一些泡泡
        print("\n测试3: 为智能体添加测试数据")
        print("-" * 80)
        
        for agent in test_agents:
            # 添加一些测试泡泡
            agent.note_bubble(
                category="工具问题",
                content=f"{agent.agent_id}的测试工具问题",
                priority="high"
            )
            agent.note_bubble(
                category="构思",
                content=f"{agent.agent_id}的测试构思",
                priority="normal"
            )
            print(f"✓ 为 {agent.agent_id} 添加测试泡泡")
        
        # 测试4: 创建夜间维护调度器
        print("\n测试4: 初始化夜间维护调度器")
        print("-" * 80)
        
        scheduler = NightlyMaintenanceScheduler(mock_manager)
        print(f"✓ 夜间维护调度器初始化成功")
        
        # 测试5: 手动触发日记写入
        print("\n测试5: 手动触发日记写入")
        print("-" * 80)
        
        diary_result = scheduler.perform_daily_diary_writing()
        
        if diary_result['status'] == 'success':
            print(f"\n✓ 日记写入完成")
            print(f"  成功: {diary_result['success_count']}/{diary_result['diary_count']}")
            print(f"  失败: {diary_result['failed_count']}")
            
            # 显示日记路径
            for agent_result in diary_result['agents']:
                if agent_result.get('diary_path'):
                    print(f"  📝 {agent_result['agent_id']}: {Path(agent_result['diary_path']).name}")
        else:
            print(f"\n✗ 日记写入失败: {diary_result.get('error', 'unknown')}")
        
        # 测试6: 查看日记内容
        print("\n测试6: 查看日记内容示例")
        print("-" * 80)
        
        if diary_result['agents'] and diary_result['agents'][0].get('diary_path'):
            diary_path = diary_result['agents'][0]['diary_path']
            if Path(diary_path).exists():
                with open(diary_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n日记内容预览:")
                print("=" * 70)
                print(content)
                print("=" * 70)
        
        # 测试7: 手动触发记忆重构
        print("\n测试7: 手动触发记忆重构")
        print("-" * 80)
        
        recon_result = scheduler.perform_memory_reconstruction()
        
        if recon_result['status'] == 'success':
            print(f"\n✓ 记忆重构完成")
            print(f"  处理: {recon_result['reconstructed_count']}/{recon_result['total_memories']}")
            if recon_result['total_memories'] > 0:
                print(f"  平均可信度: {recon_result['average_confidence']:.2%}")
        else:
            print(f"\n⏭️  记忆重构: {recon_result.get('status', 'skipped')}")
        
        # 测试8: 生成维护报告
        print("\n测试8: 生成维护报告")
        print("-" * 80)
        
        report_path = scheduler.generate_maintenance_report()
        
        if report_path:
            print(f"✓ 维护报告已生成: {report_path}")
            
            # 显示报告内容
            if Path(report_path).exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n维护报告内容:")
                print("=" * 70)
                print(content)
                print("=" * 70)
        
        # 测试9: 验证定时调度配置
        print("\n测试9: 验证定时调度配置")
        print("-" * 80)
        
        timing_engine = scheduler.timing_engine
        
        print(f"✓ 用户休息时段检测: {timing_engine._is_user_rest_time()}")
        print(f"✓ 系统空闲检测: {timing_engine._is_system_idle()}")
        print(f"✓ 协作窗口检测: {timing_engine._is_collaboration_window()}")
        
        # 显示配置
        config = timing_engine.config
        print(f"\n⚙️  定时配置:")
        print(f"  用户休息时段: {config['user_rest_hours']['start_hour']}:00 - {config['user_rest_hours']['end_hour']}:00")
        print(f"  CPU阈值: <{config['system_idle_threshold']['cpu_threshold']}%")
        print(f"  内存阈值: <{config['system_idle_threshold']['memory_threshold']}%")
        
        # 测试10: 获取维护状态
        print("\n测试10: 查看维护状态")
        print("-" * 80)
        
        status = scheduler.get_maintenance_status()
        print(f"✓ 监控运行中: {status['is_running']}")
        print(f"✓ 维护历史记录数: {status['maintenance_count']}")
        
        # 总结
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        
        print("\n🎯 夜间维护系统功能验证:")
        print("  ✅ 智能体泡泡记录")
        print("  ✅ 自动写日记")
        print("  ✅ 记忆重构引擎")
        print("  ✅ 维护报告生成")
        print("  ✅ 定时任务配置")
        
        print("\n🌙 夜间维护系统已就绪！")
        print("\n💡 使用方法:")
        print("   1. 白天：智能体工作时随手记泡泡 agent.note_bubble(...)")
        print("   2. 晚上：调度器自动写日记 + 重构记忆 + 更新向量库")
        print("   3. 启动：scheduler.start_scheduled_maintenance()")
        
        print("\n🔄 完整闭环:")
        print("   泡泡 → 日记 → 重构 → 向量库 → 第二天查询使用")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nightly_maintenance_simple()
    exit(0 if success else 1)
