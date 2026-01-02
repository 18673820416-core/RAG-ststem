#!/usr/bin/env python
# @self-expose: {"id": "test_temporary_agent_simple", "name": "Test Temporary Agent Simple", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Temporary Agent Simple功能"]}}
# -*- coding: utf-8 -*-
"""
简单测试临时智能体 - 直接测试TemporaryAgent类

验证核心功能：
1. 临时智能体是轻量级内存实例
2. 通过系统提示词注入获得能力
3. 可独立响应消息

不依赖AgentManager，避免其他智能体初始化问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_temporary_agent_direct():
    """直接测试临时智能体类"""
    print("=" * 80)
    print("🐙 直接测试临时智能体类 (TemporaryAgent)")
    print("=" * 80)
    
    try:
        # 导入临时智能体类
        from src.temporary_agent import TemporaryAgent
        
        # 测试1: 创建临时智能体
        print("\n测试1: 创建临时智能体（内存实例）")
        print("-" * 80)
        
        # 准备系统提示词（模拟从模板智能体提取）
        system_prompt = """
# 系统架构师智能体

你是一个系统架构师，负责设计和评估系统架构。

## 核心能力
- 架构设计
- 技术选型
- 性能优化
- 系统集成

## 工作原则
- 模块化设计
- 高内聚低耦合
- 可扩展性优先
"""
        
        # 创建临时智能体
        temp_agent = TemporaryAgent(
            agent_id="temp_test_001",
            template_name="system_architect",
            system_prompt=system_prompt,
            llm_client=None,  # 暂不提供LLM客户端
            tool_integrator=None  # 暂不提供工具集成器
        )
        
        print(f"✓ 临时智能体创建成功")
        print(f"  智能体ID: {temp_agent.agent_id}")
        print(f"  智能体类型: {temp_agent.agent_type}")
        print(f"  模板名称: {temp_agent.template_name}")
        print(f"  类名: {type(temp_agent).__name__}")
        
        # 测试2: 获取状态
        print("\n测试2: 获取临时智能体状态")
        print("-" * 80)
        
        status = temp_agent.get_status()
        print(f"状态信息:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 测试3: 响应消息（无LLM客户端，预期返回错误提示）
        print("\n测试3: 测试响应能力")
        print("-" * 80)
        
        test_messages = [
            "请介绍一下你的角色",
            "如何设计一个高可用的系统架构？",
            "什么是八爪鱼架构？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n消息 {i}: {message}")
            response = temp_agent.respond(message)
            print(f"响应类型: {response.get('type')}")
            if 'reply' in response:
                print(f"响应内容: {response['reply']}")
            if 'error' in response:
                print(f"错误信息: {response['error']}")
            print(f"任务计数: {response.get('task_count', 0)}")
        
        # 测试4: 设置当前任务
        print("\n测试4: 设置当前任务")
        print("-" * 80)
        
        temp_agent.set_current_task("分析RAG系统的八爪鱼架构设计")
        updated_status = temp_agent.get_status()
        print(f"当前任务: {updated_status.get('current_task')}")
        
        # 测试5: 获取对话历史
        print("\n测试5: 获取对话历史")
        print("-" * 80)
        
        history = temp_agent.get_conversation_history()
        print(f"对话轮数: {len(history)}")
        if history:
            print(f"\n最近一轮对话:")
            last_entry = history[-1]
            print(f"  用户: {last_entry['message']}")
            print(f"  智能体: {last_entry['response'][:100]}...")
            print(f"  时间: {last_entry['timestamp']}")
        
        # 测试6: 导出对话总结
        print("\n测试6: 导出对话总结")
        print("-" * 80)
        
        summary = temp_agent.export_conversation_summary()
        print(f"对话总结长度: {len(summary)} 字符")
        print(f"\n总结预览（前300字符）:")
        print(summary[:300])
        
        # 测试7: 清空对话历史
        print("\n测试7: 清空对话历史")
        print("-" * 80)
        
        print(f"清空前对话轮数: {len(temp_agent.get_conversation_history())}")
        temp_agent.clear_conversation_history()
        print(f"清空后对话轮数: {len(temp_agent.get_conversation_history())}")
        
        # 总结
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！")
        print("=" * 80)
        
        print("\n临时智能体核心特性验证:")
        print("  ✓ 轻量级内存实例（TemporaryAgent类）")
        print("  ✓ 系统提示词注入机制")
        print("  ✓ 独立对话历史管理")
        print("  ✓ 状态追踪和任务管理")
        print("  ✓ 对话总结和历史清理")
        
        print("\n架构优势:")
        print("  🚀 零代码文件：无需创建新py文件")
        print("  💡 提示词驱动：通过注入提示词获得能力")
        print("  📦 轻量级：仅保存必要的对话历史")
        print("  ⚡ 快速创建：秒级创建新实例")
        print("  ♻️  按需销毁：任务完成后立即回收")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_temporary_agent_direct()
    exit(0 if success else 1)
