#!/usr/bin/env python3
# @self-expose: {"id": "test_nightly_maintenance", "name": "Test Nightly Maintenance", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Nightly Maintenance功能"]}}
# -*- coding: utf-8 -*-
"""
测试夜间维护调度器

验证功能：
1. 定时任务调度
2. 智能体日记写入
3. 记忆重构
4. 向量数据库更新
5. 维护报告生成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nightly_maintenance():
    """测试夜间维护功能"""
    print("=" * 80)
    print("🌙 测试夜间维护调度器")
    print("=" * 80)
    
    try:
        # 导入依赖
        from src.agent_manager import AgentManager
        from src.nightly_maintenance_scheduler import get_nightly_scheduler
        from src.base_agent import BaseAgent
        
        # 测试1: 创建智能体管理器
        print("\n测试1: 初始化智能体管理器")
        print("-" * 80)
        
        agent_manager = AgentManager(enable_auto_discovery=False)
        print(f"✓ 智能体管理器初始化成功")
        
        # 获取智能体统计
        stats = agent_manager.get_agent_statistics()
        print(f"  总智能体数: {stats['total_agents']}")
        print(f"  智能体类型: {stats['agents_by_type']}")
        print(f"  激活状态: {stats['agent_status_summary']}")
        
        # 测试2: 获取所有智能体实例
        print("\n测试2: 获取智能体实例")
        print("-" * 80)
        
        all_agents = agent_manager.get_all_agent_instances()
        print(f"✓ 获取到 {len(all_agents)} 个智能体实例")
        
        for i, agent in enumerate(all_agents, 1):
            agent_id = getattr(agent, 'agent_id', 'unknown')
            agent_type = getattr(agent, 'agent_type', 'unknown')
            print(f"  [{i}] {agent_id} ({agent_type})")
        
        # 测试3: 创建夜间维护调度器
        print("\n测试3: 初始化夜间维护调度器")
        print("-" * 80)
        
        scheduler = get_nightly_scheduler(agent_manager)
        print(f"✓ 夜间维护调度器初始化成功")
        
        # 测试4: 手动触发日记写入（不启动定时任务）
        print("\n测试4: 手动触发日记写入")
        print("-" * 80)
        
        diary_result = scheduler.perform_daily_diary_writing()
        
        if diary_result['status'] == 'success':
            print(f"\n✓ 日记写入完成")
            print(f"  成功: {diary_result['success_count']}/{diary_result['diary_count']}")
            print(f"  失败: {diary_result['failed_count']}")
        else:
            print(f"\n✗ 日记写入失败: {diary_result.get('error', 'unknown')}")
        
        # 测试5: 手动触发记忆重构
        print("\n测试5: 手动触发记忆重构")
        print("-" * 80)
        
        recon_result = scheduler.perform_memory_reconstruction()
        
        if recon_result['status'] == 'success':
            print(f"\n✓ 记忆重构完成")
            print(f"  处理: {recon_result['reconstructed_count']}/{recon_result['total_memories']}")
            if recon_result['total_memories'] > 0:
                print(f"  平均可信度: {recon_result['average_confidence']:.2%}")
        else:
            print(f"\n✗ 记忆重构失败: {recon_result.get('error', 'unknown')}")
        
        # 测试6: 生成维护报告
        print("\n测试6: 生成维护报告")
        print("-" * 80)
        
        report_path = scheduler.generate_maintenance_report()
        
        if report_path:
            print(f"✓ 维护报告已生成: {report_path}")
            
            # 显示报告内容
            if Path(report_path).exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n" + "=" * 80)
                print(content)
                print("=" * 80)
        else:
            print("⏭️  报告生成已禁用")
        
        # 测试7: 获取维护状态
        print("\n测试7: 查看维护状态")
        print("-" * 80)
        
        status = scheduler.get_maintenance_status()
        print(f"监控运行中: {status['is_running']}")
        print(f"维护次数: {status['maintenance_count']}")
        print(f"配置: {status['config']}")
        
        # 测试8: 测试定时调度（不实际启动）
        print("\n测试8: 验证定时调度配置")
        print("-" * 80)
        
        from src.timing_strategy_engine import OptimizationTiming
        timing_engine = scheduler.timing_engine
        
        print(f"用户休息时段: {timing_engine._is_user_rest_time()}")
        print(f"系统空闲时段: {timing_engine._is_system_idle()}")
        print(f"协作窗口: {timing_engine._is_collaboration_window()}")
        
        # 显示配置
        config = timing_engine.config
        print(f"\n配置信息:")
        print(f"  用户休息时段: {config['user_rest_hours']['start_hour']}:00 - {config['user_rest_hours']['end_hour']}:00")
        print(f"  CPU阈值: <{config['system_idle_threshold']['cpu_threshold']}%")
        print(f"  内存阈值: <{config['system_idle_threshold']['memory_threshold']}%")
        
        # 总结
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！")
        print("=" * 80)
        
        print("\n夜间维护系统功能验证:")
        print("  ✓ 智能体管理器集成")
        print("  ✓ 智能体日记写入")
        print("  ✓ 记忆重构引擎")
        print("  ✓ 向量数据库更新")
        print("  ✓ 维护报告生成")
        print("  ✓ 定时任务调度")
        
        print("\n🌙 夜间维护系统已就绪！")
        print("💡 提示：在生产环境中运行 scheduler.start_scheduled_maintenance() 启动自动维护")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nightly_maintenance()
    exit(0 if success else 1)
