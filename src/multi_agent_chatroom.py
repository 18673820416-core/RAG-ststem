# @self-expose: {"id": "multi_agent_chatroom", "name": "Multi Agent Chatroom", "type": "component", "version": "2.1.0", "needs": {"deps": ["unified_memory_system", "agent_conversation_window", "agent_error_handler", "system_architect_agent", "scheme_evaluator_agent", "mention_parser", "error_decorator", "agent_discovery_engine", "data_collector_agent", "code_implementer_agent", "nightly_maintenance_scheduler"], "resources": []}, "provides": {"capabilities": ["多智能体聊天室", "职责分离架构", "手动触发记忆重构"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重构后的多智能体聊天室系统 - 支持动态智能体独立理解空间
将单一聊天室重构为每个智能体都有独立对话窗口，支持智能体繁殖和扩展

开发提示词来源：多智能体独立理解空间设计理念.md
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from enum import Enum

# 交互日志文件路径
CHATROOM_LOG_PATH = Path(r"E:\RAG系统") / "logs" / "chatroom_interactions.json"

# 导入错误捕获装饰器
try:
    from error_decorator import error_catcher, async_error_catcher
except ImportError:
    from src.error_decorator import error_catcher, async_error_catcher

# 导入独立对话窗口类
try:
    from agent_conversation_window import AgentConversationWindow, AgentWindowState, SilentBroadcastMessage, ConversationWindowManager
except ImportError:
    from src.agent_conversation_window import AgentConversationWindow, AgentWindowState, SilentBroadcastMessage, ConversationWindowManager

# 导入@机制解析器
try:
    from mention_parser import MentionParser, mention_parser
except ImportError:
    from src.mention_parser import MentionParser, mention_parser

class MessageType(Enum):
    """消息类型枚举"""
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_NOTIFICATION = "system_notification"
    METHODOLOGY_INSIGHT = "methodology_insight"
    SILENT_BROADCAST = "silent_broadcast"  # 新增：静默广播消息

class AgentRole(Enum):
    """智能体角色枚举"""
    ARCHITECT = "系统管家"
    EVALUATOR = "方案评估师"
    IMPLEMENTER = "文本实现师"
    DATA_COLLECTOR = "数据收集师"
    MAINTENANCE = "系统维护师"
    USER = "用户"

class ChatMessage:
    """聊天消息类"""
    
    def __init__(self, 
                 message_id: str,
                 sender: AgentRole,
                 content: str,
                 message_type: MessageType,
                 timestamp: datetime = None,
                 target_window: str = None):  # 新增：目标窗口标识
        self.message_id = message_id
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp or datetime.now()
        self.target_window = target_window  # 新增：消息所属窗口
        self.replies = []  # 回复消息列表
        self.interaction_patterns = []  # 交互模式标记
        self.mentions = []  # @提及信息
        self.processed_content = content  # 处理后的内容（包含@标签）
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "sender": self.sender.value,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "target_window": self.target_window,
            "replies": [reply.to_dict() for reply in self.replies],
            "interaction_patterns": self.interaction_patterns,
            "mentions": self.mentions,
            "processed_content": self.processed_content
        }

class MultiAgentChatroom:
    """重构后的多智能体聊天室 - 支持动态智能体独立对话窗口"""
    
    @error_catcher("MultiAgentChatroom")
    def __init__(self, rag_system_path: str = r"E:\RAG系统"):
        self.rag_system_path = Path(rag_system_path)
        self.logger = self._setup_logger()
        
        # 聊天室状态
        self.chatroom_id = str(uuid.uuid4())  # 添加聊天室ID
        self.is_active = False
        self.participants = set()
        self.conversation_history = []
        self.current_topic = "智能体协同工作流讨论"
        
        # 智能体实例
        self.agents = {}
        self._initialize_agents()
        
        # 动态智能体对话窗口字典
        self.agent_windows = {}
        self._initialize_agent_windows()
        
        # 交互记录文件
        self.interaction_log_path = CHATROOM_LOG_PATH
        self.interaction_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 方法论分析结果
        self.methodology_insights = []
        
        # 窗口间协作状态
        self.window_collaboration_level = "低"
        self.last_broadcast_time = datetime.now()
        self.last_protocol_error = None  # 最近一次协议错误（用于@不存在的智能体）
        
        # 智能体繁殖支持
        self.agent_reproduction_enabled = True
        
        # 分支窗口管理（主-分支架构）
        self.window_manager = ConversationWindowManager(base_path=str(self.rag_system_path))
        self.branch_windows = {}

        # 尝试从历史交互日志恢复最近会话（避免每次重启后完全丢失上下文）
        self._load_history_from_log(limit=50)
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("MultiAgentChatroom")
        logger.setLevel(logging.INFO)
        
        # 清理已存在的handlers，避免重复输出
        if logger.handlers:
            logger.handlers.clear()
        
        # 添加新的handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_history_from_log(self, limit: int = 50) -> None:
        """从交互日志文件加载最近的对话历史到内存

        说明：
        - 仅在聊天室初始化时调用一次，用于重启后恢复上下文；
        - 如果日志不存在或解析失败，会安全地跳过，不影响正常启动。
        """
        try:
            if not self.interaction_log_path.exists():
                return

            with self.interaction_log_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            history = data.get("conversation_history", [])[-limit:]
            if not history:
                return

            restored_messages: List[ChatMessage] = []
            for item in history:
                try:
                    msg = ChatMessage(
                        message_id=item.get("message_id", str(uuid.uuid4())),
                        sender=AgentRole.USER if item.get("sender") == "用户" else AgentRole.ARCHITECT,
                        content=item.get("content", ""),
                        message_type=MessageType.SYSTEM_NOTIFICATION if item.get("message_type") == "system_notification" else MessageType.USER_MESSAGE,
                        timestamp=datetime.fromisoformat(item.get("timestamp")) if item.get("timestamp") else datetime.now(),
                        target_window=item.get("target_window"),
                    )
                    msg.replies = []
                    msg.interaction_patterns = item.get("interaction_patterns", [])
                    msg.mentions = item.get("mentions", [])
                    msg.processed_content = item.get("processed_content", msg.content)
                    restored_messages.append(msg)
                except Exception as e:
                    self.logger.warning(f"恢复单条历史消息失败: {e}")

            if restored_messages:
                self.conversation_history.extend(restored_messages)
                self.logger.info(f"从交互日志恢复 {len(restored_messages)} 条历史消息")
        except Exception as e:
            self.logger.warning(f"从交互日志加载历史记录失败: {e}")

    @error_catcher("MultiAgentChatroom")
    def _initialize_agents(self):
        """初始化智能体 - 从智能体发现机制动态获取智能体数量"""
        try:
            # 添加当前目录到路径
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # 尝试使用智能体发现机制
            try:
                from src.agent_discovery_engine import AgentDiscoveryEngine
                from src.agent_manager import discover_all_components
                
                # 使用智能体发现引擎动态发现智能体
                discovery_engine = AgentDiscoveryEngine(base_path="src")
                discovered_agents = discovery_engine.discover_agents()
                
                # 检查是否返回了错误信息（功能未实现）
                if "error" in discovered_agents:
                    self.logger.warning(f"智能体发现功能未实现: {discovered_agents['message']}")
                    self.logger.info("将使用默认智能体配置")
                elif discovered_agents and len(discovered_agents) > 0:
                    # 智能体ID到角色枚举的固定映射（避免动态创建枚举的错误）
                    agent_id_to_role = {
                        "system_architect_agent": AgentRole.ARCHITECT,
                        "scheme_evaluator_agent": AgentRole.EVALUATOR,
                        "code_implementer_agent": AgentRole.IMPLEMENTER,
                        "data_collector_agent": AgentRole.DATA_COLLECTOR,
                        "system_maintenance_agent": AgentRole.MAINTENANCE
                    }
                    
                    # ✅ 团队领导优先原则：系统管家第一个创建，获取完整团队信息
                    # 创建顺序：领导 -> 评估 -> 实现 -> 收集 -> 维护
                    creation_order = [
                        "system_architect_agent",    # 1. 系统管家（团队领导）
                        "scheme_evaluator_agent",    # 2. 方案评估师
                        "code_implementer_agent",    # 3. 文本实现师
                        "data_collector_agent",      # 4. 数据收集师
                        "system_maintenance_agent"   # 5. 系统维护师
                    ]
                    
                    # 按照指定顺序创建智能体实例
                    for agent_id in creation_order:
                        # 跳过base_agent（基类智能体仅用于基类智能体交互页面，不参与多智能体聊天室）
                        if agent_id == "base_agent":
                            continue
                        
                        # 跳过未发现的智能体
                        if agent_id not in discovered_agents:
                            self.logger.warning(f"智能体 {agent_id} 未被发现，已跳过")
                            continue
                        
                        # 跳过未映射的智能体
                        if agent_id not in agent_id_to_role:
                            self.logger.warning(f"智能体 {agent_id} 未在角色映射中，已跳过")
                            continue
                        
                        role_enum = agent_id_to_role[agent_id]
                        agent_info = discovered_agents[agent_id]
                        
                        try:
                            module_name = agent_info["module_name"]
                            
                            if agent_info["type"] == "function":
                                # 通过获取函数创建实例
                                function_name = agent_info["function_name"]
                                module = __import__(module_name, fromlist=[function_name])
                                get_agent_func = getattr(module, function_name)
                                agent_instance = get_agent_func()
                                self.agents[role_enum] = agent_instance
                                
                                self.logger.info(f"通过发现机制创建智能体: {agent_id} -> {role_enum.value}")
                                
                            elif agent_info["type"] == "class":
                                # 通过类创建实例
                                class_name = agent_info["class_name"]
                                module = __import__(module_name, fromlist=[class_name])
                                agent_class = getattr(module, class_name)
                                agent_instance = agent_class()
                                self.agents[role_enum] = agent_instance
                                
                                self.logger.info(f"通过发现机制创建智能体: {agent_id} -> {role_enum.value}")
                                
                        except Exception as agent_error:
                            self.logger.warning(f"创建智能体 {agent_id} 失败: {agent_error}")
                    
                    if self.agents:
                        self.logger.info(f"通过智能体发现机制成功初始化 {len(self.agents)} 个智能体")
                        return
                    
                else:
                    self.logger.warning("智能体发现机制未找到智能体，回退到默认智能体")
                    
            except ImportError as discovery_error:
                self.logger.warning(f"智能体发现机制导入失败: {discovery_error}")
            
            # 回退到默认智能体（保持向后兼容）
            try:
                from system_architect_agent import get_system_manager
                from scheme_evaluator_agent import get_scheme_evaluator
                from code_implementer_agent import get_text_implementer
                from data_collector_agent import get_data_collector
                from system_maintenance_agent import get_system_maintenance
            except ImportError:
                from src.system_architect_agent import get_system_manager
                from src.scheme_evaluator_agent import get_scheme_evaluator
                from src.code_implementer_agent import get_text_implementer
                from src.data_collector_agent import get_data_collector
                from src.system_maintenance_agent import get_system_maintenance
            
            # 创建默认智能体实例（团队领导优先原则）
            # 顺序：系统管家 -> 方案评估师 -> 文本实现师 -> 数据收集师 -> 系统维护师
            self.agents[AgentRole.ARCHITECT] = get_system_manager()         # 1. 系统管家（团队领导）
            self.agents[AgentRole.EVALUATOR] = get_scheme_evaluator()       # 2. 方案评估师
            self.agents[AgentRole.IMPLEMENTER] = get_text_implementer()     # 3. 文本实现师
            self.agents[AgentRole.DATA_COLLECTOR] = get_data_collector()    # 4. 数据收集师
            self.agents[AgentRole.MAINTENANCE] = get_system_maintenance()   # 5. 系统维护师
            
            self.logger.info("使用默认智能体初始化成功（5个智能体）")
            
        except Exception as e:
            self.logger.warning(f"智能体初始化失败，将使用模拟智能体: {e}")
            self._initialize_mock_agents()
    

    def _initialize_mock_agents(self):
        """初始化模拟智能体 - 使用默认配置（不再重复调用智能体发现机制）"""
        # 创建模拟智能体类
        class MockAgent:
            def __init__(self, role: AgentRole):
                self.role = role
            
            def respond(self, message: str) -> str:
                responses = {
                    AgentRole.ARCHITECT: [
                        "从架构角度看，这个方案需要考虑系统的可扩展性和模块化设计。",
                        "我建议采用分层架构，将业务逻辑与数据访问分离。",
                        "这个架构方案需要评估技术选型和性能指标。"
                    ],
                    AgentRole.EVALUATOR: [
                        "从评估角度看，这个方案的风险等级为中等。",
                        "需要进一步分析方案的可行性和成本效益。",
                        "这个方案在功能完整性方面表现良好。"
                    ],
                    AgentRole.IMPLEMENTER: [
                        "从实现角度看，这个方案的技术难度适中。",
                        "我可以开始编写具体的代码实现。",
                        "实现过程中需要注意错误处理和日志记录。"
                    ],
                    AgentRole.DATA_COLLECTOR: [
                        "从数据收集角度看，这个方案需要确保数据来源的多样性和质量。",
                        "我可以开始收集相关数据，为系统提供充足的知识来源。",
                        "数据收集过程中需要注意数据质量和风险控制。"
                    ],
                    AgentRole.MAINTENANCE: [
                        "从系统维护角度看，当前系统健康状态良好。",
                        "我正在监控系统组件，未发现异常。",
                        "建议定期进行系统巡检和性能优化。"
                    ]
                }
                import random
                return random.choice(responses[self.role])
        
        # 直接使用默认的5个模拟智能体配置
        # 注意：智能体发现机制已在 _initialize_agents() 中尝试过
        # 若到达此处，说明智能体发现和默认智能体都失败了，直接使用模拟智能体
        for role in [AgentRole.ARCHITECT, AgentRole.EVALUATOR, AgentRole.IMPLEMENTER, AgentRole.DATA_COLLECTOR, AgentRole.MAINTENANCE]:
            self.agents[role] = MockAgent(role)
        
        self.logger.info("使用默认模拟智能体初始化成功（共5个）")
    
    def _initialize_agent_windows(self):
        """初始化智能体对话窗口"""
        try:
            # 为每个已初始化的智能体创建独立对话窗口
            for role, agent in self.agents.items():
                if role != AgentRole.USER:  # 不为用户创建窗口
                    window = AgentConversationWindow(
                        agent_id=f"{role.value}_window",  # 添加必需的agent_id参数
                        agent_role=role.value,
                        agent_instance=agent
                    )
                    self.agent_windows[role] = window
                    self.logger.info(f"创建智能体对话窗口: {role.value}")
            
            self.logger.info(f"成功创建 {len(self.agent_windows)} 个智能体对话窗口")
            
        except Exception as e:
            self.logger.error(f"智能体对话窗口初始化失败: {e}")
            # 创建模拟窗口
            self._initialize_mock_windows()
    
    def _initialize_mock_windows(self):
        """初始化模拟对话窗口"""
        for role, agent in self.agents.items():
            if role != AgentRole.USER:
                window = AgentConversationWindow(
                    agent_id=f"{role.value}_window",  # 添加必需的agent_id参数
                    agent_role=role.value,
                    agent_instance=agent
                )
                self.agent_windows[role] = window
    
    def add_new_agent(self, role: AgentRole, agent_instance: Any) -> bool:
        """添加新智能体并创建对应窗口"""
        try:
            # 添加智能体实例
            self.agents[role] = agent_instance
            
            # 创建对应的独立对话窗口
            window = AgentConversationWindow(
                agent_id=f"{role.value}_window",  # 添加必需的agent_id参数
                agent_role=role.value,
                agent_instance=agent_instance
            )
            self.agent_windows[role] = window
            
            self.logger.info(f"成功添加新智能体并创建窗口: {role.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加新智能体失败: {e}")
            return False
    
    def remove_agent(self, role: AgentRole) -> bool:
        """移除智能体及其窗口"""
        try:
            if role in self.agents:
                del self.agents[role]
            if role in self.agent_windows:
                del self.agent_windows[role]
            
            self.logger.info(f"成功移除智能体: {role.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除智能体失败: {e}")
            return False
    
    def open_task_branch(self, roles: List[AgentRole], task_name: str) -> List[str]:
        """为指定角色开启任务分支窗口"""
        opened = []
        for role in roles:
            parent_window = self.agent_windows.get(role)
            if parent_window:
                branch_window = self.window_manager.open_branch(parent_window, task_name)
                self.branch_windows[role] = branch_window
                opened.append(role.value)
        return opened
    
    def close_task_branches(self) -> List[str]:
        """关闭所有任务分支窗口并沉淀泡泡"""
        ids = []
        for role, branch_win in list(self.branch_windows.items()):
            try:
                mid = self.window_manager.close_branch_and_save_bubble(branch_win.window_id)
                if mid:
                    ids.append(mid)
            finally:
                del self.branch_windows[role]
        return ids
    
    def _to_agent_roles(self, role_names: List[str]) -> List[AgentRole]:
        """将角色名称映射为AgentRole枚举"""
        mapping = {
            "系统管家": AgentRole.ARCHITECT,
            "方案评估师": AgentRole.EVALUATOR,
            "文本实现师": AgentRole.IMPLEMENTER,
            "数据收集师": AgentRole.DATA_COLLECTOR,
            "系统维护师": AgentRole.MAINTENANCE,
            "ARCHITECT": AgentRole.ARCHITECT,
            "EVALUATOR": AgentRole.EVALUATOR,
            "IMPLEMENTER": AgentRole.IMPLEMENTER,
            "DATA_COLLECTOR": AgentRole.DATA_COLLECTOR,
            "MAINTENANCE": AgentRole.MAINTENANCE,
        }
        roles = []
        for name in role_names or []:
            if isinstance(name, AgentRole):
                roles.append(name)
            elif name in mapping:
                roles.append(mapping[name])
        return roles
    
    def _apply_agent_directives(self, agent_responses: List[ChatMessage], original_content: str) -> List[str]:
        """解析智能体响应中的结构化指令，控制分支开关与泡泡沉淀
        指令格式示例（LLM通过系统提示词教化后输出）：
        {
            "action": "open_branch",  # 或 "close_branches"
            "task_name": "改文件",
            "roles": ["文本实现师"]
        }
        """
        memory_ids = []
        try:
            for resp in agent_responses:
                text = resp.content or ""
                if "\"action\"" in text:
                    # 尝试提取JSON片段
                    start = text.find("{")
                    end = text.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        snippet = text[start:end+1]
                        try:
                            obj = json.loads(snippet)
                            action = obj.get("action")
                            if action == "open_branch":
                                task_name = obj.get("task_name") or "任务"
                                roles = self._to_agent_roles(obj.get("roles", []))
                                if roles:
                                    self.open_task_branch(roles, task_name)
                            elif action == "close_branches":
                                ids = self.close_task_branches()
                                memory_ids.extend(ids)
                            elif action == "create_temporary_agent":
                                template = obj.get("template") or "scheme_evaluator"
                                count = int(obj.get("count", 1))
                                reason = obj.get("reason", "")
                                task_name = obj.get("task_name")
                                architect = self.agents.get(AgentRole.ARCHITECT)
                                if architect and hasattr(architect, "recruit_temporary_agents"):
                                    try:
                                        result = architect.recruit_temporary_agents(template, count, reason, task_name)
                                        bubble_id = result.get("bubble_id")
                                        if bubble_id:
                                            memory_ids.append(bubble_id)
                                    except Exception:
                                        # 指令执行失败不阻断聊天流程
                                        pass
                        except Exception:
                            # 忽略解析失败，继续
                            pass
        except Exception:
            pass
        return memory_ids
    
    def get_agent_windows_info(self) -> List[Dict]:
        """获取所有智能体窗口信息"""
        windows_info = []
        for role, window in self.agent_windows.items():
            info = {
                "role": role.value,
                "window_id": str(id(window)),
                "state": window.state.value if hasattr(window, 'state') else "active",
                "conversation_count": len(window.conversation_history),
                "shannon_entropy": window.get_shannon_entropy() if hasattr(window, 'get_shannon_entropy') else 0.5,
                "logically_complete": window.is_logically_complete() if hasattr(window, 'is_logically_complete') else True
            }
            windows_info.append(info)
        return windows_info
    
    def start_chatroom(self) -> bool:
        """启动聊天室"""
        if self.is_active:
            self.logger.warning("聊天室已经在运行中")
            return False
        
        self.is_active = True
        self.participants.add(AgentRole.USER)
        
        # 添加欢迎消息，显示实际智能体数量
        actual_agent_count = len(self.agents)
        welcome_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            sender=AgentRole.USER,
            content=f"欢迎来到多智能体聊天室！当前有 {actual_agent_count} 个智能体在线，让我们一起讨论智能体协同工作流。",
            message_type=MessageType.SYSTEM_NOTIFICATION
        )
        self.conversation_history.append(welcome_message)
        
        self.logger.info(f"多智能体聊天室已启动，共 {actual_agent_count} 个智能体")
        return True
    
    @error_catcher("MultiAgentChatroom")
    def send_user_message(self, content: str) -> Dict:
        """发送用户消息并获取所有智能体窗口的响应"""
        if not self.is_active:
            return {"error": "聊天室未启动"}
        
        # 引入思维透明化追踪器，统一管理聊天室级协调步骤
        try:
            from src.thinking_tracer_tool import get_thinking_tracer
            tracer = get_thinking_tracer()
        except Exception:
            tracer = None
        
        trace_id = f"chatroom:{self.chatroom_id}:{datetime.now().isoformat()}"
        if tracer:
            tracer.start_trace(trace_id)

        def _report_step(agent_id: str, agent_name: str, step_content: str) -> None:
            """内部辅助函数：统一推送思维步骤（通过思维追踪器）"""
            if tracer:
                tracer.report_step(
                    trace_id=trace_id,
                    content=step_content,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    scope="chatroom",
                )
        
        # 处理@提及
        processed_content, mentions = mention_parser.process_message_with_mentions(content)
        
        # 创建用户消息（包含原始内容和处理后的内容）
        user_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            sender=AgentRole.USER,
            content=content,  # 原始内容
            message_type=MessageType.USER_MESSAGE
        )
        
        # 记录用户消息接收步骤
        _report_step("user", "用户", f"💭 接收用户消息：{processed_content}")
        
        # 添加@提及信息到消息对象
        user_message.mentions = mentions
        user_message.processed_content = processed_content
        
        # 添加到对话历史
        self.conversation_history.append(user_message)
        
        # 任务检测（主-分支架构）
        task_name = None
        for kw in ["计划","改文件","重构","写测试","实现","修复","上传","部署"]:
            if kw in content:
                task_name = kw
                break
        
        # 根据语义解析和智能体分工，智能地投送消息
        # 1. 处理@提及
        if mentions:
            # 如果有@提及，只将消息投递给被提及的智能体
            targeted_agents = [mention['agent_id'] for mention in mentions]
            _report_step("system", "系统管家", f"🔍 检测到@提及智能体: {','.join(targeted_agents)}，定向投递消息")
            agent_responses = self._get_agent_responses(content, targeted_agents)
        else:
            # 2. 没有@提及，基于智能体的专业领域进行消息投递
            # 保持灵活性，让智能体根据自己的身份和能力来决定是否回复
            message_lower = content.lower()
            
            # 智能体专业领域映射
            # 基于系统提示词中明确的身份和能力，将消息投递给相关专业领域的智能体
            agent_domains = {
                AgentRole.ARCHITECT: ['架构', '设计', '系统', '框架'],
                AgentRole.EVALUATOR: ['评估', '方案', '分析', '评价'],
                AgentRole.IMPLEMENTER: ['代码', '实现', '开发', '编程'],
                AgentRole.DATA_COLLECTOR: ['数据', '收集', '信息', '采集'],
                AgentRole.MAINTENANCE: ['维护', '监控', '错误', '修复', '诊断', '健康', '故障'],
            }
            
            # 确定相关的智能体
            relevant_agents = []
            for agent_role, domains in agent_domains.items():
                if any(domain in message_lower for domain in domains):
                    relevant_agents.append(agent_role)
            
            if task_name:
                # 为相关智能体开启分支窗口
                for role in relevant_agents:
                    parent_window = self.agent_windows.get(role)
                    if parent_window:
                        branch_window = self.window_manager.open_branch(parent_window, task_name)
                        self.branch_windows[role] = branch_window
                _report_step("system", "系统管家", f"🧠 检测到任务关键词 '{task_name}'，为相关智能体开启分支窗口")
            
            # 3. 消息投递策略
            if relevant_agents:
                # 有相关智能体，将消息投递给相关智能体
                # 确保系统架构师作为系统管家，始终会回复所有消息，作为对话兜底
                if AgentRole.ARCHITECT not in relevant_agents:
                    relevant_agents.append(AgentRole.ARCHITECT)
                _report_step("system_architect", "系统架构师", f"📨 将消息投递给相关智能体: {[r.value if hasattr(r, 'value') else str(r) for r in relevant_agents]}")
                agent_responses = self._get_agent_responses(content, relevant_agents)
            else:
                # 没有明确相关的智能体，让系统架构师作为系统管家回复，作为对话兜底
                if task_name:
                    # 为架构师开启分支窗口
                    parent_window = self.agent_windows.get(AgentRole.ARCHITECT)
                    if parent_window:
                        branch_window = self.window_manager.open_branch(parent_window, task_name)
                        self.branch_windows[AgentRole.ARCHITECT] = branch_window
                _report_step("system_architect", "系统架构师", "🧩 未检测到特定领域，系统架构师作为兜底智能体进行响应")
                agent_responses = self._get_agent_responses(content, [AgentRole.ARCHITECT])
        
        # 解析LLM指令（优先于关键词触发）
        branch_memory_ids_from_directives = self._apply_agent_directives(agent_responses, content)
        
        # 分析交互模式
        self._analyze_interaction_patterns(user_message, agent_responses)
        
        # 保存交互记录
        self._save_interaction_log()
        
        # 更新窗口间协作状态
        self._update_collaboration_level(agent_responses)
        
        # ✅ 手动触发记忆重构指令检测
        if "请立刻进行一次记忆重构" in content or "立即记忆重构" in content:
            _report_step("system", "系统管家", "🔄 检测到手动触发记忆重构指令，启动记忆重构任务")
            reconstruction_result = self._trigger_manual_memory_reconstruction()
            
            # 将重构结果添加到响应中
            if reconstruction_result.get('success'):
                _report_step("system", "系统管家", 
                    f"✅ 记忆重构完成：总记忆={reconstruction_result.get('total_memories', 0)}, "
                    f"删除={reconstruction_result.get('deleted_count', 0)}, "
                    f"主库={reconstruction_result.get('active_count', 0)}, "
                    f"备库/淘汰库={reconstruction_result.get('archived_retired_count', 0)}")
            else:
                _report_step("system", "系统管家", 
                    f"❌ 记忆重构失败：{reconstruction_result.get('error', '未知错误')}")
        
        # 完成/关闭分支窗口请求时，沉淀泡泡
        branch_memory_ids = branch_memory_ids_from_directives or []
        if any(t in content for t in ["完成","结束","关闭分支","沉淀泡泡"]):
            _report_step("system", "系统管家", "✅ 检测到任务完成指令，准备关闭分支窗口并沉淀泡泡")
            branch_memory_ids.extend(self.close_task_branches())
        
        # 从追踪器获取步骤并清理
        thinking_steps = []
        if tracer:
            thinking_steps = tracer.get_steps(trace_id)
            tracer.clear_trace(trace_id)
        
        return {
            "user_message": {
                **user_message.to_dict(),
                "processed_content": processed_content,
                "mentions": mentions
            },
            "agent_responses": [resp.to_dict() for resp in agent_responses],
            "methodology_insights": self.methodology_insights[-3:],  # 返回最近3个方法论洞察
            "windows_info": self.get_agent_windows_info(),  # 返回所有窗口状态信息
            "collaboration_level": self.window_collaboration_level,
            "branch_bubbles": branch_memory_ids,
            "thinking_steps": thinking_steps,
        }
    
    def _broadcast_to_all_windows(self, user_message: str) -> List[ChatMessage]:
        """向所有智能体窗口广播消息并收集响应"""
        responses = []
        
        for role, window in self.agent_windows.items():
            try:
                # 通过窗口接收消息并获取响应
                if hasattr(window, 'receive_message'):
                    response_result = window.receive_message(user_message, "user")
                    # 从返回的字典中提取实际的响应内容
                    response_content = response_result.get('response', f"{role.value}：响应时出现错误，请稍后重试。")
                else:
                    # 优先调用智能体的专业处理方法process_user_query
                    agent = self.agents[role]
                    if hasattr(agent, 'process_user_query'):
                        # 使用更先进的process_user_query方法（支持意图分析+工具调用）
                        result = agent.process_user_query(user_message, history_context=self.conversation_history[-10:])
                        # 提取响应文本
                        response_content = result.get('response', str(result))
                    elif hasattr(agent, 'respond'):
                        # 降级到基础respond方法
                        response_content = agent.respond(user_message)
                    else:
                        response_content = f"{role.value}：我正在分析您的问题..."
                
                # 确保response_content是字符串类型
                if not isinstance(response_content, str):
                    response_content = f"{role.value}：{str(response_content)}"
                
                # 创建响应消息，标记目标窗口
                response_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    sender=role,
                    content=response_content,
                    message_type=MessageType.AGENT_RESPONSE,
                    target_window=role.value  # 标记响应来自哪个窗口
                )
                
                responses.append(response_message)
                self.conversation_history.append(response_message)
                
                # 记录窗口交互
                self.logger.info(f"窗口 {role.value} 响应完成")
                
            except Exception as e:
                self.logger.error(f"窗口 {role.value} 响应失败: {e}")
                
                # 创建错误响应
                error_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    sender=role,
                    content=f"{role.value}：响应时出现错误，请稍后重试。",
                    message_type=MessageType.AGENT_RESPONSE,
                    target_window=role.value
                )
                responses.append(error_message)
        
        return responses
    
    def _update_collaboration_level(self, responses: List[ChatMessage]):
        """更新窗口间协作状态"""
        # 基于响应数量和窗口状态计算协作水平
        active_windows = len([w for w in self.agent_windows.values() 
                             if hasattr(w, 'state') and w.state != AgentWindowState.ERROR])
        
        response_count = len(responses)
        
        if response_count >= active_windows * 0.8:  # 80%的活跃窗口响应
            self.window_collaboration_level = "高"
        elif response_count >= active_windows * 0.5:  # 50%的活跃窗口响应
            self.window_collaboration_level = "中"
        else:
            self.window_collaboration_level = "低"
        
        self.logger.info(f"窗口协作水平更新: {self.window_collaboration_level} (响应数: {response_count}, 活跃窗口: {active_windows})")
    
    def send_silent_broadcast(self, content: str, sender: str = "system") -> bool:
        """发送静默广播消息到所有窗口"""
        try:
            for role, window in self.agent_windows.items():
                if hasattr(window, 'receive_silent_broadcast'):
                    window.receive_silent_broadcast(content, sender)
                else:
                    # 创建静默广播消息记录
                    silent_msg = SilentBroadcastMessage(content, sender)
                    if hasattr(window, 'silent_broadcasts'):
                        window.silent_broadcasts.append(silent_msg)
            
            self.last_broadcast_time = datetime.now()
            self.logger.info(f"静默广播发送成功: {content}")
            return True
            
        except Exception as e:
            self.logger.error(f"静默广播发送失败: {e}")
            return False
    
    def _get_agent_responses(self, user_message: str, targeted_agents: List[AgentRole] = None) -> List[ChatMessage]:
        """获取智能体响应（兼容旧版本）"""
        # 如果指定了目标智能体，只向这些智能体发送消息
        if targeted_agents:
            responses = []
            for role in targeted_agents:
                if role in self.agent_windows:
                    window = self.branch_windows.get(role) or self.agent_windows.get(role)
                    try:
                        # 🚨 检测是否存在协议错误（@不存在的智能体）
                        enhanced_message = user_message
                        if role == AgentRole.ARCHITECT and self.last_protocol_error:
                            # 注入错误信息到系统管家的上下文
                            error_info = self.last_protocol_error
                            invalid_list = ', '.join([m['display_name'] for m in error_info['invalid_mentions']])
                            available_list = ', '.join(error_info['available_agents'])
                            enhanced_message = f"""【系统协议错误抦截】
用户原始消息：{user_message}

❌ 错误类型：组件自曝光协议错误 - @了不存在的智能体
❌ 无效提及：@{invalid_list}
✅ 可用智能体：{available_list}

请你作为系统管家：
1. 向用户明确报告这个错误（使用中文）
2. 列出当前系统中所有可用智能体及其职责
3. 解释为什么不能@不存在的智能体（组件自曝光协议的设计原理）
4. 建议用户如何正确使用@机制
"""
                            # 清除错误状态，避免重复处理
                            self.last_protocol_error = None
                        
                        if hasattr(window, 'receive_message'):
                            response_result = window.receive_message(enhanced_message, "user")
                            # 从返回的字典中提取实际的响应内容
                            response_content = response_result.get('response', f"{role.value}：响应时出现错误，请稍后重试。")
                        else:
                            # 优先调用智能体的专业处理方法process_user_query
                            agent = self.agents[role]
                            if hasattr(agent, 'process_user_query'):
                                # 使用更先进的process_user_query方法（支持意图分析+工具调用）
                                result = agent.process_user_query(enhanced_message, history_context=self.conversation_history[-10:])
                                # 提取响应文本
                                response_content = result.get('response', str(result))
                            elif hasattr(agent, 'respond'):
                                # 降级到基础respond方法
                                response_content = agent.respond(enhanced_message)
                            else:
                                response_content = f"{role.value}：我正在分析您的问题..."
                        
                        # 确保 response_content 是字符串类型
                        if not isinstance(response_content, str):
                            response_content = f"{role.value}：{str(response_content)}"
                        
                        response_message = ChatMessage(
                            message_id=str(uuid.uuid4()),
                            sender=role,
                            content=response_content,
                            message_type=MessageType.AGENT_RESPONSE,
                            target_window=role.value
                        )
                        responses.append(response_message)
                        self.conversation_history.append(response_message)
                        
                    except Exception as e:
                        self.logger.error(f"智能体 {role.value} 响应失败: {e}")
                        error_message = ChatMessage(
                            message_id=str(uuid.uuid4()),
                            sender=role,
                            content=f"{role.value}：响应时出现错误，请稍后重试。",
                            message_type=MessageType.AGENT_RESPONSE,
                            target_window=role.value
                        )
                        responses.append(error_message)
            return responses
        else:
            # 默认向所有窗口广播
            return self._broadcast_to_all_windows(user_message)
    
    def _get_targeted_agents(self, mentions: List[Dict], content: str) -> List[AgentRole]:
        """根据@提及确定需要响应的智能体（含组件自曝光协议校验）"""
        targeted_agents = []
        invalid_mentions = []  # 记录无效的@提及
        
        # 如果有明确的@提及，只让被提及的智能体响应
        if mentions:
            for mention in mentions:
                agent_id = mention["agent_id"]
                # 映射agent_id到AgentRole
                agent_mapping = {
                    "architect": AgentRole.ARCHITECT,
                    "evaluator": AgentRole.EVALUATOR,
                    "implementer": AgentRole.IMPLEMENTER,
                    "collector": AgentRole.DATA_COLLECTOR,  # 数据收集师正确映射到DATA_COLLECTOR
                    "maintenance": AgentRole.MAINTENANCE  # 系统维护师
                }
                if agent_id in agent_mapping:
                    targeted_agents.append(agent_mapping[agent_id])
                else:
                    # ❌ 检测到不存在的智能体！触发二级报错机制
                    invalid_mentions.append(mention)
                    self.logger.error(
                        f"🚨 组件自曝光协议错误：@{mention['display_name']} 智能体不存在！"
                        f"\n   可用智能体：{list(agent_mapping.keys())}"
                        f"\n   触发二级报错机制：向系统维护师上报"
                    )
        
        # 如果检测到无效@提及，强制路由到系统管家报告错误
        if invalid_mentions:
            targeted_agents = [AgentRole.ARCHITECT]  # 系统管家负责报告错误
            # 将错误信息注入到消息上下文（供系统管家读取）
            self.last_protocol_error = {
                "type": "invalid_mention",
                "invalid_mentions": invalid_mentions,
                "available_agents": list(agent_mapping.keys()),
                "timestamp": datetime.now().isoformat()
            }
            return targeted_agents
        
        # 如果没有@提及，或者@提及无效，使用智能路由机制
        if not targeted_agents:
            targeted_agents = self._smart_route_agents(content)
        
        # 系统架构师托底逻辑：确保至少有一个智能体响应
        if not targeted_agents:
            targeted_agents = [AgentRole.ARCHITECT]
            self.logger.warning("智能路由未匹配到任何智能体，使用系统架构师托底")
        
        return targeted_agents
    
    def _smart_route_agents(self, content: str) -> List[AgentRole]:
        """智能路由机制 - 基于内容关键词自动匹配相关智能体"""
        targeted_agents = []
        
        # 扩展的关键词库，包含更多专业术语
        architecture_keywords = ["架构", "设计", "系统", "模块", "分层", "技术选型", "性能", 
                                "微服务", "分布式", "高可用", "可扩展", "架构图", "组件", "接口"]
        
        evaluation_keywords = ["评估", "风险", "可行性", "成本", "效益", "分析", "评估", 
                              "优缺点", "对比", "权衡", "优先级", "ROI", "投资回报", "质量"]
        
        implementation_keywords = ["实现", "代码", "技术", "开发", "测试", "部署", "编程", 
                                  "函数", "类", "方法", "算法", "调试", "优化", "重构"]
        
        data_collection_keywords = ["数据", "收集", "采集", "吃饭", "来源", "质量", "风险",
                                  "工具", "发现", "外部", "缓存", "报告", "验证"]
        
        maintenance_keywords = ["维护", "监控", "错误", "修复", "诊断", "健康", "故障",
                               "巡检", "性能", "优化", "告警", "异常", "配置", "检查"]
        
        content_lower = content.lower()
        
        # 计算关键词匹配分数
        arch_score = sum(1 for keyword in architecture_keywords if keyword in content_lower)
        eval_score = sum(1 for keyword in evaluation_keywords if keyword in content_lower)
        impl_score = sum(1 for keyword in implementation_keywords if keyword in content_lower)
        coll_score = sum(1 for keyword in data_collection_keywords if keyword in content_lower)
        maint_score = sum(1 for keyword in maintenance_keywords if keyword in content_lower)
        
        # 基于分数确定路由策略
        max_score = max(arch_score, eval_score, impl_score, coll_score, maint_score)
        
        if max_score == 0:
            # 没有明确关键词，使用系统架构师托底
            targeted_agents = [AgentRole.ARCHITECT]
        else:
            # 根据分数阈值确定路由
            score_threshold = 2  # 至少匹配2个关键词才认为是明确需求
            
            if arch_score >= score_threshold:
                targeted_agents.append(AgentRole.ARCHITECT)
            if eval_score >= score_threshold:
                targeted_agents.append(AgentRole.EVALUATOR)
            if impl_score >= score_threshold:
                targeted_agents.append(AgentRole.IMPLEMENTER)
            if coll_score >= score_threshold:
                targeted_agents.append(AgentRole.DATA_COLLECTOR)
            if maint_score >= score_threshold:
                targeted_agents.append(AgentRole.MAINTENANCE)
            
            # 如果分数接近但未达到阈值，使用模糊匹配
            if not targeted_agents:
                if arch_score > 0:
                    targeted_agents.append(AgentRole.ARCHITECT)
                if eval_score > 0:
                    targeted_agents.append(AgentRole.EVALUATOR)
                if impl_score > 0:
                    targeted_agents.append(AgentRole.IMPLEMENTER)
                if coll_score > 0:
                    targeted_agents.append(AgentRole.DATA_COLLECTOR)
                if maint_score > 0:
                    targeted_agents.append(AgentRole.MAINTENANCE)
            
            # 如果仍然没有匹配，使用系统架构师托底
            if not targeted_agents:
                targeted_agents = [AgentRole.ARCHITECT]
        
        # 记录路由决策日志
        self.logger.info(f"智能路由决策 - 架构分数: {arch_score}, 评估分数: {eval_score}, 实现分数: {impl_score}, 数据收集分数: {coll_score}, 维护分数: {maint_score}, 目标智能体: {[agent.value for agent in targeted_agents]}")
        
        return targeted_agents
    
    def _analyze_interaction_patterns(self, user_message: ChatMessage, agent_responses: List[ChatMessage]):
        """分析交互模式并提取方法论洞察"""
        
        # 分析消息内容中的关键词
        keywords = self._extract_keywords(user_message.content)
        
        # 分析智能体响应模式
        response_patterns = self._analyze_response_patterns(agent_responses)
        
        # 生成方法论洞察
        insight = self._generate_methodology_insight(keywords, response_patterns)
        
        if insight:
            methodology_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                sender=AgentRole.USER,  # 方法论洞察标记为用户生成
                content=insight,
                message_type=MessageType.METHODOLOGY_INSIGHT
            )
            
            self.conversation_history.append(methodology_message)
            self.methodology_insights.append(insight)
            
            self.logger.info(f"生成方法论洞察: {insight}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应该使用更复杂的NLP技术）
        architecture_keywords = ["架构", "设计", "系统", "模块", "分层"]
        evaluation_keywords = ["评估", "风险", "可行性", "成本", "效益"]
        implementation_keywords = ["实现", "代码", "技术", "开发", "测试"]
        maintenance_keywords = ["维护", "监控", "错误", "修复", "诊断"]
        
        keywords = []
        
        for word in architecture_keywords:
            if word in text:
                keywords.append(f"架构相关:{word}")
        
        for word in evaluation_keywords:
            if word in text:
                keywords.append(f"评估相关:{word}")
        
        for word in implementation_keywords:
            if word in text:
                keywords.append(f"实现相关:{word}")
        
        for word in maintenance_keywords:
            if word in text:
                keywords.append(f"维护相关:{word}")
        
        return keywords
    
    def _analyze_response_patterns(self, agent_responses: List[ChatMessage]) -> Dict:
        """分析智能体响应模式"""
        patterns = {
            "response_count": len(agent_responses),
            "response_types": {},
            "collaboration_level": "低"  # 低/中/高
        }
        
        # 统计各智能体的响应类型
        for response in agent_responses:
            role = response.sender.value
            if role not in patterns["response_types"]:
                patterns["response_types"][role] = 0
            patterns["response_types"][role] += 1
        
        # 评估协作水平
        if len(agent_responses) >= 3:
            patterns["collaboration_level"] = "高"
        elif len(agent_responses) >= 2:
            patterns["collaboration_level"] = "中"
        
        return patterns
    
    def _generate_methodology_insight(self, keywords: List[str], patterns: Dict) -> Optional[str]:
        """生成方法论洞察"""
        
        if not keywords:
            return None
        
        # 基于关键词和模式生成洞察
        insights = []
        
        if "架构相关" in str(keywords) and patterns["collaboration_level"] == "高":
            insights.append("当讨论架构设计时，三个智能体的高度协作能够产生更全面的技术方案。")
        
        if "评估相关" in str(keywords) and patterns["response_count"] > 1:
            insights.append("方案评估过程中，多个智能体的参与有助于识别不同维度的风险。")
        
        if "实现相关" in str(keywords):
            insights.append("代码实现阶段，智能体间的明确分工可以提高开发效率和质量。")
        
        if patterns["collaboration_level"] == "高":
            insights.append("高水平的智能体协作表明系统具备良好的交互机制设计。")
        
        return " | ".join(insights) if insights else None
    
    def _save_interaction_log(self):
        """保存交互记录到JSON文件和向量库"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "conversation_history": [msg.to_dict() for msg in self.conversation_history[-10:]],  # 保存最近10条
                "methodology_insights": self.methodology_insights,
                "participants": [p.value for p in self.participants]
            }
            
            # 保存到JSON文件
            with open(self.interaction_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            # 保存到向量库（如果向量库可用）
            self._save_to_vector_database(log_data)
                
        except Exception as e:
            self.logger.error(f"保存交互记录失败: {e}")
    
    def _save_to_vector_database(self, log_data: Dict):
        """✅ 将交互记录保存到向量数据库（职责归位至UnifiedMemorySystem）"""
        try:
            # ✅ 调用统一记忆系统（职责归位）
            from .unified_memory_system import get_unified_memory_system
            
            memory_system = get_unified_memory_system(str(self.rag_system_path))
            
            self.logger.info(f"开始将交互记录保存到向量库")
            
            # 统计已向量化和跳过的记录
            vectorized_count = 0
            skipped_count = 0
            total_saved = 0
            total_duplicates = 0
            
            # 为每条对话记录创建向量记忆
            for msg in log_data.get("conversation_history", []):
                # 检查是否已向量化
                if msg.get('vectorized', False):
                    skipped_count += 1
                    self.logger.debug(f"跳过已向量化的记录: {msg.get('timestamp', 'unknown')}")
                    continue
                
                content = msg.get('content', '')
                
                # ✅ 调用统一记忆系统的向量化存储接口
                result = memory_system.store_interaction_to_vector_db(
                    interaction_content=content,
                    metadata={
                        "source": "chatroom_interaction",
                        "source_type": "chatroom_slice",
                        "sender": msg.get('sender', 'unknown'),
                        "timestamp": msg.get('timestamp', datetime.now().isoformat()),
                        "topic": f"聊天室分片 - {msg.get('sender', 'unknown')}",
                        "tags": ["chatroom", msg.get('sender', 'unknown')]
                    }
                )
                
                # 统计结果
                saved_count = result.get('saved_count', 0)
                duplicate_count = result.get('duplicate_count', 0)
                
                total_saved += saved_count
                total_duplicates += duplicate_count
                
                # 标记为已向量化
                msg['vectorized'] = True
                msg['duplicate_count'] = duplicate_count
                msg['saved_count'] = saved_count
                vectorized_count += 1
                
                if duplicate_count > 0:
                    self.logger.info(f"消息 {msg.get('timestamp', 'unknown')}: 保存 {saved_count} 条，跳过 {duplicate_count} 条重复")
            
            self.logger.info(f"✅ 成功向量化 {vectorized_count} 条记录，跳过 {skipped_count} 条已向量化的记录")
            self.logger.info(f"✅ 总计：保存 {total_saved} 个切片，跳过 {total_duplicates} 个重复")
            
        except Exception as e:
            self.logger.warning(f"向量库保存失败（使用JSON备份）: {e}")
    
    def _trigger_manual_memory_reconstruction(self) -> Dict:
        """✅ 手动触发记忆重构任务
        
        Returns:
            Dict: {
                'success': bool,
                'total_memories': int,
                'deleted_count': int,
                'active_count': int,
                'archived_retired_count': int,
                'error': str  # 仅在失败时返回
            }
        """
        try:
            self.logger.info("🔄 手动触发记忆重构任务")
            
            # 导入夜间维护调度器
            from .nightly_maintenance_scheduler import NightlyMaintenanceScheduler
            from .vector_database import VectorDatabase
            
            # 创建调度器实例
            scheduler = NightlyMaintenanceScheduler()
            
            # 执行记忆重构
            result = scheduler.perform_memory_reconstruction()
            
            # 检查执行结果
            if result.get('status') == 'success':
                # 获取最新的记忆库统计
                vector_db = VectorDatabase()
                all_memories = vector_db.get_all_memories()
                
                active_count = len([m for m in all_memories if m.get('status', 'active') == 'active'])
                archived_count = len([m for m in all_memories if m.get('status') == 'archived'])
                retired_count = len([m for m in all_memories if m.get('status') == 'retired'])
                
                self.logger.info(
                    f"✅ 记忆重构完成: 总记忆={len(all_memories)}, "
                    f"主库(active)={active_count}, "
                    f"备库(archived)={archived_count}, "
                    f"淘汰库(retired)={retired_count}"
                )
                
                return {
                    'success': True,
                    'total_memories': result.get('total_memories', len(all_memories)),
                    'deleted_count': result.get('deleted_count', 0),
                    'active_count': active_count,
                    'archived_retired_count': archived_count + retired_count,
                    'archived_count': archived_count,
                    'retired_count': retired_count
                }
            else:
                error_msg = result.get('error', '未知错误')
                self.logger.error(f"❌ 记忆重构失败: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"❌ 手动触发记忆重构失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_content_vector(self, text: str) -> List[float]:
        """生成文本内容的简单向量表示"""
        # 简化的向量生成方法（实际应该使用专业的embedding模型）
        if not text:
            return [0.0] * 12  # 12维向量
        
        # 基于文本长度、关键词等生成简单向量
        vector = []
        
        # 1. 文本长度特征
        length_feature = min(len(text) / 1000, 1.0)  # 归一化到0-1
        vector.append(length_feature)
        
        # 2. 关键词特征（架构相关）
        arch_keywords = ["架构", "设计", "系统", "模块"]
        arch_score = sum(1 for word in arch_keywords if word in text) / len(arch_keywords)
        vector.append(arch_score)
        
        # 3. 关键词特征（评估相关）
        eval_keywords = ["评估", "风险", "可行性", "成本"]
        eval_score = sum(1 for word in eval_keywords if word in text) / len(eval_keywords)
        vector.append(eval_score)
        
        # 4. 关键词特征（实现相关）
        impl_keywords = ["实现", "代码", "技术", "开发"]
        impl_score = sum(1 for word in impl_keywords if word in text) / len(impl_keywords)
        vector.append(impl_score)
        
        # 5-12. 填充其他特征（实际应该使用更复杂的特征提取）
        for i in range(8):
            vector.append(0.1)  # 占位特征
        
        # 归一化向量
        norm = sum(x**2 for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def get_conversation_history(self, limit: int = None, time_window_minutes: int = 15) -> List[Dict]:
        """
        获取对话历史
        
        Args:
            limit: 最大消息条数（可选，优先级低于time_window_minutes）
            time_window_minutes: 时间窗口（分钟），默认15分钟（知识图谱缓存5分钟×3倍安全系数）
        
        Returns:
            对话历史列表
        """
        from datetime import datetime, timedelta
        
        # 🕐 优先使用时间窗口过滤
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=time_window_minutes)
        
        filtered_history = []
        for msg in self.conversation_history:
            try:
                msg_dict = msg.to_dict()
                timestamp_str = msg_dict.get('timestamp', '')
                
                if not timestamp_str:
                    # 无时间戳的保留
                    filtered_history.append(msg_dict)
                    continue
                
                msg_time = datetime.fromisoformat(timestamp_str)
                
                # 在时间窗口内的保留
                if msg_time >= cutoff_time:
                    filtered_history.append(msg_dict)
                    
            except (ValueError, AttributeError):
                # 时间戳解析失败，保留
                filtered_history.append(msg.to_dict())
        
        # 如果指定limit，再进行条数限制
        if limit is not None:
            return filtered_history[-limit:]
        
        return filtered_history
    
    def get_methodology_insights(self) -> List[str]:
        """获取方法论洞察列表"""
        return self.methodology_insights
    
    def query_interaction_history(self, query: str, time_range: str = None, limit: int = 10) -> List[Dict]:
        """查询历史交互记录（基于向量库）"""
        try:
            from .vector_database import VectorDatabase
            
            vector_db = VectorDatabase()
            
            # 生成查询向量
            query_vector = self._generate_content_vector(query)
            
            # 构建时间范围条件
            start_time = None
            end_time = None
            
            if time_range:
                # 解析时间范围（如："last_week", "last_month", "2024-01"）
                start_time, end_time = self._parse_time_range(time_range)
            
            # 搜索相关记忆
            memories = vector_db.search_memories(
                query=query,
                vector=query_vector,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            # 过滤聊天室交互记录
            chatroom_memories = [
                memory for memory in memories 
                if memory.get('source_type') in ['chatroom_interaction', 'methodology_insight']
            ]
            
            self.logger.info(f"查询到 {len(chatroom_memories)} 条相关交互记录")
            return chatroom_memories
            
        except Exception as e:
            self.logger.error(f"查询交互历史失败: {e}")
            return []
    
    def _parse_time_range(self, time_range: str) -> tuple[str, str]:
        """解析时间范围字符串"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        if time_range == "last_week":
            start_time = (now - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == "last_month":
            start_time = (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == "today":
            start_time = now.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        elif len(time_range) == 7 and time_range.count('-') == 1:  # 格式：2024-01
            year, month = time_range.split('-')
            start_time = f"{year}-{month}-01 00:00:00"
            # 计算下个月的第一天
            next_month = int(month) + 1
            if next_month > 12:
                next_month = 1
                year = str(int(year) + 1)
            end_time = f"{year}-{next_month:02d}-01 00:00:00"
        else:
            # 默认返回最近一个月
            start_time = (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        return start_time, end_time
    
    def generate_agent_summary(self, agent_role: str, time_range: str = "last_week") -> Dict:
        """为指定智能体生成时间段总结"""
        try:
            # 查询该智能体相关的交互记录
            query = f"{agent_role} 智能体"
            memories = self.query_interaction_history(query, time_range, limit=50)
            
            if not memories:
                return {
                    "agent_role": agent_role,
                    "time_range": time_range,
                    "summary": "该时间段内未找到相关交互记录",
                    "key_insights": [],
                    "success_count": 0,
                    "total_memories": 0
                }
            
            # 分析记忆内容
            key_insights = self._analyze_memories_for_summary(memories, agent_role)
            
            # 生成总结文本
            summary = self._generate_summary_text(agent_role, memories, key_insights, time_range)
            
            return {
                "agent_role": agent_role,
                "time_range": time_range,
                "summary": summary,
                "key_insights": key_insights,
                "success_count": len([m for m in memories if m.get('importance', 0) > 0.6]),
                "total_memories": len(memories)
            }
            
        except Exception as e:
            self.logger.error(f"生成智能体总结失败: {e}")
            return {
                "agent_role": agent_role,
                "time_range": time_range,
                "summary": f"生成总结时出错: {str(e)}",
                "key_insights": [],
                "success_count": 0,
                "total_memories": 0
            }
    
    def _analyze_memories_for_summary(self, memories: List[Dict], agent_role: str) -> List[str]:
        """分析记忆内容，提取关键洞察"""
        insights = []
        
        # 统计参与度
        participation_count = len(memories)
        if participation_count > 10:
            insights.append(f"{agent_role}在该时间段内高度活跃，参与了{participation_count}次讨论")
        elif participation_count > 5:
            insights.append(f"{agent_role}在该时间段内适度参与，共{participation_count}次发言")
        else:
            insights.append(f"{agent_role}在该时间段内参与较少，仅{participation_count}次发言")
        
        # 分析讨论主题
        topics = {}
        for memory in memories:
            content = memory.get('content', '')
            if "架构" in content:
                topics["架构设计"] = topics.get("架构设计", 0) + 1
            if "评估" in content or "风险" in content:
                topics["方案评估"] = topics.get("方案评估", 0) + 1
            if "实现" in content or "代码" in content:
                topics["技术实现"] = topics.get("技术实现", 0) + 1
        
        if topics:
            main_topic = max(topics.items(), key=lambda x: x[1])[0]
            insights.append(f"主要讨论主题: {main_topic}（共{topics[main_topic]}次提及）")
        
        # 分析方法论洞察
        methodology_memories = [m for m in memories if m.get('source_type') == 'methodology_insight']
        if methodology_memories:
            insights.append(f"生成{len(methodology_memories)}个方法论洞察")
        
        return insights
    
    def _generate_summary_text(self, agent_role: str, memories: List[Dict], insights: List[str], time_range: str) -> str:
        """生成总结文本"""
        summary_parts = [f"{agent_role}智能体在{time_range}时间段的总结报告：\n"]
        
        # 添加关键洞察
        summary_parts.extend([f"• {insight}" for insight in insights])
        
        # 添加代表性发言
        important_memories = sorted(memories, key=lambda x: x.get('importance', 0), reverse=True)[:3]
        if important_memories:
            summary_parts.append("\n代表性发言：")
            for i, memory in enumerate(important_memories, 1):
                content = memory.get('content', '')[:100] + "..." if len(memory.get('content', '')) > 100 else memory.get('content', '')
                summary_parts.append(f"{i}. {content}")
        
        return "\n".join(summary_parts)
    
    def stop_chatroom(self):
        """停止聊天室"""
        self.is_active = False
        self.participants.clear()
        self.logger.info("多智能体聊天室已停止")

def test_chatroom():
    """测试重构后的聊天室功能 - 支持动态智能体窗口"""
    chatroom = MultiAgentChatroom()
    
    # 启动聊天室
    if chatroom.start_chatroom():
        print("=== 重构后的多智能体聊天室测试 ===")
        print("支持动态智能体独立理解空间")
        
        # 显示初始窗口信息
        windows_info = chatroom.get_agent_windows_info()
        print(f"\n初始智能体窗口数量: {len(windows_info)}")
        for window in windows_info:
            print(f"  - {window['role']}: 状态={window['state']}, 对话数={window['conversation_count']}, 香农熵={window['shannon_entropy']:.2f}")
        
        # 测试用户消息
        test_messages = [
            "大家好！我们来讨论一下智能体协同工作流的设计。",
            "构架师，你觉得应该如何设计系统的架构？",
            "评估师，这个方案的风险如何？",
            "实现师，技术实现上有什么建议？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 测试消息 {i} ---")
            print(f"用户: {message}")
            
            result = chatroom.send_user_message(message)
            
            if "error" not in result:
                # 显示智能体响应
                print("智能体响应:")
                for response in result["agent_responses"]:
                    print(f"  {response['sender']}: {response['content']}")
                
                # 显示窗口状态
                print("窗口状态更新:")
                for window in result["windows_info"]:
                    print(f"  {window['role']}: 香农熵={window['shannon_entropy']:.2f}, 逻辑完整性={window['logically_complete']}")
                
                # 显示协作水平
                print(f"窗口协作水平: {result['collaboration_level']}")
                
                # 显示方法论洞察
                if result["methodology_insights"]:
                    print("方法论洞察:")
                    for insight in result["methodology_insights"]:
                        print(f"  - {insight}")
            else:
                print(f"错误: {result['error']}")
        
        # 测试静默广播
        print("\n--- 测试静默广播 ---")
        success = chatroom.send_silent_broadcast("系统通知：即将进行智能体繁殖测试")
        if success:
            print("静默广播发送成功")
        else:
            print("静默广播发送失败")
        
        # 显示对话历史
        print("\n=== 对话历史 ===")
        history = chatroom.get_conversation_history()
        for msg in history:
            window_info = f" [窗口: {msg.get('target_window', 'N/A')}]" if msg.get('target_window') else ""
            print(f"{msg['timestamp']} [{msg['sender']}]{window_info}: {msg['content']}")
        
        # 显示方法论洞察总结
        print("\n=== 方法论洞察总结 ===")
        insights = chatroom.get_methodology_insights()
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        # 停止聊天室
        chatroom.stop_chatroom()
        print("\n=== 测试完成 ===")
    else:
        print("聊天室启动失败")

if __name__ == "__main__":
    test_chatroom()