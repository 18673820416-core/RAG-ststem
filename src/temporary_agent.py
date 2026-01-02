# @self-expose: {"id": "temporary_agent", "name": "Temporary Agent", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Temporary Agent功能"]}}
# -*- coding: utf-8 -*-
"""
临时智能体 - 八爪鱼架构的动态腕足
仅存在于内存中的LLM实例，通过对话窗口+系统提示词注入获得智能体能力

核心设计理念：
- 零代码文件：无需创建新的py文件
- 轻量级：只有对话上下文，无重量级类实例
- 大规模并行：内存允许的情况下可创建数百个临时智能体
- 动态能力赋予：通过注入不同系统提示词，获得不同智能体角色

开发提示词来源：八爪鱼自繁殖自进化驱动架构设计
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TemporaryAgent:
    """
    临时智能体 - 内存中的LLM实例
    
    本质：对话窗口 + 系统提示词注入
    与正式智能体的区别：
    - 正式智能体：完整的类实现，有代码文件，长期存在
    - 临时智能体：仅在内存中，通过提示词注入获得能力，短期任务后销毁
    """
    
    def __init__(self, 
                 agent_id: str,
                 template_name: str,
                 system_prompt: str,
                 llm_client: Any = None,
                 tool_integrator: Any = None):
        """
        初始化临时智能体
        
        Args:
            agent_id: 临时智能体ID（如：temp_system_architect_20251202_143052）
            template_name: 模板智能体名称（如：system_architect）
            system_prompt: 注入的系统提示词（从模板智能体获取）
            llm_client: LLM客户端实例（共享）
            tool_integrator: 工具集成器实例（共享）
        """
        self.agent_id = agent_id
        self.agent_type = f"temporary_{template_name}"
        self.template_name = template_name
        self.system_prompt = system_prompt
        
        # 共享的LLM客户端和工具集成器（不创建新实例，节省资源）
        self.llm_client = llm_client
        self.tool_integrator = tool_integrator
        
        # 独立的对话历史（每个临时智能体有独立的理解空间）
        self.conversation_history: List[Dict[str, Any]] = []
        
        # 临时智能体元数据
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "template": template_name,
            "is_temporary": True,
            "task_count": 0,  # 处理的任务数量
            "last_active": datetime.now().isoformat()
        }
        
        # 认知上下文（轻量级版本）
        self.cognitive_context = {
            "recent_topics": [],  # 最近讨论的话题
            "key_decisions": [],  # 关键决策记录
            "current_task": None  # 当前任务
        }
        
        logger.info(f"临时智能体创建成功: {agent_id} (模板: {template_name})")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        响应用户消息（核心能力）
        
        Args:
            message: 用户输入消息
            context: 额外的上下文信息（可选）
            
        Returns:
            响应结果
        """
        try:
            # 更新活跃时间和任务计数
            self.metadata["last_active"] = datetime.now().isoformat()
            self.metadata["task_count"] += 1
            
            # 构建完整的提示词上下文
            prompt_context = self._build_prompt_context(message, context)
            
            # 调用LLM生成响应
            if self.llm_client:
                response = self.llm_client.chat(prompt_context)
            else:
                response = f"[临时智能体 {self.agent_id}] 收到消息: {message}\n（LLM客户端不可用，无法生成响应）"
            
            # 记录到对话历史
            self._update_conversation_history(message, response)
            
            return {
                "type": "text_reply",
                "reply": response,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "task_count": self.metadata["task_count"]
            }
            
        except Exception as e:
            logger.error(f"临时智能体 {self.agent_id} 响应失败: {e}")
            return {
                "type": "error",
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_prompt_context(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        构建提示词上下文
        
        核心机制：系统提示词 + 对话历史 + 当前消息
        """
        context_parts = []
        
        # 1. 系统提示词（角色定义）
        context_parts.append(f"# 系统提示词\n{self.system_prompt}\n")
        
        # 2. 对话历史（最近5轮，避免上下文过长）
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]
            history_text = "\n".join([
                f"用户: {entry['message']}\n智能体: {entry['response']}"
                for entry in recent_history
            ])
            context_parts.append(f"# 对话历史\n{history_text}\n")
        
        # 3. 额外上下文（如果提供）
        if context:
            context_parts.append(f"# 额外上下文\n{json.dumps(context, ensure_ascii=False, indent=2)}\n")
        
        # 4. 当前消息
        context_parts.append(f"# 当前用户消息\n{message}\n")
        context_parts.append(f"# 请基于系统提示词和对话历史生成响应")
        
        return "\n".join(context_parts)
    
    def _update_conversation_history(self, message: str, response: str):
        """更新对话历史"""
        self.conversation_history.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持历史记录长度（最多保留20轮，更轻量级）
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具（委托给工具集成器）
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具调用结果
        """
        if not self.tool_integrator:
            return {"success": False, "error": "工具集成器不可用"}
        
        return self.tool_integrator.call_tool(
            tool_name, 
            parameters, 
            caller_info={
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "is_temporary": True
            }, 
            usage_intention="temporary_agent_task"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """获取临时智能体状态"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "template": self.template_name,
            "is_temporary": True,
            "created_at": self.metadata["created_at"],
            "last_active": self.metadata["last_active"],
            "task_count": self.metadata["task_count"],
            "conversation_turns": len(self.conversation_history),
            "current_task": self.cognitive_context.get("current_task")
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history
    
    def set_current_task(self, task_description: str):
        """设置当前任务"""
        self.cognitive_context["current_task"] = task_description
        logger.info(f"临时智能体 {self.agent_id} 设置任务: {task_description}")
    
    def clear_conversation_history(self):
        """清空对话历史（释放内存）"""
        history_count = len(self.conversation_history)
        self.conversation_history = []
        logger.info(f"临时智能体 {self.agent_id} 清空对话历史: {history_count} 轮")
    
    def export_conversation_summary(self) -> str:
        """导出对话总结（用于记忆归档）"""
        summary_lines = [
            f"临时智能体对话总结",
            f"智能体ID: {self.agent_id}",
            f"模板: {self.template_name}",
            f"创建时间: {self.metadata['created_at']}",
            f"任务数量: {self.metadata['task_count']}",
            f"对话轮数: {len(self.conversation_history)}",
            "",
            "## 对话历史"
        ]
        
        for i, entry in enumerate(self.conversation_history, 1):
            summary_lines.append(f"### 第{i}轮")
            summary_lines.append(f"用户: {entry['message']}")
            summary_lines.append(f"智能体: {entry['response']}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
