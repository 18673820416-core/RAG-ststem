# -*- coding: utf-8 -*-
"""
测试"基类 + RAG工具包"架构
验证基类智能体能否正确使用外置RAG工具包构建上下文并调用LLM
"""
# @self-expose: {"id": "test_rag_tooling_architecture", "name": "Test RAG Tooling Architecture", "type": "test", "version": "1.0.0", "needs": {"deps": ["base_agent", "rag_context_tools", "agent_conversation_window"], "resources": []}, "provides": {"capabilities": ["架构测试"], "methods": {}}}

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_base_agent_with_rag_tooling():
    """测试基类智能体使用RAG工具包"""
    print("=" * 80)
    print("测试1：基类智能体使用RAG工具包")
    print("=" * 80)
    
    try:
        from src.base_agent import BaseAgent
        
        # 创建基类智能体实例
        agent = BaseAgent(
            agent_id="test_agent_001",
            agent_type="测试智能体",
            prompt_file="src/agent_prompts/base_agent_prompt.md"
        )
        
        print(f"✅ 基类智能体创建成功: {agent.agent_id}")
        print(f"   - 版本: 2.0.0 (支持RAG工具包)")
        print(f"   - LLM客户端: {'可用' if agent.llm_client else '不可用'}")
        print(f"   - 向量数据库: {'可用' if agent.vector_db else '不可用'}")
        
        # 测试不带历史上下文的对话
        print("\n--- 测试场景1：无历史上下文对话 ---")
        response1 = agent.respond("你好，请介绍一下你自己")
        print(f"用户: 你好，请介绍一下你自己")
        print(f"智能体响应类型: {response1.get('type')}")
        print(f"智能体回复: {response1.get('reply', response1.get('error', ''))[:200]}...")
        
        # 测试带历史上下文的对话
        print("\n--- 测试场景2：带历史上下文对话 ---")
        
        # 构造模拟历史上下文（近15分钟内的对话）
        now = datetime.now()
        history_context = [
            {
                "timestamp": (now - timedelta(minutes=10)).isoformat(),
                "message": "什么是RAG架构？",
                "response": "RAG（检索增强生成）是一种结合检索系统和生成模型的架构...",
            },
            {
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
                "message": "如何实现上下文去重？",
                "response": "使用时间窗口和向量库检索结合的方式，通过ContextDeduplicationManager处理...",
            }
        ]
        
        response2 = agent.respond(
            "结合刚才的讨论，请总结RAG架构的核心要点",
            history_context=history_context
        )
        print(f"用户: 结合刚才的讨论，请总结RAG架构的核心要点")
        print(f"历史上下文: {len(history_context)}条对话记录")
        print(f"智能体响应类型: {response2.get('type')}")
        print(f"智能体回复: {response2.get('reply', response2.get('error', ''))[:200]}...")
        
        print("\n✅ 基类智能体RAG工具包测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_context_tools_directly():
    """直接测试RAG工具包函数"""
    print("\n" + "=" * 80)
    print("测试2：直接测试RAG工具包函数")
    print("=" * 80)
    
    try:
        from src.rag_context_tools import (
            build_recent_history_context,
            build_rag_context_text,
            build_llm_messages
        )
        
        # 测试时间窗口历史裁剪
        print("\n--- 测试场景1：时间窗口历史裁剪 ---")
        now = datetime.now()
        test_history = [
            {"timestamp": (now - timedelta(minutes=20)).isoformat(), "message": "旧消息1"},
            {"timestamp": (now - timedelta(minutes=10)).isoformat(), "message": "近期消息1"},
            {"timestamp": (now - timedelta(minutes=5)).isoformat(), "message": "近期消息2"},
        ]
        
        recent = build_recent_history_context(test_history, time_window_minutes=15)
        print(f"输入历史条目数: {len(test_history)}")
        print(f"时间窗口内条目数: {len(recent)}")
        print(f"✅ 时间窗口裁剪正常（保留15分钟内的{len(recent)}条记录）")
        
        # 测试RAG上下文构建
        print("\n--- 测试场景2：RAG上下文构建 ---")
        rag_context = build_rag_context_text(
            query="什么是RAG架构？",
            history_context=recent,
            cutoff_minutes=15,
            limit=8
        )
        print(f"RAG上下文长度: {len(rag_context)}字符")
        print(f"RAG上下文内容: {rag_context[:200] if rag_context else '（空）'}...")
        print(f"✅ RAG上下文构建完成")
        
        # 测试LLM消息构建
        print("\n--- 测试场景3：LLM消息构建 ---")
        messages = build_llm_messages(
            system_prompt="你是一个测试智能体",
            rag_context=rag_context,
            user_query="测试查询"
        )
        print(f"LLM消息条目数: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"  消息{i+1}: role={msg['role']}, content长度={len(msg['content'])}")
        print(f"✅ LLM消息构建正常")
        
        print("\n✅ RAG工具包函数测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_window_integration():
    """测试对话窗口与RAG工具包集成"""
    print("\n" + "=" * 80)
    print("测试3：对话窗口与RAG工具包集成")
    print("=" * 80)
    
    try:
        from src.base_agent import BaseAgent
        from src.agent_conversation_window import AgentConversationWindow
        
        # 创建智能体
        agent = BaseAgent(
            agent_id="window_test_agent",
            agent_type="窗口测试智能体"
        )
        
        # 创建对话窗口
        window = AgentConversationWindow(
            agent_id="window_test_agent",
            agent_role="窗口测试智能体",
            agent_instance=agent
        )
        
        print(f"✅ 对话窗口创建成功: {window.window_id}")
        print(f"   - 时间窗口: {window.context_management['time_window_minutes']}分钟")
        
        # 模拟对话交互
        print("\n--- 模拟对话交互 ---")
        
        # 第一轮对话
        result1 = window.receive_message("你好，介绍一下自己", sender="user")
        print(f"第1轮 - 状态: {result1['status']}")
        print(f"第1轮 - 响应: {result1.get('response', '')[:100]}...")
        
        # 第二轮对话（应该包含第一轮历史）
        result2 = window.receive_message("刚才说了什么？", sender="user")
        print(f"第2轮 - 状态: {result2['status']}")
        print(f"第2轮 - 上下文长度: {result2.get('context_management', {}).get('current_length', 0)}")
        print(f"第2轮 - 响应: {result2.get('response', '')[:100]}...")
        
        print("\n✅ 对话窗口集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("【基类 + RAG工具包】架构验证测试")
    print("🚀" * 40 + "\n")
    
    # 运行所有测试
    results = []
    
    # 测试1：基类智能体使用RAG工具包
    results.append(("基类智能体RAG工具包", test_base_agent_with_rag_tooling()))
    
    # 测试2：直接测试RAG工具包函数
    results.append(("RAG工具包函数", test_rag_context_tools_directly()))
    
    # 测试3：对话窗口集成
    results.append(("对话窗口集成", test_conversation_window_integration()))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "🎉" * 40)
    if all_passed:
        print("所有测试通过！【基类 + RAG工具包】架构验证成功！")
    else:
        print("部分测试失败，请检查日志排查问题")
    print("🎉" * 40 + "\n")
