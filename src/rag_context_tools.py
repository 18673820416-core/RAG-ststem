# -*- coding: utf-8 -*-
"""
RAG上下文工具包（外置工具模块）
遵循"基类+工具包"架构模式，提供可复用的RAG上下文构建能力
"""
# @self-expose: {"id": "rag_context_tools", "name": "RAG Context Tools", "type": "tool", "version": "1.0.0", "needs": {"deps": ["vector_database", "context_deduplication_manager"], "resources": []}, "provides": {"capabilities": ["时间窗口历史裁剪", "长期记忆检索", "去重上下文构建", "LLM消息构建"], "methods": {"build_recent_history_context": {"signature": "(history_items, time_window_minutes) -> List[Dict]", "description": "根据时间窗口裁剪近期对话历史"}, "retrieve_long_term_memories": {"signature": "(query, cutoff_minutes, limit) -> List[Dict]", "description": "检索长期记忆（超过时间窗口）"}, "build_rag_context_text": {"signature": "(query, history_context, cutoff_minutes, limit) -> str", "description": "构建去重后的RAG上下文文本"}, "build_llm_messages": {"signature": "(system_prompt, rag_context, user_query) -> List[Dict]", "description": "统一构建LLM messages"}}}}

from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    from src.vector_database import VectorDatabase
except Exception:
    VectorDatabase = None

from src.context_deduplication_manager import get_dedup_manager


def build_recent_history_context(
    history_items: Optional[List[Dict]] = None,
    time_window_minutes: int = 15,
) -> List[Dict]:
    """
    根据时间窗口裁剪近期对话历史（0-15分钟）
    history_items 由上层传入，结构至少包含 'timestamp'（ISO 字符串）和 'role'/'content'
    
    Args:
        history_items: 历史对话条目列表
        time_window_minutes: 时间窗口（分钟）
        
    Returns:
        过滤后的历史对话列表
    """
    if not history_items:
        return []

    now = datetime.now()
    cutoff_time = now - timedelta(minutes=time_window_minutes)

    filtered: List[Dict] = []
    for item in history_items:
        ts = item.get("timestamp") or item.get("full_timestamp") or ""
        if not ts:
            # 无时间戳的保留（可能是老数据）
            filtered.append(item)
            continue
        try:
            t = datetime.fromisoformat(ts)
            if t >= cutoff_time:
                filtered.append(item)
        except Exception:
            # 时间戳解析失败，保留该条目
            filtered.append(item)

    return filtered


def retrieve_long_term_memories(
    query: str,
    cutoff_minutes: int = 15,
    limit: int = 8,
) -> List[Dict]:
    """
    检索长期记忆（> cutoff_minutes 的向量库内容），不关心 LLM，只返回结构化记忆列表
    
    Args:
        query: 查询字符串
        cutoff_minutes: 时间分界点（分钟）
        limit: 最大返回数量
        
    Returns:
        长期记忆列表
    """
    if not VectorDatabase:
        return []

    cutoff_time = datetime.now() - timedelta(minutes=cutoff_minutes)
    end_time_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

    try:
        vector_db = VectorDatabase()
        memories = vector_db.search_memories(
            query=query,
            end_time=end_time_str,
            limit=limit,
        )
        return memories or []
    except Exception:
        return []


def build_rag_context_text(
    query: str,
    history_context: Optional[List[Dict]] = None,
    cutoff_minutes: int = 15,
    limit: int = 8,
) -> str:
    """
    用时间窗口 + 向量库 + 去重管理器，构建一段可供 LLM 使用的 RAG 上下文文本
    
    Args:
        query: 用户查询
        history_context: 历史对话上下文
        cutoff_minutes: 时间分界点（分钟）
        limit: 向量库检索数量限制
        
    Returns:
        去重后的RAG上下文文本
    """
    # 1. 裁剪近期历史
    recent_history = build_recent_history_context(
        history_items=history_context or [],
        time_window_minutes=cutoff_minutes,
    )

    # 2. 检索长期记忆
    long_term_memories = retrieve_long_term_memories(
        query=query,
        cutoff_minutes=cutoff_minutes,
        limit=limit,
    )

    # 3. 去重管理器处理
    dedup_manager = get_dedup_manager(history_window_minutes=cutoff_minutes)

    rag_context = dedup_manager.build_deduplicated_context(
        query=query,
        history_context=recent_history,
        retrieval_results=long_term_memories,
        enable_retrieval=bool(long_term_memories),
    )

    return rag_context or ""


def build_llm_messages(
    system_prompt: str,
    rag_context: str,
    user_query: str,
) -> List[Dict]:
    """
    统一构建 LLM messages：
    - system：基础身份/规则
    - system：去重后的长期记忆上下文（如有）
    - user：用户本次提问
    
    Args:
        system_prompt: 系统提示词
        rag_context: RAG上下文（已去重）
        user_query: 用户查询
        
    Returns:
        LLM messages列表
    """
    messages: List[Dict] = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if rag_context:
        messages.append({
            "role": "system",
            "content": (
                "以下是与你当前问题相关的长期记忆/历史上下文（已按时间窗口与向量库去重处理）：\n"
                f"{rag_context}"
            )
        })

    messages.append({"role": "user", "content": user_query})
    return messages
