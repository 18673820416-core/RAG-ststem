# @self-expose: {"id": "agent_communication", "name": "Agent Communication", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Communication功能"]}}
"""
智能体通信接口 - 支持三智能体协同工作

通信流程：
1. 构架师提出方案 → 评估师评估 → 主人确认 → 实现师执行
2. 支持状态跟踪和消息传递
3. 提供确认和反馈机制
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

class AgentType(Enum):
    """智能体类型"""
    ARCHITECT = "architect"  # 构架师
    EVALUATOR = "evaluator"  # 评估师
    IMPLEMENTER = "implementer"  # 实现师
    OWNER = "owner"  # 主人

class MessageType(Enum):
    """消息类型"""
    SCHEME_PROPOSAL = "scheme_proposal"  # 方案提议
    EVALUATION_REQUEST = "evaluation_request"  # 评估请求
    EVALUATION_RESULT = "evaluation_result"  # 评估结果
    CONFIRMATION_REQUEST = "confirmation_request"  # 确认请求
    CONFIRMATION_RESPONSE = "confirmation_response"  # 确认响应
    IMPLEMENTATION_REQUEST = "implementation_request"  # 实现请求
    IMPLEMENTATION_RESULT = "implementation_result"  # 实现结果
    FEEDBACK = "feedback"  # 反馈
    ERROR = "error"  # 错误

class SchemeStatus(Enum):
    """方案状态"""
    PROPOSED = "proposed"  # 已提议
    EVALUATING = "evaluating"  # 评估中
    EVALUATED = "evaluated"  # 已评估
    WAITING_CONFIRMATION = "waiting_confirmation"  # 等待确认
    CONFIRMED = "confirmed"  # 已确认
    IMPLEMENTING = "implementing"  # 实现中
    IMPLEMENTED = "implemented"  # 已实现
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消

@dataclass
class Scheme:
    """方案数据结构"""
    scheme_id: str
    name: str
    description: str
    proposed_functions: List[str]
    architect_id: str
    created_time: str
    status: SchemeStatus
    
    # 方案详情
    technical_details: Optional[Dict] = None
    resource_requirements: Optional[Dict] = None
    expected_benefits: Optional[Dict] = None
    
    # 评估结果
    evaluation_result: Optional[Dict] = None
    
    # 实现结果
    implementation_result: Optional[Dict] = None
    
    # 确认信息
    confirmation_result: Optional[Dict] = None

@dataclass
class Message:
    """消息数据结构"""
    message_id: str
    message_type: MessageType
    sender_id: str
    receiver_id: str
    scheme_id: str
    content: Dict[str, Any]
    timestamp: str
    
    # 消息状态
    is_read: bool = False
    is_processed: bool = False

class AgentCommunicationSystem:
    """智能体通信系统"""
    
    def __init__(self, storage_file: str = "agent_communication.json"):
        self.storage_file = storage_file
        self.schemes: Dict[str, Scheme] = {}
        self.messages: Dict[str, Message] = {}
        self.agents: Dict[str, AgentType] = {}
        
        # 加载历史数据
        self._load_data()
    
    def _load_data(self):
        """加载历史数据"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 加载方案
            for scheme_id, scheme_data in data.get('schemes', {}).items():
                scheme_data['status'] = SchemeStatus(scheme_data['status'])
                self.schemes[scheme_id] = Scheme(**scheme_data)
            
            # 加载消息
            for msg_id, msg_data in data.get('messages', {}).items():
                msg_data['message_type'] = MessageType(msg_data['message_type'])
                self.messages[msg_id] = Message(**msg_data)
                
            # 加载智能体
            for agent_id, agent_type in data.get('agents', {}).items():
                self.agents[agent_id] = AgentType(agent_type)
                
        except FileNotFoundError:
            # 文件不存在，初始化空数据
            self._save_data()
    
    def _save_data(self):
        """保存数据"""
        data = {
            'schemes': {scheme_id: asdict(scheme) for scheme_id, scheme in self.schemes.items()},
            'messages': {msg_id: asdict(msg) for msg_id, msg in self.messages.items()},
            'agents': {agent_id: agent_type.value for agent_id, agent_type in self.agents.items()}
        }
        
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_agent(self, agent_id: str, agent_type: AgentType):
        """注册智能体"""
        self.agents[agent_id] = agent_type
        self._save_data()
    
    def propose_scheme(self, architect_id: str, scheme_data: Dict) -> str:
        """构架师提出方案"""
        # 验证构架师身份
        if architect_id not in self.agents or self.agents[architect_id] != AgentType.ARCHITECT:
            raise ValueError("只有构架师可以提出方案")
        
        # 创建方案
        scheme_id = str(uuid.uuid4())
        scheme = Scheme(
            scheme_id=scheme_id,
            name=scheme_data.get('name', '未命名方案'),
            description=scheme_data.get('description', ''),
            proposed_functions=scheme_data.get('proposed_functions', []),
            architect_id=architect_id,
            created_time=datetime.now().isoformat(),
            status=SchemeStatus.PROPOSED,
            technical_details=scheme_data.get('technical_details'),
            resource_requirements=scheme_data.get('resource_requirements'),
            expected_benefits=scheme_data.get('expected_benefits')
        )
        
        self.schemes[scheme_id] = scheme
        
        # 发送评估请求给评估师
        self._send_evaluation_request(scheme_id)
        
        self._save_data()
        return scheme_id
    
    def _send_evaluation_request(self, scheme_id: str):
        """发送评估请求给评估师"""
        scheme = self.schemes[scheme_id]
        
        # 找到评估师
        evaluator_id = self._find_agent(AgentType.EVALUATOR)
        if not evaluator_id:
            raise ValueError("未找到评估师智能体")
        
        # 创建评估请求消息
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            message_type=MessageType.EVALUATION_REQUEST,
            sender_id=scheme.architect_id,
            receiver_id=evaluator_id,
            scheme_id=scheme_id,
            content={
                'scheme_name': scheme.name,
                'scheme_description': scheme.description,
                'proposed_functions': scheme.proposed_functions,
                'technical_details': scheme.technical_details
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.messages[message_id] = message
        
        # 更新方案状态
        scheme.status = SchemeStatus.EVALUATING
    
    def submit_evaluation_result(self, evaluator_id: str, scheme_id: str, 
                              evaluation_result: Dict) -> str:
        """评估师提交评估结果"""
        # 验证评估师身份
        if evaluator_id not in self.agents or self.agents[evaluator_id] != AgentType.EVALUATOR:
            raise ValueError("只有评估师可以提交评估结果")
        
        scheme = self.schemes[scheme_id]
        
        # 更新方案评估结果
        scheme.evaluation_result = evaluation_result
        scheme.status = SchemeStatus.EVALUATED
        
        # 发送确认请求给主人
        self._send_confirmation_request(scheme_id, evaluator_id)
        
        self._save_data()
        return scheme_id
    
    def _send_confirmation_request(self, scheme_id: str, sender_id: str):
        """发送确认请求给主人"""
        scheme = self.schemes[scheme_id]
        
        # 找到主人
        owner_id = self._find_agent(AgentType.OWNER)
        if not owner_id:
            raise ValueError("未找到主人智能体")
        
        # 创建确认请求消息
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            message_type=MessageType.CONFIRMATION_REQUEST,
            sender_id=sender_id,
            receiver_id=owner_id,
            scheme_id=scheme_id,
            content={
                'scheme_name': scheme.name,
                'evaluation_result': scheme.evaluation_result,
                'recommendations': scheme.evaluation_result.get('recommendations', [])
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.messages[message_id] = message
        
        # 更新方案状态
        scheme.status = SchemeStatus.WAITING_CONFIRMATION
    
    def submit_confirmation_response(self, owner_id: str, scheme_id: str, 
                                   is_confirmed: bool, feedback: str = "") -> str:
        """主人提交确认响应"""
        # 验证主人身份
        if owner_id not in self.agents or self.agents[owner_id] != AgentType.OWNER:
            raise ValueError("只有主人可以确认方案")
        
        scheme = self.schemes[scheme_id]
        
        # 更新方案确认结果
        scheme.confirmation_result = {
            'is_confirmed': is_confirmed,
            'feedback': feedback,
            'confirmed_time': datetime.now().isoformat()
        }
        
        if is_confirmed:
            scheme.status = SchemeStatus.CONFIRMED
            # 发送实现请求给实现师
            self._send_implementation_request(scheme_id, owner_id)
        else:
            scheme.status = SchemeStatus.REJECTED
        
        self._save_data()
        return scheme_id
    
    def _send_implementation_request(self, scheme_id: str, sender_id: str):
        """发送实现请求给实现师"""
        scheme = self.schemes[scheme_id]
        
        # 找到实现师
        implementer_id = self._find_agent(AgentType.IMPLEMENTER)
        if not implementer_id:
            raise ValueError("未找到实现师智能体")
        
        # 创建实现请求消息
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            message_type=MessageType.IMPLEMENTATION_REQUEST,
            sender_id=sender_id,
            receiver_id=implementer_id,
            scheme_id=scheme_id,
            content={
                'scheme_name': scheme.name,
                'technical_details': scheme.technical_details,
                'evaluation_result': scheme.evaluation_result,
                'confirmation_result': scheme.confirmation_result
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.messages[message_id] = message
        
        # 更新方案状态
        scheme.status = SchemeStatus.IMPLEMENTING
    
    def submit_implementation_result(self, implementer_id: str, scheme_id: str, 
                                   implementation_result: Dict) -> str:
        """实现师提交实现结果"""
        # 验证实现师身份
        if implementer_id not in self.agents or self.agents[implementer_id] != AgentType.IMPLEMENTER:
            raise ValueError("只有实现师可以提交实现结果")
        
        scheme = self.schemes[scheme_id]
        
        # 更新方案实现结果
        scheme.implementation_result = implementation_result
        scheme.status = SchemeStatus.IMPLEMENTED
        
        self._save_data()
        return scheme_id
    
    def _find_agent(self, agent_type: AgentType) -> Optional[str]:
        """查找指定类型的智能体"""
        for agent_id, a_type in self.agents.items():
            if a_type == agent_type:
                return agent_id
        return None
    
    def get_messages_for_agent(self, agent_id: str, unread_only: bool = True) -> List[Message]:
        """获取指定智能体的消息"""
        messages = []
        for message in self.messages.values():
            if message.receiver_id == agent_id:
                if unread_only and message.is_read:
                    continue
                messages.append(message)
        
        # 按时间排序
        messages.sort(key=lambda x: x.timestamp)
        return messages
    
    def mark_message_read(self, message_id: str):
        """标记消息为已读"""
        if message_id in self.messages:
            self.messages[message_id].is_read = True
            self._save_data()
    
    def mark_message_processed(self, message_id: str):
        """标记消息为已处理"""
        if message_id in self.messages:
            self.messages[message_id].is_processed = True
            self._save_data()
    
    def get_scheme_status(self, scheme_id: str) -> Optional[SchemeStatus]:
        """获取方案状态"""
        if scheme_id in self.schemes:
            return self.schemes[scheme_id].status
        return None
    
    def get_scheme_details(self, scheme_id: str) -> Optional[Scheme]:
        """获取方案详情"""
        return self.schemes.get(scheme_id)
    
    def get_schemes_by_status(self, status: SchemeStatus) -> List[Scheme]:
        """按状态获取方案"""
        return [scheme for scheme in self.schemes.values() if scheme.status == status]


def create_scheme_summary(scheme: Scheme) -> str:
    """创建方案摘要"""
    summary = f"""
# 方案摘要

## 基本信息
- 方案ID：{scheme.scheme_id}
- 方案名称：{scheme.name}
- 状态：{scheme.status.value}
- 创建时间：{scheme.created_time}

## 方案描述
{scheme.description}

## 提议功能
"""
    
    for i, func in enumerate(scheme.proposed_functions, 1):
        summary += f"{i}. {func}\n"
    
    if scheme.evaluation_result:
        summary += f"\n## 评估结果\n"
        eval_result = scheme.evaluation_result
        summary += f"- 被需要度：{eval_result.get('need_degree', 0):.1f}分\n"
        summary += f"- 不冗余度：{eval_result.get('non_redundancy_degree', 0):.1f}分\n"
        summary += f"- 综合评分：{eval_result.get('overall_score', 0):.1f}分\n"
        summary += f"- 是否通过：{'是' if eval_result.get('pass_status', False) else '否'}\n"
    
    if scheme.confirmation_result:
        summary += f"\n## 确认结果\n"
        conf_result = scheme.confirmation_result
        summary += f"- 是否确认：{'是' if conf_result.get('is_confirmed', False) else '否'}\n"
        if conf_result.get('feedback'):
            summary += f"- 反馈：{conf_result['feedback']}\n"
    
    return summary


def main():
    """测试通信系统"""
    comm_system = AgentCommunicationSystem()
    
    # 注册智能体
    comm_system.register_agent("architect_001", AgentType.ARCHITECT)
    comm_system.register_agent("evaluator_001", AgentType.EVALUATOR)
    comm_system.register_agent("implementer_001", AgentType.IMPLEMENTER)
    comm_system.register_agent("owner_001", AgentType.OWNER)
    
    # 构架师提出方案
    scheme_data = {
        'name': '智能文档解析引擎',
        'description': '用于解析微信群中的施工信息并生成台账',
        'proposed_functions': ['施工信息解析', '台账生成', '数据存储'],
        'technical_details': {
            'technology_stack': ['Python', 'FastAPI', 'PostgreSQL'],
            'complexity': 'medium'
        }
    }
    
    scheme_id = comm_system.propose_scheme("architect_001", scheme_data)
    print(f"方案已提交，ID：{scheme_id}")
    
    # 检查评估师收到的消息
    messages = comm_system.get_messages_for_agent("evaluator_001")
    print(f"评估师收到 {len(messages)} 条新消息")
    
    # 模拟评估师处理消息
    if messages:
        message = messages[0]
        print(f"消息内容：{message.content}")
        
        # 标记消息为已读和已处理
        comm_system.mark_message_read(message.message_id)
        comm_system.mark_message_processed(message.message_id)
        
        # 模拟评估结果
        evaluation_result = {
            'need_degree': 85.5,
            'non_redundancy_degree': 78.2,
            'overall_score': 81.9,
            'pass_status': True,
            'recommendations': ['建议优化数据存储方案']
        }
        
        comm_system.submit_evaluation_result("evaluator_001", scheme_id, evaluation_result)
        print("评估结果已提交")
    
    # 检查方案状态
    scheme = comm_system.get_scheme_details(scheme_id)
    if scheme:
        print(f"当前方案状态：{scheme.status.value}")

if __name__ == "__main__":
    main()