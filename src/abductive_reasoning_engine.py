# @self-expose: {"id": "abductive_reasoning_engine", "name": "Abductive Reasoning Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Abductive Reasoning Engine功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
溯因推理引擎
实现智能体系统的溯因推理能力
支持基于观察结果推断最可能的解释或原因
"""

import os
import sys
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

class AbductiveConfig:
    """溯因推理配置类"""
    
    def __init__(self):
        self.reasoning_methods = ['causal_inference', 'pattern_matching', 'hypothesis_generation']
        self.max_hypotheses = 5
        self.confidence_threshold = 0.7
        self.evidence_weight = {
            'direct': 1.0,
            'indirect': 0.7,
            'circumstantial': 0.5
        }
        self.temporal_constraints = True
        self.causal_chains_max_length = 3

class ReasoningResult:
    """推理结果类"""
    
    def __init__(self, success: bool = True, data: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error
        }

class Hypothesis:
    """假设类"""
    
    def __init__(self, description: str, confidence: float, evidence: List[Dict[str, Any]] = None):
        self.description = description
        self.confidence = confidence
        self.evidence = evidence or []
        self.supporting_factors = []
        self.contradicting_factors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'description': self.description,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'supporting_factors': self.supporting_factors,
            'contradicting_factors': self.contradicting_factors
        }

class AbductiveReasoningEngine:
    """溯因推理引擎核心类"""
    
    def __init__(self, config: AbductiveConfig = None):
        self.config = config or AbductiveConfig()
        self.knowledge_base = {}
        self.causal_models = {}
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化知识库"""
        try:
            # 基础因果知识
            self.knowledge_base = {
                'causal_patterns': {
                    'cause_effect': ['如果A发生，那么B可能发生'],
                    'temporal_sequence': ['A在B之前发生，可能表示因果关系'],
                    'correlation': ['A和B同时出现，可能有共同原因']
                },
                'common_explanations': {
                    'system_failure': ['硬件故障', '软件错误', '网络问题', '配置错误'],
                    'human_error': ['操作失误', '理解错误', '注意力分散'],
                    'environmental': ['温度变化', '湿度影响', '电源波动']
                },
                'reasoning_rules': {
                    'simplicity': ['最简单的解释通常最可能'],
                    'consistency': ['解释应与已知事实一致'],
                    'completeness': ['解释应涵盖所有观察结果']
                }
            }
            
            # 因果模型
            self.causal_models = {
                'technical_system': self._create_technical_system_model(),
                'human_behavior': self._create_human_behavior_model(),
                'natural_phenomena': self._create_natural_phenomena_model()
            }
            
            print("溯因推理引擎知识库初始化成功")
            
        except Exception as e:
            print(f"知识库初始化失败: {e}")
    
    def _create_technical_system_model(self) -> Dict[str, Any]:
        """创建技术系统因果模型"""
        return {
            'components': ['硬件', '软件', '网络', '配置', '数据'],
            'failure_modes': {
                '硬件': ['过热', '老化', '物理损坏', '电源问题'],
                '软件': ['bug', '内存泄漏', '兼容性问题', '版本冲突'],
                '网络': ['延迟', '丢包', '带宽不足', '连接中断'],
                '配置': ['参数错误', '权限问题', '路径错误', '环境变量']
            },
            'causal_relationships': {
                '硬件故障': ['系统崩溃', '性能下降', '数据丢失'],
                '软件错误': ['功能异常', '数据错误', '安全漏洞'],
                '网络问题': ['连接超时', '数据传输失败', '同步错误']
            }
        }
    
    def _create_human_behavior_model(self) -> Dict[str, Any]:
        """创建人类行为因果模型"""
        return {
            'factors': ['知识', '技能', '态度', '情绪', '环境'],
            'error_types': {
                '知识不足': ['概念错误', '流程不熟', '标准不了解'],
                '技能欠缺': ['操作不熟练', '判断失误', '反应迟钝'],
                '态度问题': ['粗心大意', '过度自信', '缺乏责任心'],
                '情绪影响': ['压力过大', '疲劳', '分心']
            },
            'behavioral_patterns': {
                '错误操作': ['误点击', '参数设置错误', '流程跳过'],
                '判断失误': ['风险评估错误', '优先级判断错误'],
                '沟通问题': ['信息传达不清', '理解偏差']
            }
        }
    
    def _create_natural_phenomena_model(self) -> Dict[str, Any]:
        """创建自然现象因果模型"""
        return {
            'environmental_factors': ['温度', '湿度', '气压', '电磁场'],
            'natural_events': ['天气变化', '季节交替', '昼夜循环'],
            'impact_patterns': {
                '温度变化': ['设备性能波动', '材料膨胀收缩'],
                '湿度影响': ['电路短路', '材料腐蚀'],
                '电磁干扰': ['信号干扰', '数据错误']
            }
        }
    
    def causal_inference(self, observations: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Hypothesis]:
        """因果推理：基于观察结果推断可能的原因"""
        try:
            hypotheses = []
            
            # 分析观察结果
            observation_analysis = self._analyze_observations(observations)
            
            # 根据上下文选择合适的因果模型
            relevant_models = self._select_relevant_models(context)
            
            # 生成可能的因果链
            causal_chains = self._generate_causal_chains(observation_analysis, relevant_models)
            
            # 评估每个因果链的合理性
            for chain in causal_chains[:self.config.max_hypotheses]:
                hypothesis = self._evaluate_causal_chain(chain, observation_analysis)
                if hypothesis.confidence >= self.config.confidence_threshold:
                    hypotheses.append(hypothesis)
            
            # 按置信度排序
            hypotheses.sort(key=lambda x: x.confidence, reverse=True)
            
            return hypotheses
            
        except Exception as e:
            print(f"因果推理失败: {e}")
            return []
    
    def pattern_matching(self, observations: List[Dict[str, Any]], patterns: List[Dict[str, Any]] = None) -> List[Hypothesis]:
        """模式匹配：将观察结果与已知模式进行匹配"""
        try:
            hypotheses = []
            
            if not patterns:
                patterns = self._get_default_patterns()
            
            # 提取观察特征
            observation_features = self._extract_observation_features(observations)
            
            # 与模式进行匹配
            for pattern in patterns:
                match_score = self._calculate_pattern_match(observation_features, pattern)
                
                if match_score >= self.config.confidence_threshold:
                    hypothesis = Hypothesis(
                        description=f"符合模式: {pattern.get('name', '未知模式')}",
                        confidence=match_score,
                        evidence=observations
                    )
                    
                    # 分析支持因素
                    supporting_factors = self._analyze_supporting_factors(observation_features, pattern)
                    hypothesis.supporting_factors = supporting_factors
                    
                    hypotheses.append(hypothesis)
            
            # 按匹配度排序
            hypotheses.sort(key=lambda x: x.confidence, reverse=True)
            
            return hypotheses[:self.config.max_hypotheses]
            
        except Exception as e:
            print(f"模式匹配失败: {e}")
            return []
    
    def hypothesis_generation(self, observations: List[Dict[str, Any]], constraints: Dict[str, Any] = None) -> List[Hypothesis]:
        """假设生成：基于观察结果生成可能的解释"""
        try:
            hypotheses = []
            
            # 分析观察结果的特性
            observation_properties = self._analyze_observation_properties(observations)
            
            # 生成可能的解释空间
            explanation_space = self._generate_explanation_space(observation_properties, constraints)
            
            # 评估每个解释的合理性
            for explanation in explanation_space[:self.config.max_hypotheses * 2]:  # 生成更多候选
                hypothesis = self._evaluate_explanation(explanation, observations)
                
                if hypothesis.confidence >= self.config.confidence_threshold / 2:  # 降低阈值以获取更多假设
                    hypotheses.append(hypothesis)
            
            # 按置信度排序并限制数量
            hypotheses.sort(key=lambda x: x.confidence, reverse=True)
            
            return hypotheses[:self.config.max_hypotheses]
            
        except Exception as e:
            print(f"假设生成失败: {e}")
            return []
    
    def _analyze_observations(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析观察结果"""
        analysis = {
            'events': [],
            'timeline': [],
            'key_factors': [],
            'anomalies': []
        }
        
        for obs in observations:
            # 提取事件信息
            if 'event' in obs:
                analysis['events'].append(obs['event'])
            
            # 提取时间信息
            if 'timestamp' in obs:
                analysis['timeline'].append({
                    'event': obs.get('description', '未知事件'),
                    'timestamp': obs['timestamp']
                })
            
            # 识别关键因素
            if 'factors' in obs:
                analysis['key_factors'].extend(obs['factors'])
            
            # 检测异常
            if 'anomaly' in obs and obs['anomaly']:
                analysis['anomalies'].append(obs)
        
        # 按时间排序时间线
        analysis['timeline'].sort(key=lambda x: x['timestamp'])
        
        return analysis
    
    def _select_relevant_models(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """选择相关的因果模型"""
        relevant_models = []
        
        if context:
            # 根据上下文关键词选择模型
            context_text = str(context).lower()
            
            if any(word in context_text for word in ['技术', '系统', '软件', '硬件']):
                relevant_models.append(self.causal_models['technical_system'])
            
            if any(word in context_text for word in ['人', '操作', '行为', '错误']):
                relevant_models.append(self.causal_models['human_behavior'])
            
            if any(word in context_text for word in ['环境', '自然', '天气', '温度']):
                relevant_models.append(self.causal_models['natural_phenomena'])
        
        # 如果没有匹配的上下文，返回所有模型
        if not relevant_models:
            relevant_models = list(self.causal_models.values())
        
        return relevant_models
    
    def _generate_causal_chains(self, analysis: Dict[str, Any], models: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """生成可能的因果链"""
        causal_chains = []
        
        # 基于异常事件生成因果链
        for anomaly in analysis['anomalies']:
            for model in models:
                chains = self._generate_chains_from_anomaly(anomaly, model)
                causal_chains.extend(chains)
        
        # 基于时间序列生成因果链
        if len(analysis['timeline']) > 1:
            temporal_chains = self._generate_temporal_chains(analysis['timeline'])
            causal_chains.extend(temporal_chains)
        
        return causal_chains
    
    def _generate_chains_from_anomaly(self, anomaly: Dict[str, Any], model: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """从异常生成因果链"""
        chains = []
        
        # 获取可能的根本原因
        root_causes = self._get_possible_root_causes(anomaly, model)
        
        for cause in root_causes:
            chain = [
                {'type': 'root_cause', 'description': cause, 'confidence': 0.8},
                {'type': 'intermediate', 'description': '导致系统异常', 'confidence': 0.9},
                {'type': 'effect', 'description': anomaly.get('description', '异常事件'), 'confidence': 1.0}
            ]
            chains.append(chain)
        
        return chains
    
    def _get_possible_root_causes(self, anomaly: Dict[str, Any], model: Dict[str, Any]) -> List[str]:
        """获取可能的根本原因"""
        causes = []
        
        # 根据异常描述匹配故障模式
        anomaly_desc = str(anomaly.get('description', '')).lower()
        
        for component, failure_modes in model.get('failure_modes', {}).items():
            for mode in failure_modes:
                if any(word in anomaly_desc for word in mode.lower().split()):
                    causes.append(f"{component}的{mode}")
        
        # 如果没有匹配，返回通用原因
        if not causes:
            causes = ['未知系统故障', '配置错误', '外部干扰']
        
        return causes[:3]  # 限制返回数量
    
    def _generate_temporal_chains(self, timeline: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """基于时间序列生成因果链"""
        chains = []
        
        if len(timeline) < 2:
            return chains
        
        # 生成连续事件的因果链
        for i in range(len(timeline) - 1):
            event1 = timeline[i]
            event2 = timeline[i + 1]
            
            chain = [
                {'type': 'cause', 'description': event1['event'], 'timestamp': event1['timestamp']},
                {'type': 'effect', 'description': event2['event'], 'timestamp': event2['timestamp']}
            ]
            
            chains.append(chain)
        
        return chains
    
    def _evaluate_causal_chain(self, chain: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Hypothesis:
        """评估因果链的合理性"""
        try:
            # 计算链的置信度
            confidence = self._calculate_chain_confidence(chain)
            
            # 检查与观察的一致性
            consistency_score = self._check_consistency(chain, analysis)
            
            # 综合置信度
            final_confidence = confidence * consistency_score
            
            # 生成假设描述
            description = self._generate_chain_description(chain)
            
            hypothesis = Hypothesis(description, final_confidence)
            
            # 收集证据
            hypothesis.evidence = analysis['anomalies'] if analysis['anomalies'] else analysis['events'][:3]
            
            return hypothesis
            
        except Exception as e:
            print(f"因果链评估失败: {e}")
            return Hypothesis("评估失败", 0.0)
    
    def _calculate_chain_confidence(self, chain: List[Dict[str, Any]]) -> float:
        """计算因果链置信度"""
        if not chain:
            return 0.0
        
        # 基于链长度和节点置信度计算
        length_factor = 1.0 / len(chain)  # 链越短越可信
        node_confidence = np.mean([node.get('confidence', 0.5) for node in chain])
        
        return length_factor * node_confidence
    
    def _check_consistency(self, chain: List[Dict[str, Any]], analysis: Dict[str, Any]) -> float:
        """检查与观察的一致性"""
        consistency_score = 1.0
        
        # 检查时间一致性
        if self.config.temporal_constraints and analysis['timeline']:
            temporal_score = self._check_temporal_consistency(chain, analysis['timeline'])
            consistency_score *= temporal_score
        
        # 检查逻辑一致性
        logic_score = self._check_logical_consistency(chain)
        consistency_score *= logic_score
        
        return consistency_score
    
    def _check_temporal_consistency(self, chain: List[Dict[str, Any]], timeline: List[Dict[str, Any]]) -> float:
        """检查时间一致性"""
        # 简化检查：确保因果链的时间顺序合理
        chain_timestamps = [node.get('timestamp') for node in chain if 'timestamp' in node]
        
        if len(chain_timestamps) > 1:
            # 检查时间是否递增
            if sorted(chain_timestamps) == chain_timestamps:
                return 1.0
            else:
                return 0.5  # 时间顺序有问题
        
        return 0.8  # 时间信息不足，给予中等分数
    
    def _check_logical_consistency(self, chain: List[Dict[str, Any]]) -> float:
        """检查逻辑一致性"""
        # 简化检查：确保因果链逻辑合理
        if len(chain) < 2:
            return 0.6  # 链太短
        
        # 检查因果关系是否合理
        cause_effect_pairs = []
        for i in range(len(chain) - 1):
            cause = chain[i].get('description', '').lower()
            effect = chain[i + 1].get('description', '').lower()
            cause_effect_pairs.append((cause, effect))
        
        # 简单的合理性检查
        reasonable_pairs = 0
        for cause, effect in cause_effect_pairs:
            if any(word in cause for word in ['故障', '错误', '问题']) and any(word in effect for word in ['异常', '失败', '错误']):
                reasonable_pairs += 1
            elif '导致' in cause or '引起' in cause:
                reasonable_pairs += 1
            else:
                reasonable_pairs += 0.5  # 中等合理
        
        return reasonable_pairs / len(cause_effect_pairs) if cause_effect_pairs else 0.5
    
    def _generate_chain_description(self, chain: List[Dict[str, Any]]) -> str:
        """生成因果链描述"""
        if not chain:
            return "未知原因"
        
        descriptions = []
        for node in chain:
            desc = node.get('description', '未知')
            if 'root_cause' in node.get('type', ''):
                descriptions.append(f"根本原因: {desc}")
            elif 'effect' in node.get('type', ''):
                descriptions.append(f"导致: {desc}")
            else:
                descriptions.append(desc)
        
        return " -> ".join(descriptions)
    
    def _get_default_patterns(self) -> List[Dict[str, Any]]:
        """获取默认模式"""
        return [
            {
                'name': '系统故障模式',
                'features': ['性能下降', '错误日志', '服务中断'],
                'explanation': '硬件或软件故障导致系统异常'
            },
            {
                'name': '网络问题模式', 
                'features': ['连接超时', '数据传输慢', '丢包'],
                'explanation': '网络连接问题影响系统性能'
            },
            {
                'name': '配置错误模式',
                'features': ['参数错误', '权限问题', '路径错误'],
                'explanation': '系统配置不正确导致功能异常'
            }
        ]
    
    def _extract_observation_features(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取观察特征"""
        features = {
            'keywords': [],
            'event_types': [],
            'severity_levels': [],
            'temporal_pattern': ''
        }
        
        for obs in observations:
            # 提取关键词
            if 'description' in obs:
                features['keywords'].extend(obs['description'].split()[:5])
            
            # 提取事件类型
            if 'type' in obs:
                features['event_types'].append(obs['type'])
            
            # 提取严重程度
            if 'severity' in obs:
                features['severity_levels'].append(obs['severity'])
        
        # 分析时间模式
        if len(observations) > 1:
            features['temporal_pattern'] = self._analyze_temporal_pattern(observations)
        
        return features
    
    def _analyze_temporal_pattern(self, observations: List[Dict[str, Any]]) -> str:
        """分析时间模式"""
        timestamps = [obs.get('timestamp') for obs in observations if 'timestamp' in obs]
        
        if len(timestamps) < 2:
            return '孤立事件'
        
        # 简化分析
        return '连续事件' if len(timestamps) > 3 else '偶发事件'
    
    def _calculate_pattern_match(self, features: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """计算模式匹配度"""
        match_score = 0.0
        total_weight = 0
        
        # 关键词匹配
        if 'features' in pattern:
            pattern_features = pattern['features']
            keyword_matches = 0
            
            for pattern_feature in pattern_features:
                for keyword in features['keywords']:
                    if pattern_feature.lower() in keyword.lower():
                        keyword_matches += 1
                        break
            
            keyword_score = keyword_matches / len(pattern_features) if pattern_features else 0
            match_score += keyword_score * 0.6
            total_weight += 0.6
        
        # 事件类型匹配
        if features['event_types']:
            # 简化匹配逻辑
            event_score = min(len(features['event_types']) / 3, 1.0) * 0.4
            match_score += event_score
            total_weight += 0.4
        
        return match_score / total_weight if total_weight > 0 else 0
    
    def _analyze_supporting_factors(self, features: Dict[str, Any], pattern: Dict[str, Any]) -> List[str]:
        """分析支持因素"""
        factors = []
        
        # 基于匹配特征生成支持因素
        if 'features' in pattern:
            matched_features = []
            for pattern_feature in pattern['features']:
                for keyword in features['keywords']:
                    if pattern_feature.lower() in keyword.lower():
                        matched_features.append(pattern_feature)
                        break
            
            if matched_features:
                factors.append(f"匹配特征: {', '.join(matched_features)}")
        
        # 基于事件类型
        if features['event_types']:
            factors.append(f"事件类型: {', '.join(set(features['event_types']))}")
        
        # 基于时间模式
        if features['temporal_pattern']:
            factors.append(f"时间模式: {features['temporal_pattern']}")
        
        return factors
    
    def _analyze_observation_properties(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析观察结果属性"""
        properties = {
            'complexity': len(observations),  # 事件数量
            'diversity': len(set(obs.get('type', '未知') for obs in observations)),  # 事件类型多样性
            'severity': np.mean([obs.get('severity', 5) for obs in observations]) if observations else 5,  # 平均严重程度
            'temporal_density': self._calculate_temporal_density(observations)  # 时间密度
        }
        
        return properties
    
    def _calculate_temporal_density(self, observations: List[Dict[str, Any]]) -> float:
        """计算时间密度"""
        timestamps = [obs.get('timestamp') for obs in observations if 'timestamp' in obs]
        
        if len(timestamps) < 2:
            return 0.0
        
        # 计算时间间隔的倒数作为密度指标
        sorted_timestamps = sorted(timestamps)
        intervals = [sorted_timestamps[i+1] - sorted_timestamps[i] for i in range(len(sorted_timestamps)-1)]
        
        if intervals:
            avg_interval = np.mean(intervals)
            return 1.0 / avg_interval if avg_interval > 0 else 1.0
        
        return 0.0
    
    def _generate_explanation_space(self, properties: Dict[str, Any], constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """生成解释空间"""
        explanations = []
        
        # 基于复杂度生成解释
        if properties['complexity'] > 5:
            explanations.append({'type': 'systemic', 'description': '系统性故障', 'confidence': 0.7})
        
        if properties['diversity'] > 2:
            explanations.append({'type': 'multi_cause', 'description': '多因素共同作用', 'confidence': 0.6})
        
        if properties['severity'] > 7:
            explanations.append({'type': 'critical', 'description': '严重故障', 'confidence': 0.8})
        
        if properties['temporal_density'] > 0.5:
            explanations.append({'type': 'cascade', 'description': '连锁反应', 'confidence': 0.6})
        
        # 添加通用解释
        explanations.extend([
            {'type': 'single_point', 'description': '单点故障', 'confidence': 0.5},
            {'type': 'external', 'description': '外部干扰', 'confidence': 0.4},
            {'type': 'random', 'description': '随机事件', 'confidence': 0.3}
        ])
        
        return explanations
    
    def _evaluate_explanation(self, explanation: Dict[str, Any], observations: List[Dict[str, Any]]) -> Hypothesis:
        """评估解释的合理性"""
        base_confidence = explanation.get('confidence', 0.5)
        
        # 基于观察结果调整置信度
        observation_factors = self._calculate_observation_factors(observations, explanation)
        
        # 综合置信度
        final_confidence = base_confidence * observation_factors
        
        hypothesis = Hypothesis(explanation['description'], final_confidence, observations)
        
        # 添加支持因素
        hypothesis.supporting_factors = [f"解释类型: {explanation['type']}", f"基础置信度: {base_confidence}"]
        
        return hypothesis
    
    def _calculate_observation_factors(self, observations: List[Dict[str, Any]], explanation: Dict[str, Any]) -> float:
        """计算观察结果对解释的支持度"""
        factor = 1.0
        
        # 基于解释类型调整因子
        exp_type = explanation.get('type', '')
        
        if exp_type == 'systemic' and len(observations) > 3:
            factor *= 1.2
        
        if exp_type == 'critical' and any(obs.get('severity', 0) > 8 for obs in observations):
            factor *= 1.3
        
        if exp_type == 'cascade' and len(observations) > 2:
            factor *= 1.1
        
        return min(factor, 2.0)  # 限制最大调整幅度
    
    def reason(self, reasoning_method: str, observations: List[Dict[str, Any]], 
               context: Dict[str, Any] = None, constraints: Dict[str, Any] = None) -> ReasoningResult:
        """溯因推理主方法"""
        try:
            if reasoning_method not in self.config.reasoning_methods:
                return ReasoningResult(success=False, error=f"不支持的推理方法: {reasoning_method}")
            
            hypotheses = []
            
            if reasoning_method == 'causal_inference':
                hypotheses = self.causal_inference(observations, context)
            elif reasoning_method == 'pattern_matching':
                hypotheses = self.pattern_matching(observations)
            elif reasoning_method == 'hypothesis_generation':
                hypotheses = self.hypothesis_generation(observations, constraints)
            
            # 转换为字典格式
            hypotheses_dict = [hypo.to_dict() for hypo in hypotheses]
            
            result_data = {
                'reasoning_method': reasoning_method,
                'hypotheses': hypotheses_dict,
                'total_hypotheses': len(hypotheses),
                'top_hypothesis': hypotheses_dict[0] if hypotheses_dict else None
            }
            
            return ReasoningResult(success=True, data=result_data)
            
        except Exception as e:
            return ReasoningResult(success=False, error=f"溯因推理失败: {str(e)}")

class AbductiveReasoningTool:
    """溯因推理工具类（用于智能体集成）"""
    
    def __init__(self):
        self.engine = AbductiveReasoningEngine()
        self.tool_name = "AbductiveReasoningEngine"
        self.tool_description = "溯因推理引擎，支持基于观察结果推断最可能的解释或原因"
        self.tool_usage = "用于分析复杂问题，生成合理的解释假设"
    
    def call(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用溯因推理工具"""
        try:
            if operation == "reason":
                reasoning_method = parameters.get('reasoning_method', 'causal_inference')
                observations = parameters.get('observations', [])
                context = parameters.get('context', {})
                constraints = parameters.get('constraints', {})
                
                result = self.engine.reason(reasoning_method, observations, context, constraints)
                return result.to_dict()
                
            elif operation == "causal_inference":
                observations = parameters.get('observations', [])
                context = parameters.get('context', {})
                
                hypotheses = self.engine.causal_inference(observations, context)
                hypotheses_dict = [hypo.to_dict() for hypo in hypotheses]
                
                return {
                    'success': True, 
                    'data': {
                        'reasoning_method': 'causal_inference',
                        'hypotheses': hypotheses_dict
                    }
                }
                
            elif operation == "pattern_matching":
                observations = parameters.get('observations', [])
                patterns = parameters.get('patterns')
                
                hypotheses = self.engine.pattern_matching(observations, patterns)
                hypotheses_dict = [hypo.to_dict() for hypo in hypotheses]
                
                return {
                    'success': True, 
                    'data': {
                        'reasoning_method': 'pattern_matching',
                        'hypotheses': hypotheses_dict
                    }
                }
                
            elif operation == "hypothesis_generation":
                observations = parameters.get('observations', [])
                constraints = parameters.get('constraints', {})
                
                hypotheses = self.engine.hypothesis_generation(observations, constraints)
                hypotheses_dict = [hypo.to_dict() for hypo in hypotheses]
                
                return {
                    'success': True, 
                    'data': {
                        'reasoning_method': 'hypothesis_generation',
                        'hypotheses': hypotheses_dict
                    }
                }
                
            else:
                return {'success': False, 'error': f'未知操作: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': f'工具调用失败: {str(e)}'}

# 测试代码
if __name__ == "__main__":
    # 创建溯因推理引擎实例
    reasoning_engine = AbductiveReasoningEngine()
    
    # 测试观察结果
    test_observations = [
        {
            'description': '系统响应时间变慢',
            'timestamp': '2024-01-01 10:00:00',
            'severity': 6,
            'type': 'performance'
        },
        {
            'description': '数据库连接错误',
            'timestamp': '2024-01-01 10:05:00', 
            'severity': 8,
            'type': 'error'
        },
        {
            'description': '内存使用率过高',
            'timestamp': '2024-01-01 10:10:00',
            'severity': 7,
            'type': 'resource'
        }
    ]
    
    # 测试因果推理
    result = reasoning_engine.causal_inference(test_observations)
    print("因果推理结果:")
    for i, hypothesis in enumerate(result):
        print(f"假设 {i+1}: {hypothesis.description} (置信度: {hypothesis.confidence:.2f})")
    
    # 测试模式匹配
    result = reasoning_engine.pattern_matching(test_observations)
    print("\n模式匹配结果:")
    for i, hypothesis in enumerate(result):
        print(f"假设 {i+1}: {hypothesis.description} (置信度: {hypothesis.confidence:.2f})")
    
    # 测试主推理方法
    reasoning_result = reasoning_engine.reason('causal_inference', test_observations)
    print("\n主推理方法结果:")
    print(json.dumps(reasoning_result.to_dict(), indent=2, ensure_ascii=False))