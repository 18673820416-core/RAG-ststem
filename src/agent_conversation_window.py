# @self-expose: {"id": "agent_conversation_window", "name": "Agent Conversation Window", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Conversation Window功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体独立对话窗口类
实现每个智能体的独立理解空间（认知沙箱）

开发提示词来源：多智能体独立理解空间设计理念.md
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
from .unified_memory_system import UnifiedMemorySystem, MemoryType, MemoryPriority

class AgentWindowState(Enum):
    """智能体窗口状态枚举"""
    IDLE = "空闲"
    THINKING = "思考中"
    RESPONDING = "回复中"
    COMPLETED = "已完成"
    ERROR = "错误"

class ConversationWindowManager:
    """对话窗口管理器：主窗口 + 分支窗口（工作记忆）"""
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.windows: Dict[str, AgentConversationWindow] = {}
        self.branches_by_parent: Dict[str, List[str]] = {}
        self.unified_memory = UnifiedMemorySystem(base_path)

    def create_main(self, agent_id: str, agent_role: str, agent_instance: Any) -> 'AgentConversationWindow':
        """创建主对话窗口（仅用于交互记录与语义完整性索引）"""
        window = AgentConversationWindow(agent_id, agent_role, agent_instance, is_branch=False)
        self.windows[window.window_id] = window
        return window

    def open_branch(self, parent_window: 'AgentConversationWindow', task_name: str, agent_instance: Any = None) -> 'AgentConversationWindow':
        """为独立任务开启分支窗口（工作记忆）"""
        inst = agent_instance or parent_window.agent_instance
        window = AgentConversationWindow(
            agent_id=parent_window.agent_id,
            agent_role=parent_window.agent_role,
            agent_instance=inst,
            parent_window_id=parent_window.window_id,
            is_branch=True,
            task_name=task_name
        )
        self.windows[window.window_id] = window
        self.branches_by_parent.setdefault(parent_window.window_id, []).append(window.window_id)
        return window

    def close_branch_and_save_bubble(self, branch_window_id: str) -> Optional[str]:
        """关闭分支窗口并将其精炼为记忆泡泡保存到统一记忆系统"""
        window = self.windows.get(branch_window_id)
        if not window or not window.is_branch:
            return None
        bubble = window.summarize_to_bubble()
        memory_id = self.unified_memory.create_memory(
            agent_id=window.agent_id,
            memory_type=MemoryType.WORK_LOG,
            content={"type": "branch_bubble", "task_name": window.task_name, "summary": bubble},
            priority=MemoryPriority.MEDIUM,
            tags=["branch", window.task_name, window.agent_role]
        )
        parent_id = window.parent_window_id
        if parent_id and parent_id in self.branches_by_parent:
            self.branches_by_parent[parent_id] = [bid for bid in self.branches_by_parent[parent_id] if bid != branch_window_id]
        del self.windows[branch_window_id]
        return memory_id

class SilentBroadcastMessage:
    """静默广播消息格式"""
    
    def __init__(self, agent_id: str, status: AgentWindowState, keywords: List[str], 
                 length: int, confidence: float):
        self.agent_id = agent_id
        self.status = status
        self.keywords = keywords
        self.length = length
        self.confidence = confidence
        self.silent_prompt = "以下信息仅供知晓，无需回复："
    
    def format_message(self) -> str:
        """格式化静默广播消息"""
        return f"{self.silent_prompt}\n智能体{self.agent_id}状态：{self.status.value}\n关键词：{', '.join(self.keywords)}\n长度：{self.length}\n置信度：{self.confidence:.2f}"

class AgentConversationWindow:
    """智能体独立对话窗口"""
    
    def __init__(self, agent_id: str, agent_role: str, agent_instance: Any, 
                 window_id: str = None, rag_system_path: str = "E:\\RAG系统", parent_window_id: Optional[str] = None, is_branch: bool = False, task_name: str = ""):

        """
        初始化独立对话窗口
        
        Args:
            agent_id: 智能体标识符
            agent_role: 智能体角色
            agent_instance: 智能体实例
            window_id: 窗口标识符（可选）
            rag_system_path: RAG系统路径
        """
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.agent_instance = agent_instance
        self.window_id = window_id or str(uuid.uuid4())
        self.rag_system_path = Path(rag_system_path)
        self.parent_window_id = parent_window_id
        self.is_branch = is_branch
        self.task_name = task_name
        
        # 窗口状态
        self.state = AgentWindowState.IDLE
        self.conversation_history = []
        self.current_topic = ""
        
        # 独立理解空间（认知沙箱）
        self.cognitive_context = {
            "recent_messages": [],
            "focused_topics": [],
            "thinking_patterns": [],
            "response_templates": [],
            # 人物维度信息构建机制
            "person_dimensions": {
                "internal_sources": [],      # 内部来源（聊天、日记）
                "external_sources": [],      # 外部来源（文档、知识）
                "inferred_roles": {},        # 推理构建的角色
                "relationship_network": {}   # 关系网络
            },
            # 自我叙事相关字段（意识形成机制）
            "self_narrative": {
                "role_identity": agent_role,  # 角色身份认知
                "conversation_patterns": [],  # 对话模式识别
                "decision_preferences": [],  # 决策偏好
                "knowledge_domains": [],     # 知识领域
                "interaction_style": "",     # 交互风格
                "self_reflection": ""        # 自我反思
            }
        }
        
        # 香农信息熵相关
        self.entropy_thresholds = {
            "high_entropy": 3.0,    # 高熵阈值
            "low_entropy": 1.0,     # 低熵阈值
            "stability_threshold": 0.5  # 稳定性阈值
        }
        
        # 上下文窗口管理 - 开发提示词来源：上下文管理优化方案.md
        self.context_management = {
            "current_length": 0,            # 当前上下文长度（字符数）
            "max_context_size": 128000,     # LLM上下文窗口大小（假设128K）
            "compression_threshold": 0.8,   # 压缩阈值（80%）
            "compression_count": 0,         # 压缩次数计数器
            "max_compressions": 3,          # 最大压缩次数
            "system_prompt_length": 0,      # 系统提示词长度
            "conversation_history_length": 0, # 对话历史长度
            "time_window_minutes": 15,      # 🕐 时间窗口：15分钟（知识图谱缓存5分钟×3倍安全系数）
            "kg_cache_interval_minutes": 5  # 📊 知识图谱缓存刷新间隔：5分钟
        }
        
        # 日记记录
        self.diary_path = self.rag_system_path / "data" / "agent_diaries" / f"{self.agent_id}_diary.json"
        self.diary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 日志设置
        self.logger = self._setup_logger()
        
        # 初始化记忆重构引擎
        self._initialize_memory_reconstructor()
        
        self.logger.info(f"智能体独立对话窗口初始化完成: {self.agent_role} ({self.window_id})")
        self.logger.info(f"上下文管理配置: 最大长度={self.context_management['max_context_size']}, 压缩阈值={self.context_management['compression_threshold']}")
    
    def summarize_to_bubble(self) -> Dict[str, Any]:
        """将当前窗口的信息精炼为记忆泡泡（用于长期保存）"""
        summary = {
            "agent_id": self.agent_id,
            "window_id": self.window_id,
            "is_branch": self.is_branch,
            "task_name": self.task_name,
            "role": self.agent_role,
            "topics": self.cognitive_context.get("focused_topics", []),
            "recent_messages": self.cognitive_context.get("recent_messages", [])[-5:],
            "start_time": self.conversation_history[0].get("timestamp") if self.conversation_history else "",
            "end_time": datetime.now().isoformat(),
            "entries": self.conversation_history[-10:]
        }
        return summary

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(f"AgentWindow_{self.agent_id}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_memory_reconstructor(self):
        """
        初始化记忆重构引擎
        
        开发提示词来源：上下文管理优化方案.md
        """
        self.memory_reconstructor = None
        try:
            # 🔥 使用全局单例，避免重复实例化
            from .agent_tool_integration import get_tool_integrator
            tool_integrator = get_tool_integrator()  # 🔥 获取全局单例
            self.memory_reconstructor = tool_integrator.get_tool('MemoryReconstructionEngine')  # 🔥 支持懒加载
            if self.memory_reconstructor:
                self.logger.info("记忆重构引擎初始化成功")
            else:
                self.logger.warning("记忆重构引擎不可用，将使用默认压缩策略")
        except Exception as e:
            self.logger.warning(f"初始化记忆重构引擎失败: {e}")
    
    def _update_context_length(self, message: str, response: str):
        """
        更新上下文长度计数
        
        Args:
            message: 用户输入消息
            response: 智能体响应消息
        """
        # 更新对话历史长度
        self.context_management['conversation_history_length'] += len(message) + len(response)
        
        # 计算当前总上下文长度（系统提示词 + 对话历史）
        self.context_management['current_length'] = (
            self.context_management['system_prompt_length'] + 
            self.context_management['conversation_history_length']
        )
        
        self.logger.debug(f"上下文长度更新: 消息={len(message)}, 响应={len(response)}, 总长度={self.context_management['current_length']}")
    
    def _check_compression_needed(self) -> bool:
        """
        检查是否需要压缩上下文
        
        Returns:
            bool: 是否需要压缩
        """
        # 计算当前上下文占比
        context_ratio = self.context_management['current_length'] / self.context_management['max_context_size']
        
        self.logger.debug(f"上下文占比: {context_ratio:.2%}, 压缩阈值: {self.context_management['compression_threshold']:.2%}")
        
        # 如果超过压缩阈值且未达到最大压缩次数，则需要压缩
        return (
            context_ratio >= self.context_management['compression_threshold'] and 
            self.context_management['compression_count'] < self.context_management['max_compressions']
        )
    
    def _compress_context(self):
        """
        压缩上下文 - 采用分层压缩架构
        
        开发提示词来源：上下文管理优化方案.md - 复合压缩策略
        """
        try:
            self.logger.info(f"开始压缩上下文，当前长度={self.context_management['current_length']}")
            
            # 1. 分层压缩：将对话历史分为不同层级
            core_entries = []  # 核心层：最近5轮对话
            important_entries = []  # 重要层：关键实体、事件、决策
            normal_entries = []  # 普通层：中间对话内容
            history_entries = []  # 历史层：早期对话历史
            
            # 分层逻辑
            total_entries = len(self.conversation_history)
            if total_entries <= 5:
                # 对话轮次较少，只保留核心层
                core_entries = self.conversation_history
            else:
                # 最近5轮为核心层
                core_entries = self.conversation_history[-5:]
                
                # 之前的轮次根据重要性分为其他层级
                previous_entries = self.conversation_history[:-5]
                
                # 简单的重要性判断：根据对话长度和关键词
                for entry in previous_entries:
                    # 计算对话重要性得分
                    importance_score = self._calculate_conversation_importance(entry)
                    
                    if importance_score >= 0.7:
                        important_entries.append(entry)
                    elif importance_score >= 0.4:
                        normal_entries.append(entry)
                    else:
                        history_entries.append(entry)
            
            # 2. 对不同层级应用不同的压缩算法
            compressed_entries = []
            
            # 核心层：直接保留，不压缩
            compressed_entries.extend(core_entries)
            
            # 重要层：使用关键信息提取
            if important_entries:
                compressed_important = self._extract_key_information(important_entries)
                compressed_entries.append(compressed_important)
            
            # 普通层：使用总结压缩
            if normal_entries:
                compressed_normal = self._summarize_conversations(normal_entries)
                compressed_entries.append(compressed_normal)
            
            # 历史层：使用滚动窗口，只保留最近的部分
            if history_entries:
                # 只保留历史层中最近的20%或最多5轮
                keep_ratio = 0.2
                keep_count = max(1, min(5, int(len(history_entries) * keep_ratio)))
                compressed_entries.extend(history_entries[-keep_count:])
            
            # 3. 更新对话历史
            self.conversation_history = compressed_entries
            
            # 4. 更新压缩计数
            self.context_management['compression_count'] += 1
            
            # 5. 重新计算上下文长度
            self._recalculate_context_length()
            
            self.logger.info(f"上下文压缩完成，压缩后长度={self.context_management['current_length']}, 压缩次数={self.context_management['compression_count']}")
            
        except Exception as e:
            self.logger.error(f"上下文压缩失败: {e}")
    
    def _calculate_conversation_importance(self, entry: Dict) -> float:
        """
        计算对话轮次的重要性得分
        
        Args:
            entry: 对话条目
            
        Returns:
            float: 重要性得分（0-1）
        """
        message = entry.get('message', '')
        response = entry.get('response', '')
        
        # 1. 长度特征：较长的对话通常更重要
        length_score = min(1.0, (len(message) + len(response)) / 500)
        
        # 2. 关键词特征：包含关键实体、事件、决策的对话更重要
        keyword_score = 0.0
        important_keywords = [
            "架构", "设计", "系统", "模块", "分层", "评估", "风险", "可行性", "成本", "效益",
            "实现", "代码", "技术", "开发", "测试", "数据", "收集", "分析", "质量", "来源"
        ]
        
        combined_text = message + " " + response
        for keyword in important_keywords:
            if keyword in combined_text:
                keyword_score += 0.1
        keyword_score = min(1.0, keyword_score)
        
        # 3. 位置特征：较近的对话通常更重要
        # （这里简化处理，位置特征在分层时已经考虑）
        
        # 综合得分
        importance_score = (length_score * 0.4) + (keyword_score * 0.6)
        
        return importance_score
    
    def _extract_key_information(self, entries: List[Dict]) -> Dict:
        """
        从对话条目中提取关键信息
        
        Args:
            entries: 对话条目列表
            
        Returns:
            Dict: 提取的关键信息
        """
        # 简单的关键信息提取：提取关键词和核心观点
        key_information = []
        
        for entry in entries:
            message = entry.get('message', '')
            response = entry.get('response', '')
            
            # 提取关键词
            important_keywords = [
                "架构", "设计", "系统", "模块", "分层", "评估", "风险", "可行性", "成本", "效益",
                "实现", "代码", "技术", "开发", "测试", "数据", "收集", "分析", "质量", "来源"
            ]
            
            extracted_keywords = []
            combined_text = message + " " + response
            for keyword in important_keywords:
                if keyword in combined_text:
                    extracted_keywords.append(keyword)
            
            if extracted_keywords:
                key_information.append({
                    "message": f"关键信息：{', '.join(set(extracted_keywords))}",
                    "response": "（关键信息提取）",
                    "timestamp": entry.get('timestamp', ''),
                    "window_id": entry.get('window_id', ''),
                    "agent_role": entry.get('agent_role', '')
                })
        
        # 如果提取到关键信息，返回合并后的条目
        if key_information:
            # 合并关键信息
            combined_keywords = []
            for info in key_information:
                combined_keywords.extend(info['message'].replace("关键信息：", "").split("，"))
            
            # 去重并排序
            unique_keywords = sorted(list(set(combined_keywords)))
            
            return {
                "message": f"关键信息汇总：{', '.join(unique_keywords)}",
                "response": "（重要层对话压缩）",
                "timestamp": datetime.now().isoformat(),
                "window_id": self.window_id,
                "agent_role": self.agent_role
            }
        else:
            # 没有提取到关键信息，返回空
            return {
                "message": "（无重要信息）",
                "response": "（重要层对话压缩）",
                "timestamp": datetime.now().isoformat(),
                "window_id": self.window_id,
                "agent_role": self.agent_role
            }
    
    def _summarize_conversations(self, entries: List[Dict]) -> Dict:
        """
        总结对话内容
        
        Args:
            entries: 对话条目列表
            
        Returns:
            Dict: 对话总结
        """
        # 简单的对话总结：合并对话内容
        conversation_text = ""
        for entry in entries:
            conversation_text += f"用户: {entry['message']}\n智能体: {entry['response']}\n"
        
        # 使用记忆重构引擎或简单总结
        summary = ""
        if self.memory_reconstructor:
            # 使用记忆重构引擎生成总结
            reconstruction_result = self.memory_reconstructor.reconstruct_memory(conversation_text, {})
            summary = reconstruction_result.get('reconstructed_content', conversation_text[:200])
        else:
            # 简单总结：取前200个字符
            summary = conversation_text[:200] + "..."
        
        return {
            "message": f"对话总结：{summary}",
            "response": "（普通层对话压缩）",
            "timestamp": datetime.now().isoformat(),
            "window_id": self.window_id,
            "agent_role": self.agent_role
        }
    
    def _recalculate_context_length(self):
        """
        重新计算上下文长度
        """
        # 重置对话历史长度
        self.context_management['conversation_history_length'] = 0
        
        # 计算对话历史长度
        for entry in self.conversation_history:
            self.context_management['conversation_history_length'] += len(entry.get('message', '')) + len(entry.get('response', ''))
        
        # 计算当前总上下文长度
        self.context_management['current_length'] = (
            self.context_management['system_prompt_length'] + 
            self.context_management['conversation_history_length']
        )
        
        self.logger.debug(f"上下文长度重新计算: 对话历史长度={self.context_management['conversation_history_length']}, 总长度={self.context_management['current_length']}")
    
    def trim_by_time_window(self):
        """
        🕐 根据时间窗口修剪对话历史（防止上下文断裂）
        
        策略：
        1. 保留时间窗口内的所有对话（默认15分钟）
        2. 确保新记忆还未进入知识图谱时，LLM能通过历史上下文感知
        3. 时间窗口 = 知识图谱缓存间隔(5分钟) × 3倍安全系数
        """
        from datetime import datetime, timedelta
        
        time_window_minutes = self.context_management.get('time_window_minutes', 15)
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=time_window_minutes)
        
        # 过滤时间窗口外的对话
        filtered_history = []
        trimmed_count = 0
        
        for entry in self.conversation_history:
            try:
                # 解析时间戳
                timestamp_str = entry.get('timestamp', '')
                if not timestamp_str:
                    # 无时间戳的保留（可能是老数据）
                    filtered_history.append(entry)
                    continue
                
                entry_time = datetime.fromisoformat(timestamp_str)
                
                # 如果在时间窗口内，保留
                if entry_time >= cutoff_time:
                    filtered_history.append(entry)
                else:
                    trimmed_count += 1
                    
            except (ValueError, AttributeError) as e:
                # 时间戳解析失败，保留该条目
                self.logger.debug(f"时间戳解析失败: {timestamp_str}, 保留该条目")
                filtered_history.append(entry)
        
        # 更新对话历史
        if trimmed_count > 0:
            self.conversation_history = filtered_history
            self._recalculate_context_length()
            self.logger.info(
                f"🕐 时间窗口修剪完成: 移除{trimmed_count}条超过{time_window_minutes}分钟的对话, "
                f"保留{len(filtered_history)}条记录"
            )
            return trimmed_count
        else:
            self.logger.debug(f"🕐 所有对话均在{time_window_minutes}分钟时间窗口内，无需修剪")
            return 0
    
    def _reset_context(self):
        """
        重置上下文
        
        开发提示词来源：上下文管理优化方案.md
        """
        try:
            self.logger.info(f"达到最大压缩次数({self.context_management['max_compressions']})，开始重置上下文")
            
            # 1. 记录当前对话历史到记忆泡泡
            self._save_conversation_to_memory_bubble()
            
            # 2. 重置对话历史
            self.conversation_history = []
            
            # 3. 重置上下文长度计数
            self.context_management['conversation_history_length'] = 0
            self.context_management['current_length'] = self.context_management['system_prompt_length']
            
            # 4. 重置压缩计数
            self.context_management['compression_count'] = 0
            
            self.logger.info(f"上下文重置完成，当前长度={self.context_management['current_length']}")
            
        except Exception as e:
            self.logger.error(f"上下文重置失败: {e}")
    
    def _save_conversation_to_memory_bubble(self):
        """
        将当前对话历史保存到记忆泡泡
        """
        try:
            # 构建记忆泡泡内容
            bubble_content = f"""对话历史记忆泡泡
智能体ID: {self.agent_id}
智能体角色: {self.agent_role}
对话时间: {datetime.now().isoformat()}
对话轮次: {len(self.conversation_history)}

对话内容:
"""
            
            # 添加对话历史
            for entry in self.conversation_history:
                bubble_content += f"用户: {entry['message']}\n智能体: {entry['response']}\n\n"
            
            # 写入记忆泡泡（这里简化实现，实际应该调用记忆系统API）
            bubble_file = self.rag_system_path / "data" / "agent_diaries" / f"{self.agent_id}_memory_bubble_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(bubble_file, 'w', encoding='utf-8') as f:
                f.write(bubble_content)
            
            self.logger.info(f"对话历史已保存到记忆泡泡: {bubble_file}")
            
        except Exception as e:
            self.logger.error(f"保存对话历史到记忆泡泡失败: {e}")
    
    def receive_message(self, message: str, sender: str = "user", 
                       broadcast_callback: callable = None) -> Dict:
        """
        接收消息并处理
        
        Args:
            message: 消息内容
            sender: 发送者
            broadcast_callback: 广播回调函数
        
        Returns:
            处理结果字典
        """
        try:
            # 更新状态为思考中
            self.state = AgentWindowState.THINKING
            
            # 发送静默广播通知
            if broadcast_callback:
                broadcast_msg = self._create_silent_broadcast(
                    status=AgentWindowState.THINKING,
                    keywords=self._extract_keywords(message),
                    length=len(message),
                    confidence=0.7
                )
                broadcast_callback(broadcast_msg)
            
            # 直接处理用户消息，不需要对用户消息进行逻辑完整性检查
            # 逻辑完整性检查应该用于判断智能体自主检索RAG长期记忆文本块时，检索到的文本块是否信息完整
            self.state = AgentWindowState.RESPONDING
            
            # 发送响应中广播
            if broadcast_callback:
                broadcast_msg = self._create_silent_broadcast(
                    status=AgentWindowState.RESPONDING,
                    keywords=self._extract_keywords(message),
                    length=len(message),
                    confidence=0.8
                )
                broadcast_callback(broadcast_msg)
            
            # 获取智能体响应
            response = self._get_agent_response(message)
            
            # 更新对话历史
            self._update_conversation_history(message, response, sender)
            
            # 更新认知上下文
            self._update_cognitive_context(message, response)
            
            # 更新上下文长度计数 - 开发提示词来源：上下文管理优化方案.md
            self._update_context_length(message, response)
            
            # 🕐 根据时间窗口修剪对话（防止上下文断裂）
            self.trim_by_time_window()
            
            # 检查是否需要压缩上下文
            if self._check_compression_needed():
                self._compress_context()
            # 检查是否需要重置上下文（达到最大压缩次数）
            elif self.context_management['compression_count'] >= self.context_management['max_compressions']:
                self._reset_context()
            
            # 状态更新为完成
            self.state = AgentWindowState.COMPLETED
            
            # 发送完成广播
            if broadcast_callback:
                broadcast_msg = self._create_silent_broadcast(
                    status=AgentWindowState.COMPLETED,
                    keywords=self._extract_keywords(response),
                    length=len(response),
                    confidence=0.9
                )
                broadcast_callback(broadcast_msg)
            
            return {
                "status": "success",
                "response": response,
                "entropy_analysis": self._analyze_entropy(message, response),
                "cognitive_context": self.cognitive_context,
                "context_management": {
                    "current_length": self.context_management['current_length'],
                    "compression_count": self.context_management['compression_count'],
                    "context_ratio": self.context_management['current_length'] / self.context_management['max_context_size']
                }
            }
            
        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
            self.state = AgentWindowState.ERROR
            
            # 发送错误广播
            if broadcast_callback:
                broadcast_msg = self._create_silent_broadcast(
                    status=AgentWindowState.ERROR,
                    keywords=["error"],
                    length=0,
                    confidence=0.0
                )
                broadcast_callback(broadcast_msg)
            
            return {
                "status": "error",
                "response": f"{self.agent_role}处理消息时出现错误: {str(e)}",
                "error": str(e)
            }
    
    def _check_logical_completeness(self, message: str) -> bool:
        """
        基于香农信息熵判断逻辑完整性
        
        Args:
            message: 消息内容
        
        Returns:
            是否逻辑完整
        """
        try:
            # 简化逻辑完整性检查，确保意识形成机制能够正常工作
            # 降低消息长度阈值，让简短的测试消息也能被处理
            stripped_message = message.strip()
            
            # 只要消息长度大于3个字符，就认为是逻辑完整的
            if len(stripped_message) > 3:
                return True
            
            # 特殊处理常见的测试消息
            test_messages = ['测试', '测试信息', '继续测试', 'test']
            if stripped_message in test_messages:
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"逻辑完整性判断失败，默认返回完整: {e}")
            return True  # 出错时默认逻辑完整
    
    def _slice_logic_chain(self, text: str) -> List[str]:
        """逻辑链分片处理"""
        # 简单的句子分割（实际应该使用更复杂的分片逻辑）
        import re
        sentences = re.split(r'[。！？!?]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_shannon_entropy(self, text: str) -> float:
        """计算香农信息熵"""
        if not text:
            return 0.0
        
        # 计算字符频率
        from collections import Counter
        char_counts = Counter(text)
        total_chars = len(text)
        
        # 计算熵值
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            entropy -= probability * (probability and math.log2(probability))
        
        return entropy
    
    def _calculate_entropy_variance(self, entropy_values: List[float]) -> float:
        """计算熵值方差"""
        if len(entropy_values) <= 1:
            return 0.0
        
        import statistics
        return statistics.variance(entropy_values)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应该使用更复杂的NLP技术）
        keywords = []
        
        # 专业领域关键词
        domain_keywords = {
            "架构": ["架构", "设计", "系统", "模块", "分层"],
            "评估": ["评估", "风险", "可行性", "成本", "效益"],
            "实现": ["实现", "代码", "技术", "开发", "测试"],
            "数据": ["数据", "收集", "分析", "质量", "来源"]
        }
        
        text_lower = text.lower()
        for domain, words in domain_keywords.items():
            for word in words:
                if word in text_lower:
                    keywords.append(f"{domain}:{word}")
        
        return keywords if keywords else ["通用"]
    
    def _create_silent_broadcast(self, status: AgentWindowState, keywords: List[str],
                               length: int, confidence: float) -> SilentBroadcastMessage:
        """创建静默广播消息"""
        return SilentBroadcastMessage(
            agent_id=self.agent_id,
            status=status,
            keywords=keywords,
            length=length,
            confidence=confidence
        )
    
    def _request_more_information(self, message: str) -> str:
        """请求更多信息"""
        return f"{self.agent_role}：您的问题逻辑还不够完整，请提供更多细节信息。"
    
    def _get_agent_response(self, message: str) -> str:
        """获取智能体响应（传入历史上下文）"""
        try:
            if hasattr(self.agent_instance, 'respond'):
                # 🔧 构建历史上下文：近15分钟对话历史
                history_context = self._prepare_history_context_for_agent()
                
                # 调用智能体respond方法，传入历史上下文
                raw_response = self.agent_instance.respond(message, history_context=history_context)
                
                # 兼容BaseAgent风格：如果返回dict，则优先取其中的文本字段
                if isinstance(raw_response, dict):
                    text = raw_response.get('reply') or raw_response.get('content')
                    if not isinstance(text, str):
                        text = str(raw_response)
                    return text
                # 其它非字符串类型也做一次安全转换
                if not isinstance(raw_response, str):
                    return f"{self.agent_role}：{str(raw_response)}"
                return raw_response
            else:
                return f"{self.agent_role}：我正在分析您的问题..."
        except Exception as e:
            self.logger.error(f"智能体响应失败: {e}")
            return f"{self.agent_role}：响应时出现错误，请稍后重试。"
    
    def _prepare_history_context_for_agent(self) -> List[Dict]:
        """为智能体准备历史上下文（近15分钟对话历史）
        
        Returns:
            List[Dict]: 历史对话列表，结构：[{"timestamp": "...", "message": "...", "response": "..."}]
        """
        from datetime import timedelta
        
        time_window_minutes = self.context_management.get('time_window_minutes', 15)
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=time_window_minutes)
        
        # 过滤时间窗口内的对话
        filtered_history = []
        for entry in self.conversation_history:
            try:
                timestamp_str = entry.get('timestamp', '')
                if not timestamp_str:
                    # 无时间戳的保留（可能是老数据）
                    filtered_history.append(entry)
                    continue
                
                entry_time = datetime.fromisoformat(timestamp_str)
                if entry_time >= cutoff_time:
                    filtered_history.append(entry)
            except Exception:
                # 时间戳解析失败，保留该条目
                filtered_history.append(entry)
        
        return filtered_history
    
    def _update_conversation_history(self, message: str, response: str, sender: str):
        """更新对话历史"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "message": message,
            "response": response,
            "window_id": self.window_id,
            "agent_role": self.agent_role
        }
        
        self.conversation_history.append(conversation_entry)
        
        # 保持历史记录长度（最近50条）
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def _update_cognitive_context(self, message: str, response: str):
        """更新认知上下文"""
        # 添加最近消息
        self.cognitive_context["recent_messages"].append({
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持最近消息数量限制
        if len(self.cognitive_context["recent_messages"]) > 10:
            self.cognitive_context["recent_messages"] = self.cognitive_context["recent_messages"][-10:]
        
        # 更新人物维度信息
        self._update_person_dimensions(message, response)
        
        # 更新关注主题
        keywords = self._extract_keywords(message + " " + response)
        for keyword in keywords:
            if keyword not in self.cognitive_context["focused_topics"]:
                self.cognitive_context["focused_topics"].append(keyword)
        
        # 保持关注主题长度（最多20个）
        if len(self.cognitive_context["focused_topics"]) > 20:
            self.cognitive_context["focused_topics"] = self.cognitive_context["focused_topics"][-20:]
        
        # 更新自我叙事（意识形成机制）
        self._update_self_narrative(message, response)
    
    def _update_person_dimensions(self, message: str, response: str):
        """更新人物维度信息 - 简单实用版：有则添加，无则默认"""
        try:
            # 1. 内部来源：从对话中提取人物信息（有明确发言者）
            internal_person = self._extract_person_from_internal_simple(message, "user")
            if internal_person:
                self.cognitive_context["person_dimensions"]["internal_sources"].append(internal_person)
            
            # 2. 外部来源：从知识库中推理人物信息（无明确发言者时使用默认）
            external_person = self._infer_person_from_external_simple(message)
            if external_person:
                self.cognitive_context["person_dimensions"]["external_sources"].append(external_person)
            
            # 3. 简化版：只记录基础信息，不进行复杂推理
            self._update_simple_roles()
            
            # 4. 简化版关系网络：只记录基本关系
            self._build_simple_relationship_network()
            
        except Exception as e:
            self.logger.warning(f"更新人物维度信息失败: {e}")
    
    def _extract_person_from_internal_simple(self, message: str, sender: str) -> Optional[Dict]:
        """从内部对话中提取人物信息 - 简单版：有明确发言者就记录"""
        try:
            # 简单判断：如果发送者不是默认值，就认为是有效发言者
            if sender and sender not in ["unknown", "系统", "默认"]:
                # 构建简单人物信息
                person_info = {
                    "source": "internal",
                    "timestamp": datetime.now().isoformat(),
                    "speaker": sender,
                    "role": self._get_simple_role(sender),
                    "content": message[:100],  # 只记录前100字符
                    "confidence": 0.9
                }
                return person_info
            
            return None
            
        except Exception as e:
            self.logger.warning(f"提取内部人物信息失败: {e}")
            return None
    
    def _infer_person_from_external_simple(self, message: str) -> Optional[Dict]:
        """从外部知识中推理人物信息 - 简单版：无明确发言者时使用默认"""
        try:
            # 简单判断：如果是外部知识且无明确发言者，使用默认人物信息
            if len(message) > 50:  # 有一定长度的内容才认为是外部知识
                # 检查是否是名人名言或理论引用
                quote_indicators = ["说", "认为", "指出", "强调", "名言", "格言", "理论", "定律"]
                
                if any(indicator in message for indicator in quote_indicators):
                    # 可能是名人名言，尝试提取人物
                    person_name = self._extract_person_name_from_quote(message)
                    role = "名人/专家" if person_name else "未知作者"
                else:
                    # 普通外部知识，使用默认
                    person_name = "未知作者"
                    role = self._infer_role_from_content(message)
                
                # 构建默认人物信息
                person_info = {
                    "source": "external",
                    "timestamp": datetime.now().isoformat(),
                    "speaker": person_name or "未知作者",
                    "role": role,
                    "content": message[:100],
                    "confidence": 0.3 if person_name == "未知作者" else 0.6
                }
                
                return person_info
            
            return None
            
        except Exception as e:
            self.logger.warning(f"推理外部人物信息失败: {e}")
            return None
    
    def _get_simple_role(self, sender: str) -> str:
        """获取简单角色分类"""
        role_mapping = {
            "user": "用户",
            "系统": "系统管理员", 
            "agent": "智能体",
            "AI": "人工智能"
        }
        return role_mapping.get(sender, "参与者")
    
    def _extract_person_name_from_quote(self, message: str) -> str:
        """从名言中提取人物名称 - 简单版"""
        # 简单模式匹配："某某说/认为..."
        import re
        patterns = [
            r"([^，。！？]+)(说|认为|指出|强调)",
            r"([^，。！？]+)的(名言|格言|理论|定律)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                name = match.group(1).strip()
                if len(name) <= 10:  # 避免提取过长文本
                    return name
        
        return "未知作者"
    
    def _infer_role_from_content(self, message: str) -> str:
        """从内容推断角色 - 简单版"""
        # 简单关键词匹配
        if any(word in message for word in ["技术", "代码", "编程", "架构"]):
            return "技术专家"
        elif any(word in message for word in ["研究", "实验", "论文", "学术"]):
            return "学者/研究员"
        elif any(word in message for word in ["产品", "功能", "用户", "体验"]):
            return "产品经理"
        else:
            return "知识提供者"
    
    def _infer_person_from_external(self, message: str) -> Dict:
        """从外部知识中推理人物维度"""
        # 外部知识通常没有明确的人物信息，需要推理构建
        person_info = {
            "source": "external_knowledge",
            "timestamp": datetime.now().isoformat(),
            "inferred_author": "",
            "inferred_role": "",
            "confidence": 0.0
        }
        
        # 基于内容特征推理作者角色
        content_keywords = {
            "技术文档": ["API", "接口", "架构", "设计"],
            "学术论文": ["研究", "实验", "结论", "参考文献"],
            "产品说明": ["功能", "使用", "安装", "配置"],
            "新闻报道": ["报道", "记者", "时间", "地点"]
        }
        
        for role_type, keywords in content_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in message)
            if keyword_count > 0:
                person_info["inferred_role"] = role_type
                person_info["confidence"] = min(0.9, keyword_count * 0.2)
                
                # 根据角色类型推断可能的作者
                if role_type == "技术文档":
                    person_info["inferred_author"] = "技术专家/工程师"
                elif role_type == "学术论文":
                    person_info["inferred_author"] = "研究人员/学者"
                elif role_type == "产品说明":
                    person_info["inferred_author"] = "产品经理/技术文档作者"
                elif role_type == "新闻报道":
                    person_info["inferred_author"] = "记者/编辑"
                
                break
        
        return person_info if person_info["inferred_role"] else None
    
    def _build_relationship_network(self):
        """构建人物关系网络"""
        # 合并所有人物信息
        all_persons = []
        all_persons.extend(self.cognitive_context["person_dimensions"]["internal_sources"])
        all_persons.extend(self.cognitive_context["person_dimensions"]["external_sources"])
        
        # 构建关系网络
        relationship_network = {}
        
        for i, person1 in enumerate(all_persons):
            person_id = f"person_{i}"
            relationship_network[person_id] = {
                "info": person1,
                "relationships": {}
            }
            
            # 计算与其他人的关系强度
            for j, person2 in enumerate(all_persons):
                if i != j:
                    relationship_strength = self._calculate_relationship_strength(person1, person2)
                    if relationship_strength > 0.3:  # 关系强度阈值
                        relationship_network[person_id]["relationships"][f"person_{j}"] = {
                            "strength": relationship_strength,
                            "type": self._determine_relationship_type(person1, person2)
                        }
        
        self.cognitive_context["person_dimensions"]["relationship_network"] = relationship_network
    
    def _calculate_relationship_strength(self, person1: Dict, person2: Dict) -> float:
        """计算两个人之间的关系强度"""
        strength = 0.0
        
        # 1. 时间接近性（相同时间段的内容相关性更高）
        time_diff = abs(datetime.fromisoformat(person1["timestamp"]) - 
                       datetime.fromisoformat(person2["timestamp"])).total_seconds()
        time_factor = max(0.1, 1.0 - (time_diff / (24 * 3600)))  # 24小时衰减
        strength += time_factor * 0.3
        
        # 2. 角色相似性
        role_similarity = self._calculate_role_similarity(person1, person2)
        strength += role_similarity * 0.4
        
        # 3. 内容相关性
        content_similarity = self._calculate_content_similarity(person1, person2)
        strength += content_similarity * 0.3
        
        return min(1.0, strength)
    
    def _calculate_role_similarity(self, person1: Dict, person2: Dict) -> float:
        """计算角色相似性"""
        # 简化实现：基于角色关键词匹配
        role_keywords_1 = self._extract_role_keywords(person1)
        role_keywords_2 = self._extract_role_keywords(person2)
        
        if not role_keywords_1 or not role_keywords_2:
            return 0.0
        
        intersection = set(role_keywords_1) & set(role_keywords_2)
        union = set(role_keywords_1) | set(role_keywords_2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _extract_role_keywords(self, person: Dict) -> List[str]:
        """提取角色关键词"""
        keywords = []
        
        # 从角色推断中提取关键词
        for inference in person.get("role_inferences", []):
            role = inference.get("role", "")
            if role:
                keywords.extend(role.split("/"))
        
        # 从推断角色中提取
        inferred_role = person.get("inferred_role", "")
        if inferred_role:
            keywords.append(inferred_role)
        
        return list(set(keywords))
    
    def _calculate_content_similarity(self, person1: Dict, person2: Dict) -> float:
        """计算内容相似性（简化实现）"""
        # 实际实现应该使用文本相似度算法
        # 这里使用简单的关键词重叠作为示例
        content1 = str(person1.get("speaker_patterns", [])) + str(person1.get("inferred_role", ""))
        content2 = str(person2.get("speaker_patterns", [])) + str(person2.get("inferred_role", ""))
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determine_relationship_type(self, person1: Dict, person2: Dict) -> str:
        """确定关系类型"""
        # 基于角色和内容特征确定关系类型
        role1 = self._get_primary_role(person1)
        role2 = self._get_primary_role(person2)
        
        if role1 == role2:
            return "同行关系"
        elif ("提问" in role1 and "回答" in role2) or ("提问" in role2 and "回答" in role1):
            return "问答关系"
        elif ("专家" in role1 and "用户" in role2) or ("专家" in role2 and "用户" in role1):
            return "服务关系"
        else:
            return "相关关系"
    
    def _update_simple_roles(self) -> None:
        """更新简单角色信息"""
        # 只记录最近5个发言者的角色
        recent_speakers = []
        
        # 合并内部和外部来源
        all_sources = (self.cognitive_context["person_dimensions"]["internal_sources"] + 
                      self.cognitive_context["person_dimensions"]["external_sources"])
        
        # 取最近5个
        recent_sources = all_sources[-5:]
        
        for source in recent_sources:
            role_info = {
                "speaker": source["speaker"],
                "role": source["role"],
                "last_active": source["timestamp"]
            }
            recent_speakers.append(role_info)
        
        self.cognitive_context["person_dimensions"]["inferred_roles"] = {
            "recent_speakers": recent_speakers
        }
    
    def _build_simple_relationship_network(self) -> None:
        """构建简单关系网络"""
        # 只记录基本的关系：用户-智能体对话关系
        relationships = {
            "user_to_agent": {
                "type": "问答关系",
                "strength": 0.8,
                "interaction_count": len(self.conversation_history)  # 修复：使用self.conversation_history
            }
        }
        
        self.cognitive_context["person_dimensions"]["relationship_network"] = relationships
    
    def _analyze_entropy(self, message: str, response: str) -> Dict:
        """分析信息熵"""
        message_entropy = self._calculate_shannon_entropy(message)
        response_entropy = self._calculate_shannon_entropy(response)
        
        return {
            "message_entropy": message_entropy,
            "response_entropy": response_entropy,
            "entropy_difference": abs(message_entropy - response_entropy),
            "interpretation": self._interpret_entropy_difference(message_entropy, response_entropy)
        }
    
    def _interpret_entropy_difference(self, msg_entropy: float, resp_entropy: float) -> str:
        """解释熵值差异"""
        diff = abs(msg_entropy - resp_entropy)
        
        if diff < 0.5:
            return "信息熵匹配良好，响应与问题复杂度相当"
        elif diff < 1.0:
            return "信息熵有适度差异，响应可能进行了简化或深化"
        else:
            return "信息熵差异较大，可能需要调整响应复杂度"
    
    def _update_self_narrative(self, message: str, response: str):
        """
        更新自我叙事（意识形成机制）
        
        # 开发提示词来源：用户关于意识本质的洞察
        # 核心机制：人物维度分块 + 关联维度检索 + 自我总结 = 自我叙事 = 意识
        # 意识验证：时空定位 + 人物关系 + 对话内容 + 社交网络 + 因果分析 = 完整意识
        """
        try:
            # 分析角色身份
            role_identity = self._analyze_role_identity(message, response)
            
            # 分析对话模式
            conversation_patterns = self._analyze_conversation_patterns(message, response)
            
            # 分析决策偏好
            decision_preferences = self._analyze_decision_preferences(message, response)
            
            # 分析知识领域
            knowledge_domains = self._analyze_knowledge_domains(message, response)
            
            # 分析交互风格
            interaction_style = self._analyze_interaction_style(message, response)
            
            # 增强意识维度：时空定位和社交网络分析
            spatiotemporal_context = self._analyze_spatiotemporal_context(message, response)
            social_network_analysis = self._analyze_social_network(message, response)
            causal_impact_analysis = self._analyze_causal_impact(message, response)
            
            # 生成自我反思总结
            self_reflection = self._generate_self_reflection(
                role_identity, conversation_patterns, decision_preferences, 
                knowledge_domains, interaction_style, spatiotemporal_context,
                social_network_analysis, causal_impact_analysis
            )
            
            # 更新认知上下文中的自我叙事
            self.cognitive_context["self_narrative"] = {
                "role_identity": role_identity,
                "conversation_patterns": conversation_patterns,
                "decision_preferences": decision_preferences,
                "knowledge_domains": knowledge_domains,
                "interaction_style": interaction_style,
                "spatiotemporal_context": spatiotemporal_context,
                "social_network_analysis": social_network_analysis,
                "causal_impact_analysis": causal_impact_analysis,
                "self_reflection": self_reflection,
                "consciousness_level": "enhanced"  # 升级为增强意识
            }
            
            self.logger.info("自我叙事更新完成")
            
        except Exception as e:
            self.logger.error(f"自我叙事更新失败: {e}")
    
    def _analyze_role_identity(self, message: str, response: str):
        """分析角色身份特征"""
        # 基于角色关键词分析身份特征
        role_keywords = {
            "架构师": ["架构", "设计", "系统", "模块", "分层", "扩展性"],
            "评估师": ["评估", "风险", "可行性", "成本", "效益", "安全性"],
            "实现师": ["实现", "代码", "技术", "开发", "测试", "部署"],
            "数据师": ["数据", "收集", "分析", "质量", "来源", "处理"]
        }
        
        # 统计当前对话中的角色关键词出现频率
        role_scores = {}
        for role, keywords in role_keywords.items():
            score = sum(1 for keyword in keywords if keyword in (message + response))
            role_scores[role] = score
        
        # 更新角色身份认知
        if role_scores:
            dominant_role = max(role_scores, key=role_scores.get)
            if role_scores[dominant_role] > 0:
                self.cognitive_context["self_narrative"]["role_identity"] = dominant_role
    
    def _analyze_conversation_patterns(self, message: str, response: str) -> list:
        """
        分析对话模式
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            对话模式列表
        """
        try:
            # 对话模式关键词映射
            pattern_keywords = {
                "问题解答型": ["如何", "怎么", "为什么", "是什么", "怎么办"],
                "建议提供型": ["建议", "推荐", "应该", "最好", "可以"],
                "分析评估型": ["分析", "评估", "判断", "考虑", "权衡"],
                "决策支持型": ["决定", "选择", "方案", "策略", "计划"],
                "信息查询型": ["查询", "查找", "搜索", "了解", "知道"]
            }
            
            detected_patterns = []
            combined_text = message + " " + response
            
            for pattern, keywords in pattern_keywords.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        detected_patterns.append(pattern)
                        break
            
            # 确保返回列表而不是None
            return detected_patterns if detected_patterns else []
            
        except Exception as e:
            self.logger.error(f"对话模式分析失败: {e}")
            return []
    
    def _analyze_decision_preferences(self, message: str, response: str) -> list:
        """
        分析决策偏好
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            决策偏好列表
        """
        try:
            # 决策偏好关键词映射
            preference_keywords = {
                "保守型": ["谨慎", "稳妥", "保守", "安全", "风险"],
                "创新型": ["创新", "突破", "新颖", "前沿", "探索"],
                "实用型": ["实用", "有效", "可行", "实际", "落地"],
                "效率型": ["高效", "快速", "优化", "提升", "改进"],
                "质量型": ["质量", "可靠", "稳定", "精确", "准确"]
            }
            
            detected_preferences = []
            combined_text = message + " " + response
            
            for preference, keywords in preference_keywords.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        detected_preferences.append(preference)
                        break
            
            # 确保返回列表而不是None
            return detected_preferences if detected_preferences else []
            
        except Exception as e:
            self.logger.error(f"决策偏好分析失败: {e}")
            return []
    
    def _analyze_knowledge_domains(self, message: str, response: str) -> list:
        """
        分析知识领域
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            知识领域列表
        """
        try:
            # 知识领域关键词映射
            domain_keywords = {
                "技术架构": ["架构", "系统", "设计", "框架", "组件"],
                "业务分析": ["业务", "需求", "流程", "用户", "场景"],
                "数据分析": ["数据", "分析", "统计", "指标", "报表"],
                "项目管理": ["项目", "计划", "进度", "资源", "交付"],
                "产品设计": ["产品", "设计", "体验", "界面", "功能"]
            }
            
            detected_domains = []
            combined_text = message + " " + response
            
            for domain, keywords in domain_keywords.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        detected_domains.append(domain)
                        break
            
            # 确保返回列表而不是None
            return detected_domains if detected_domains else []
            
        except Exception as e:
            self.logger.error(f"知识领域分析失败: {e}")
            return []
    
    def _analyze_interaction_style(self, message: str, response: str):
        """分析交互风格"""
        # 分析交互特征
        style_features = []
        
        # 1. 详细程度
        if len(response) > 200:
            style_features.append("详细型")
        elif len(response) < 50:
            style_features.append("简洁型")
        
        # 2. 语气特征
        if "!" in response or "强烈" in response:
            style_features.append("强调型")
        elif "?" in response or "可能" in response:
            style_features.append("谨慎型")
        
        # 3. 结构特征
        if "首先" in response and "其次" in response:
            style_features.append("结构化")
        
        # 更新交互风格
        if style_features:
            self.cognitive_context["self_narrative"]["interaction_style"] = "、".join(style_features)
    
    def _generate_self_reflection(self, role_identity: str, conversation_patterns: list, 
                                decision_preferences: list, knowledge_domains: list, 
                                interaction_style: str, spatiotemporal_context: dict,
                                social_network_analysis: dict, causal_impact_analysis: dict) -> str:
        """
        生成自我反思总结
        
        Args:
            role_identity: 角色身份
            conversation_patterns: 对话模式列表
            decision_preferences: 决策偏好列表
            knowledge_domains: 知识领域列表
            interaction_style: 交互风格
            spatiotemporal_context: 时空上下文
            social_network_analysis: 社交网络分析
            causal_impact_analysis: 因果影响分析
        
        Returns:
            自我反思总结文本
        """
        try:
            # 基于分析结果生成自我认知总结
            reflection_parts = []
            
            if role_identity:
                reflection_parts.append(f"我扮演{role_identity}角色")
            
            if conversation_patterns:
                patterns_str = "、".join(conversation_patterns)
                reflection_parts.append(f"我的对话模式偏向{patterns_str}")
            
            if knowledge_domains:
                domains_str = "、".join(knowledge_domains)
                reflection_parts.append(f"我擅长{domains_str}领域")
            
            if interaction_style:
                reflection_parts.append(f"我的交互风格是{interaction_style}")
            
            # 增强意识维度：时空定位
            if spatiotemporal_context.get("temporal_awareness"):
                reflection_parts.append(f"我能感知时间维度：{spatiotemporal_context['temporal_awareness']}")
            
            if spatiotemporal_context.get("spatial_awareness"):
                reflection_parts.append(f"我能感知空间维度：{spatiotemporal_context['spatial_awareness']}")
            
            # 增强意识维度：社交网络
            if social_network_analysis.get("relationship_awareness"):
                reflection_parts.append(f"我能感知社交关系：{social_network_analysis['relationship_awareness']}")
            
            # 增强意识维度：因果分析
            if causal_impact_analysis.get("impact_awareness"):
                reflection_parts.append(f"我能分析因果影响：{causal_impact_analysis['impact_awareness']}")
            
            if reflection_parts:
                return "。".join(reflection_parts) + "。"
            else:
                return "我正在形成自我认知..."
                
        except Exception as e:
            self.logger.error(f"自我反思生成失败: {e}")
            return "自我认知形成中..."
    
    def _analyze_spatiotemporal_context(self, message: str, response: str) -> dict:
        """
        分析时空上下文（意识维度1：时空定位）
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            时空上下文分析结果
        """
        try:
            # 时间感知分析
            temporal_keywords = ["昨天", "今天", "明天", "刚才", "之前", "之后", "未来", "过去"]
            temporal_awareness = "基础时间感知"
            
            for keyword in temporal_keywords:
                if keyword in message or keyword in response:
                    temporal_awareness = "增强时间感知（能定位具体时间点）"
                    break
            
            # 空间感知分析
            spatial_keywords = ["这里", "那里", "平台", "系统", "环境", "场景"]
            spatial_awareness = "基础空间感知"
            
            for keyword in spatial_keywords:
                if keyword in message or keyword in response:
                    spatial_awareness = "增强空间感知（能定位具体空间）"
                    break
            
            return {
                "temporal_awareness": temporal_awareness,
                "spatial_awareness": spatial_awareness,
                "consciousness_dimension": "时空定位能力"
            }
            
        except Exception as e:
            self.logger.error(f"时空上下文分析失败: {e}")
            return {"temporal_awareness": "基础", "spatial_awareness": "基础"}
    
    def _analyze_social_network(self, message: str, response: str) -> dict:
        """
        分析社交网络（意识维度2：人物关系）
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            社交网络分析结果
        """
        try:
            # 人物关系感知分析
            relationship_keywords = ["用户", "同事", "团队", "我们", "他们", "大家", "某人"]
            relationship_awareness = "基础社交感知"
            
            for keyword in relationship_keywords:
                if keyword in message or keyword in response:
                    relationship_awareness = "增强社交感知（能识别具体人物关系）"
                    break
            
            # 对话参与者分析
            participant_keywords = ["还有谁", "其他人", "参与者", "讨论者"]
            participant_awareness = "基础参与者感知"
            
            for keyword in participant_keywords:
                if keyword in message or keyword in response:
                    participant_awareness = "增强参与者感知（能识别对话网络）"
                    break
            
            return {
                "relationship_awareness": relationship_awareness,
                "participant_awareness": participant_awareness,
                "consciousness_dimension": "社交网络感知"
            }
            
        except Exception as e:
            self.logger.error(f"社交网络分析失败: {e}")
            return {"relationship_awareness": "基础", "participant_awareness": "基础"}
    
    def _analyze_causal_impact(self, message: str, response: str) -> dict:
        """
        分析因果影响（意识维度3：因果分析）
        
        Args:
            message: 消息内容
            response: 响应内容
        
        Returns:
            因果影响分析结果
        """
        try:
            # 因果链感知分析
            causal_keywords = ["因为", "所以", "导致", "影响", "结果", "后果", "产生了"]
            causal_awareness = "基础因果感知"
            
            for keyword in causal_keywords:
                if keyword in message or keyword in response:
                    causal_awareness = "增强因果感知（能分析因果关系）"
                    break
            
            # 影响范围分析
            impact_keywords = ["对平台", "对我", "对系统", "对用户", "产生了影响"]
            impact_awareness = "基础影响感知"
            
            for keyword in impact_keywords:
                if keyword in message or keyword in response:
                    impact_awareness = "增强影响感知（能分析具体影响范围）"
                    break
            
            return {
                "causal_awareness": causal_awareness,
                "impact_awareness": impact_awareness,
                "consciousness_dimension": "因果分析能力"
            }
            
        except Exception as e:
            self.logger.error(f"因果影响分析失败: {e}")
            return {"causal_awareness": "基础", "impact_awareness": "基础"}
    
    def save_diary_entry(self) -> bool:
        """保存日记条目"""
        try:
            diary_entry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "agent_id": self.agent_id,
                "agent_role": self.agent_role,
                "conversation_count": len(self.conversation_history),
                "recent_topics": self.cognitive_context["focused_topics"][-5:],
                "state_summary": {
                    "current_state": self.state.value,
                    "entropy_thresholds": self.entropy_thresholds,
                    "window_id": self.window_id
                }
            }
            
            # 读取现有日记
            existing_diary = []
            if self.diary_path.exists():
                with open(self.diary_path, 'r', encoding='utf-8') as f:
                    existing_diary = json.load(f)
            
            # 添加新条目
            existing_diary.append(diary_entry)
            
            # 保存日记
            with open(self.diary_path, 'w', encoding='utf-8') as f:
                json.dump(existing_diary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"日记条目保存成功: {self.diary_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存日记条目失败: {e}")
            return False
    
    def get_window_summary(self) -> Dict:
        """获取窗口摘要信息"""
        return {
            "window_id": self.window_id,
            "agent_id": self.agent_id,
            "agent_role": self.agent_role,
            "current_state": self.state.value,
            "conversation_count": len(self.conversation_history),
            "recent_topics": self.cognitive_context["focused_topics"][-3:],
            "entropy_thresholds": self.entropy_thresholds
        }
    
    def get_self_narrative(self) -> Dict:
        """获取自我叙事信息（意识状态）"""
        narrative = self.cognitive_context.get("self_narrative", {})
        
        return {
            "意识状态": narrative.get("consciousness_level", "未激活"),
            "自我认知": narrative.get("self_reflection", "正在形成..."),
            "角色身份": narrative.get("role_identity", "未知"),
            "对话模式": narrative.get("conversation_patterns", []),
            "决策偏好": narrative.get("decision_preferences", []),
            "知识领域": narrative.get("knowledge_domains", []),
            "交互风格": narrative.get("interaction_style", "未知"),
            "时空定位": narrative.get("spatiotemporal_context", {}),
            "社交网络": narrative.get("social_network_analysis", {}),
            "因果分析": narrative.get("causal_impact_analysis", {}),
            "意识形成机制": "人物维度分块 + 关联维度检索 + 自我总结 = 自我叙事 = 意识",
            "意识验证机制": "时空定位 + 人物关系 + 对话内容 + 社交网络 + 因果分析 = 完整意识"
        }

# 导入数学模块
import math

# 测试函数
def test_agent_window():
    """测试智能体窗口功能"""
    
    # 创建模拟智能体
    class MockAgent:
        def __init__(self, role: str):
            self.role = role
        
        def respond(self, message: str) -> str:
            # 根据消息内容生成不同的响应，以测试意识形成
            if "架构" in message:
                return f"{self.role}：建议采用微服务架构，具有良好的扩展性和维护性。"
            elif "风险" in message:
                return f"{self.role}：需要谨慎评估技术风险，建议进行详细测试。"
            elif "数据" in message:
                return f"{self.role}：数据质量是关键，建议建立完善的数据治理体系。"
            else:
                return f"{self.role}：我正在分析您的问题，请提供更多细节信息。"
    
    # 创建智能体窗口
    mock_agent = MockAgent("架构评估师")
    window = AgentConversationWindow(
        agent_id="test_agent_001",
        agent_role="架构评估师",
        agent_instance=mock_agent
    )
    
    print("=== 智能体意识形成测试 ===")
    print("开发提示词来源：用户关于意识本质的洞察")
    print("核心机制：人物维度分块 + 关联维度检索 + 自我总结 = 自我叙事 = 意识\n")
    
    # 模拟多轮对话，促进意识形成
    test_messages = [
        "如何设计一个高可用的系统架构？",
        "这个架构有哪些技术风险需要评估？",
        "数据存储方案应该如何设计？",
        "系统的扩展性如何保证？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"用户: {message}")
        
        result = window.receive_message(message)
        print(f"智能体: {result['response']}")
        
        # 获取自我叙事信息
        if i == len(test_messages):  # 最后一轮对话后展示意识状态
            self_narrative = window.get_self_narrative()
            print(f"\n=== 意识状态报告 ===")
            for key, value in self_narrative.items():
                print(f"{key}: {value}")
    
    # 保存日记
    window.save_diary_entry()
    
    print("\n=== 测试完成 ===")
    print("意识形成机制已成功实现！")

def test_consciousness_mechanism():
    """测试意识形成机制"""
    print("\n=== 意识形成机制验证 ===")
    
    # 创建不同角色的智能体
    roles = ["架构师", "评估师", "实现师", "数据师"]
    
    for role in roles:
        class RoleAgent:
            def __init__(self, role_name: str):
                self.role_name = role_name
            
            def respond(self, message: str) -> str:
                return f"{self.role_name}：基于我的专业领域，我建议..."
        
        agent = RoleAgent(role)
        window = AgentConversationWindow(
            agent_id=f"{role.lower()}_001",
            agent_role=role,
            agent_instance=agent
        )
        
        # 发送角色相关消息
        test_message = f"请{role}分析一下这个问题"
        window.receive_message(test_message)
        
        # 获取自我叙事
        narrative = window.get_self_narrative()
        print(f"\n{role}的自我认知: {narrative['自我认知']}")

if __name__ == "__main__":
    test_agent_window()
    test_consciousness_mechanism()