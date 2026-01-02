# @self-expose: {"id": "agent_reporting_mechanism", "name": "Agent Reporting Mechanism", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Reporting Mechanism功能"]}}
"""
智能体主动报告机制
实现智能体主动报告问题和优化建议

开发提示词来源：用户要求建立架构自优化记忆锚点，实现智能体主动报告机制
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """报告类型"""
    PROBLEM = "problem"  # 问题报告
    OPTIMIZATION = "optimization"  # 优化建议
    PERFORMANCE = "performance"  # 性能问题
    SECURITY = "security"  # 安全问题
    USABILITY = "usability"  # 可用性问题
    FEEDBACK = "feedback"  # 用户反馈

class ReportPriority(Enum):
    """报告优先级"""
    LOW = "low"  # 低优先级
    MEDIUM = "medium"  # 中优先级
    HIGH = "high"  # 高优先级
    CRITICAL = "critical"  # 紧急优先级

@dataclass
class AgentReport:
    """智能体报告数据结构"""
    report_id: str
    reporter_agent: str
    report_type: ReportType
    title: str
    description: str
    priority: ReportPriority
    context_data: Dict[str, Any]
    evidence: List[str]  # 证据或相关数据
    suggested_actions: List[str]
    timestamp: str
    status: str  # "new", "acknowledged", "in_progress", "resolved"

@dataclass
class ReportAcknowledgement:
    """报告确认数据结构"""
    ack_id: str
    report_id: str
    acknowledging_agent: str
    acknowledgement_note: str
    assigned_priority: ReportPriority
    estimated_resolution_time: str
    timestamp: str

@dataclass
class ReportResolution:
    """报告解决结果数据结构"""
    resolution_id: str
    report_id: str
    resolving_agent: str
    resolution_description: str
    resolution_type: str  # "fixed", "workaround", "won't_fix", "duplicate"
    impact_assessment: Dict[str, Any]
    lessons_learned: List[str]
    timestamp: str

class AgentReportingMechanism:
    """智能体主动报告机制"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件
        self.reports_file = self.data_dir / "agent_reports.json"
        self.acknowledgements_file = self.data_dir / "report_acknowledgements.json"
        self.resolutions_file = self.data_dir / "report_resolutions.json"
        
        # 报告处理配置
        self.reporting_config = {
            "auto_acknowledge_threshold": {
                "low_priority": True,
                "medium_priority": False,
                "high_priority": False,
                "critical_priority": False
            },
            "escalation_rules": {
                "unacknowledged_timeout_hours": 24,
                "in_progress_timeout_hours": 72,
                "critical_escalation_agents": ["system_architect", "main_brain"]
            },
            "report_categories": {
                "performance": {
                    "handling_agent": "performance_monitor_agent",
                    "auto_escalate_after_hours": 12
                },
                "security": {
                    "handling_agent": "security_audit_agent",
                    "auto_escalate_after_hours": 2
                },
                "usability": {
                    "handling_agent": "user_experience_agent",
                    "auto_escalate_after_hours": 48
                }
            }
        }
        
        # 初始化数据存储
        self._initialize_data_files()
        
        # 报告处理回调函数
        self.report_handlers = {}
        
        logger.info("智能体主动报告机制初始化完成")
    
    def _initialize_data_files(self):
        """初始化数据文件"""
        for file_path in [self.reports_file, self.acknowledgements_file, self.resolutions_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def submit_report(self, reporter_agent: str, report_type: ReportType, 
                     title: str, description: str, priority: ReportPriority,
                     context_data: Dict[str, Any], evidence: List[str],
                     suggested_actions: List[str]) -> str:
        """提交智能体报告"""
        
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reporter_agent}"
        
        report = AgentReport(
            report_id=report_id,
            reporter_agent=reporter_agent,
            report_type=report_type,
            title=title,
            description=description,
            priority=priority,
            context_data=context_data,
            evidence=evidence,
            suggested_actions=suggested_actions,
            timestamp=datetime.now().isoformat(),
            status="new"
        )
        
        # 保存报告
        reports = self._load_data(self.reports_file)
        reports.append(asdict(report))
        self._save_data(self.reports_file, reports)
        
        logger.info(f"智能体报告已提交: {report_id} - {title} (优先级: {priority.value})")
        
        # 根据优先级自动处理
        self._process_new_report(report_id)
        
        return report_id
    
    def _process_new_report(self, report_id: str):
        """处理新报告"""
        reports = self._load_data(self.reports_file)
        report = next((r for r in reports if r["report_id"] == report_id), None)
        
        if not report:
            logger.error(f"报告不存在: {report_id}")
            return
        
        priority = ReportPriority(report["priority"])
        
        # 检查是否需要自动确认
        auto_acknowledge = self.reporting_config["auto_acknowledge_threshold"].get(
            f"{priority.value}_priority", False
        )
        
        if auto_acknowledge:
            self._auto_acknowledge_report(report_id)
        else:
            # 触发人工或智能体处理
            self._trigger_report_handling(report_id)
    
    def _auto_acknowledge_report(self, report_id: str):
        """自动确认低优先级报告"""
        reports = self._load_data(self.reports_file)
        report = next((r for r in reports if r["report_id"] == report_id), None)
        
        if not report:
            return
        
        # 创建自动确认记录
        ack_id = f"ack_{datetime.now().strftime('%Y%m%d_%H%M%S')}_auto"
        
        acknowledgement = ReportAcknowledgement(
            ack_id=ack_id,
            report_id=report_id,
            acknowledging_agent="system_auto_acknowledge",
            acknowledgement_note="低优先级报告自动确认，将按计划处理",
            assigned_priority=ReportPriority(report["priority"]),
            estimated_resolution_time="7天内",
            timestamp=datetime.now().isoformat()
        )
        
        # 保存确认记录
        acknowledgements = self._load_data(self.acknowledgements_file)
        acknowledgements.append(asdict(acknowledgement))
        self._save_data(self.acknowledgements_file, acknowledgements)
        
        # 更新报告状态
        report["status"] = "acknowledged"
        self._save_data(self.reports_file, reports)
        
        logger.info(f"报告自动确认: {report_id}")
        
        # 触发报告处理
        self._trigger_report_resolution(report_id)
    
    def _trigger_report_handling(self, report_id: str):
        """触发报告处理"""
        reports = self._load_data(self.reports_file)
        report = next((r for r in reports if r["report_id"] == report_id), None)
        
        if not report:
            return
        
        report_type = ReportType(report["report_type"])
        
        # 根据报告类型确定处理智能体
        handling_agent = self._get_handling_agent_for_report_type(report_type)
        
        # 通知处理智能体
        self._notify_handling_agent(report_id, handling_agent)
        
        logger.info(f"报告处理已触发: {report_id} -> {handling_agent}")
    
    def _get_handling_agent_for_report_type(self, report_type: ReportType) -> str:
        """根据报告类型获取处理智能体"""
        category_config = self.reporting_config["report_categories"].get(
            report_type.value, {}
        )
        
        return category_config.get("handling_agent", "system_architect")
    
    def _notify_handling_agent(self, report_id: str, handling_agent: str):
        """通知处理智能体"""
        # 在实际系统中，这里会调用相应的智能体API
        logger.info(f"通知处理智能体 {handling_agent} 处理报告: {report_id}")
        
        # 调用注册的报告处理器
        if handling_agent in self.report_handlers:
            try:
                handler = self.report_handlers[handling_agent]
                handler(report_id)
            except Exception as e:
                logger.error(f"报告处理器调用失败: {handling_agent} - {e}")
    
    def acknowledge_report(self, acknowledging_agent: str, report_id: str,
                          acknowledgement_note: str, assigned_priority: ReportPriority,
                          estimated_resolution_time: str) -> str:
        """确认报告"""
        
        # 验证报告存在
        reports = self._load_data(self.reports_file)
        report = next((r for r in reports if r["report_id"] == report_id), None)
        
        if not report:
            raise ValueError(f"报告不存在: {report_id}")
        
        # 创建确认记录
        ack_id = f"ack_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{acknowledging_agent}"
        
        acknowledgement = ReportAcknowledgement(
            ack_id=ack_id,
            report_id=report_id,
            acknowledging_agent=acknowledging_agent,
            acknowledgement_note=acknowledgement_note,
            assigned_priority=assigned_priority,
            estimated_resolution_time=estimated_resolution_time,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存确认记录
        acknowledgements = self._load_data(self.acknowledgements_file)
        acknowledgements.append(asdict(acknowledgement))
        self._save_data(self.acknowledgements_file, acknowledgements)
        
        # 更新报告状态
        report["status"] = "acknowledged"
        self._save_data(self.reports_file, reports)
        
        logger.info(f"报告已确认: {report_id} by {acknowledging_agent}")
        
        return ack_id
    
    def resolve_report(self, resolving_agent: str, report_id: str,
                      resolution_description: str, resolution_type: str,
                      impact_assessment: Dict[str, Any], lessons_learned: List[str]) -> str:
        """解决报告"""
        
        # 验证报告存在
        reports = self._load_data(self.reports_file)
        report = next((r for r in reports if r["report_id"] == report_id), None)
        
        if not report:
            raise ValueError(f"报告不存在: {report_id}")
        
        # 创建解决记录
        resolution_id = f"resolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{resolving_agent}"
        
        resolution = ReportResolution(
            resolution_id=resolution_id,
            report_id=report_id,
            resolving_agent=resolving_agent,
            resolution_description=resolution_description,
            resolution_type=resolution_type,
            impact_assessment=impact_assessment,
            lessons_learned=lessons_learned,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存解决记录
        resolutions = self._load_data(self.resolutions_file)
        resolutions.append(asdict(resolution))
        self._save_data(self.resolutions_file, resolutions)
        
        # 更新报告状态
        report["status"] = "resolved"
        self._save_data(self.reports_file, reports)
        
        logger.info(f"报告已解决: {report_id} by {resolving_agent}")
        
        # 如果解决类型是"fixed"，触发优化流程
        if resolution_type == "fixed":
            self._trigger_optimization_from_report(report_id)
        
        return resolution_id
    
    def _trigger_optimization_from_report(self, report_id: str):
        """从报告触发优化流程"""
        # 集成到系统迭代循环引擎
        try:
            from system_iteration_engine import get_iteration_engine
            iteration_engine = get_iteration_engine()
            
            # 获取报告信息
            reports = self._load_data(self.reports_file)
            report = next((r for r in reports if r["report_id"] == report_id), None)
            
            if report:
                # 报告问题
                problem_id = iteration_engine.report_problem(
                    reporter_agent=report["reporter_agent"],
                    problem_description=report["description"],
                    problem_type=report["report_type"],
                    severity=report["priority"],
                    context_data=report["context_data"]
                )
                
                logger.info(f"报告问题已进入迭代循环: {problem_id}")
                
        except ImportError:
            logger.warning("系统迭代循环引擎未找到，优化流程将延迟")
    
    def register_report_handler(self, agent_name: str, handler: Callable):
        """注册报告处理器"""
        self.report_handlers[agent_name] = handler
        logger.info(f"报告处理器已注册: {agent_name}")
    
    def get_reporting_statistics(self) -> Dict[str, Any]:
        """获取报告统计信息"""
        reports = self._load_data(self.reports_file)
        acknowledgements = self._load_data(self.acknowledgements_file)
        resolutions = self._load_data(self.resolutions_file)
        
        # 按类型统计
        type_stats = {}
        for report_type in ReportType:
            type_reports = [r for r in reports if r["report_type"] == report_type.value]
            type_stats[report_type.value] = {
                "total_reports": len(type_reports),
                "new": len([r for r in type_reports if r["status"] == "new"]),
                "acknowledged": len([r for r in type_reports if r["status"] == "acknowledged"]),
                "in_progress": len([r for r in type_reports if r["status"] == "in_progress"]),
                "resolved": len([r for r in type_reports if r["status"] == "resolved"])
            }
        
        # 按优先级统计
        priority_stats = {}
        for priority in ReportPriority:
            priority_reports = [r for r in reports if r["priority"] == priority.value]
            priority_stats[priority.value] = {
                "total_reports": len(priority_reports),
                "resolution_rate": len([r for r in priority_reports if r["status"] == "resolved"]) / len(priority_reports) if priority_reports else 0
            }
        
        return {
            "total_reports": len(reports),
            "total_acknowledgements": len(acknowledgements),
            "total_resolutions": len(resolutions),
            "overall_resolution_rate": len([r for r in reports if r["status"] == "resolved"]) / len(reports) if reports else 0,
            "type_statistics": type_stats,
            "priority_statistics": priority_stats,
            "average_resolution_time_hours": self._calculate_average_resolution_time(),
            "recent_activity": {
                "last_7_days": {
                    "reports": len([r for r in reports if self._is_recent(r["timestamp"], 7)]),
                    "resolutions": len([res for res in resolutions if self._is_recent(res["timestamp"], 7)])
                }
            }
        }
    
    def _calculate_average_resolution_time(self) -> float:
        """计算平均解决时间（小时）"""
        reports = self._load_data(self.reports_file)
        resolutions = self._load_data(self.resolutions_file)
        
        resolved_reports = [r for r in reports if r["status"] == "resolved"]
        
        if not resolved_reports:
            return 0.0
        
        total_hours = 0
        count = 0
        
        for report in resolved_reports:
            report_time = datetime.fromisoformat(report["timestamp"])
            
            # 找到对应的解决记录
            resolution = next((res for res in resolutions if res["report_id"] == report["report_id"]), None)
            if resolution:
                resolution_time = datetime.fromisoformat(resolution["timestamp"])
                hours_diff = (resolution_time - report_time).total_seconds() / 3600
                total_hours += hours_diff
                count += 1
        
        return total_hours / count if count > 0 else 0.0
    
    def _is_recent(self, timestamp: str, days: int) -> bool:
        """检查时间戳是否在指定天数内"""
        try:
            target_time = datetime.fromisoformat(timestamp)
            cutoff_time = datetime.now() - timedelta(days=days)
            return target_time > cutoff_time
        except:
            return False
    
    def _load_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """加载数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, file_path: Path, data: List[Dict[str, Any]]):
        """保存数据文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 全局报告机制实例
reporting_mechanism = AgentReportingMechanism()

def get_reporting_mechanism() -> AgentReportingMechanism:
    """获取报告机制实例"""
    return reporting_mechanism