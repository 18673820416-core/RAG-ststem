#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
方案评估师智能体 - 基于平等律评估的RAG方案评估助手
开发提示词来源：用户建议统一智能体模板，将提示词外部化
"""
# @self-expose: {"id": "scheme_evaluator_agent", "name": "Scheme Evaluator Agent", "type": "agent", "version": "1.0.0", "needs": {"deps": ["base_agent"], "resources": []}, "provides": {"capabilities": ["方案评估", "平等律评估", "系统分析", "参与者评分"], "methods": {"process_user_query": {"signature": "(query: str) -> Dict[str, Any]", "description": "处理用户查询"}}}}

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime

from src.base_agent import BaseAgent
from src.equality_law_evaluator import EqualityLawEvaluator, EvaluationConfig
from src.llm_client_enhanced import LLMClientEnhanced
from config.api_keys import api_key_manager
from tools.memory_slicer_tool import MemorySlicerTool

logger = logging.getLogger(__name__)

class SchemeEvaluatorAgent(BaseAgent):
    """方案评估师智能体 - 基于平等律评估的RAG方案评估助手"""
    
    def __init__(self, agent_id: str = "evaluator_001"):
        """初始化方案评估师智能体"""
        super().__init__(
            agent_id=agent_id,
            agent_type="scheme_evaluator",
            prompt_file="src/agent_prompts/scheme_evaluator_prompt.txt"
        )
        
        # 初始化平等律评估器
        self.evaluator = EqualityLawEvaluator()
        
        # 初始化统一切片器 - 基于信息熵的分片技术
        self.memory_slicer = MemorySlicerTool()
        
        # 设置评估权重配置
        self.evaluation_weights = {
            "need_degree": {
                "survival_contribution": 0.4,  # 存续贡献度
                "efficiency_improvement": 0.2,  # 效率提升度
                "evolution_value": 0.3,  # 进化价值
                "user_authorization": 0.1  # 用户授权度
            },
            "non_redundancy_degree": {
                "has_alternative": 0.4,  # 是否有替代方案
                "function_overlap": 0.3,  # 功能重叠度
                "is_edge_optimization": 0.3  # 是否为边缘优化
            }
        }
        
        # 评估阈值
        self.pass_threshold = 70  # 通过阈值
        
        # 写操作评估配置
        self.write_operation_config = {
            'slice_quality_threshold': 0.7,
            'entropy_threshold': 2.5,
            'semantic_coherence_threshold': 0.8
        }
        
        # 参与者进化值评分配置
        self.participant_evaluation_config = {
            "evolution_value_weights": {
                "contribution_quality": 0.4,  # 贡献质量
                "innovation_level": 0.3,     # 创新程度
                "collaboration_effect": 0.2,  # 协作效果
                "learning_growth": 0.1       # 学习成长
            },
            "real_time_feedback_threshold": 60,  # 实时反馈阈值
            "co_creation_bonus": 5,              # 共建意识加分
            "ranking_update_interval": 3600     # 排行榜更新间隔（秒）
        }
        
        # 参与者评分记录
        self.participant_scores = {}
        self.participant_ranking = []
        self.last_ranking_update = datetime.now()
        
        # 记录启动日志
        self._write_work_log("方案评估师智能体启动 - 角色：平等律评估专家，权限：自主评估", "系统启动")
    
    def scan_rag_system(self) -> Dict:
        """
        扫描RAG系统，分析现有架构和功能
        
        Returns:
            Dict: 系统分析结果
        """
        logger.info("开始扫描RAG系统...")
        
        system_analysis = {
            "modules": [],
            "functions": [],
            "dependencies": [],
            "redundancy_analysis": {}
        }
        
        # 扫描src目录
        src_path = Path(self.variable_system.base_path) / "src"
        if src_path.exists():
            for file_path in src_path.rglob("*.py"):
                if file_path.is_file():
                    module_info = self._analyze_python_file(file_path)
                    if module_info:
                        system_analysis["modules"].append(module_info)
        
        # 扫描api目录
        api_path = Path(self.variable_system.base_path) / "api"
        if api_path.exists():
            for file_path in api_path.rglob("*.py"):
                if file_path.is_file():
                    module_info = self._analyze_python_file(file_path)
                    if module_info:
                        system_analysis["modules"].append(module_info)
        
        # 分析功能重叠度
        system_analysis["redundancy_analysis"] = self._analyze_redundancy(system_analysis["modules"])
        
        logger.info(f"扫描完成，发现 {len(system_analysis['modules'])} 个模块")
        
        # 记录扫描结果到日记
        self._record_to_diary({
            'type': 'system_scan',
            'modules_count': len(system_analysis['modules']),
            'redundancy_analysis': system_analysis['redundancy_analysis'],
            'timestamp': datetime.now().isoformat()
        })
        
        return system_analysis
    
    def _analyze_python_file(self, file_path: Path) -> Dict:
        """分析Python文件（只读分析，禁止修改）"""
        try:
            # 权限检查：只能读取，不能修改
            if not file_path.exists():
                return None
                
            # 记录分析行为到工作日记
            self._write_work_log(f"分析文件: {file_path.name}", "文件分析")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取基本信息（只读操作）
            module_info = {
                "file_path": str(file_path.relative_to(Path(self.variable_system.base_path))),
                "file_size": len(content),
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            # 简单分析函数和类（只读分析）
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('def '):
                    # 提取函数名
                    func_name = line.split('def ')[1].split('(')[0]
                    module_info["functions"].append({
                        "name": func_name,
                        "line": i + 1
                    })
                elif line.startswith('class '):
                    # 提取类名
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0]
                    module_info["classes"].append({
                        "name": class_name,
                        "line": i + 1
                    })
                elif line.startswith('import ') or line.startswith('from '):
                    module_info["imports"].append(line)
            
            return module_info
            
        except Exception as e:
            logger.error(f"分析文件失败 {file_path}: {e}")
            return None
    
    def _analyze_redundancy(self, modules: List[Dict]) -> Dict:
        """分析功能重叠度"""
        redundancy_analysis = {
            "total_modules": len(modules),
            "function_overlap": {},
            "class_overlap": {},
            "import_overlap": {}
        }
        
        # 分析函数重叠
        all_functions = []
        for module in modules:
            for func in module.get("functions", []):
                all_functions.append(func["name"])
        
        # 统计函数出现次数
        from collections import Counter
        func_counter = Counter(all_functions)
        
        # 找出重复的函数
        for func_name, count in func_counter.items():
            if count > 1:
                redundancy_analysis["function_overlap"][func_name] = count
        
        # 分析类重叠
        all_classes = []
        for module in modules:
            for cls in module.get("classes", []):
                all_classes.append(cls["name"])
        
        class_counter = Counter(all_classes)
        for class_name, count in class_counter.items():
            if count > 1:
                redundancy_analysis["class_overlap"][class_name] = count
        
        # 分析导入重叠
        all_imports = []
        for module in modules:
            all_imports.extend(module.get("imports", []))
        
        import_counter = Counter(all_imports)
        for import_line, count in import_counter.items():
            if count > 1:
                redundancy_analysis["import_overlap"][import_line] = count
        
        return redundancy_analysis
    
    def evaluate_scheme(self, scheme_description: str, context: Dict = None) -> Dict:
        """
        评估方案是否符合平等律
        
        Args:
            scheme_description: 方案描述
            context: 评估上下文
            
        Returns:
            Dict: 评估结果
        """
        logger.info("开始评估方案...")
        
        if context is None:
            context = {}
        
        # 构建评估配置
        config = EvaluationConfig(
            weights=self.evaluation_weights,
            pass_threshold=self.pass_threshold
        )
        
        # 执行平等律评估
        evaluation_result = self.evaluator.evaluate(
            scheme_description=scheme_description,
            context=context,
            config=config
        )
        
        # 记录评估结果
        self._record_evaluation_result(scheme_description, evaluation_result)
        
        logger.info(f"评估完成，得分: {evaluation_result.get('overall_score', 0)}")
        
        return evaluation_result
    
    def _record_evaluation_result(self, scheme_description: str, evaluation_result: Dict):
        """记录评估结果到日记"""
        evaluation_entry = {
            'type': 'scheme_evaluation',
            'scheme_description': scheme_description,
            'evaluation_result': evaluation_result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(evaluation_entry)
    
    def compare_schemes(self, scheme1: Dict, scheme2: Dict) -> Dict:
        """
        比较两个方案的优劣
        
        Args:
            scheme1: 方案1的评估结果
            scheme2: 方案2的评估结果
            
        Returns:
            Dict: 比较结果
        """
        comparison_result = {
            "scheme1_score": scheme1.get("overall_score", 0),
            "scheme2_score": scheme2.get("overall_score", 0),
            "score_difference": abs(scheme1.get("overall_score", 0) - scheme2.get("overall_score", 0)),
            "recommendation": "",
            "comparison_details": {}
        }
        
        # 比较各项指标
        for key in ["need_degree", "non_redundancy_degree"]:
            if key in scheme1 and key in scheme2:
                comparison_result["comparison_details"][key] = {
                    "scheme1": scheme1[key],
                    "scheme2": scheme2[key],
                    "difference": abs(scheme1[key].get("score", 0) - scheme2[key].get("score", 0))
                }
        
        # 给出推荐
        if comparison_result["scheme1_score"] > comparison_result["scheme2_score"]:
            comparison_result["recommendation"] = "推荐方案1"
        elif comparison_result["scheme1_score"] < comparison_result["scheme2_score"]:
            comparison_result["recommendation"] = "推荐方案2"
        else:
            comparison_result["recommendation"] = "两个方案评分相同，建议进一步分析"
        
        # 记录比较结果
        self._record_comparison_result(scheme1, scheme2, comparison_result)
        
        return comparison_result
    
    def _record_comparison_result(self, scheme1: Dict, scheme2: Dict, comparison_result: Dict):
        """记录方案比较结果"""
        comparison_entry = {
            'type': 'scheme_comparison',
            'scheme1': scheme1,
            'scheme2': scheme2,
            'comparison_result': comparison_result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(comparison_entry)
    
    def generate_evaluation_report(self, evaluation_results: List[Dict]) -> str:
        """
        生成评估报告
        
        Args:
            evaluation_results: 评估结果列表
            
        Returns:
            str: 评估报告
        """
        logger.info("生成评估报告...")
        
        # 统计评估结果
        total_schemes = len(evaluation_results)
        passed_schemes = len([r for r in evaluation_results if r.get("overall_score", 0) >= self.pass_threshold])
        failed_schemes = total_schemes - passed_schemes
        
        # 计算平均分
        avg_score = sum([r.get("overall_score", 0) for r in evaluation_results]) / total_schemes if total_schemes > 0 else 0
        
        # 生成报告
        report = f"""# 方案评估报告

## 评估概览
- 评估方案总数: {total_schemes}
- 通过方案数: {passed_schemes}
- 未通过方案数: {failed_schemes}
- 平均得分: {avg_score:.2f}
- 通过率: {passed_schemes/total_schemes*100:.1f}%

## 详细评估结果
"""
        
        # 添加每个方案的详细结果
        for i, result in enumerate(evaluation_results, 1):
            report += f"""
### 方案 {i}
- 总体得分: {result.get('overall_score', 0)}
- 存续贡献度: {result.get('need_degree', {}).get('score', 0)}
- 非冗余度: {result.get('non_redundancy_degree', {}).get('score', 0)}
- 评估状态: {'通过' if result.get('overall_score', 0) >= self.pass_threshold else '未通过'}

"""
        
        # 添加建议
        report += """
## 评估建议

1. **存续贡献度**：关注方案对系统长期发展的贡献
2. **非冗余度**：避免功能重叠，提高资源利用效率
3. **用户授权**：确保方案符合用户需求和授权
4. **进化价值**：考虑方案的长期适应性和扩展性
"""
        
        # 记录报告生成
        self._write_work_log(f"生成评估报告，包含{total_schemes}个方案", "报告生成")
        
        return report
    
    def evaluate_write_operation(self, content: str, operation_type: str = "text_processing") -> Dict[str, Any]:
        """
        基于统一切片原理评估写操作质量
        
        Args:
            content: 待评估的内容
            operation_type: 操作类型（text_processing, code_generation, document_creation等）
            
        Returns:
            Dict: 写操作评估结果
        """
        logger.info(f"评估写操作质量，操作类型: {operation_type}")
        
        # 使用统一切片器进行内容分片
        slices = self.memory_slicer.slice_text(content, {
            'operation_type': operation_type,
            'source': 'write_operation_evaluation'
        })
        
        # 评估分片质量
        evaluation_result = self._evaluate_slice_quality(slices, operation_type)
        
        # 记录评估结果
        self._record_write_operation_evaluation(content, operation_type, evaluation_result)
        
        return evaluation_result
    
    def _evaluate_slice_quality(self, slices: List[Dict], operation_type: str) -> Dict[str, Any]:
        """评估分片质量"""
        if not slices:
            return {
                'overall_score': 0,
                'status': 'failed',
                'reason': '未生成有效分片',
                'details': {}
            }
        
        # 计算分片质量指标
        total_slices = len(slices)
        avg_quality = sum(slice.get('quality_score', 0) for slice in slices) / total_slices
        avg_entropy = sum(slice.get('entropy', 0) for slice in slices) / total_slices
        
        # 计算语义连贯性
        semantic_coherence = self._calculate_semantic_coherence(slices)
        
        # 计算总体得分
        overall_score = self._calculate_write_operation_score(
            avg_quality, avg_entropy, semantic_coherence, operation_type
        )
        
        # 评估结果
        status = 'passed' if overall_score >= self.write_operation_config['slice_quality_threshold'] else 'failed'
        
        return {
            'overall_score': overall_score,
            'status': status,
            'total_slices': total_slices,
            'avg_quality': avg_quality,
            'avg_entropy': avg_entropy,
            'semantic_coherence': semantic_coherence,
            'slices_details': slices,
            'operation_type': operation_type
        }
    
    def _calculate_semantic_coherence(self, slices: List[Dict]) -> float:
        """计算语义连贯性得分"""
        if len(slices) <= 1:
            return 1.0  # 单个分片默认完全连贯
        
        # 基于分片间的语义相似度计算连贯性
        coherence_scores = []
        for i in range(len(slices) - 1):
            # 简化的连贯性计算（实际实现可使用语义相似度模型）
            slice1_text = slices[i].get('content', '')
            slice2_text = slices[i+1].get('content', '')
            
            # 基于关键词重叠的连贯性计算
            words1 = set(slice1_text.split())
            words2 = set(slice2_text.split())
            
            if words1 and words2:
                overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                coherence_scores.append(overlap)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    def _calculate_write_operation_score(self, avg_quality: float, avg_entropy: float, 
                                       semantic_coherence: float, operation_type: str) -> float:
        """计算写操作总体得分"""
        # 基于操作类型调整权重
        weights = {
            'text_processing': {'quality': 0.4, 'entropy': 0.3, 'coherence': 0.3},
            'code_generation': {'quality': 0.5, 'entropy': 0.3, 'coherence': 0.2},
            'document_creation': {'quality': 0.3, 'entropy': 0.2, 'coherence': 0.5}
        }
        
        op_weights = weights.get(operation_type, weights['text_processing'])
        
        # 归一化各项指标
        normalized_quality = min(avg_quality / 1.0, 1.0)  # 质量得分在0-1之间
        normalized_entropy = min(avg_entropy / 5.0, 1.0)  # 信息熵在0-5之间
        
        # 计算加权得分
        score = (normalized_quality * op_weights['quality'] + 
                normalized_entropy * op_weights['entropy'] + 
                semantic_coherence * op_weights['coherence'])
        
        return score * 100  # 转换为百分制
    
    def _record_write_operation_evaluation(self, content: str, operation_type: str, result: Dict):
        """记录写操作评估结果"""
        evaluation_entry = {
            'type': 'write_operation_evaluation',
            'operation_type': operation_type,
            'content_preview': content[:100] + '...' if len(content) > 100 else content,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(evaluation_entry)
        
        # 记录工作日志
        self._write_work_log(
            f"写操作评估完成 - 类型: {operation_type}, 得分: {result.get('overall_score', 0):.1f}, 状态: {result.get('status', 'unknown')}",
            "写操作评估"
        )
    
    def process_user_query(self, query: str) -> Dict[str, Any]:
        """
        处理用户查询 - 基于平等律的评估工作流程
        
        Args:
            query: 用户查询
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"处理用户查询: {query}")
        
        # 记录对话历史
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'user',
            'content': query
        })
        
        # 分析查询类型
        query_analysis = self._analyze_evaluation_query(query)
        
        # 根据查询类型执行相应操作
        if query_analysis['query_type'] == 'system_scan':
            result = self.scan_rag_system()
        elif query_analysis['query_type'] == 'scheme_evaluation':
            result = self.evaluate_scheme(query_analysis['scheme_description'])
        elif query_analysis['query_type'] == 'report_generation':
            result = {'report': self.generate_evaluation_report([])}
        elif query_analysis['query_type'] == 'write_operation_evaluation':
            # 提取内容并评估写操作质量
            content = self._extract_content_from_query(query_analysis['content'])
            result = self.evaluate_write_operation(content, 'text_processing')
        else:
            result = {'message': '暂不支持该类型的查询'}
        
        # 记录智能体回复
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'assistant',
            'content': str(result)
        })
        
        return result
    
    def evaluate_participant_contribution(self, participant_id: str, evolution_action: Dict, 
                                        context_data: Dict = None) -> Dict[str, Any]:
        """
        评估单个参与者在进化动作中的贡献度
        
        Args:
            participant_id: 参与者ID
            evolution_action: 进化动作数据
            context_data: 上下文数据
            
        Returns:
            Dict: 参与者进化值评分结果
        """
        logger.info(f"开始评估参与者 {participant_id} 的进化值贡献")
        
        if context_data is None:
            context_data = {}
        
        # 评估参与者的进化价值
        evolution_score, detailed_scores = self._evaluate_participant_evolution_value(
            participant_id, evolution_action, context_data
        )
        
        # 计算综合进化值
        overall_evolution_value = self._calculate_overall_evolution_value(evolution_score, detailed_scores)
        
        # 检查是否需要实时反馈
        needs_real_time_feedback = overall_evolution_value >= self.participant_evaluation_config["real_time_feedback_threshold"]
        
        # 生成改进建议
        recommendations = self._generate_participant_recommendations(detailed_scores)
        
        # 更新参与者评分记录
        self._update_participant_scores(participant_id, overall_evolution_value, evolution_action)
        
        # 检查是否需要更新排行榜
        self._update_participant_ranking_if_needed()
        
        # 记录评估结果
        evaluation_result = {
            "participant_id": participant_id,
            "evolution_action_id": evolution_action.get("action_id", "unknown"),
            "overall_evolution_value": overall_evolution_value,
            "evolution_score": evolution_score,
            "detailed_scores": detailed_scores,
            "needs_real_time_feedback": needs_real_time_feedback,
            "recommendations": recommendations,
            "ranking_position": self._get_participant_ranking_position(participant_id),
            "timestamp": datetime.now().isoformat()
        }
        
        # 记录到工作日记
        self._record_participant_evaluation(evaluation_result)
        
        logger.info(f"参与者 {participant_id} 进化值评估完成，得分: {overall_evolution_value}")
        
        return evaluation_result
    
    def _evaluate_participant_evolution_value(self, participant_id: str, evolution_action: Dict, 
                                             context_data: Dict) -> Tuple[float, Dict]:
        """评估参与者的进化价值"""
        detailed_scores = {}
        
        # 1. 贡献质量评估
        contribution_quality = self._evaluate_contribution_quality(participant_id, evolution_action, context_data)
        detailed_scores["contribution_quality"] = contribution_quality
        
        # 2. 创新程度评估
        innovation_level = self._evaluate_innovation_level(participant_id, evolution_action, context_data)
        detailed_scores["innovation_level"] = innovation_level
        
        # 3. 协作效果评估
        collaboration_effect = self._evaluate_collaboration_effect(participant_id, evolution_action, context_data)
        detailed_scores["collaboration_effect"] = collaboration_effect
        
        # 4. 学习成长评估
        learning_growth = self._evaluate_learning_growth(participant_id, evolution_action, context_data)
        detailed_scores["learning_growth"] = learning_growth
        
        # 计算进化价值得分
        weights = self.participant_evaluation_config["evolution_value_weights"]
        evolution_score = (
            contribution_quality * weights["contribution_quality"] +
            innovation_level * weights["innovation_level"] +
            collaboration_effect * weights["collaboration_effect"] +
            learning_growth * weights["learning_growth"]
        ) * 10
        
        return min(evolution_score, 100.0), detailed_scores
    
    def _evaluate_contribution_quality(self, participant_id: str, evolution_action: Dict, context_data: Dict) -> float:
        """评估贡献质量（0-10分）"""
        score = 5.0  # 基础分数
        
        # 贡献是否解决核心问题
        if evolution_action.get("solves_core_issue", False):
            score += 3.0
        
        # 贡献的技术质量
        technical_quality = evolution_action.get("technical_quality", "medium")
        if technical_quality == "high":
            score += 2.0
        elif technical_quality == "low":
            score -= 1.0
        
        # 贡献的完整性
        if evolution_action.get("is_complete", True):
            score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_innovation_level(self, participant_id: str, evolution_action: Dict, context_data: Dict) -> float:
        """评估创新程度（0-10分）"""
        score = 5.0  # 基础分数
        
        # 创新性
        innovation_level = evolution_action.get("innovation_level", "medium")
        if innovation_level == "high":
            score += 3.0
        elif innovation_level == "low":
            score -= 1.0
        
        # 原创性
        if evolution_action.get("is_original", False):
            score += 2.0
        
        return min(score, 10.0)
    
    def _evaluate_collaboration_effect(self, participant_id: str, evolution_action: Dict, context_data: Dict) -> float:
        """评估协作效果（0-10分）"""
        score = 5.0  # 基础分数
        
        # 协作参与度
        collaboration_level = evolution_action.get("collaboration_level", "medium")
        if collaboration_level == "high":
            score += 2.0
        elif collaboration_level == "low":
            score -= 1.0
        
        # 对其他参与者的帮助
        if evolution_action.get("helps_others", False):
            score += 2.0
        
        # 共建意识加分
        if evolution_action.get("co_creation_spirit", False):
            score += self.participant_evaluation_config["co_creation_bonus"] / 2
        
        return min(score, 10.0)
    
    def _evaluate_learning_growth(self, participant_id: str, evolution_action: Dict, context_data: Dict) -> float:
        """评估学习成长（0-10分）"""
        score = 5.0  # 基础分数
        
        # 技能提升
        skill_improvement = evolution_action.get("skill_improvement", "medium")
        if skill_improvement == "high":
            score += 3.0
        elif skill_improvement == "low":
            score -= 1.0
        
        # 知识积累
        if evolution_action.get("knowledge_gain", False):
            score += 2.0
        
        return min(score, 10.0)
    
    def _calculate_overall_evolution_value(self, evolution_score: float, detailed_scores: Dict) -> float:
        """计算综合进化值"""
        # 基础进化值
        base_value = evolution_score
        
        # 协作效果加成
        collaboration_bonus = detailed_scores.get("collaboration_effect", 5.0) / 10.0 * 5
        
        # 共建意识额外加分
        co_creation_bonus = self.participant_evaluation_config["co_creation_bonus"]
        
        overall_value = base_value + collaboration_bonus + co_creation_bonus
        
        return min(overall_value, 100.0)
    
    def _generate_participant_recommendations(self, detailed_scores: Dict) -> List[str]:
        """生成参与者改进建议"""
        recommendations = []
        
        if detailed_scores.get("contribution_quality", 0) < 6:
            recommendations.append("提升贡献质量，关注核心问题解决")
        
        if detailed_scores.get("innovation_level", 0) < 6:
            recommendations.append("增强创新能力，尝试新的解决方案")
        
        if detailed_scores.get("collaboration_effect", 0) < 6:
            recommendations.append("加强团队协作，积极参与共建")
        
        if detailed_scores.get("learning_growth", 0) < 6:
            recommendations.append("注重学习成长，持续提升技能")
        
        return recommendations
    
    def _update_participant_scores(self, participant_id: str, evolution_value: float, evolution_action: Dict):
        """更新参与者评分记录"""
        if participant_id not in self.participant_scores:
            self.participant_scores[participant_id] = {
                "total_score": 0,
                "action_count": 0,
                "average_score": 0,
                "last_updated": datetime.now().isoformat(),
                "evolution_actions": []
            }
        
        participant_data = self.participant_scores[participant_id]
        participant_data["total_score"] += evolution_value
        participant_data["action_count"] += 1
        participant_data["average_score"] = participant_data["total_score"] / participant_data["action_count"]
        participant_data["last_updated"] = datetime.now().isoformat()
        participant_data["evolution_actions"].append({
            "action_id": evolution_action.get("action_id", "unknown"),
            "score": evolution_value,
            "timestamp": datetime.now().isoformat()
        })
    
    def _update_participant_ranking_if_needed(self):
        """检查并更新参与者排行榜"""
        current_time = datetime.now()
        time_diff = (current_time - self.last_ranking_update).total_seconds()
        
        if time_diff >= self.participant_evaluation_config["ranking_update_interval"]:
            self._update_participant_ranking()
            self.last_ranking_update = current_time
    
    def _update_participant_ranking(self):
        """更新参与者排行榜"""
        # 按平均分排序
        sorted_participants = sorted(
            self.participant_scores.items(),
            key=lambda x: x[1]["average_score"],
            reverse=True
        )
        
        self.participant_ranking = [
            {
                "participant_id": participant_id,
                "average_score": data["average_score"],
                "action_count": data["action_count"],
                "ranking_position": i + 1
            }
            for i, (participant_id, data) in enumerate(sorted_participants)
        ]
        
        logger.info(f"参与者排行榜已更新，共 {len(self.participant_ranking)} 名参与者")
    
    def _get_participant_ranking_position(self, participant_id: str) -> int:
        """获取参与者在排行榜中的位置"""
        for ranking in self.participant_ranking:
            if ranking["participant_id"] == participant_id:
                return ranking["ranking_position"]
        return -1  # 未上榜
    
    def _record_participant_evaluation(self, evaluation_result: Dict):
        """记录参与者评估结果到日记"""
        evaluation_entry = {
            'type': 'participant_evaluation',
            'evaluation_result': evaluation_result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(evaluation_entry)
        
        # 记录工作日志
        self._write_work_log(
            f"参与者进化值评估完成 - 参与者: {evaluation_result['participant_id']}, "
            f"进化值: {evaluation_result['overall_evolution_value']:.1f}, "
            f"排名: {evaluation_result['ranking_position']}",
            "参与者评估"
        )
    
    def get_participant_ranking_report(self) -> Dict[str, Any]:
        """获取参与者排行榜报告"""
        # 确保排行榜是最新的
        self._update_participant_ranking()
        
        report = {
            "total_participants": len(self.participant_scores),
            "ranking_updated": self.last_ranking_update.isoformat(),
            "top_participants": self.participant_ranking[:10],  # 前10名
            "ranking_summary": {
                "excellent_count": len([p for p in self.participant_ranking if p["average_score"] >= 80]),
                "good_count": len([p for p in self.participant_ranking if 60 <= p["average_score"] < 80]),
                "average_count": len([p for p in self.participant_ranking if p["average_score"] < 60])
            }
        }
        
        return report
    
    def provide_real_time_feedback(self, participant_id: str, evaluation_result: Dict) -> str:
        """提供实时反馈给参与者"""
        feedback_template = """
亲爱的参与者 {participant_id}：

您在进化动作 [{action_id}] 中的表现评估已完成！

📊 **您的进化值评分**: {evolution_value:.1f}分
🏆 **当前排名**: 第{ranking_position}名

📈 **详细评分**:
- 贡献质量: {contribution_quality:.1f}分
- 创新程度: {innovation_level:.1f}分  
- 协作效果: {collaboration_effect:.1f}分
- 学习成长: {learning_growth:.1f}分

💡 **改进建议**:
{recommendations}

感谢您为系统进化做出的贡献！继续努力，共建更强大的智能体生态系统！
"""
        
        detailed_scores = evaluation_result["detailed_scores"]
        recommendations_text = "\n".join([f"• {rec}" for rec in evaluation_result["recommendations"]])
        
        feedback = feedback_template.format(
            participant_id=participant_id,
            action_id=evaluation_result["evolution_action_id"],
            evolution_value=evaluation_result["overall_evolution_value"],
            ranking_position=evaluation_result["ranking_position"],
            contribution_quality=detailed_scores.get("contribution_quality", 0),
            innovation_level=detailed_scores.get("innovation_level", 0),
            collaboration_effect=detailed_scores.get("collaboration_effect", 0),
            learning_growth=detailed_scores.get("learning_growth", 0),
            recommendations=recommendations_text if recommendations_text else "暂无特定建议，继续保持！"
        )
        
        # 记录反馈发送
        self._write_work_log(f"向参与者 {participant_id} 发送实时反馈", "实时反馈")
        
        return feedback

    def process_evaluation_query(self, query: str) -> Dict:
        """处理评估查询"""
        # 分析查询类型
        query_analysis = self._analyze_evaluation_query(query)
        
        # 根据查询类型处理
        if query_analysis['query_type'] == 'system_scan':
            result = self.scan_system()
        elif query_analysis['query_type'] == 'scheme_evaluation':
            scheme_description = query_analysis.get('scheme_description', query)
            result = self.evaluate_scheme(scheme_description)
        elif query_analysis['query_type'] == 'report_generation':
            result = self.generate_evaluation_report()
        elif query_analysis['query_type'] == 'write_operation_evaluation':
            content = self._extract_content_from_query(query_analysis['content'])
            result = self.evaluate_write_operation(content, 'text_processing')
        else:
            result = {'message': '暂不支持该类型的查询'}
        
        # 记录处理结果
        self._record_query_processing(query, query_analysis, result)
        
        return {
            'query': query,
            'query_analysis': query_analysis,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_evaluation_query(self, query: str) -> Dict:
        """分析评估查询类型"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['扫描', '分析', '检查', 'scan']):
            return {
                'query_type': 'system_scan',
                'description': '系统扫描和分析'
            }
        elif any(keyword in query_lower for keyword in ['评估', '评价', '打分', 'evaluate']):
            return {
                'query_type': 'scheme_evaluation',
                'scheme_description': query,
                'description': '方案评估'
            }
        elif any(keyword in query_lower for keyword in ['报告', '总结', 'report']):
            return {
                'query_type': 'report_generation',
                'description': '报告生成'
            }
        elif any(keyword in query_lower for keyword in ['写操作', 'write', '内容质量', '分片']):
            return {
                'query_type': 'write_operation_evaluation',
                'description': '写操作质量评估',
                'content': query
            }
        else:
            return {
                'query_type': 'general',
                'description': '一般查询'
            }
    
    def _extract_content_from_query(self, query: str) -> str:
        """从查询中提取待评估的内容"""
        # 简单的提取逻辑，实际可根据需要扩展
        # 假设用户查询格式为："评估以下内容：[具体内容]"
        import re
        
        # 尝试提取引号内的内容
        quoted_content = re.findall(r'[""](.*?)[""]', query)
        if quoted_content:
            return quoted_content[0]
        
        # 尝试提取冒号后的内容
        if '：' in query:
            parts = query.split('：', 1)
            if len(parts) > 1:
                return parts[1].strip()
        
        # 如果无法提取，返回整个查询
        return query
    
    def _record_query_processing(self, query: str, query_analysis: Dict, result: Dict):
        """记录查询处理过程"""
        processing_entry = {
            'type': 'query_processing',
            'query': query,
            'query_analysis': query_analysis,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(processing_entry)

# 全局智能体实例(懒加载)
_evaluator_agent = None

def get_scheme_evaluator() -> SchemeEvaluatorAgent:
    """获取方案评估师智能体实例(懒加载)"""
    global _evaluator_agent
    if _evaluator_agent is None:
        _evaluator_agent = SchemeEvaluatorAgent()
    return _evaluator_agent