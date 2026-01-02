#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
思维透明化工具模组 - Thinking Transparency Tool Module
负责统一管理智能体思维步骤的记录与导出，供BaseAgent、多智能体聊天室等按需引用。
"""

# @self-expose: {"id": "thinking_tracer_tool", "name": "Thinking Tracer Tool", "type": "tool", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["register_thinking_tracer_tool", "thinking_step_trace"]}}

from typing import List, Dict, Any, Optional
from datetime import datetime
from threading import RLock


class ThinkingTracer:
    """思维透明化追踪器

    - 负责按会话维度记录思维步骤
    - 支持多来源：智能体内部推理步骤 / 聊天室协调层步骤
    - 提供统一的结构，供前端展示
    """

    def __init__(self) -> None:
        # key: trace_id (会话/对话轮次标识) -> steps list
        self._traces: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = RLock()

    def start_trace(self, trace_id: str) -> None:
        """开启新的思维追踪会话（若已存在则复用）"""
        with self._lock:
            self._traces.setdefault(trace_id, [])

    def report_step(
        self,
        trace_id: str,
        content: str,
        agent_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        scope: str = "agent",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录一个思维步骤

        :param trace_id: 会话/对话轮次标识
        :param content: 步骤内容（已适配用户可见）
        :param agent_id: 发出该步骤的智能体ID或角色
        :param agent_name: 发出该步骤的智能体名称（用于前端展示）
        :param scope: 步骤作用域："agent"（单智能体内部）或 "chatroom"（多智能体协调层）
        :param extra: 可选的扩展字段字典
        """
        step = {
            "agent_id": agent_id or "system",
            "agent_name": agent_name or "系统",
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "scope": scope,
        }
        if extra:
            step.update(extra)

        with self._lock:
            self._traces.setdefault(trace_id, []).append(step)

    def get_steps(self, trace_id: str) -> List[Dict[str, Any]]:
        """获取指定会话的全部思维步骤"""
        with self._lock:
            return list(self._traces.get(trace_id, []))

    def clear_trace(self, trace_id: str) -> None:
        """清理指定会话的步骤（例如会话结束或结果已返回前端后）"""
        with self._lock:
            if trace_id in self._traces:
                del self._traces[trace_id]


# 全局单例追踪器
_thinking_tracer = ThinkingTracer()


def get_thinking_tracer() -> ThinkingTracer:
    """获取全局思维透明化追踪器实例"""
    return _thinking_tracer


def register_thinking_tracer_tool(agent_tool_integration) -> bool:
    """将思维透明化追踪器注册到AgentToolIntegration及工具管理体系

    约定：
    - 工具名："thinking_tracer"
    - 由AgentToolIntegration负责与上层BaseAgent/多智能体聊天室对接
    """
    try:
        # 兼容AgentToolIntegration.register_tool接口
        if hasattr(agent_tool_integration, "register_tool"):
            agent_tool_integration.register_tool(
                tool_name="thinking_tracer",
                tool_description="统一管理智能体与聊天室的思维透明化步骤记录",
                tool_usage="通过get_thinking_tracer()获取实例，在推理关键节点调用report_step记录步骤",
            )
        return True
    except Exception:
        return False
