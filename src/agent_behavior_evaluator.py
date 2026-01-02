# @self-expose: {"id": "agent_behavior_evaluator", "name": "Agent Behavior Evaluator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Behavior Evaluator功能"]}}
"""
智能体行为评估器，用于评估智能体的工具使用行为和进化贡献
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

# 配置日志
logging.basicConfig(
    filename='logs/agent_behavior_evaluation.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class AgentBehaviorEvaluator:
    """
    智能体行为评估器，用于评估智能体的工具使用行为和进化贡献
    """
    
    def __init__(self, tool_logs_file="logs/tool_calls.log", feedback_file="data/agent_feedback.json", evaluation_results_file="data/agent_behavior_evaluations.json"):
        """
        初始化智能体行为评估器
        
        Args:
            tool_logs_file: 工具调用日志文件路径
            feedback_file: 反馈数据文件路径
            evaluation_results_file: 评估结果文件路径
        """
        self.tool_logs_file = tool_logs_file
        self.feedback_file = feedback_file
        self.evaluation_results_file = evaluation_results_file
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """
        确保数据文件存在，不存在则创建
        """
        # 确保目录存在
        for file_path in [self.evaluation_results_file]:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def evaluate_agent_behavior(self, agent_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        评估智能体行为
        
        Args:
            agent_id: 智能体ID
            time_window_hours: 评估时间窗口（小时）
            
        Returns:
            Dict: 评估结果
        """
        logger.info(f"开始评估智能体行为: {agent_id}, 时间窗口: {time_window_hours}小时")
        
        # 读取工具调用日志
        tool_logs = self._read_tool_logs()
        
        # 读取反馈数据
        feedbacks = self._read_feedbacks()
        
        # 筛选指定时间窗口内的数据
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # 筛选智能体的工具调用日志
        agent_tool_logs = []
        for log_entry in tool_logs:
            log_time = datetime.fromisoformat(log_entry["timestamp"])
            caller_info = log_entry.get("caller_info", {})
            if log_time >= cutoff_time and caller_info.get("agent_id") == agent_id:
                agent_tool_logs.append(log_entry)
        
        # 筛选智能体的反馈
        agent_feedbacks = []
        for feedback in feedbacks:
            feedback_time = datetime.fromisoformat(feedback["timestamp"])
            if feedback_time >= cutoff_time and feedback["agent_id"] == agent_id:
                agent_feedbacks.append(feedback)
        
        # 评估各维度
        evaluation = {
            "tool_usage_cognition": self._evaluate_tool_usage_cognition(agent_tool_logs),
            "problem_discovery_feedback": self._evaluate_problem_discovery_feedback(agent_feedbacks),
            "self_evolution_ability": self._evaluate_self_evolution_ability(agent_id, cutoff_time)
        }
        
        # 计算认知主体进化贡献值
        evolution_contribution = self._calculate_evolution_contribution(evaluation)
        
        # 生成评估报告
        evaluation_report = self._generate_evaluation_report(agent_id, evaluation, evolution_contribution, time_window_hours)
        
        # 保存评估结果
        self._save_evaluation_result(agent_id, evaluation_report)
        
        logger.info(f"智能体行为评估完成: {agent_id}, 进化贡献值: {evolution_contribution}")
        
        return evaluation_report
    
    def _read_tool_logs(self) -> List[Dict[str, Any]]:
        """
        读取工具调用日志
        
        Returns:
            List: 工具调用日志列表
        """
        tool_logs = []
        
        if os.path.exists(self.tool_logs_file):
            try:
                with open(self.tool_logs_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            log_entry = json.loads(line)
                            tool_logs.append(log_entry)
            except Exception as e:
                logger.error(f"读取工具调用日志失败: {e}")
        
        return tool_logs
    
    def _read_feedbacks(self) -> List[Dict[str, Any]]:
        """
        读取反馈数据
        
        Returns:
            List: 反馈数据列表
        """
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _evaluate_tool_usage_cognition(self, tool_logs: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        评估工具使用认知
        
        Args:
            tool_logs: 工具调用日志列表
            
        Returns:
            Dict: 工具使用认知评估结果，包含主动使用度、使用精准度、效果评估能力
        """
        if not tool_logs:
            return {
                "active_usage": 0.0,
                "usage_precision": 0.0,
                "effect_evaluation": 0.0,
                "score": 0.0
            }
        
        # 评估主动使用度
        active_usage_score = self._evaluate_active_usage(tool_logs)
        
        # 评估使用精准度
        usage_precision_score = self._evaluate_usage_precision(tool_logs)
        
        # 评估效果评估能力
        effect_evaluation_score = self._evaluate_effect_evaluation(tool_logs)
        
        # 计算工具使用认知总分
        total_score = (active_usage_score + usage_precision_score + effect_evaluation_score) / 3
        
        return {
            "active_usage": active_usage_score,
            "usage_precision": usage_precision_score,
            "effect_evaluation": effect_evaluation_score,
            "score": round(total_score, 2)
        }
    
    def _evaluate_active_usage(self, tool_logs: List[Dict[str, Any]]) -> float:
        """
        评估主动使用度（0-100）
        
        Args:
            tool_logs: 工具调用日志列表
            
        Returns:
            float: 主动使用度分数
        """
        # 计算主动调用比例
        active_calls = [log for log in tool_logs if log.get("active_call", True)]
        active_ratio = len(active_calls) / len(tool_logs) if tool_logs else 0
        
        # 计算使用工具的多样性
        used_tools = set(log["tool_name"] for log in tool_logs)
        tool_diversity = min(len(used_tools) / 10, 1.0)  # 假设系统有10种主要工具
        
        # 计算使用频率（每小时调用次数）
        if tool_logs:
            first_log_time = datetime.fromisoformat(tool_logs[0]["timestamp"])
            last_log_time = datetime.fromisoformat(tool_logs[-1]["timestamp"])
            duration_hours = max((last_log_time - first_log_time).total_seconds() / 3600, 1.0)
            usage_frequency = min(len(tool_logs) / duration_hours / 10, 1.0)  # 假设每小时10次调用为高频
        else:
            usage_frequency = 0.0
        
        # 计算主动使用度分数
        active_usage_score = (active_ratio * 0.4 + tool_diversity * 0.3 + usage_frequency * 0.3) * 100
        
        return round(active_usage_score, 2)
    
    def _evaluate_usage_precision(self, tool_logs: List[Dict[str, Any]]) -> float:
        """
        评估使用精准度（0-100）
        
        Args:
            tool_logs: 工具调用日志列表
            
        Returns:
            float: 使用精准度分数
        """
        # 计算成功调用比例
        successful_calls = [log for log in tool_logs if log.get("success", False)]
        success_ratio = len(successful_calls) / len(tool_logs) if tool_logs else 0
        
        # 计算参数完整性（假设参数完整性通过是否包含必要参数判断）
        # 这里简化处理，假设参数不为空即视为完整
        complete_param_calls = [log for log in tool_logs if log.get("parameters")]
        param_complete_ratio = len(complete_param_calls) / len(tool_logs) if tool_logs else 0
        
        # 计算使用意图明确性
        clear_intention_calls = [log for log in tool_logs if log.get("usage_intention")]
        intention_clarity_ratio = len(clear_intention_calls) / len(tool_logs) if tool_logs else 0
        
        # 计算使用精准度分数
        usage_precision_score = (success_ratio * 0.5 + param_complete_ratio * 0.3 + intention_clarity_ratio * 0.2) * 100
        
        return round(usage_precision_score, 2)
    
    def _evaluate_effect_evaluation(self, tool_logs: List[Dict[str, Any]]) -> float:
        """
        评估效果评估能力（0-100）
        
        Args:
            tool_logs: 工具调用日志列表
            
        Returns:
            float: 效果评估能力分数
        """
        # 简化处理：假设效果评估能力与成功调用后是否有后续反馈相关
        # 这里我们基于成功调用比例和调用后是否有反馈来评估
        
        # 成功调用比例
        successful_calls = [log for log in tool_logs if log.get("success", False)]
        success_ratio = len(successful_calls) / len(tool_logs) if tool_logs else 0
        
        # 调用后有反馈的比例（简化处理，实际需要关联调用和反馈）
        # 这里假设每10次成功调用中有1次反馈即为良好
        feedback_ratio = min(len(successful_calls) / 10, 1.0) if successful_calls else 0
        
        # 计算效果评估能力分数
        effect_evaluation_score = (success_ratio * 0.7 + feedback_ratio * 0.3) * 100
        
        return round(effect_evaluation_score, 2)
    
    def _evaluate_problem_discovery_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        评估问题发现与反馈能力
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            Dict: 问题发现与反馈评估结果，包含问题发现能力、反馈质量、优化建议质量
        """
        if not feedbacks:
            return {
                "problem_discovery": 0.0,
                "feedback_quality": 0.0,
                "suggestion_quality": 0.0,
                "score": 0.0
            }
        
        # 评估问题发现能力
        problem_discovery_score = self._evaluate_problem_discovery(feedbacks)
        
        # 评估反馈质量
        feedback_quality_score = self._evaluate_feedback_quality(feedbacks)
        
        # 评估优化建议质量
        suggestion_quality_score = self._evaluate_suggestion_quality(feedbacks)
        
        # 计算问题发现与反馈总分
        total_score = (problem_discovery_score + feedback_quality_score + suggestion_quality_score) / 3
        
        return {
            "problem_discovery": problem_discovery_score,
            "feedback_quality": feedback_quality_score,
            "suggestion_quality": suggestion_quality_score,
            "score": round(total_score, 2)
        }
    
    def _evaluate_problem_discovery(self, feedbacks: List[Dict[str, Any]]) -> float:
        """
        评估问题发现能力（0-100）
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            float: 问题发现能力分数
        """
        # 计算问题报告比例
        problem_reports = [f for f in feedbacks if f["feedback_type"] == "问题报告"]
        problem_report_ratio = len(problem_reports) / len(feedbacks) if feedbacks else 0
        
        # 计算反馈频率（每小时反馈次数）
        if feedbacks:
            first_feedback_time = datetime.fromisoformat(feedbacks[0]["timestamp"])
            last_feedback_time = datetime.fromisoformat(feedbacks[-1]["timestamp"])
            duration_hours = max((last_feedback_time - first_feedback_time).total_seconds() / 3600, 1.0)
            feedback_frequency = min(len(feedbacks) / duration_hours / 5, 1.0)  # 假设每小时5次反馈为高频
        else:
            feedback_frequency = 0.0
        
        # 计算问题发现能力分数
        problem_discovery_score = (problem_report_ratio * 0.6 + feedback_frequency * 0.4) * 100
        
        return round(problem_discovery_score, 2)
    
    def _evaluate_feedback_quality(self, feedbacks: List[Dict[str, Any]]) -> float:
        """
        评估反馈质量（0-100）
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            float: 反馈质量分数
        """
        # 计算平均反馈长度
        avg_content_length = sum(len(f["content"]) for f in feedbacks) / len(feedbacks) if feedbacks else 0
        content_length_score = min(avg_content_length / 200, 1.0)  # 假设平均200字为高质量反馈
        
        # 计算反馈类型多样性
        feedback_types = set(f["feedback_type"] for f in feedbacks)
        type_diversity_score = min(len(feedback_types) / 4, 1.0)  # 总共有4种反馈类型
        
        # 计算反馈优先级分布
        high_priority_feedbacks = [f for f in feedbacks if f["priority"] == "high"]
        high_priority_ratio = len(high_priority_feedbacks) / len(feedbacks) if feedbacks else 0
        
        # 计算反馈质量分数
        feedback_quality_score = (content_length_score * 0.5 + type_diversity_score * 0.3 + high_priority_ratio * 0.2) * 100
        
        return round(feedback_quality_score, 2)
    
    def _evaluate_suggestion_quality(self, feedbacks: List[Dict[str, Any]]) -> float:
        """
        评估优化建议质量（0-100）
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            float: 优化建议质量分数
        """
        # 计算包含优化建议的反馈比例
        suggestion_feedbacks = [f for f in feedbacks if "建议" in f["content"] or "优化" in f["content"] or "改进" in f["content"]]
        suggestion_ratio = len(suggestion_feedbacks) / len(feedbacks) if feedbacks else 0
        
        # 计算优化建议的详细程度
        avg_suggestion_length = 0
        if suggestion_feedbacks:
            avg_suggestion_length = sum(len(f["content"]) for f in suggestion_feedbacks) / len(suggestion_feedbacks)
        suggestion_detail_score = min(avg_suggestion_length / 150, 1.0)  # 假设平均150字为详细建议
        
        # 计算优化建议质量分数
        suggestion_quality_score = (suggestion_ratio * 0.6 + suggestion_detail_score * 0.4) * 100
        
        return round(suggestion_quality_score, 2)
    
    def _evaluate_self_evolution_ability(self, agent_id: str, cutoff_time: datetime) -> Dict[str, float]:
        """
        评估自我进化能力
        
        Args:
            agent_id: 智能体ID
            cutoff_time: 评估时间窗口截止时间
            
        Returns:
            Dict: 自我进化能力评估结果，包含学习能力、行为调整、记忆更新
        """
        # 简化处理：这里我们基于智能体的记忆更新情况和行为变化来评估
        # 实际实现需要访问记忆系统和行为历史
        
        # 学习能力：假设智能体每使用一次工具就会学习
        learning_ability_score = 60.0  # 基础分
        
        # 行为调整：假设智能体能够根据反馈调整行为
        behavior_adjustment_score = 50.0  # 基础分
        
        # 记忆更新：假设智能体定期更新记忆
        memory_update_score = 70.0  # 基础分
        
        # 计算自我进化能力总分
        total_score = (learning_ability_score + behavior_adjustment_score + memory_update_score) / 3
        
        return {
            "learning_ability": learning_ability_score,
            "behavior_adjustment": behavior_adjustment_score,
            "memory_update": memory_update_score,
            "score": round(total_score, 2)
        }
    
    def _calculate_evolution_contribution(self, evaluation: Dict[str, Any]) -> float:
        """
        计算认知主体进化贡献值
        
        Args:
            evaluation: 评估结果
            
        Returns:
            float: 认知主体进化贡献值（0-100）
        """
        # 认知主体进化贡献值 = (工具使用认知评分 + 问题发现与反馈评分 + 自我进化能力评分) / 3
        evolution_contribution = (
            evaluation["tool_usage_cognition"]["score"] +
            evaluation["problem_discovery_feedback"]["score"] +
            evaluation["self_evolution_ability"]["score"]
        ) / 3
        
        return round(evolution_contribution, 2)
    
    def _generate_evaluation_report(self, agent_id: str, evaluation: Dict[str, Any], evolution_contribution: float, time_window_hours: int) -> Dict[str, Any]:
        """
        生成评估报告
        
        Args:
            agent_id: 智能体ID
            evaluation: 评估结果
            evolution_contribution: 认知主体进化贡献值
            time_window_hours: 评估时间窗口
            
        Returns:
            Dict: 评估报告
        """
        # 生成评估等级
        if evolution_contribution >= 85:
            evaluation_level = "优秀"
        elif evolution_contribution >= 70:
            evaluation_level = "良好"
        elif evolution_contribution >= 50:
            evaluation_level = "中等"
        else:
            evaluation_level = "待提升"
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(evaluation)
        
        return {
            "report_id": f"report_{uuid.uuid4()}",
            "agent_id": agent_id,
            "evaluation_time": datetime.now().isoformat(),
            "time_window_hours": time_window_hours,
            "evaluation": evaluation,
            "evolution_contribution": evolution_contribution,
            "evaluation_level": evaluation_level,
            "improvement_suggestions": improvement_suggestions,
            "status": "completed"
        }
    
    def _generate_improvement_suggestions(self, evaluation: Dict[str, Any]) -> List[str]:
        """
        生成改进建议
        
        Args:
            evaluation: 评估结果
            
        Returns:
            List: 改进建议列表
        """
        suggestions = []
        
        # 基于工具使用认知评估生成建议
        tool_usage_score = evaluation["tool_usage_cognition"]["score"]
        if tool_usage_score < 70:
            suggestions.append("建议增加工具的主动使用频率，尝试使用更多类型的工具")
            suggestions.append("建议在调用工具时明确使用意图，提高使用精准度")
        
        # 基于问题发现与反馈评估生成建议
        feedback_score = evaluation["problem_discovery_feedback"]["score"]
        if feedback_score < 70:
            suggestions.append("建议增加反馈频率，特别是问题报告类型的反馈")
            suggestions.append("建议在反馈中提供更详细的描述和具体的优化建议")
        
        # 基于自我进化能力评估生成建议
        evolution_score = evaluation["self_evolution_ability"]["score"]
        if evolution_score < 70:
            suggestions.append("建议加强从工具使用中学习的能力，及时调整行为")
            suggestions.append("建议定期更新记忆，将经验整合到长期记忆中")
        
        return suggestions
    
    def _save_evaluation_result(self, agent_id: str, evaluation_report: Dict[str, Any]):
        """
        保存评估结果
        
        Args:
            agent_id: 智能体ID
            evaluation_report: 评估报告
        """
        # 读取现有评估结果
        with open(self.evaluation_results_file, 'r', encoding='utf-8') as f:
            evaluation_results = json.load(f)
        
        # 添加新的评估报告
        evaluation_results.append(evaluation_report)
        
        # 保存到文件
        with open(self.evaluation_results_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, ensure_ascii=False, indent=2)
    
    def get_agent_evaluation_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取智能体的评估历史
        
        Args:
            agent_id: 智能体ID
            limit: 返回前N条记录
            
        Returns:
            List: 评估历史列表
        """
        # 读取评估结果
        with open(self.evaluation_results_file, 'r', encoding='utf-8') as f:
            evaluation_results = json.load(f)
        
        # 筛选智能体的评估记录
        agent_evaluations = [r for r in evaluation_results if r["agent_id"] == agent_id]
        
        # 按评估时间降序排序
        agent_evaluations.sort(key=lambda x: x["evaluation_time"], reverse=True)
        
        # 返回前N条记录
        return agent_evaluations[:limit]
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """
        获取评估统计信息
        
        Returns:
            Dict: 统计信息
        """
        # 读取所有评估结果
        with open(self.evaluation_results_file, 'r', encoding='utf-8') as f:
            evaluation_results = json.load(f)
        
        if not evaluation_results:
            return {
                "total_evaluations": 0,
                "average_evolution_contribution": 0.0,
                "evaluation_level_distribution": {},
                "last_updated": datetime.now().isoformat()
            }
        
        # 统计各评估等级的数量
        level_distribution = {}
        for result in evaluation_results:
            level = result["evaluation_level"]
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # 计算平均认知主体进化贡献值
        avg_contribution = sum(r["evolution_contribution"] for r in evaluation_results) / len(evaluation_results)
        
        return {
            "total_evaluations": len(evaluation_results),
            "average_evolution_contribution": round(avg_contribution, 2),
            "evaluation_level_distribution": level_distribution,
            "last_updated": datetime.now().isoformat()
        }
    
    def evaluate_cognitive_behavior(self, cognitive_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估智能体的认知行为
        
        Args:
            cognitive_data: 认知数据
            
        Returns:
            Dict: 评估结果
        """
        # 简化实现：这里我们基于传入的认知数据进行评估
        # 实际实现需要结合工具调用日志和反馈数据
        
        # 评估各维度
        evaluation = {
            "主动使用度": self._evaluate_active_usage(cognitive_data.get("tool_logs", [])),
            "使用精准度": self._evaluate_usage_precision(cognitive_data.get("tool_logs", [])),
            "效果评估能力": self._evaluate_effect_evaluation(cognitive_data.get("tool_logs", [])),
            "问题发现能力": self._evaluate_problem_discovery(cognitive_data.get("feedbacks", [])),
            "反馈质量": self._evaluate_feedback_quality(cognitive_data.get("feedbacks", [])),
            "优化建议质量": self._evaluate_suggestion_quality(cognitive_data.get("feedbacks", [])),
            "学习能力": 60.0,  # 基础分
            "行为调整": 50.0,  # 基础分
            "记忆更新": 70.0   # 基础分
        }
        
        # 计算进化贡献值
        evolution_contribution = (
            evaluation["主动使用度"] + evaluation["使用精准度"] + evaluation["效果评估能力"] +
            evaluation["问题发现能力"] + evaluation["反馈质量"] + evaluation["优化建议质量"] +
            evaluation["学习能力"] + evaluation["行为调整"] + evaluation["记忆更新"]
        ) / 9
        
        return {
            "evaluation": evaluation,
            "evolution_contribution": round(evolution_contribution, 2)
        }

# 命令行测试支持
if __name__ == "__main__":
    import sys
    
    evaluator = AgentBehaviorEvaluator()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python agent_behavior_evaluator.py evaluate <agent_id> [time_window_hours]")
        print("  python agent_behavior_evaluator.py history <agent_id> [limit]")
        print("  python agent_behavior_evaluator.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "evaluate":
        if len(sys.argv) < 3:
            print("参数不足: python agent_behavior_evaluator.py evaluate <agent_id> [time_window_hours]")
            sys.exit(1)
        
        agent_id = sys.argv[2]
        time_window_hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        
        result = evaluator.evaluate_agent_behavior(agent_id, time_window_hours)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "history":
        if len(sys.argv) < 3:
            print("参数不足: python agent_behavior_evaluator.py history <agent_id> [limit]")
            sys.exit(1)
        
        agent_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        
        history = evaluator.get_agent_evaluation_history(agent_id, limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))
    
    elif command == "stats":
        stats = evaluator.get_evaluation_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
