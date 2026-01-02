# -*- coding: utf-8 -*-
"""
基类智能体(BaseAgent)
- 外部化系统提示词：从文件加载，符合“认知减负”原则
- 工具黑箱化：通过工具集成器委托调用，避免在智能体中重复实现工具逻辑
- 最小可用能力：响应用户消息、解析简单的命令型请求、支持创建记忆
"""
# @self-expose: {"id": "base_agent", "name": "Base Agent", "type": "agent", "version": "2.0.0", "needs": {"deps": ["agent_tool_integration", "vector_database", "llm_client", "memory_bubble_manager", "rag_context_tools"], "resources": []}, "provides": {"capabilities": ["基础智能体能力", "工具调用", "记忆管理", "泡泡系统", "反馈系统", "RAG上下文构建"], "methods": {"respond": {"signature": "(message: str, history_context: Optional[List[Dict]]) -> Dict[str, Any]", "description": "处理用户消息并返回响应（支持历史上下文传入）"}, "call_tool": {"signature": "(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]", "description": "委托工具集成器调用具体工具"}, "create_memory": {"signature": "(content: str, memory_type: str, priority: str, tags: Optional[List[str]]) -> Optional[str]", "description": "创建记忆条目并写入向量数据库"}, "note_bubble": {"signature": "(category: str, content: str, context: Optional[Dict], priority: str) -> Optional[str]", "description": "快速记录记忆泡泡"}, "write_daily_diary": {"signature": "(cleanup_resolved: bool) -> Optional[str]", "description": "写每日工作日记"}, "submit_tool_feedback": {"signature": "(tool_name: str, feedback_type: str, content: str, priority: str) -> Dict[str, Any]", "description": "智能体主动提交工具反馈"}}}}

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from src.agent_tool_integration import get_tool_integrator
except Exception:
    # 延迟导入失败时占位，避免初始化崩溃
    get_tool_integrator = None

try:
    from src.vector_database import VectorDatabase
except Exception:
    VectorDatabase = None  # 运行环境未就绪时的占位

try:
    from src.llm_client_enhanced import LLMClientEnhanced
except Exception:
    LLMClientEnhanced = None  # LLM不可用时禁止伪文本降级

try:
    from src.rag_context_tools import build_rag_context_text, build_llm_messages
except Exception:
    build_rag_context_text = None
    build_llm_messages = None

try:
    from src.memory_bubble_manager import MemoryBubbleManager
except Exception:
    MemoryBubbleManager = None  # 泡泡管理器可选

try:
    from src.agent_feedback_collector import AgentFeedbackCollector
except Exception:
    AgentFeedbackCollector = None  # 反馈收集器可选


class BaseAgent:
    """统一的基类智能体，实现提示词加载与工具能力接入"""

    def __init__(self, agent_id: str, agent_type: str, prompt_file: str = "src/agent_prompts/base_agent_prompt.md"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.prompt_file = prompt_file

        # 工具集成器（黑箱化工具调用）
        self.tool_integrator = get_tool_integrator() if get_tool_integrator else None

        # LLM客户端（必须可用，否则显式报错）
        self.llm_client = LLMClientEnhanced() if LLMClientEnhanced else None

        # 向量数据库（用于create_memory和RAG检索）
        self.vector_db = VectorDatabase() if VectorDatabase else None
        
        # 记忆泡泡管理器（基类功能，所有智能体自动具备）
        self.bubble_manager = MemoryBubbleManager(agent_id) if MemoryBubbleManager else None
        
        # 反馈收集器（基类功能，所有智能体自动具备）
        self.feedback_collector = AgentFeedbackCollector() if AgentFeedbackCollector else None

        # 提示词相关
        self.full_system_prompt: str = self.get_system_prompt()
        self.core_system_prompt: str = ""
        self.extended_system_prompt: str = ""
        self._split_system_prompt()

    # -----------------------------------------
    # 提示词加载与分层
    # -----------------------------------------
    def get_system_prompt(self) -> str:
        """从外部文件加载系统提示词，文件不存在时返回降级提示词"""
        try:
            path = Path(self.prompt_file)
            if not path.exists():
                # 尝试以工作区根为基准
                alt = Path("E:/RAG系统") / self.prompt_file
                if alt.exists():
                    path = alt
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
        # 降级（保证可运行）
        return (
            "# 基类智能体系统提示词\n"
            "你是一个基础RAG智能体，外部化工具与提示词，遵循黑箱化与认知减负原则。\n"
            "当检测到可执行命令文本时，调用命令行工具；否则结合提示词与上下文生成响应。"
        )

    def _split_system_prompt(self):
        """将系统提示词分为核心层与扩展层（启发式）"""
        content = self.full_system_prompt or ""
        # 优先在结构化分段处切分
        markers = [
            "## 工具使用说明",
            "## 响应策略",
            "### 工具调用格式",
        ]
        split_idx = -1
        for mk in markers:
            idx = content.find(mk)
            if idx != -1:
                split_idx = idx
                break
        if split_idx == -1:
            # 回退：按长度切分，核心层偏短以便认知减负
            split_idx = min(len(content), 1200)
        self.core_system_prompt = content[:split_idx]
        self.extended_system_prompt = content[split_idx:]

    # -----------------------------------------
    # 核心对话能力（基于RAG工具包重构）
    # -----------------------------------------
    def respond(self, message: str, history_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """标准对话入口：
        - 上层负责传入 history_context（近 15 分钟对话历史，结构化列表）
        - 基类负责：构建 RAG 上下文 + 调用 LLM
        
        Args:
            message: 用户消息
            history_context: 历史对话上下文（可选，由上层传入，如AgentConversationWindow）
                           结构：[{"timestamp": "ISO时间", "message": "...", "response": "..."}]
        
        Returns:
            响应字典，包含type、reply等字段
        """
        # 1) 解析命令（匹配单引号或双引号中的指令）
        cmd = self._extract_command(message)
        if cmd:
            result = self.call_tool("command_line", {"command": cmd, "timeout": 15})
            return {
                "type": "tool_call_result",
                "tool": "command_line",
                "request": cmd,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

        # 2) 正常对话：只走真实LLM，不做伪降级
        if not self.llm_client:
            return {
                "type": "error",
                "error": "LLM未就绪或未配置API密钥",
                "reply": "",
                "timestamp": datetime.now().isoformat(),
            }

        # 2.1 使用RAG工具包构建上下文
        rag_context = ""
        if build_rag_context_text:
            try:
                rag_context = build_rag_context_text(
                    query=message,
                    history_context=history_context or [],
                    cutoff_minutes=15,
                    limit=8,
                )
            except Exception:
                rag_context = ""

        # 2.2 使用RAG工具包构建messages
        system_prompt = (
            getattr(self, "core_system_prompt", None) or 
            getattr(self, "full_system_prompt", None) or 
            "你是一个基于工具和长期记忆增强的智能体。"
        )
        
        if build_llm_messages:
            messages = build_llm_messages(
                system_prompt=system_prompt,
                rag_context=rag_context,
                user_query=message,
            )
        else:
            # 降级方案：手动构建
            messages = [{"role": "system", "content": system_prompt}]
            if rag_context:
                messages.append({
                    "role": "system",
                    "content": f"以下是与你当前问题相关的长期记忆上下文(已按时间窗口与向量库去重):\n{rag_context}"
                })
            messages.append({"role": "user", "content": message})

        # 2.3 调用LLM
        try:
            reply_text = self.llm_client.chat_completion(messages)
        except Exception as e:
            return {
                "type": "error",
                "error": f"LLM调用异常: {str(e)}",
                "reply": "",
                "timestamp": datetime.now().isoformat(),
            }
        
        if not reply_text:
            return {
                "type": "error",
                "error": "LLM未返回结果",
                "reply": "",
                "timestamp": datetime.now().isoformat(),
            }
        
        return {
            "type": "text_reply",
            "reply": reply_text,
            "timestamp": datetime.now().isoformat(),
        }

    def _fallback_reply(self, message: str, prompt: Optional[str] = None) -> str:
        """基础降级回复：结合核心提示词作简要回应"""
        return (
            f"收到：{message}\n"
            f"（基于核心系统提示词的基础回复。可用工具：命令行/文件读写/记忆检索等。）"
        )
    
    def _extract_command(self, text: str) -> Optional[str]:
        """从文本中提取命令字符串：优先匹配引号内内容，其次匹配常见命令词"""
        # 先匹配引号包裹的内容
        m = re.search(r"['\"]([^'\"]+)['\"]", text)
        if m:
            return m.group(1).strip()
        # 次优匹配：常见命令关键词
        keywords = ["ls", "dir", "python", "pip", "git"]
        for kw in keywords:
            if kw in text:
                return kw
        return None

    # -----------------------------------------
    # 工具委托（黑箱）
    # -----------------------------------------
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """委托工具集成器调用具体工具"""
        if not self.tool_integrator:
            return {"success": False, "error": "工具集成器不可用"}
        return self.tool_integrator.call_tool(tool_name, parameters, caller_info={
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
        }, usage_intention="base_agent_auto")

    # -----------------------------------------
    # 记忆创建（用于测试与最小可用能力）
    # -----------------------------------------
    def create_memory(self, content: str, memory_type: str = "conversation", priority: str = "medium", tags: Optional[List[str]] = None) -> Optional[str]:
        """创建记忆条目并写入向量数据库（简化版）"""
        if not self.vector_db:
            return None
        memory_data = {
            "topic": memory_type,
            "content": content,
            "source_type": "agent",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "importance": 0.6 if priority == "high" else (0.5 if priority == "medium" else 0.3),
            "confidence": 0.8,
            "tags": tags or [],
        }
        try:
            return self.vector_db.add_memory(memory_data)
        except Exception:
            return None

    # -----------------------------------------
    # 记忆泡泡功能（基类功能，所有智能体自动具备）
    # -----------------------------------------
    def note_bubble(self, category: str, content: str, context: Optional[Dict[str, Any]] = None, priority: str = "normal") -> Optional[str]:
        """快速记录记忆泡泡（随手记）
        
        Args:
            category: 泡泡类型（问题/构思/优化建议/理解困难/工具问题/记忆问题）
            content: 记录内容
            context: 上下文信息
            priority: 优先级（low/normal/high/urgent）
            
        Returns:
            bubble_id: 泡泡ID（时间戳）
            
        Examples:
            # 工具问题
            agent.note_bubble("工具问题", "file_reading工具处理大文件时很慢", 
                            context={"tool": "file_reading"})
            
            # 优化构思
            agent.note_bubble("构思", "计划实现自动化测试框架")
            
            # 理解困难
            agent.note_bubble("理解困难", "检索到的文本块语义不清晰",
                            context={"memory_id": "mem_12345"}, priority="high")
        """
        if not self.bubble_manager:
            return None
        return self.bubble_manager.quick_note(category, content, context, priority)
    
    def resolve_bubble(self, bubble_id: str, resolution_note: str = "") -> bool:
        """标记泡泡已解决
        
        Args:
            bubble_id: 泡泡ID
            resolution_note: 解决说明
            
        Returns:
            是否成功标记
        """
        if not self.bubble_manager:
            return False
        return self.bubble_manager.mark_resolved(bubble_id, resolution_note)
    
    def get_unresolved_issues(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取未解决的问题（用于上报给系统管家）
        
        Args:
            days: 获取最近N天的未解决问题
            
        Returns:
            未解决的泡泡列表
        """
        if not self.bubble_manager:
            return []
        return self.bubble_manager.get_unresolved_bubbles(days)
    
    def write_daily_diary(self, cleanup_resolved: bool = True) -> Optional[str]:
        """写每日工作日记（基于记忆泡泡）
        
        流程：
        1. 获取今天的记忆泡泡
        2. 导出为日记格式
        3. 保存到智能体专属日记文件
        4. （可选）清理已解决的泡泡
        
        Args:
            cleanup_resolved: 是否清理已解决的泡泡
            
        Returns:
            日记文件路径
        """
        if not self.bubble_manager:
            return None
        
        # 导出日记内容
        diary_content = self.bubble_manager.export_for_diary()
        
        # 保存到智能体专属日记目录
        diary_dir = Path("data/agent_diaries") / self.agent_id
        diary_dir.mkdir(parents=True, exist_ok=True)
        
        diary_filename = f"{datetime.now().strftime('%Y%m%d')}_工作日记.md"
        diary_path = diary_dir / diary_filename
        
        with open(diary_path, 'w', encoding='utf-8') as f:
            f.write(diary_content)
        
        # 清理已解决的泡泡
        if cleanup_resolved:
            cleaned_count = self.bubble_manager.cleanup_resolved_bubbles()
            # 追加清理记录
            with open(diary_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n**泡泡清理**: 已清理 {cleaned_count} 个已解决的泡泡\n")
        
        return str(diary_path)
    
    def get_bubble_statistics(self) -> Dict[str, Any]:
        """获取泡泡统计信息"""
        if not self.bubble_manager:
            return {"error": "泡泡管理器不可用"}
        return self.bubble_manager.get_statistics()

    # -----------------------------------------
    # 智能体反馈功能（进化值评估体系的核心组成）
    # -----------------------------------------
    def submit_tool_feedback(self, tool_name: str, feedback_type: str, 
                            content: str, priority: str = "medium") -> Dict[str, Any]:
        """智能体主动提交工具反馈
        
        这是进化值评估体系的关键功能，允许智能体主动反馈工具使用体验和优化建议，
        驱动工具集合进化，进而实现智能体和系统的整体进化。
        
        进化传递链条：
        智能体主动反馈 → 工具集合进化 → 智能体进化 → 系统进化
        
        Args:
            tool_name: 工具名称（如：MemoryRetrievalTool, FileReadingTool）
            feedback_type: 反馈类型
                - "使用体验"：工具使用过程中的体验反馈
                - "功能优化"：对现有功能的优化建议
                - "新功能需求"：需要新增的功能
                - "问题报告"：工具使用中遇到的问题
            content: 反馈内容（详细描述问题、建议或体验）
            priority: 优先级
                - "low"：低优先级（一般性建议）
                - "medium"：中优先级（常规优化）
                - "high"：高优先级（重要问题或关键优化）
            
        Returns:
            Dict: 反馈提交结果
                - status: "success" 或 "error"
                - feedback_id: 反馈ID（成功时）
                - message: 错误信息（失败时）
            
        Examples:
            # 工具使用体验反馈
            agent.submit_tool_feedback(
                tool_name="FileReadingTool",
                feedback_type="使用体验",
                content="处理大文件（>10MB）时响应较慢，建议优化",
                priority="medium"
            )
            
            # 功能优化建议
            agent.submit_tool_feedback(
                tool_name="MemoryRetrievalTool",
                feedback_type="功能优化",
                content="建议增加语义相似度阈值参数，可以过滤低相关性结果",
                priority="high"
            )
            
            # 问题报告
            agent.submit_tool_feedback(
                tool_name="CommandLineTool",
                feedback_type="问题报告",
                content="Windows环境下执行某些命令时出现编码错误",
                priority="high"
            )
            
            # 新功能需求
            agent.submit_tool_feedback(
                tool_name="VectorDatabase",
                feedback_type="新功能需求",
                content="希望支持批量删除记忆的功能，方便记忆清理",
                priority="low"
            )
        """
        if not self.feedback_collector:
            return {
                "status": "error",
                "message": "反馈收集器不可用，无法提交反馈"
            }
        
        # 调用反馈收集器提交反馈
        result = self.feedback_collector.collect_feedback(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            tool_name=tool_name,
            feedback_type=feedback_type,
            content=content,
            priority=priority
        )
        
        # 记录反馈到泡泡（可选，用于日记记录）
        if result.get("status") == "success" and self.bubble_manager:
            self.bubble_manager.quick_note(
                category="工具问题" if feedback_type == "问题报告" else "优化建议",
                content=f"已提交工具反馈: {tool_name} - {feedback_type}\n{content}",
                context={
                    "feedback_id": result.get("feedback_id"),
                    "tool_name": tool_name,
                    "feedback_type": feedback_type
                },
                priority=priority
            )
        
        return result
    
    def get_my_feedbacks(self, status: Optional[str] = None, 
                        tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取智能体提交的反馈列表
        
        Args:
            status: 反馈状态过滤（pending/evaluated/processed）
            tool_name: 工具名称过滤
            
        Returns:
            List: 反馈列表
        """
        if not self.feedback_collector:
            return []
        
        # 获取所有反馈
        all_feedbacks = self.feedback_collector.get_all_feedbacks(
            status=status,
            tool_name=tool_name
        )
        
        # 筛选属于当前智能体的反馈
        my_feedbacks = [f for f in all_feedbacks if f["agent_id"] == self.agent_id]
        
        return my_feedbacks
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """获取智能体的反馈统计信息
        
        Returns:
            Dict: 统计信息
                - total_feedbacks: 总反馈数
                - by_type: 按反馈类型统计
                - by_priority: 按优先级统计
                - by_status: 按状态统计
                - by_tool: 按工具统计
        """
        my_feedbacks = self.get_my_feedbacks()
        
        if not my_feedbacks:
            return {
                "total_feedbacks": 0,
                "by_type": {},
                "by_priority": {},
                "by_status": {},
                "by_tool": {}
            }
        
        # 统计
        by_type = {}
        by_priority = {}
        by_status = {}
        by_tool = {}
        
        for feedback in my_feedbacks:
            # 按类型统计
            feedback_type = feedback["feedback_type"]
            by_type[feedback_type] = by_type.get(feedback_type, 0) + 1
            
            # 按优先级统计
            priority = feedback["priority"]
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # 按状态统计
            status = feedback["status"]
            by_status[status] = by_status.get(status, 0) + 1
            
            # 按工具统计
            tool_name = feedback["tool_name"]
            by_tool[tool_name] = by_tool.get(tool_name, 0) + 1
        
        return {
            "total_feedbacks": len(my_feedbacks),
            "by_type": by_type,
            "by_priority": by_priority,
            "by_status": by_status,
            "by_tool": by_tool
        }

    # -----------------------------------------
    # 工作日志与日记记录（基类功能）
    # -----------------------------------------
    def _write_work_log(self, content: str, category: str = "工作日志"):
        """记录工作日志
            
        Args:
            content: 日志内容
            category: 日志分类
        """
        # 导入日志模块
        import logging
        logger = logging.getLogger(f"{self.agent_type}_{self.agent_id}")
        logger.info(f"[{category}] {content}")
        
    def _record_to_diary(self, entry: Dict[str, Any]):
        """记录到日记
            
        Args:
            entry: 日记条目，包含type、timestamp等字段
        """
        # 导入日志模块
        import logging
        logger = logging.getLogger(f"{self.agent_type}_{self.agent_id}")
        logger.debug(f"日记记录: {entry.get('type', '未知类型')}")
            
        # 如果有泡泡管理器，可以记录到泡泡中
        if self.bubble_manager:
            try:
                self.bubble_manager.quick_note(
                    category="日记记录",
                    content=f"{entry.get('type', '未知类型')}: {str(entry)[:200]}",
                    context=entry,
                    priority="normal"
                )
            except Exception:
                pass
    
    # -----------------------------------------
    # 日志/摘要(与管理器对接的最小实现)
    # -----------------------------------------
    def get_diary_summary(self, limit: int = 20) -> Dict[str, Any]:
        """提供简单的日记摘要接口,便于管理器聚合显示"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "system_prompt_lengths": {
                "core": len(self.core_system_prompt or ""),
                "extended": len(self.extended_system_prompt or ""),
            },
            "recent_logs": [],
            "limit": limit,
        }
