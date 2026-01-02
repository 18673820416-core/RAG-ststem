# @self-expose: {"id": "feedback_evaluator", "name": "Feedback Evaluator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Feedback Evaluator功能"]}}
"""
反馈评估器，用于评估反馈质量并排序优先级
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any
import os

# 配置日志
logging.basicConfig(
    filename='logs/feedback_evaluation.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class FeedbackEvaluator:
    """
    反馈评估器，用于评估反馈质量并排序优先级
    """
    
    def __init__(self, feedback_file="data/agent_feedback.json", evaluation_file="data/feedback_evaluations.json"):
        """
        初始化反馈评估器
        
        Args:
            feedback_file: 反馈数据文件路径
            evaluation_file: 评估结果文件路径
        """
        self.feedback_file = feedback_file
        self.evaluation_file = evaluation_file
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """
        确保数据文件存在，不存在则创建
        """
        # 确保目录存在
        for file_path in [self.feedback_file, self.evaluation_file]:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def evaluate_feedback(self, feedback_id: str = None) -> Dict[str, Any]:
        """
        评估反馈质量
        
        Args:
            feedback_id: 反馈ID，None表示评估所有待评估的反馈
            
        Returns:
            Dict: 评估结果
        """
        if feedback_id:
            # 评估单个反馈
            return self._evaluate_single_feedback(feedback_id)
        else:
            # 评估所有待评估的反馈
            return self._evaluate_all_pending_feedback()
    
    def _evaluate_single_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """
        评估单个反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Dict: 评估结果
        """
        # 读取反馈数据
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        # 查找目标反馈
        target_feedback = None
        for feedback in feedbacks:
            if feedback["id"] == feedback_id:
                target_feedback = feedback
                break
        
        if not target_feedback:
            logger.warning(f"未找到反馈: {feedback_id}")
            return {"status": "error", "message": f"未找到反馈: {feedback_id}"}
        
        # 评估反馈
        evaluation = self._calculate_feedback_evaluation(target_feedback)
        
        # 保存评估结果
        self._save_evaluation_result(feedback_id, evaluation)
        
        # 更新反馈状态
        self._update_feedback_status(feedback_id, "evaluated")
        
        logger.info(f"反馈评估完成: {feedback_id}, 综合评分: {evaluation['overall_score']}")
        return {"status": "success", "feedback_id": feedback_id, "evaluation": evaluation}
    
    def _evaluate_all_pending_feedback(self) -> Dict[str, Any]:
        """
        评估所有待评估的反馈
        
        Returns:
            Dict: 评估结果统计
        """
        # 读取反馈数据
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        # 筛选待评估的反馈
        pending_feedbacks = [f for f in feedbacks if f["status"] == "pending"]
        
        evaluation_results = []
        for feedback in pending_feedbacks:
            evaluation = self._calculate_feedback_evaluation(feedback)
            self._save_evaluation_result(feedback["id"], evaluation)
            self._update_feedback_status(feedback["id"], "evaluated")
            evaluation_results.append({
                "feedback_id": feedback["id"],
                "evaluation": evaluation
            })
        
        logger.info(f"批量评估完成，共评估 {len(evaluation_results)} 条反馈")
        return {
            "status": "success",
            "total_evaluated": len(evaluation_results),
            "results": evaluation_results
        }
    
    def _calculate_feedback_evaluation(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算反馈评估分数
        
        Args:
            feedback: 反馈数据
            
        Returns:
            Dict: 评估结果，包含各维度分数和综合评分
        """
        # 评估维度权重
        weights = {
            "value_degree": 0.4,      # 价值度权重
            "feasibility": 0.3,       # 可行性权重
            "urgency": 0.2,           # 紧急度权重
            "agent_consensus": 0.1     # 智能体共识权重
        }
        
        # 计算各维度分数
        value_degree = self._evaluate_value_degree(feedback)
        feasibility = self._evaluate_feasibility(feedback)
        urgency = self._evaluate_urgency(feedback)
        agent_consensus = self._evaluate_agent_consensus(feedback)
        
        # 计算综合评分
        overall_score = (
            value_degree * weights["value_degree"] +
            feasibility * weights["feasibility"] +
            urgency * weights["urgency"] +
            agent_consensus * weights["agent_consensus"]
        )
        
        # 计算优先级
        priority = self._calculate_priority(overall_score)
        
        return {
            "value_degree": value_degree,
            "feasibility": feasibility,
            "urgency": urgency,
            "agent_consensus": agent_consensus,
            "overall_score": round(overall_score, 2),
            "priority": priority,
            "evaluation_time": datetime.now().isoformat()
        }
    
    def _evaluate_value_degree(self, feedback: Dict[str, Any]) -> float:
        """
        评估反馈的价值度（0-100）
        
        Args:
            feedback: 反馈数据
            
        Returns:
            float: 价值度分数
        """
        # 基于反馈类型和内容质量评估价值度
        feedback_type = feedback["feedback_type"]
        content = feedback["content"]
        
        # 反馈类型基础分数
        type_scores = {
            "问题报告": 80,       # 问题报告通常价值较高
            "功能优化": 70,       # 功能优化有明确的改进方向
            "新功能需求": 60,     # 新功能需求需要评估可行性
            "使用体验": 50        # 使用体验反馈价值相对较低
        }
        
        base_score = type_scores.get(feedback_type, 50)
        
        # 内容质量调整
        content_length = len(content)
        if content_length < 50:
            # 内容过于简短，扣分
            content_adjustment = -20
        elif 50 <= content_length < 200:
            # 内容适中，不调整
            content_adjustment = 0
        else:
            # 内容详细，加分
            content_adjustment = 10
        
        # 检查是否包含具体建议
        if "建议" in content or "优化" in content or "改进" in content:
            content_adjustment += 10
        
        # 计算最终分数
        final_score = base_score + content_adjustment
        return max(0, min(100, final_score))
    
    def _evaluate_feasibility(self, feedback: Dict[str, Any]) -> float:
        """
        评估反馈的可行性（0-100）
        
        Args:
            feedback: 反馈数据
            
        Returns:
            float: 可行性分数
        """
        # 基于反馈类型和内容评估可行性
        feedback_type = feedback["feedback_type"]
        content = feedback["content"]
        
        # 反馈类型基础可行性
        type_feasibility = {
            "问题报告": 85,       # 问题报告通常有明确的解决方向
            "功能优化": 75,       # 功能优化相对容易实现
            "新功能需求": 50,     # 新功能需求需要更多资源
            "使用体验": 65        # 使用体验优化可行性中等
        }
        
        base_score = type_feasibility.get(feedback_type, 50)
        
        # 内容详细度调整
        if "具体" in content or "详细" in content or "步骤" in content:
            base_score += 15
        
        return max(0, min(100, base_score))
    
    def _evaluate_urgency(self, feedback: Dict[str, Any]) -> float:
        """
        评估反馈的紧急度（0-100）
        
        Args:
            feedback: 反馈数据
            
        Returns:
            float: 紧急度分数
        """
        # 基于反馈类型和优先级评估紧急度
        feedback_type = feedback["feedback_type"]
        priority = feedback["priority"]
        
        # 优先级基础分数
        priority_scores = {
            "high": 80,
            "medium": 50,
            "low": 20
        }
        
        base_score = priority_scores.get(priority, 50)
        
        # 反馈类型紧急度调整
        type_urgency = {
            "问题报告": 20,       # 问题报告通常需要紧急处理
            "功能优化": 10,       # 功能优化紧急度中等
            "新功能需求": 5,       # 新功能需求紧急度较低
            "使用体验": 5         # 使用体验优化紧急度较低
        }
        
        urgency_adjustment = type_urgency.get(feedback_type, 0)
        
        return max(0, min(100, base_score + urgency_adjustment))
    
    def _evaluate_agent_consensus(self, feedback: Dict[str, Any]) -> float:
        """
        评估智能体共识度（0-100）
        
        Args:
            feedback: 反馈数据
            
        Returns:
            float: 共识度分数
        """
        # 读取所有反馈，统计相同工具和问题的反馈数量
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            all_feedbacks = json.load(f)
        
        # 统计相同工具和相似内容的反馈数量
        tool_name = feedback["tool_name"]
        content = feedback["content"].lower()
        
        similar_feedbacks = []
        for f in all_feedbacks:
            if f["tool_name"] == tool_name and f["id"] != feedback["id"]:
                f_content = f["content"].lower()
                # 简单的相似性判断：检查关键词重叠
                if any(keyword in f_content for keyword in content.split()[:5]):
                    similar_feedbacks.append(f)
        
        # 计算共识度分数
        consensus_count = len(similar_feedbacks)
        if consensus_count == 0:
            return 30  # 没有共识，分数较低
        elif consensus_count == 1:
            return 50  # 有一个相似反馈，中等共识
        elif consensus_count == 2:
            return 70  # 有两个相似反馈，较高共识
        else:
            return 90  # 有三个以上相似反馈，高共识
    
    def _calculate_priority(self, overall_score: float) -> str:
        """
        根据综合评分计算优先级
        
        Args:
            overall_score: 综合评分
            
        Returns:
            str: 优先级（low, medium, high, critical）
        """
        if overall_score >= 85:
            return "critical"
        elif overall_score >= 70:
            return "high"
        elif overall_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _save_evaluation_result(self, feedback_id: str, evaluation: Dict[str, Any]):
        """
        保存评估结果
        
        Args:
            feedback_id: 反馈ID
            evaluation: 评估结果
        """
        # 读取现有评估结果
        with open(self.evaluation_file, 'r', encoding='utf-8') as f:
            evaluations = json.load(f)
        
        # 检查是否已存在评估结果
        existing_index = None
        for i, eval_item in enumerate(evaluations):
            if eval_item["feedback_id"] == feedback_id:
                existing_index = i
                break
        
        # 创建评估记录
        evaluation_record = {
            "id": f"eval_{uuid.uuid4()}",
            "feedback_id": feedback_id,
            "evaluation": evaluation,
            "created_at": datetime.now().isoformat()
        }
        
        # 更新或添加评估结果
        if existing_index is not None:
            evaluations[existing_index] = evaluation_record
        else:
            evaluations.append(evaluation_record)
        
        # 保存到文件
        with open(self.evaluation_file, 'w', encoding='utf-8') as f:
            json.dump(evaluations, f, ensure_ascii=False, indent=2)
    
    def _update_feedback_status(self, feedback_id: str, status: str):
        """
        更新反馈状态
        
        Args:
            feedback_id: 反馈ID
            status: 新状态
        """
        # 读取反馈数据
        with open(self.feedback_file, 'r+', encoding='utf-8') as f:
            feedbacks = json.load(f)
            
            # 更新反馈状态
            updated = False
            for feedback in feedbacks:
                if feedback["id"] == feedback_id:
                    feedback["status"] = status
                    updated = True
                    break
            
            if updated:
                f.seek(0)
                f.truncate()
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    
    def get_evaluation_result(self, feedback_id: str) -> Dict[str, Any]:
        """
        获取反馈评估结果
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Dict: 评估结果
        """
        # 读取评估结果
        with open(self.evaluation_file, 'r', encoding='utf-8') as f:
            evaluations = json.load(f)
        
        # 查找目标评估结果
        for evaluation in evaluations:
            if evaluation["feedback_id"] == feedback_id:
                return evaluation
        
        return None
    
    def get_all_evaluations(self, priority: str = None) -> List[Dict[str, Any]]:
        """
        获取所有评估结果，支持按优先级过滤
        
        Args:
            priority: 优先级过滤
            
        Returns:
            List: 评估结果列表
        """
        # 读取评估结果
        with open(self.evaluation_file, 'r', encoding='utf-8') as f:
            evaluations = json.load(f)
        
        # 按优先级过滤
        if priority:
            evaluations = [e for e in evaluations if e["evaluation"]["priority"] == priority]
        
        # 按综合评分降序排序
        evaluations.sort(key=lambda x: x["evaluation"]["overall_score"], reverse=True)
        
        return evaluations
    
    def generate_optimization_tasks(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        生成优化任务列表
        
        Args:
            top_n: 生成前N个优先级最高的任务
            
        Returns:
            List: 优化任务列表
        """
        # 获取所有评估结果，按优先级排序
        all_evaluations = self.get_all_evaluations()
        
        # 读取对应的反馈信息
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            all_feedbacks = json.load(f)
        
        feedback_map = {f["id"]: f for f in all_feedbacks}
        
        # 生成优化任务
        optimization_tasks = []
        for evaluation in all_evaluations[:top_n]:
            feedback_id = evaluation["feedback_id"]
            feedback = feedback_map.get(feedback_id)
            if feedback:
                task = {
                    "task_id": f"task_{uuid.uuid4()}",
                    "feedback_id": feedback_id,
                    "tool_name": feedback["tool_name"],
                    "feedback_type": feedback["feedback_type"],
                    "feedback_content": feedback["content"],
                    "evaluation": evaluation["evaluation"],
                    "created_at": datetime.now().isoformat(),
                    "status": "pending"
                }
                optimization_tasks.append(task)
        
        return optimization_tasks
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        获取反馈评估统计信息
        
        Returns:
            Dict: 统计信息
        """
        # 读取所有评估结果
        all_evaluations = self.get_all_evaluations()
        
        # 统计各优先级的反馈数量
        priority_counts = {}
        for evaluation in all_evaluations:
            priority = evaluation["evaluation"]["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # 统计平均评分
        if all_evaluations:
            average_score = sum(e["evaluation"]["overall_score"] for e in all_evaluations) / len(all_evaluations)
        else:
            average_score = 0
        
        return {
            "total_evaluations": len(all_evaluations),
            "priority_distribution": priority_counts,
            "average_score": round(average_score, 2),
            "last_updated": datetime.now().isoformat()
        }

# 命令行测试支持
if __name__ == "__main__":
    import sys
    
    evaluator = FeedbackEvaluator()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python feedback_evaluator.py evaluate [feedback_id]")
        print("  python feedback_evaluator.py list [priority]")
        print("  python feedback_evaluator.py get <feedback_id>")
        print("  python feedback_evaluator.py tasks [top_n]")
        print("  python feedback_evaluator.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "evaluate":
        if len(sys.argv) > 2:
            # 评估单个反馈
            feedback_id = sys.argv[2]
            result = evaluator.evaluate_feedback(feedback_id)
        else:
            # 评估所有待评估的反馈
            result = evaluator.evaluate_feedback()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "list":
        priority = sys.argv[2] if len(sys.argv) > 2 else None
        evaluations = evaluator.get_all_evaluations(priority)
        print(json.dumps(evaluations, ensure_ascii=False, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("参数不足: python feedback_evaluator.py get <feedback_id>")
            sys.exit(1)
        feedback_id = sys.argv[2]
        evaluation = evaluator.get_evaluation_result(feedback_id)
        if evaluation:
            print(json.dumps(evaluation, ensure_ascii=False, indent=2))
        else:
            print(f"未找到评估结果: {feedback_id}")
    
    elif command == "tasks":
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        tasks = evaluator.generate_optimization_tasks(top_n)
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
    
    elif command == "stats":
        stats = evaluator.get_feedback_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
