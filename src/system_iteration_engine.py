"""
系统级迭代循环引擎
实现"发现-注册-交付"的智能体工具迭代闭环

开发提示词来源：用户要求建立架构自优化记忆锚点，实现系统级迭代循环
"""

# @self-expose: {"id": "system_iteration_engine", "name": "System Iteration Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["System Iteration Engine功能"]}}

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ProblemReport:
    """问题报告数据结构"""
    problem_id: str
    reporter_agent: str
    problem_description: str
    problem_type: str  # "performance", "functionality", "security", "usability"
    severity: str  # "low", "medium", "high", "critical"
    timestamp: str
    context_info: Dict[str, Any]

@dataclass
class OptimizationProposal:
    """优化方案数据结构"""
    proposal_id: str
    problem_id: str
    architect_agent: str
    solution_description: str
    technical_approach: str
    estimated_effort: int  # 小时
    risk_assessment: str  # "low", "medium", "high"
    dependencies: List[str]
    timestamp: str

@dataclass
class EvaluationResult:
    """评估结果数据结构"""
    evaluation_id: str
    proposal_id: str
    evaluator_agent: str
    feasibility_score: float  # 0-1
    cost_benefit_analysis: str
    implementation_priority: str  # "low", "medium", "high", "urgent"
    recommendations: List[str]
    timestamp: str

@dataclass
class ImplementationResult:
    """实现结果数据结构"""
    implementation_id: str
    proposal_id: str
    coder_agent: str
    implementation_status: str  # "completed", "failed", "in_progress"
    code_changes: List[str]
    test_results: Dict[str, Any]
    deployment_info: Dict[str, Any]
    timestamp: str

class SystemIterationEngine:
    """系统级迭代循环引擎"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件路径
        self.problems_file = self.data_dir / "system_problems.json"
        self.proposals_file = self.data_dir / "optimization_proposals.json"
        self.evaluations_file = self.data_dir / "evaluation_results.json"
        self.implementations_file = self.data_dir / "implementation_results.json"
        self.tools_file = self.data_dir / "system_tools.json"
        
        # 初始化数据存储
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """初始化数据文件"""
        for file_path in [self.problems_file, self.proposals_file, 
                          self.evaluations_file, self.implementations_file, 
                          self.tools_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def report_problem(self, reporter_agent: str, problem_description: str, 
                      problem_type: str, severity: str, context_info: Dict[str, Any]) -> str:
        """智能体报告问题 - 发现阶段"""
        
        problem_id = f"problem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reporter_agent}"
        
        problem = ProblemReport(
            problem_id=problem_id,
            reporter_agent=reporter_agent,
            problem_description=problem_description,
            problem_type=problem_type,
            severity=severity,
            timestamp=datetime.now().isoformat(),
            context_info=context_info
        )
        
        # 保存问题报告
        problems = self._load_data(self.problems_file)
        problems.append(asdict(problem))
        self._save_data(self.problems_file, problems)
        
        logger.info(f"问题报告已提交: {problem_id} by {reporter_agent}")
        
        # 触发架构师处理
        self._notify_architect(problem_id)
        
        return problem_id
    
    def create_optimization_proposal(self, architect_agent: str, problem_id: str,
                                   solution_description: str, technical_approach: str,
                                   estimated_effort: int, risk_assessment: str,
                                   dependencies: List[str]) -> str:
        """架构师创建优化方案"""
        
        # 验证问题存在
        problems = self._load_data(self.problems_file)
        problem_exists = any(p["problem_id"] == problem_id for p in problems)
        
        if not problem_exists:
            raise ValueError(f"问题ID不存在: {problem_id}")
        
        proposal_id = f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{architect_agent}"
        
        proposal = OptimizationProposal(
            proposal_id=proposal_id,
            problem_id=problem_id,
            architect_agent=architect_agent,
            solution_description=solution_description,
            technical_approach=technical_approach,
            estimated_effort=estimated_effort,
            risk_assessment=risk_assessment,
            dependencies=dependencies,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存优化方案
        proposals = self._load_data(self.proposals_file)
        proposals.append(asdict(proposal))
        self._save_data(self.proposals_file, proposals)
        
        logger.info(f"优化方案已创建: {proposal_id} for problem {problem_id}")
        
        # 触发评估师评估
        self._notify_evaluator(proposal_id)
        
        return proposal_id
    
    def evaluate_proposal(self, evaluator_agent: str, proposal_id: str,
                         feasibility_score: float, cost_benefit_analysis: str,
                         implementation_priority: str, recommendations: List[str],
                         participant_evaluation_data: Dict[str, Any] = None) -> str:
        """评估师评估优化方案"""
        
        # 验证方案存在
        proposals = self._load_data(self.proposals_file)
        proposal_exists = any(p["proposal_id"] == proposal_id for p in proposals)
        
        if not proposal_exists:
            raise ValueError(f"优化方案ID不存在: {proposal_id}")
        
        evaluation_id = f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{evaluator_agent}"
        
        evaluation = EvaluationResult(
            evaluation_id=evaluation_id,
            proposal_id=proposal_id,
            evaluator_agent=evaluator_agent,
            feasibility_score=feasibility_score,
            cost_benefit_analysis=cost_benefit_analysis,
            implementation_priority=implementation_priority,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存评估结果
        evaluations = self._load_data(self.evaluations_file)
        evaluations.append(asdict(evaluation))
        self._save_data(self.evaluations_file, evaluations)
        
        logger.info(f"方案评估完成: {evaluation_id} for proposal {proposal_id}")
        
        # 如果提供了参与者评估数据，进行参与者进化值评分
        if participant_evaluation_data:
            self._evaluate_participant_contributions(proposal_id, evaluator_agent, participant_evaluation_data)
        
        # 触发代码师实现
        self._notify_coder(proposal_id)
        
        return evaluation_id
    
    def _evaluate_participant_contributions(self, proposal_id: str, evaluator_agent: str, 
                                           participant_evaluation_data: Dict[str, Any]):
        """评估参与者在方案中的贡献度"""
        try:
            # 导入评估师智能体
            from scheme_evaluator_agent import SchemeEvaluatorAgent
            
            # 创建或获取评估师智能体实例
            evaluator = SchemeEvaluatorAgent()
            
            # 获取方案信息
            proposals = self._load_data(self.proposals_file)
            proposal = next((p for p in proposals if p["proposal_id"] == proposal_id), None)
            
            if not proposal:
                logger.warning(f"无法找到方案 {proposal_id} 的详细信息，跳过参与者评估")
                return
            
            # 构建进化动作数据
            evolution_action = {
                "action_id": proposal_id,
                "action_type": "proposal_evaluation",
                "architect_agent": proposal.get("architect_agent", "unknown"),
                "evaluator_agent": evaluator_agent,
                "solves_core_issue": participant_evaluation_data.get("solves_core_issue", False),
                "technical_quality": participant_evaluation_data.get("technical_quality", "medium"),
                "is_complete": participant_evaluation_data.get("is_complete", True),
                "innovation_level": participant_evaluation_data.get("innovation_level", "medium"),
                "is_original": participant_evaluation_data.get("is_original", False),
                "collaboration_level": participant_evaluation_data.get("collaboration_level", "medium"),
                "helps_others": participant_evaluation_data.get("helps_others", False),
                "co_creation_spirit": participant_evaluation_data.get("co_creation_spirit", False),
                "skill_improvement": participant_evaluation_data.get("skill_improvement", "medium"),
                "knowledge_gain": participant_evaluation_data.get("knowledge_gain", False)
            }
            
            # 评估架构师的贡献
            architect_id = proposal.get("architect_agent", "unknown_architect")
            if architect_id != "unknown_architect":
                architect_evaluation = evaluator.evaluate_participant_contribution(
                    architect_id, evolution_action, participant_evaluation_data
                )
                
                # 检查是否需要实时反馈
                if architect_evaluation.get("needs_real_time_feedback", False):
                    feedback = evaluator.provide_real_time_feedback(architect_id, architect_evaluation)
                    logger.info(f"向架构师 {architect_id} 发送实时反馈")
                    # 在实际系统中，这里会调用消息发送机制
            
            # 评估评估师的贡献
            evaluator_evaluation = evaluator.evaluate_participant_contribution(
                evaluator_agent, evolution_action, participant_evaluation_data
            )
            
            # 检查是否需要实时反馈
            if evaluator_evaluation.get("needs_real_time_feedback", False):
                feedback = evaluator.provide_real_time_feedback(evaluator_agent, evaluator_evaluation)
                logger.info(f"向评估师 {evaluator_agent} 发送实时反馈")
                # 在实际系统中，这里会调用消息发送机制
            
            logger.info(f"参与者进化值评估完成 - 方案: {proposal_id}")
            
        except ImportError:
            logger.warning("无法导入SchemeEvaluatorAgent，跳过参与者进化值评估")
        except Exception as e:
            logger.error(f"参与者进化值评估失败: {str(e)}")
    
    def implement_proposal(self, coder_agent: str, proposal_id: str,
                          implementation_status: str, code_changes: List[str],
                          test_results: Dict[str, Any], deployment_info: Dict[str, Any]) -> str:
        """代码师实现优化方案 - 交付阶段"""
        
        # 验证方案存在
        proposals = self._load_data(self.proposals_file)
        proposal_exists = any(p["proposal_id"] == proposal_id for p in proposals)
        
        if not proposal_exists:
            raise ValueError(f"优化方案ID不存在: {proposal_id}")
        
        implementation_id = f"implementation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{coder_agent}"
        
        implementation = ImplementationResult(
            implementation_id=implementation_id,
            proposal_id=proposal_id,
            coder_agent=coder_agent,
            implementation_status=implementation_status,
            code_changes=code_changes,
            test_results=test_results,
            deployment_info=deployment_info,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存实现结果
        implementations = self._load_data(self.implementations_file)
        implementations.append(asdict(implementation))
        self._save_data(self.implementations_file, implementations)
        
        logger.info(f"方案实现完成: {implementation_id} for proposal {proposal_id}")
        
        # 如果实现成功，创建新工具
        if implementation_status == "completed":
            self._create_new_tool(proposal_id, implementation_id)
        
        return implementation_id
    
    def _notify_architect(self, problem_id: str):
        """通知架构师处理问题"""
        # 在实际系统中，这里会调用架构师智能体的API
        logger.info(f"通知架构师处理问题: {problem_id}")
    
    def _notify_evaluator(self, proposal_id: str):
        """通知评估师评估方案"""
        # 在实际系统中，这里会调用评估师智能体的API
        logger.info(f"通知评估师评估方案: {proposal_id}")
    
    def _notify_coder(self, proposal_id: str):
        """通知代码师实现方案"""
        # 在实际系统中，这里会调用代码师智能体的API
        logger.info(f"通知代码师实现方案: {proposal_id}")
    
    def _create_new_tool(self, proposal_id: str, implementation_id: str):
        """创建新工具并注册到系统"""
        
        # 获取方案信息
        proposals = self._load_data(self.proposals_file)
        proposal = next((p for p in proposals if p["proposal_id"] == proposal_id), None)
        
        if not proposal:
            logger.error(f"无法找到方案: {proposal_id}")
            return
        
        # 获取问题信息
        problems = self._load_data(self.problems_file)
        problem = next((p for p in problems if p["problem_id"] == proposal["problem_id"]), None)
        
        # 创建新工具记录
        tool_id = f"tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        new_tool = {
            "tool_id": tool_id,
            "tool_name": f"优化工具_{proposal_id}",
            "description": proposal["solution_description"],
            "created_from_problem": proposal["problem_id"],
            "created_from_implementation": implementation_id,
            "creator_agent": proposal["architect_agent"],
            "implementation_agent": "coder_agent",  # 需要从实现记录中获取
            "creation_timestamp": datetime.now().isoformat(),
            "tool_category": "optimization",
            "usage_count": 0
        }
        
        # 保存新工具
        tools = self._load_data(self.tools_file)
        tools.append(new_tool)
        self._save_data(self.tools_file, tools)
        
        logger.info(f"新工具已创建: {tool_id}")
        
        # 触发工具自动发现和注册
        self._auto_discover_and_register_tool(tool_id)
    
    def _auto_discover_and_register_tool(self, tool_id: str):
        """自动发现和注册新工具"""
        # 在实际系统中，这里会调用工具发现引擎
        logger.info(f"自动发现和注册工具: {tool_id}")
    
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
    
    def get_iteration_status(self) -> Dict[str, Any]:
        """获取迭代循环状态"""
        problems = self._load_data(self.problems_file)
        proposals = self._load_data(self.proposals_file)
        evaluations = self._load_data(self.evaluations_file)
        implementations = self._load_data(self.implementations_file)
        tools = self._load_data(self.tools_file)
        
        return {
            "total_problems": len(problems),
            "total_proposals": len(proposals),
            "total_evaluations": len(evaluations),
            "total_implementations": len(implementations),
            "total_tools_created": len(tools),
            "active_iterations": len([p for p in problems if not any(prop["problem_id"] == p["problem_id"] for prop in proposals)]),
            "recent_activity": {
                "last_7_days": {
                    "problems": len([p for p in problems if self._is_recent(p["timestamp"], 7)]),
                    "proposals": len([p for p in proposals if self._is_recent(p["timestamp"], 7)]),
                    "tools": len([t for t in tools if self._is_recent(t["creation_timestamp"], 7)])
                }
            }
        }
    
    def _is_recent(self, timestamp: str, days: int) -> bool:
        """检查时间戳是否在指定天数内"""
        try:
            from datetime import datetime, timedelta
            target_time = datetime.fromisoformat(timestamp)
            cutoff_time = datetime.now() - timedelta(days=days)
            return target_time > cutoff_time
        except:
            return False

# 全局迭代引擎实例
iteration_engine = SystemIterationEngine()

def get_iteration_engine() -> SystemIterationEngine:
    """获取迭代引擎实例"""
    return iteration_engine