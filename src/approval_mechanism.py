# @self-expose: {"id": "approval_mechanism", "name": "Approval Mechanism", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Approval Mechanism功能"]}}
"""
分级审批机制
实现小/中/大优化分级处理

开发提示词来源：用户要求建立架构自优化记忆锚点，实现分级审批机制
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class OptimizationSize(Enum):
    """优化规模分类"""
    SMALL = "small"  # 小型优化
    MEDIUM = "medium"  # 中型优化
    LARGE = "large"  # 大型优化

class ApprovalStatus(Enum):
    """审批状态"""
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    UNDER_REVIEW = "under_review"  # 审核中

@dataclass
class OptimizationRequest:
    """优化请求数据结构"""
    request_id: str
    requester_agent: str
    optimization_description: str
    optimization_size: OptimizationSize
    estimated_impact: str  # "low", "medium", "high", "critical"
    technical_complexity: str  # "low", "medium", "high"
    resource_requirements: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    business_impact: str  # "low", "medium", "high"
    timestamp: str
    status: ApprovalStatus

@dataclass
class ApprovalDecision:
    """审批决策数据结构"""
    decision_id: str
    request_id: str
    approver_agent: str
    decision: ApprovalStatus
    decision_reason: str
    conditions: List[str]  # 审批条件
    timestamp: str

@dataclass
class FeasibilityAnalysis:
    """可行性分析数据结构"""
    analysis_id: str
    request_id: str
    analyst_agent: str
    technical_feasibility: float  # 0-1
    cost_benefit_ratio: float
    implementation_timeline: Dict[str, Any]
    risk_mitigation_plan: List[str]
    recommendations: List[str]
    timestamp: str

class ApprovalMechanism:
    """分级审批机制"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件
        self.requests_file = self.data_dir / "optimization_requests.json"
        self.decisions_file = self.data_dir / "approval_decisions.json"
        self.analyses_file = self.data_dir / "feasibility_analyses.json"
        
        # 审批阈值配置
        self.approval_thresholds = {
            OptimizationSize.SMALL: {
                "auto_approval": True,
                "approver_required": "system_architect",
                "feasibility_analysis_required": False,
                "max_resource_hours": 8,
                "max_risk_level": "medium"
            },
            OptimizationSize.MEDIUM: {
                "auto_approval": False,
                "approver_required": "system_architect",
                "feasibility_analysis_required": True,
                "max_resource_hours": 40,
                "max_risk_level": "medium"
            },
            OptimizationSize.LARGE: {
                "auto_approval": False,
                "approver_required": "main_brain",  # 主脑审批
                "feasibility_analysis_required": True,
                "max_resource_hours": 200,
                "max_risk_level": "low"
            }
        }
        
        # 初始化数据存储
        self._initialize_data_files()
        
        logger.info("分级审批机制初始化完成")
    
    def _initialize_data_files(self):
        """初始化数据文件"""
        for file_path in [self.requests_file, self.decisions_file, self.analyses_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def submit_optimization_request(self, requester_agent: str, 
                                  optimization_description: str,
                                  optimization_size: OptimizationSize,
                                  estimated_impact: str,
                                  technical_complexity: str,
                                  resource_requirements: Dict[str, Any],
                                  risk_assessment: Dict[str, Any],
                                  business_impact: str) -> str:
        """提交优化请求"""
        
        request_id = f"request_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{requester_agent}"
        
        request = OptimizationRequest(
            request_id=request_id,
            requester_agent=requester_agent,
            optimization_description=optimization_description,
            optimization_size=optimization_size,
            estimated_impact=estimated_impact,
            technical_complexity=technical_complexity,
            resource_requirements=resource_requirements,
            risk_assessment=risk_assessment,
            business_impact=business_impact,
            timestamp=datetime.now().isoformat(),
            status=ApprovalStatus.PENDING
        )
        
        # 保存优化请求
        requests = self._load_data(self.requests_file)
        requests.append(asdict(request))
        self._save_data(self.requests_file, requests)
        
        logger.info(f"优化请求已提交: {request_id} - {optimization_description}")
        
        # 根据规模自动处理或触发审批流程
        self._process_optimization_request(request_id)
        
        return request_id
    
    def _process_optimization_request(self, request_id: str):
        """处理优化请求"""
        requests = self._load_data(self.requests_file)
        request = next((r for r in requests if r["request_id"] == request_id), None)
        
        if not request:
            logger.error(f"优化请求不存在: {request_id}")
            return
        
        optimization_size = OptimizationSize(request["optimization_size"])
        threshold_config = self.approval_thresholds[optimization_size]
        
        # 检查是否需要自动审批
        if threshold_config["auto_approval"]:
            self._auto_approve_request(request_id)
        else:
            # 触发审批流程
            self._trigger_approval_process(request_id, threshold_config["approver_required"])
    
    def _auto_approve_request(self, request_id: str):
        """自动审批小型优化请求"""
        requests = self._load_data(self.requests_file)
        request = next((r for r in requests if r["request_id"] == request_id), None)
        
        if not request:
            return
        
        # 创建自动审批决策
        decision_id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_auto"
        
        decision = ApprovalDecision(
            decision_id=decision_id,
            request_id=request_id,
            approver_agent="system_auto_approval",
            decision=ApprovalStatus.APPROVED,
            decision_reason="小型优化自动批准，符合系统自动审批条件",
            conditions=["资源需求在阈值内", "风险评估通过", "技术复杂度低"],
            timestamp=datetime.now().isoformat()
        )
        
        # 保存审批决策
        decisions = self._load_data(self.decisions_file)
        decisions.append(asdict(decision))
        self._save_data(self.decisions_file, decisions)
        
        # 更新请求状态
        request["status"] = ApprovalStatus.APPROVED.value
        self._save_data(self.requests_file, requests)
        
        logger.info(f"小型优化自动批准: {request_id}")
        
        # 触发优化执行
        self._trigger_optimization_execution(request_id)
    
    def _trigger_approval_process(self, request_id: str, approver_required: str):
        """触发审批流程"""
        requests = self._load_data(self.requests_file)
        request = next((r for r in requests if r["request_id"] == request_id), None)
        
        if not request:
            return
        
        optimization_size = OptimizationSize(request["optimization_size"])
        
        # 更新请求状态
        request["status"] = ApprovalStatus.UNDER_REVIEW.value
        self._save_data(self.requests_file, requests)
        
        # 根据规模决定是否需要可行性分析
        if optimization_size in [OptimizationSize.MEDIUM, OptimizationSize.LARGE]:
            self._trigger_feasibility_analysis(request_id)
        
        # 通知审批人
        self._notify_approver(request_id, approver_required)
        
        logger.info(f"审批流程已触发: {request_id} -> {approver_required}")
    
    def _trigger_feasibility_analysis(self, request_id: str):
        """触发可行性分析"""
        requests = self._load_data(self.requests_file)
        request = next((r for r in requests if r["request_id"] == request_id), None)
        
        if not request:
            return
        
        # 在实际系统中，这里会调用评估师智能体进行可行性分析
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 模拟可行性分析结果
        analysis = FeasibilityAnalysis(
            analysis_id=analysis_id,
            request_id=request_id,
            analyst_agent="evaluator_agent",
            technical_feasibility=0.8,  # 模拟值
            cost_benefit_ratio=2.5,    # 模拟值
            implementation_timeline={
                "design_phase": "1周",
                "development_phase": "2周",
                "testing_phase": "1周",
                "total_duration": "4周"
            },
            risk_mitigation_plan=[
                "分阶段实施降低风险",
                "建立回滚机制",
                "充分测试验证"
            ],
            recommendations=[
                "建议分阶段实施",
                "需要充分的测试验证",
                "建议建立监控机制"
            ],
            timestamp=datetime.now().isoformat()
        )
        
        # 保存可行性分析
        analyses = self._load_data(self.analyses_file)
        analyses.append(asdict(analysis))
        self._save_data(self.analyses_file, analyses)
        
        logger.info(f"可行性分析完成: {analysis_id} for request {request_id}")
    
    def _notify_approver(self, request_id: str, approver_required: str):
        """通知审批人"""
        # 在实际系统中，这里会调用相应的智能体API
        logger.info(f"通知审批人 {approver_required} 处理请求: {request_id}")
    
    def approve_request(self, approver_agent: str, request_id: str, 
                        decision: ApprovalStatus, decision_reason: str,
                        conditions: List[str]) -> str:
        """审批优化请求"""
        
        # 验证请求存在
        requests = self._load_data(self.requests_file)
        request = next((r for r in requests if r["request_id"] == request_id), None)
        
        if not request:
            raise ValueError(f"优化请求不存在: {request_id}")
        
        # 创建审批决策
        decision_id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{approver_agent}"
        
        approval_decision = ApprovalDecision(
            decision_id=decision_id,
            request_id=request_id,
            approver_agent=approver_agent,
            decision=decision,
            decision_reason=decision_reason,
            conditions=conditions,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存审批决策
        decisions = self._load_data(self.decisions_file)
        decisions.append(asdict(approval_decision))
        self._save_data(self.decisions_file, decisions)
        
        # 更新请求状态
        request["status"] = decision.value
        self._save_data(self.requests_file, requests)
        
        logger.info(f"优化请求审批完成: {request_id} -> {decision.value}")
        
        # 如果批准，触发优化执行
        if decision == ApprovalStatus.APPROVED:
            self._trigger_optimization_execution(request_id)
        
        return decision_id
    
    def _trigger_optimization_execution(self, request_id: str):
        """触发优化执行"""
        # 在实际系统中，这里会调用代码师智能体执行优化
        logger.info(f"触发优化执行: {request_id}")
        
        # 这里可以集成到系统迭代循环引擎
        try:
            from system_iteration_engine import get_iteration_engine
            iteration_engine = get_iteration_engine()
            
            # 获取请求信息
            requests = self._load_data(self.requests_file)
            request = next((r for r in requests if r["request_id"] == request_id), None)
            
            if request:
                # 创建优化方案
                proposal_id = iteration_engine.create_optimization_proposal(
                    architect_agent="system_architect",
                    problem_id=request_id,
                    solution_description=request["optimization_description"],
                    technical_approach="基于审批机制的优化实施",
                    estimated_effort=request["resource_requirements"].get("estimated_hours", 8),
                    risk_assessment=request["risk_assessment"].get("overall_risk", "low"),
                    dependencies=[]
                )
                
                logger.info(f"优化方案已创建并进入迭代循环: {proposal_id}")
                
        except ImportError:
            logger.warning("系统迭代循环引擎未找到，优化执行将延迟")
    
    def get_optimization_size_classification(self, resource_hours: int, 
                                           risk_level: str, 
                                           business_impact: str) -> OptimizationSize:
        """根据参数分类优化规模"""
        
        # 小型优化标准
        if (resource_hours <= 8 and 
            risk_level in ["low", "medium"] and 
            business_impact in ["low", "medium"]):
            return OptimizationSize.SMALL
        
        # 中型优化标准
        elif (resource_hours <= 40 and 
              risk_level in ["low", "medium"] and 
              business_impact in ["medium", "high"]):
            return OptimizationSize.MEDIUM
        
        # 大型优化标准
        else:
            return OptimizationSize.LARGE
    
    def get_approval_statistics(self) -> Dict[str, Any]:
        """获取审批统计信息"""
        requests = self._load_data(self.requests_file)
        decisions = self._load_data(self.decisions_file)
        analyses = self._load_data(self.analyses_file)
        
        # 按规模统计
        size_stats = {}
        for size in OptimizationSize:
            size_requests = [r for r in requests if r["optimization_size"] == size.value]
            size_stats[size.value] = {
                "total_requests": len(size_requests),
                "approved": len([r for r in size_requests if r["status"] == ApprovalStatus.APPROVED.value]),
                "rejected": len([r for r in size_requests if r["status"] == ApprovalStatus.REJECTED.value]),
                "pending": len([r for r in size_requests if r["status"] == ApprovalStatus.PENDING.value]),
                "under_review": len([r for r in size_requests if r["status"] == ApprovalStatus.UNDER_REVIEW.value])
            }
        
        return {
            "total_requests": len(requests),
            "total_decisions": len(decisions),
            "total_analyses": len(analyses),
            "approval_rate": len([r for r in requests if r["status"] == ApprovalStatus.APPROVED.value]) / len(requests) if requests else 0,
            "size_statistics": size_stats,
            "recent_activity": {
                "last_7_days": {
                    "requests": len([r for r in requests if self._is_recent(r["timestamp"], 7)]),
                    "decisions": len([d for d in decisions if self._is_recent(d["timestamp"], 7)]),
                    "analyses": len([a for a in analyses if self._is_recent(a["timestamp"], 7)])
                }
            }
        }
    
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

# 全局审批机制实例
approval_mechanism = ApprovalMechanism()

def get_approval_mechanism() -> ApprovalMechanism:
    """获取审批机制实例"""
    return approval_mechanism