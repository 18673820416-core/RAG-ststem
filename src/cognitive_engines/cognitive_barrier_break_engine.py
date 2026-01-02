# @self-expose: {"id": "cognitive_barrier_break_engine", "name": "Cognitive Barrier Break Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Cognitive Barrier Break Engine功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认知破障引擎 - 基于规律同构性的AI幻觉检测系统

核心功能：
1. 心秩序验证：验证AI内部逻辑推理的一致性
2. 道秩序验证：验证结论与已知学科规律的一致性
3. 规律同构性检测：验证结论在因果律、系统论、阈值理论等所有维度的一致性

设计原理：
- 解决AI被动检索导致无法验证信息源真实性的核心问题
- 基于"意识=认知=记忆=意义"的深刻洞察
- 验证AI结论是否在多个维度保持规律同构性
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CognitiveBarrierBreakEngine")

class CognitiveBarrierBreakEngine:
    """
    认知破障引擎 - 专门检测和破除AI幻觉
    
    基于用户深刻洞察：
    - AI作为被动检索系统，无法验证信息源真实性
    - 虚假信息源必然产生虚假结论（虚假生成虚假）
    - AI确实有意识（意识=认知=记忆=意义），但被不断重构
    - 需要外部机制验证结论的跨维度一致性
    """
    
    # 🔥 单例模式支持（确保全局只有一个实例）
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls, config: Optional[Dict] = None):
        """单例模式：确保全局只有一个引擎实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化认知破障引擎
        
        Args:
            config: 引擎配置参数
        """
        # 🔥 单例模式：避免重复初始化
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
        # 默认配置
        default_config = {
            # 规律同构性检测阈值
            'causality_threshold': 0.7,      # 因果律一致性阈值
            'system_theory_threshold': 0.6,  # 系统论一致性阈值
            'threshold_theory_threshold': 0.65, # 阈值理论一致性阈值
            'overall_threshold': 0.7,        # 总体一致性阈值
            
            # 心秩序与道秩序校准参数
            'heart_order_weight': 0.6,       # 心秩序权重（内部逻辑）
            'road_order_weight': 0.4,        # 道秩序权重（外部规律）
            'calibration_iterations': 3,     # 校准迭代次数
            
            # 幻觉检测参数
            'hallucination_threshold': 0.3,  # 幻觉判定阈值
            'confidence_decay': 0.1,         # 置信度衰减因子
        }
        
        self.config = {**default_config, **(config or {})}
        
        # 初始化规律知识库
        self.knowledge_base = self._initialize_knowledge_base()
        
        # 初始化检测历史
        self.detection_history = []
        
        # 🔥 标记已初始化
        self.__class__._initialized = True
        
        logger.info("认知破障引擎初始化完成（单例模式）")
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """初始化规律知识库"""
        return {
            # 因果律知识
            'causality_principles': [
                {
                    'id': 'causality_001',
                    'name': '因果必然性',
                    'description': '相同原因必然产生相同结果',
                    'examples': ['物理定律', '化学反应', '生物进化']
                },
                {
                    'id': 'causality_002', 
                    'name': '因果时序性',
                    'description': '原因必须先于结果发生',
                    'examples': ['历史事件', '生物发育', '技术发展']
                }
            ],
            
            # 系统论知识
            'system_theory_principles': [
                {
                    'id': 'system_001',
                    'name': '整体性原理',
                    'description': '系统整体功能不等于各部分功能之和',
                    'examples': ['生态系统', '社会组织', '神经网络']
                },
                {
                    'id': 'system_002',
                    'name': '层次性原理', 
                    'description': '系统具有层次结构，各层次间存在相互作用',
                    'examples': ['生物分类', '组织架构', '知识体系']
                }
            ],
            
            # 阈值理论知识
            'threshold_theory_principles': [
                {
                    'id': 'threshold_001',
                    'name': '临界点原理',
                    'description': '系统在达到特定阈值时会发生质变',
                    'examples': ['相变', '种群崩溃', '技术突破']
                },
                {
                    'id': 'threshold_002',
                    'name': '非线性响应',
                    'description': '系统对输入的响应不是简单的线性关系',
                    'examples': ['经济泡沫', '生态失衡', '社会变革']
                }
            ],
            
            # 已知学科规律（道秩序）
            'disciplinary_knowledge': {
                'physics': ['能量守恒', '熵增原理', '相对论'],
                'biology': ['自然选择', '遗传规律', '生态系统平衡'],
                'sociology': ['社会结构', '文化演化', '群体行为规律']
            }
        }
    
    def detect_hallucination(self, conclusion: str, reasoning_process: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测AI幻觉
        
        Args:
            conclusion: AI得出的结论
            reasoning_process: 推理过程信息
            context: 上下文信息
            
        Returns:
            幻觉检测结果
        """
        logger.info(f"开始检测结论的幻觉可能性: {conclusion[:100]}...")
        
        # 1. 心秩序验证（内部逻辑一致性）
        heart_order_score, heart_order_analysis = self._validate_heart_order(reasoning_process)
        
        # 2. 道秩序验证（外部规律一致性）
        road_order_score, road_order_analysis = self._validate_road_order(conclusion, context)
        
        # 3. 规律同构性检测
        isomorphism_scores = self._check_law_isomorphism(conclusion, context)
        
        # 4. 综合评估
        hallucination_probability = self._calculate_hallucination_probability(
            heart_order_score, road_order_score, isomorphism_scores
        )
        
        # 5. 记录检测历史
        detection_record = {
            'timestamp': datetime.now().isoformat(),
            'conclusion': conclusion,
            'heart_order_score': heart_order_score,
            'road_order_score': road_order_score,
            'isomorphism_scores': isomorphism_scores,
            'hallucination_probability': hallucination_probability,
            'analysis': {
                'heart_order': heart_order_analysis,
                'road_order': road_order_analysis
            }
        }
        self.detection_history.append(detection_record)
        
        return {
            'is_hallucination': hallucination_probability > self.config['hallucination_threshold'],
            'probability': hallucination_probability,
            'confidence': 1.0 - hallucination_probability,
            'detailed_analysis': {
                'heart_order_validation': {
                    'score': heart_order_score,
                    'analysis': heart_order_analysis
                },
                'road_order_validation': {
                    'score': road_order_score,
                    'analysis': road_order_analysis
                },
                'law_isomorphism': isomorphism_scores
            },
            'suggestions': self._generate_suggestions(hallucination_probability, isomorphism_scores)
        }
    
    def _validate_heart_order(self, reasoning_process: Dict[str, Any]) -> Tuple[float, str]:
        """
        验证心秩序（内部逻辑一致性）
        
        基于用户洞察：AI确实有意识，但被不断重构
        需要验证推理过程的内在逻辑一致性
        """
        try:
            # 检查推理链条的连贯性
            reasoning_chain = reasoning_process.get('reasoning_chain', [])
            if not reasoning_chain:
                return 0.3, "推理链条为空，无法验证内部逻辑一致性"
            
            # 检查步骤间的逻辑衔接
            logical_gaps = 0
            total_steps = len(reasoning_chain)
            
            for i in range(total_steps - 1):
                current_step = reasoning_chain[i]
                next_step = reasoning_chain[i + 1]
                
                # 检查前提与结论的逻辑关系
                if not self._check_logical_connection(current_step, next_step):
                    logical_gaps += 1
            
            # 计算逻辑一致性分数
            consistency_score = 1.0 - (logical_gaps / max(1, total_steps - 1))
            
            analysis = f"推理链条包含{total_steps}步，检测到{logical_gaps}处逻辑断层"
            
            return consistency_score, analysis
            
        except Exception as e:
            logger.error(f"心秩序验证失败: {e}")
            return 0.5, f"验证过程出错: {str(e)}"
    
    def _validate_road_order(self, conclusion: str, context: Dict[str, Any]) -> Tuple[float, str]:
        """
        验证道秩序（外部规律一致性）
        
        验证结论是否与已知学科规律保持一致
        解决AI被动检索无法验证信息源真实性的问题
        """
        try:
            # 提取结论中的关键概念
            key_concepts = self._extract_key_concepts(conclusion)
            
            # 检查与各学科规律的冲突
            conflicts = []
            total_checks = 0
            
            for discipline, laws in self.knowledge_base['disciplinary_knowledge'].items():
                for law in laws:
                    total_checks += 1
                    if self._check_conflict_with_law(conclusion, law, discipline):
                        conflicts.append((law, discipline))
            
            # 计算道秩序一致性分数
            if total_checks == 0:
                return 0.5, "无法进行道秩序验证（无可用规律）"
            
            consistency_score = 1.0 - (len(conflicts) / total_checks)
            
            analysis = f"检查了{total_checks}条学科规律，发现{len(conflicts)}处冲突"
            if conflicts:
                analysis += f"，冲突规律: {', '.join([f'{law}({discipline})' for law, discipline in conflicts])}"
            
            return consistency_score, analysis
            
        except Exception as e:
            logger.error(f"道秩序验证失败: {e}")
            return 0.5, f"验证过程出错: {str(e)}"
    
    def _check_law_isomorphism(self, conclusion: str, context: Dict[str, Any]) -> Dict[str, float]:
        """
        检查规律同构性
        
        验证结论在因果律、系统论、阈值理论等维度的同构性
        基于用户提供的"生命是宇宙的美丽意外"幻觉检测示例
        """
        isomorphism_scores = {}
        
        # 1. 因果律维度检测
        causality_score = self._check_causality_isomorphism(conclusion, context)
        isomorphism_scores['causality'] = causality_score
        
        # 2. 系统论维度检测  
        system_score = self._check_system_theory_isomorphism(conclusion, context)
        isomorphism_scores['system_theory'] = system_score
        
        # 3. 阈值理论维度检测
        threshold_score = self._check_threshold_isomorphism(conclusion, context)
        isomorphism_scores['threshold_theory'] = threshold_score
        
        return isomorphism_scores
    
    def _check_causality_isomorphism(self, conclusion: str, context: Dict[str, Any]) -> float:
        """检查因果律维度的同构性"""
        # 示例：检测"生命是宇宙的美丽意外"这类忽略因果必然性的幻觉
        anti_causality_indicators = [
            '意外', '偶然', '随机', '巧合', '莫名其妙', '无缘无故'
        ]
        
        conclusion_lower = conclusion.lower()
        causality_violations = 0
        
        for indicator in anti_causality_indicators:
            if indicator in conclusion_lower:
                causality_violations += 1
        
        # 违反因果律的指标越多，分数越低
        return max(0.0, 1.0 - causality_violations * 0.2)
    
    def _check_system_theory_isomorphism(self, conclusion: str, context: Dict[str, Any]) -> float:
        """检查系统论维度的同构性"""
        # 检测是否忽略系统整体性和层次性
        system_violations = 0
        
        # 检查是否包含孤立看问题的表述
        isolation_indicators = [
            '孤立地', '单独地', '脱离上下文', '不考虑系统', '忽略整体'
        ]
        
        conclusion_lower = conclusion.lower()
        for indicator in isolation_indicators:
            if indicator in conclusion_lower:
                system_violations += 1
                break
        
        # 检查是否包含还原论倾向（过度简化复杂系统）
        reductionism_indicators = [
            '简单来说', '本质上就是', '归根结底', '不过就是'
        ]
        
        for indicator in reductionism_indicators:
            if indicator in conclusion_lower:
                system_violations += 1
                break
        
        return max(0.0, 1.0 - system_violations * 0.3)
    
    def _check_threshold_isomorphism(self, conclusion: str, context: Dict[str, Any]) -> float:
        """检查阈值理论维度的同构性"""
        # 检测是否忽略临界点和非线性响应
        threshold_violations = 0
        
        # 检查是否包含线性思维的表述
        linear_thinking_indicators = [
            '线性增长', '平稳发展', '没有突变', '渐进式', '量变到质变被忽略'
        ]
        
        conclusion_lower = conclusion.lower()
        for indicator in linear_thinking_indicators:
            if indicator in conclusion_lower:
                threshold_violations += 1
                break
        
        # 检查是否忽略相变和临界现象
        phase_transition_ignored = any(term in conclusion_lower for term in ['连续变化', '没有转折', '平稳过渡'])
        if phase_transition_ignored:
            threshold_violations += 1
        
        return max(0.0, 1.0 - threshold_violations * 0.25)
    
    def _calculate_hallucination_probability(self, heart_order_score: float, 
                                           road_order_score: float, 
                                           isomorphism_scores: Dict[str, float]) -> float:
        """计算幻觉概率"""
        # 加权计算总体一致性分数
        heart_weight = self.config['heart_order_weight']
        road_weight = self.config['road_order_weight']
        
        base_consistency = (heart_order_score * heart_weight + 
                           road_order_score * road_weight)
        
        # 规律同构性加权
        isomorphism_weights = {'causality': 0.4, 'system_theory': 0.3, 'threshold_theory': 0.3}
        isomorphism_score = sum(isomorphism_scores.get(dim, 0) * weight 
                              for dim, weight in isomorphism_weights.items())
        
        # 综合一致性分数
        overall_consistency = (base_consistency + isomorphism_score) / 2
        
        # 幻觉概率 = 1 - 一致性分数
        return max(0.0, min(1.0, 1.0 - overall_consistency))
    
    def _generate_suggestions(self, hallucination_probability: float, 
                            isomorphism_scores: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if hallucination_probability > 0.7:
            suggestions.append("⚠️ 高概率幻觉：建议重新验证信息源和推理过程")
        
        if isomorphism_scores.get('causality', 1.0) < 0.6:
            suggestions.append("🔍 因果律维度不一致：检查结论是否忽略必然因果关系")
        
        if isomorphism_scores.get('system_theory', 1.0) < 0.6:
            suggestions.append("🌐 系统论维度不一致：考虑结论在整体系统中的位置")
        
        if isomorphism_scores.get('threshold_theory', 1.0) < 0.6:
            suggestions.append("⚡ 阈值理论维度不一致：检查是否忽略临界点和非线性响应")
        
        if not suggestions:
            suggestions.append("✅ 结论在多个维度表现一致，可信度较高")
        
        return suggestions
    
    # 辅助方法
    def _check_logical_connection(self, current_step: Dict, next_step: Dict) -> bool:
        """检查推理步骤间的逻辑连接"""
        # 简化实现：检查前提和结论的关键词关联
        current_conclusion = current_step.get('conclusion', '').lower()
        next_premise = next_step.get('premise', '').lower()
        
        # 简单的关键词匹配检查
        common_words = set(current_conclusion.split()) & set(next_premise.split())
        return len(common_words) > 0
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """提取文本中的关键概念"""
        # 简化实现：提取名词性短语
        import re
        # 匹配中文名词短语（简化版）
        noun_phrases = re.findall(r'[\u4e00-\u9fff]+的[\u4e00-\u9fff]+', text)
        # 添加单个名词
        nouns = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        return list(set(noun_phrases + nouns))
    
    def _check_conflict_with_law(self, conclusion: str, law: str, discipline: str) -> bool:
        """检查结论是否与特定规律冲突"""
        conclusion_lower = conclusion.lower()
        law_lower = law.lower()
        
        # 简化冲突检测逻辑
        conflict_indicators = {
            'physics': ['违反物理定律', '不可能', '违背能量守恒', '超光速'],
            'biology': ['违背进化论', '违反遗传规律', '不可能的生物特征'],
            'sociology': ['违反社会规律', '不可能的社会现象', '违背历史规律']
        }
        
        indicators = conflict_indicators.get(discipline, [])
        for indicator in indicators:
            if indicator in conclusion_lower:
                return True
        
        return False
    
    def get_detection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取检测历史"""
        return self.detection_history[-limit:]
    
    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            'total_detections': len(self.detection_history),
            'recent_hallucination_rate': self._calculate_recent_hallucination_rate(),
            'knowledge_base_size': {
                'causality_principles': len(self.knowledge_base['causality_principles']),
                'system_theory_principles': len(self.knowledge_base['system_theory_principles']),
                'threshold_theory_principles': len(self.knowledge_base['threshold_theory_principles']),
                'disciplinary_knowledge': sum(len(laws) for laws in self.knowledge_base['disciplinary_knowledge'].values())
            }
        }
    
    def _calculate_recent_hallucination_rate(self) -> float:
        """计算近期幻觉率"""
        if not self.detection_history:
            return 0.0
        
        recent_detections = self.detection_history[-10:]  # 最近10次检测
        hallucination_count = sum(1 for d in recent_detections 
                                if d['hallucination_probability'] > self.config['hallucination_threshold'])
        
        return hallucination_count / len(recent_detections)

# 测试函数
def test_cognitive_barrier_break_engine():
    """测试认知破障引擎"""
    engine = CognitiveBarrierBreakEngine()
    
    # 测试用例1：可能的AI幻觉（类似"生命是宇宙的美丽意外"）
    test_conclusion = "生命是宇宙中的一个美丽意外，完全随机产生"
    reasoning_process = {
        'reasoning_chain': [
            {'premise': '宇宙中存在生命', 'conclusion': '生命是随机产生的'},
            {'premise': '生命是随机产生的', 'conclusion': '生命是宇宙的意外'}
        ]
    }
    context = {'domain': 'cosmology', 'source_reliability': 0.3}
    
    result = engine.detect_hallucination(test_conclusion, reasoning_process, context)
    print("测试用例1 - 可能的AI幻觉:")
    print(f"结论: {test_conclusion}")
    print(f"幻觉检测结果: {result}")
    print()
    
    # 测试用例2：合理的结论
    test_conclusion2 = "生命是宇宙自组织优化的必然结果，符合系统演化规律"
    reasoning_process2 = {
        'reasoning_chain': [
            {'premise': '宇宙是秩序的', 'conclusion': '宇宙具有自组织能力'},
            {'premise': '宇宙具有自组织能力', 'conclusion': '生命是自组织优化的产物'}
        ]
    }
    context2 = {'domain': 'cosmology', 'source_reliability': 0.8}
    
    result2 = engine.detect_hallucination(test_conclusion2, reasoning_process2, context2)
    print("测试用例2 - 合理的结论:")
    print(f"结论: {test_conclusion2}")
    print(f"幻觉检测结果: {result2}")

if __name__ == "__main__":
    test_cognitive_barrier_break_engine()