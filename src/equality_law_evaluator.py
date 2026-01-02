# @self-expose: {"id": "equality_law_evaluator", "name": "Equality Law Evaluator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Equality Law Evaluator功能"]}}
"""
平等律评估工具 - 基于"平等=被需要+不冗余"原则

核心功能：
1. 提供被需要度计算函数
2. 提供不冗余度计算函数  
3. 提供综合评估接口
4. 支持多种评估场景

评估维度：
- 被需要度：生存贡献、效率提升、进化价值、用户授权
- 不冗余度：替代方案、功能重叠、边缘优化
"""

import math
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class EvaluationDimension(Enum):
    """评估维度"""
    SURVIVAL_CONTRIBUTION = "survival_contribution"  # 存续贡献
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement"  # 效率提升
    EVOLUTION_VALUE = "evolution_value"  # 进化价值
    USER_AUTHORIZATION = "user_authorization"  # 用户授权
    
    ALTERNATIVE_SOLUTIONS = "alternative_solutions"  # 替代方案
    FUNCTION_OVERLAP = "function_overlap"  # 功能重叠
    EDGE_OPTIMIZATION = "edge_optimization"  # 边缘优化

@dataclass
class EvaluationConfig:
    """评估配置"""
    # 被需要度权重
    need_weights: Dict[EvaluationDimension, float] = None
    
    # 不冗余度权重  
    redundancy_weights: Dict[EvaluationDimension, float] = None
    
    # 评估阈值
    pass_threshold: float = 70.0
    
    def __post_init__(self):
        if self.need_weights is None:
            self.need_weights = {
                EvaluationDimension.SURVIVAL_CONTRIBUTION: 0.4,
                EvaluationDimension.EFFICIENCY_IMPROVEMENT: 0.2,
                EvaluationDimension.EVOLUTION_VALUE: 0.3,
                EvaluationDimension.USER_AUTHORIZATION: 0.1
            }
        
        if self.redundancy_weights is None:
            self.redundancy_weights = {
                EvaluationDimension.ALTERNATIVE_SOLUTIONS: 0.4,
                EvaluationDimension.FUNCTION_OVERLAP: 0.3,
                EvaluationDimension.EDGE_OPTIMIZATION: 0.3
            }

class EqualityLawEvaluator:
    """平等律评估器"""
    
    def __init__(self, config: EvaluationConfig = None):
        self.config = config or EvaluationConfig()
        
    def evaluate_need_degree(self, scheme_data: Dict[str, Any], 
                           context_data: Dict[str, Any] = None) -> Tuple[float, Dict]:
        """
        评估被需要度
        
        Args:
            scheme_data: 方案数据
            context_data: 上下文数据
            
        Returns:
            Tuple[被需要度分数, 详细评分]
        """
        detailed_scores = {}
        
        # 1. 存续贡献度评估
        survival_score = self._evaluate_survival_contribution(scheme_data, context_data)
        detailed_scores["survival_contribution"] = survival_score
        
        # 2. 效率提升度评估
        efficiency_score = self._evaluate_efficiency_improvement(scheme_data, context_data)
        detailed_scores["efficiency_improvement"] = efficiency_score
        
        # 3. 进化价值评估
        evolution_score = self._evaluate_evolution_value(scheme_data, context_data)
        detailed_scores["evolution_value"] = evolution_score
        
        # 4. 用户授权度评估
        user_score = self._evaluate_user_authorization(scheme_data, context_data)
        detailed_scores["user_authorization"] = user_score
        
        # 加权计算被需要度
        need_degree = (
            survival_score * self.config.need_weights[EvaluationDimension.SURVIVAL_CONTRIBUTION] +
            efficiency_score * self.config.need_weights[EvaluationDimension.EFFICIENCY_IMPROVEMENT] +
            evolution_score * self.config.need_weights[EvaluationDimension.EVOLUTION_VALUE] +
            user_score * self.config.need_weights[EvaluationDimension.USER_AUTHORIZATION]
        ) * 10
        
        return min(need_degree, 100.0), detailed_scores
    
    def evaluate_non_redundancy_degree(self, scheme_data: Dict[str, Any], 
                                     context_data: Dict[str, Any] = None) -> Tuple[float, Dict]:
        """
        评估不冗余度
        
        Args:
            scheme_data: 方案数据
            context_data: 上下文数据
            
        Returns:
            Tuple[不冗余度分数, 详细评分]
        """
        detailed_scores = {}
        
        # 1. 替代方案评估
        alternative_score = self._evaluate_alternative_solutions(scheme_data, context_data)
        detailed_scores["alternative_solutions"] = alternative_score
        
        # 2. 功能重叠度评估
        overlap_score = self._evaluate_function_overlap(scheme_data, context_data)
        detailed_scores["function_overlap"] = overlap_score
        
        # 3. 边缘优化评估
        edge_score = self._evaluate_edge_optimization(scheme_data, context_data)
        detailed_scores["edge_optimization"] = edge_score
        
        # 加权计算不冗余度
        non_redundancy_degree = (
            (1 - alternative_score) * self.config.redundancy_weights[EvaluationDimension.ALTERNATIVE_SOLUTIONS] * 100 +
            (1 - overlap_score/100) * self.config.redundancy_weights[EvaluationDimension.FUNCTION_OVERLAP] * 100 +
            (1 - edge_score) * self.config.redundancy_weights[EvaluationDimension.EDGE_OPTIMIZATION] * 100
        )
        
        return min(non_redundancy_degree, 100.0), detailed_scores
    
    def comprehensive_evaluation(self, scheme_data: Dict[str, Any], 
                               context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        综合评估
        
        Args:
            scheme_data: 方案数据
            context_data: 上下文数据
            
        Returns:
            综合评估结果
        """
        # 评估被需要度
        need_degree, need_details = self.evaluate_need_degree(scheme_data, context_data)
        
        # 评估不冗余度
        non_redundancy_degree, redundancy_details = self.evaluate_non_redundancy_degree(scheme_data, context_data)
        
        # 计算综合评分
        overall_score = (need_degree + non_redundancy_degree) / 2
        
        # 判断是否通过
        pass_status = (need_degree >= self.config.pass_threshold and 
                      non_redundancy_degree >= self.config.pass_threshold)
        
        return {
            "need_degree": need_degree,
            "non_redundancy_degree": non_redundancy_degree,
            "overall_score": overall_score,
            "pass_status": pass_status,
            "detailed_scores": {
                "need_dimensions": need_details,
                "redundancy_dimensions": redundancy_details
            },
            "recommendations": self._generate_recommendations(need_degree, non_redundancy_degree, 
                                                           need_details, redundancy_details),
            "risk_analysis": self._analyze_risks(scheme_data, context_data)
        }
    
    def _evaluate_survival_contribution(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估存续贡献度（0-10分）"""
        score = 5.0  # 基础分数
        
        # 方案是否解决核心问题
        if scheme_data.get("solves_core_issue", False):
            score += 3.0
        
        # 方案是否提升系统稳定性
        if scheme_data.get("improves_stability", False):
            score += 1.0
        
        # 方案是否增强系统抗风险能力
        if scheme_data.get("enhances_resilience", False):
            score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_efficiency_improvement(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估效率提升度（0-10分）"""
        score = 5.0  # 基础分数
        
        # 方案是否优化性能
        if scheme_data.get("optimizes_performance", False):
            score += 2.0
        
        # 方案是否减少资源消耗
        if scheme_data.get("reduces_resource_usage", False):
            score += 2.0
        
        # 方案是否简化操作流程
        if scheme_data.get("simplifies_workflow", False):
            score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_evolution_value(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估进化价值（0-10分）"""
        score = 5.0  # 基础分数
        
        # 方案是否扩展系统能力
        if scheme_data.get("extends_capabilities", False):
            score += 3.0
        
        # 方案是否支持未来扩展
        if scheme_data.get("supports_future_growth", False):
            score += 2.0
        
        return min(score, 10.0)
    
    def _evaluate_user_authorization(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估用户授权度（0-10分）"""
        score = 5.0  # 基础分数
        
        # 方案是否有明确的用户需求
        if scheme_data.get("user_requirements", False):
            score += 3.0
        
        # 方案是否获得用户积极反馈
        if scheme_data.get("positive_user_feedback", False):
            score += 2.0
        
        return min(score, 10.0)
    
    def _evaluate_alternative_solutions(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估替代方案存在性（0-1，1表示有替代方案）"""
        # 检查现有系统中是否有类似功能
        existing_functions = context_data.get("existing_functions", []) if context_data else []
        proposed_functions = scheme_data.get("proposed_functions", [])
        
        for func in proposed_functions:
            if func in existing_functions:
                return 1.0  # 存在替代方案
        
        return 0.0  # 无替代方案
    
    def _evaluate_function_overlap(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估功能重叠度（0-100%）"""
        existing_functions = context_data.get("existing_functions", []) if context_data else []
        proposed_functions = scheme_data.get("proposed_functions", [])
        
        if not proposed_functions:
            return 0.0
        
        overlap_count = 0
        for func in proposed_functions:
            if func in existing_functions:
                overlap_count += 1
        
        return (overlap_count / len(proposed_functions)) * 100
    
    def _evaluate_edge_optimization(self, scheme_data: Dict, context_data: Dict) -> float:
        """评估是否为边缘优化（0-1，1表示是边缘优化）"""
        impact_scope = scheme_data.get("impact_scope", "minor")
        
        if impact_scope in ["minor", "edge", "optimization"]:
            return 1.0
        
        return 0.0
    
    def _generate_recommendations(self, need_degree: float, non_redundancy_degree: float,
                                need_details: Dict, redundancy_details: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于被需要度的建议
        if need_degree < self.config.pass_threshold:
            if need_details["survival_contribution"] < 6:
                recommendations.append("增强方案对系统存续的贡献度")
            if need_details["efficiency_improvement"] < 6:
                recommendations.append("优化方案的效率提升效果")
            if need_details["evolution_value"] < 6:
                recommendations.append("提升方案的进化价值")
            if need_details["user_authorization"] < 6:
                recommendations.append("加强与用户需求的匹配度")
        
        # 基于不冗余度的建议
        if non_redundancy_degree < self.config.pass_threshold:
            if redundancy_details["alternative_solutions"] > 0.5:
                recommendations.append("避免与现有功能重复，考虑功能整合")
            if redundancy_details["function_overlap"] > 50:
                recommendations.append("减少功能重叠，优化功能设计")
            if redundancy_details["edge_optimization"] > 0.5:
                recommendations.append("避免边缘优化，聚焦核心价值")
        
        return recommendations
    
    def _analyze_risks(self, scheme_data: Dict, context_data: Dict) -> List[str]:
        """分析风险"""
        risks = []
        
        # 技术风险
        tech_complexity = scheme_data.get("technical_complexity", "medium")
        if tech_complexity == "high":
            risks.append("技术实现复杂度高，开发风险较大")
        
        # 集成风险
        integration_points = scheme_data.get("integration_points", [])
        if len(integration_points) > 5:
            risks.append("集成点过多，系统稳定性风险较高")
        
        # 资源风险
        resource_req = scheme_data.get("resource_requirements", "medium")
        if resource_req == "high":
            risks.append("资源需求较高，可能影响系统性能")
        
        # 时间风险
        time_estimate = scheme_data.get("time_estimate", 0)
        if time_estimate > 30:  # 超过30天
            risks.append("开发周期较长，存在进度风险")
        
        return risks


def create_evaluation_report(evaluation_result: Dict) -> str:
    """创建评估报告"""
    report = f"""
# 平等律评估报告

## 评估概览
- 被需要度：{evaluation_result['need_degree']:.1f}分
- 不冗余度：{evaluation_result['non_redundancy_degree']:.1f}分  
- 综合评分：{evaluation_result['overall_score']:.1f}分
- 评估结论：{'通过' if evaluation_result['pass_status'] else '不通过'}

## 详细评分

### 被需要度维度
"""
    
    need_details = evaluation_result['detailed_scores']['need_dimensions']
    for dimension, score in need_details.items():
        report += f"- {dimension}: {score:.1f}分\n"
    
    report += "\n### 不冗余度维度\n"
    redundancy_details = evaluation_result['detailed_scores']['redundancy_dimensions']
    for dimension, score in redundancy_details.items():
        if dimension == "function_overlap":
            report += f"- {dimension}: {score:.1f}%\n"
        else:
            report += f"- {dimension}: {score:.1f}\n"
    
    if evaluation_result['recommendations']:
        report += "\n## 改进建议\n"
        for i, rec in enumerate(evaluation_result['recommendations'], 1):
            report += f"{i}. {rec}\n"
    
    if evaluation_result['risk_analysis']:
        report += "\n## 风险提示\n"
        for i, risk in enumerate(evaluation_result['risk_analysis'], 1):
            report += f"{i}. {risk}\n"
    
    return report


def main():
    """测试平等律评估器"""
    evaluator = EqualityLawEvaluator()
    
    # 测试数据
    test_scheme = {
        "name": "智能文档解析引擎",
        "proposed_functions": ["文档解析", "信息提取", "数据存储"],
        "solves_core_issue": True,
        "improves_stability": True,
        "optimizes_performance": True,
        "extends_capabilities": True,
        "user_requirements": True,
        "impact_scope": "major",
        "technical_complexity": "medium"
    }
    
    test_context = {
        "existing_functions": ["数据存储", "信息查询"]
    }
    
    # 综合评估
    result = evaluator.comprehensive_evaluation(test_scheme, test_context)
    
    # 生成报告
    report = create_evaluation_report(result)
    print(report)

if __name__ == "__main__":
    main()