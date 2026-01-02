#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分层学习引擎
实现智能体系统的分层学习能力
支持从经验中学习并构建层次化的知识结构
"""
# @self-expose: {"id": "hierarchical_learning_engine", "name": "Hierarchical Learning Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Hierarchical Learning Engine功能"]}}

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

class LearningConfig:
    """学习配置类"""
    
    def __init__(self):
        self.learning_modes = ['supervised', 'unsupervised', 'reinforcement']
        self.hierarchy_levels = 3
        self.learning_rate = 0.1
        self.exploration_rate = 0.3
        self.memory_capacity = 1000
        self.knowledge_retention = 0.9

class LearningResult:
    """学习结果类"""
    
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

class KnowledgeNode:
    """知识节点类"""
    
    def __init__(self, concept: str, level: int, confidence: float = 0.5):
        self.concept = concept
        self.level = level
        self.confidence = confidence
        self.parents = []
        self.children = []
        self.experiences = []
        self.associations = {}
    
    def add_experience(self, experience: Dict[str, Any]):
        """添加经验"""
        self.experiences.append(experience)
        # 限制经验数量
        if len(self.experiences) > 100:
            self.experiences = self.experiences[-50:]  # 保留最近50条
    
    def update_confidence(self, success: bool):
        """更新置信度"""
        if success:
            self.confidence = min(1.0, self.confidence + 0.1)
        else:
            self.confidence = max(0.0, self.confidence - 0.1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'concept': self.concept,
            'level': self.level,
            'confidence': self.confidence,
            'experience_count': len(self.experiences),
            'parent_count': len(self.parents),
            'child_count': len(self.children)
        }

class HierarchicalLearningEngine:
    """分层学习引擎核心类"""
    
    def __init__(self, config: LearningConfig = None):
        self.config = config or LearningConfig()
        self.knowledge_graph = {}
        self.experience_buffer = []
        self.learning_history = []
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化知识库"""
        try:
            # 创建基础概念节点
            basic_concepts = [
                ('问题识别', 1),
                ('解决方案', 1), 
                ('错误分析', 1),
                ('模式识别', 2),
                ('策略选择', 2),
                ('结果评估', 2),
                ('抽象推理', 3),
                ('元认知', 3)
            ]
            
            for concept, level in basic_concepts:
                self.knowledge_graph[concept] = KnowledgeNode(concept, level)
            
            # 建立基础关联
            self._create_basic_associations()
            
            print("分层学习引擎知识库初始化成功")
            
        except Exception as e:
            print(f"知识库初始化失败: {e}")
    
    def _create_basic_associations(self):
        """创建基础关联"""
        # 问题识别 -> 解决方案
        if '问题识别' in self.knowledge_graph and '解决方案' in self.knowledge_graph:
            self.knowledge_graph['问题识别'].associations['解决方案'] = 0.8
        
        # 错误分析 -> 问题识别
        if '错误分析' in self.knowledge_graph and '问题识别' in self.knowledge_graph:
            self.knowledge_graph['错误分析'].associations['问题识别'] = 0.9
        
        # 模式识别 -> 策略选择
        if '模式识别' in self.knowledge_graph and '策略选择' in self.knowledge_graph:
            self.knowledge_graph['模式识别'].associations['策略选择'] = 0.7
        
        # 结果评估 -> 策略选择
        if '结果评估' in self.knowledge_graph and '策略选择' in self.knowledge_graph:
            self.knowledge_graph['结果评估'].associations['策略选择'] = 0.6
    
    def supervised_learning(self, training_data: List[Dict[str, Any]]) -> LearningResult:
        """监督学习：基于标注数据学习"""
        try:
            learned_concepts = []
            
            for data_point in training_data:
                # 提取特征和标签
                features = data_point.get('features', {})
                label = data_point.get('label', '')
                
                if label:
                    # 创建或更新概念节点
                    concept_node = self._get_or_create_concept(label, 1)
                    
                    # 添加经验
                    experience = {
                        'type': 'supervised',
                        'features': features,
                        'label': label,
                        'timestamp': data_point.get('timestamp', '未知时间')
                    }
                    concept_node.add_experience(experience)
                    
                    # 更新关联
                    self._update_associations_from_features(concept_node, features)
                    
                    learned_concepts.append(concept_node.concept)
            
            return LearningResult(success=True, data={
                'learning_mode': 'supervised',
                'learned_concepts': learned_concepts,
                'total_data_points': len(training_data)
            })
            
        except Exception as e:
            return LearningResult(success=False, error=f"监督学习失败: {str(e)}")
    
    def unsupervised_learning(self, unlabeled_data: List[Dict[str, Any]]) -> LearningResult:
        """无监督学习：发现数据中的模式"""
        try:
            discovered_patterns = []
            
            for data_point in unlabeled_data:
                features = data_point.get('features', {})
                
                # 聚类分析
                clusters = self._cluster_features(features)
                
                # 模式发现
                patterns = self._discover_patterns(clusters)
                
                for pattern in patterns:
                    # 创建模式节点
                    pattern_node = self._get_or_create_concept(pattern, 2)
                    
                    # 添加经验
                    experience = {
                        'type': 'unsupervised',
                        'features': features,
                        'pattern': pattern,
                        'timestamp': data_point.get('timestamp', '未知时间')
                    }
                    pattern_node.add_experience(experience)
                    
                    discovered_patterns.append(pattern)
            
            return LearningResult(success=True, data={
                'learning_mode': 'unsupervised',
                'discovered_patterns': discovered_patterns,
                'total_data_points': len(unlabeled_data)
            })
            
        except Exception as e:
            return LearningResult(success=False, error=f"无监督学习失败: {str(e)}")
    
    def reinforcement_learning(self, experience: Dict[str, Any]) -> LearningResult:
        """强化学习：基于奖励信号学习"""
        try:
            state = experience.get('state', {})
            action = experience.get('action', '')
            reward = experience.get('reward', 0)
            next_state = experience.get('next_state', {})
            
            # 创建或获取状态节点
            state_concept = self._extract_state_concept(state)
            state_node = self._get_or_create_concept(state_concept, 2)
            
            # 创建或获取动作节点
            action_node = self._get_or_create_concept(action, 1)
            
            # 更新Q值（简化版）
            q_value = self._update_q_value(state_node, action_node, reward, next_state)
            
            # 添加经验
            learning_experience = {
                'type': 'reinforcement',
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'q_value': q_value,
                'timestamp': experience.get('timestamp', '未知时间')
            }
            state_node.add_experience(learning_experience)
            
            # 更新策略
            best_action = self._update_policy(state_node)
            
            return LearningResult(success=True, data={
                'learning_mode': 'reinforcement',
                'state_concept': state_concept,
                'action': action,
                'reward': reward,
                'updated_q_value': q_value,
                'best_next_action': best_action
            })
            
        except Exception as e:
            return LearningResult(success=False, error=f"强化学习失败: {str(e)}")
    
    def _get_or_create_concept(self, concept: str, level: int) -> KnowledgeNode:
        """获取或创建概念节点"""
        if concept not in self.knowledge_graph:
            self.knowledge_graph[concept] = KnowledgeNode(concept, level)
        
        return self.knowledge_graph[concept]
    
    def _update_associations_from_features(self, concept_node: KnowledgeNode, features: Dict[str, Any]):
        """从特征更新关联"""
        for feature_name, feature_value in features.items():
            if isinstance(feature_value, (int, float)) and feature_value > 0:
                # 创建特征节点关联
                feature_concept = f"特征_{feature_name}"
                feature_node = self._get_or_create_concept(feature_concept, 1)
                
                # 更新关联强度
                current_strength = concept_node.associations.get(feature_concept, 0)
                new_strength = min(1.0, current_strength + 0.1)
                concept_node.associations[feature_concept] = new_strength
    
    def _cluster_features(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """特征聚类（简化版）"""
        clusters = []
        
        # 基于特征值范围进行简单聚类
        numeric_features = {k: v for k, v in features.items() if isinstance(v, (int, float))}
        
        if numeric_features:
            # 计算特征向量范数
            feature_norm = np.linalg.norm(list(numeric_features.values()))
            
            if feature_norm > 10:
                clusters.append({'type': '高维特征', 'features': numeric_features})
            elif feature_norm > 5:
                clusters.append({'type': '中维特征', 'features': numeric_features})
            else:
                clusters.append({'type': '低维特征', 'features': numeric_features})
        
        return clusters
    
    def _discover_patterns(self, clusters: List[Dict[str, Any]]) -> List[str]:
        """发现模式"""
        patterns = []
        
        for cluster in clusters:
            cluster_type = cluster.get('type', '')
            features = cluster.get('features', {})
            
            if cluster_type == '高维特征':
                patterns.append('复杂模式')
            elif cluster_type == '中维特征':
                patterns.append('中等复杂度模式')
            elif cluster_type == '低维特征':
                patterns.append('简单模式')
            
            # 基于特征特性添加模式
            if len(features) > 3:
                patterns.append('多特征模式')
            if any(v > 8 for v in features.values() if isinstance(v, (int, float))):
                patterns.append('强特征模式')
        
        return list(set(patterns))  # 去重
    
    def _extract_state_concept(self, state: Dict[str, Any]) -> str:
        """提取状态概念"""
        # 基于状态特征生成概念
        state_features = []
        
        for key, value in state.items():
            if isinstance(value, bool) and value:
                state_features.append(key)
            elif isinstance(value, (int, float)) and value > 0:
                state_features.append(f"{key}_正")
            elif isinstance(value, str):
                state_features.append(value)
        
        if state_features:
            return f"状态_{'_'.join(state_features[:3])}"  # 限制特征数量
        else:
            return "未知状态"
    
    def _update_q_value(self, state_node: KnowledgeNode, action_node: KnowledgeNode, 
                       reward: float, next_state: Dict[str, Any]) -> float:
        """更新Q值（简化版）"""
        # 获取当前Q值
        q_key = f"Q_{action_node.concept}"
        current_q = state_node.associations.get(q_key, 0.0)
        
        # 计算下一状态的最大Q值
        next_state_concept = self._extract_state_concept(next_state)
        next_state_node = self._get_or_create_concept(next_state_concept, 2)
        
        max_next_q = 0.0
        for key, value in next_state_node.associations.items():
            if key.startswith('Q_') and value > max_next_q:
                max_next_q = value
        
        # Q学习更新公式
        learning_rate = self.config.learning_rate
        discount_factor = 0.9
        
        new_q = current_q + learning_rate * (reward + discount_factor * max_next_q - current_q)
        
        # 更新关联
        state_node.associations[q_key] = new_q
        
        return new_q
    
    def _update_policy(self, state_node: KnowledgeNode) -> str:
        """更新策略"""
        # 选择Q值最高的动作
        best_action = ""
        best_q = -float('inf')
        
        for key, value in state_node.associations.items():
            if key.startswith('Q_') and value > best_q:
                best_q = value
                best_action = key[2:]  # 去掉"Q_"前缀
        
        # 探索策略
        if np.random.random() < self.config.exploration_rate or not best_action:
            # 随机选择动作
            available_actions = ['分析问题', '制定方案', '执行操作', '评估结果']
            best_action = np.random.choice(available_actions)
        
        return best_action
    
    def build_knowledge_hierarchy(self) -> LearningResult:
        """构建知识层次结构"""
        try:
            # 按层次组织知识
            hierarchy = {}
            
            for level in range(1, self.config.hierarchy_levels + 1):
                level_nodes = []
                
                for concept, node in self.knowledge_graph.items():
                    if node.level == level:
                        level_nodes.append(node.to_dict())
                
                hierarchy[f'level_{level}'] = {
                    'node_count': len(level_nodes),
                    'nodes': level_nodes
                }
            
            # 分析层次关系
            cross_level_associations = self._analyze_cross_level_associations()
            
            return LearningResult(success=True, data={
                'hierarchy': hierarchy,
                'total_concepts': len(self.knowledge_graph),
                'cross_level_associations': cross_level_associations
            })
            
        except Exception as e:
            return LearningResult(success=False, error=f"知识层次构建失败: {str(e)}")
    
    def _analyze_cross_level_associations(self) -> Dict[str, Any]:
        """分析跨层次关联"""
        associations = {
            'level_1_to_2': 0,
            'level_2_to_3': 0,
            'level_1_to_3': 0
        }
        
        for concept, node in self.knowledge_graph.items():
            for associated_concept, strength in node.associations.items():
                if associated_concept in self.knowledge_graph:
                    target_node = self.knowledge_graph[associated_concept]
                    
                    if node.level == 1 and target_node.level == 2:
                        associations['level_1_to_2'] += 1
                    elif node.level == 2 and target_node.level == 3:
                        associations['level_2_to_3'] += 1
                    elif node.level == 1 and target_node.level == 3:
                        associations['level_1_to_3'] += 1
        
        return associations
    
    def consolidate_knowledge(self) -> LearningResult:
        """知识巩固：整合和优化知识结构"""
        try:
            # 知识修剪：移除低置信度节点
            pruned_concepts = []
            concepts_to_remove = []
            
            for concept, node in self.knowledge_graph.items():
                if node.confidence < 0.3 and len(node.experiences) < 3:
                    concepts_to_remove.append(concept)
                    pruned_concepts.append(concept)
            
            for concept in concepts_to_remove:
                del self.knowledge_graph[concept]
            
            # 知识融合：合并相似概念
            merged_concepts = self._merge_similar_concepts()
            
            # 知识强化：增强重要关联
            strengthened_associations = self._strengthen_important_associations()
            
            return LearningResult(success=True, data={
                'pruned_concepts': pruned_concepts,
                'merged_concepts': merged_concepts,
                'strengthened_associations': strengthened_associations,
                'remaining_concepts': len(self.knowledge_graph)
            })
            
        except Exception as e:
            return LearningResult(success=False, error=f"知识巩固失败: {str(e)}")
    
    def _merge_similar_concepts(self) -> List[str]:
        """合并相似概念"""
        merged = []
        
        # 简化版：合并名称相似的概念
        concepts = list(self.knowledge_graph.keys())
        
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts[i+1:], i+1):
                # 简单的相似度计算
                similarity = self._calculate_concept_similarity(concept1, concept2)
                
                if similarity > 0.8:  # 高相似度阈值
                    # 合并概念（保留置信度较高的）
                    node1 = self.knowledge_graph[concept1]
                    node2 = self.knowledge_graph[concept2]
                    
                    if node1.confidence >= node2.confidence:
                        # 合并到concept1
                        self._merge_nodes(node1, node2)
                        del self.knowledge_graph[concept2]
                        merged.append(f"{concept2} -> {concept1}")
                    else:
                        # 合并到concept2
                        self._merge_nodes(node2, node1)
                        del self.knowledge_graph[concept1]
                        merged.append(f"{concept1} -> {concept2}")
                    
                    break  # 避免重复合并
        
        return merged
    
    def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """计算概念相似度"""
        # 基于字符串相似度的简化计算
        words1 = set(concept1.split('_'))
        words2 = set(concept2.split('_'))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_nodes(self, target_node: KnowledgeNode, source_node: KnowledgeNode):
        """合并节点"""
        # 合并经验
        target_node.experiences.extend(source_node.experiences)
        
        # 合并关联
        for concept, strength in source_node.associations.items():
            if concept in target_node.associations:
                target_node.associations[concept] = max(target_node.associations[concept], strength)
            else:
                target_node.associations[concept] = strength
        
        # 更新置信度
        target_node.confidence = max(target_node.confidence, source_node.confidence)
    
    def _strengthen_important_associations(self) -> int:
        """增强重要关联"""
        strengthened_count = 0
        
        for concept, node in self.knowledge_graph.items():
            for associated_concept, strength in node.associations.items():
                if strength > 0.7:  # 强关联
                    # 进一步增强
                    new_strength = min(1.0, strength + 0.1)
                    node.associations[associated_concept] = new_strength
                    strengthened_count += 1
        
        return strengthened_count
    
    def learn(self, learning_mode: str, data: List[Dict[str, Any]] = None, 
              experience: Dict[str, Any] = None) -> LearningResult:
        """学习主方法"""
        try:
            if learning_mode not in self.config.learning_modes:
                return LearningResult(success=False, error=f"不支持的学习模式: {learning_mode}")
            
            if learning_mode == 'supervised' and data:
                return self.supervised_learning(data)
            elif learning_mode == 'unsupervised' and data:
                return self.unsupervised_learning(data)
            elif learning_mode == 'reinforcement' and experience:
                return self.reinforcement_learning(experience)
            else:
                return LearningResult(success=False, error="缺少必要的学习数据")
            
        except Exception as e:
            return LearningResult(success=False, error=f"学习失败: {str(e)}")

class HierarchicalLearningTool:
    """分层学习工具类（用于智能体集成）"""
    
    def __init__(self):
        self.engine = HierarchicalLearningEngine()
        self.tool_name = "HierarchicalLearningEngine"
        self.tool_description = "分层学习引擎，支持从经验中学习并构建层次化的知识结构"
        self.tool_usage = "用于持续学习和知识积累，提高智能体的适应能力"
    
    def call(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用分层学习工具"""
        try:
            if operation == "learn":
                learning_mode = parameters.get('learning_mode', 'supervised')
                data = parameters.get('data')
                experience = parameters.get('experience')
                
                result = self.engine.learn(learning_mode, data, experience)
                return result.to_dict()
                
            elif operation == "supervised_learning":
                training_data = parameters.get('training_data', [])
                result = self.engine.supervised_learning(training_data)
                return result.to_dict()
                
            elif operation == "unsupervised_learning":
                unlabeled_data = parameters.get('unlabeled_data', [])
                result = self.engine.unsupervised_learning(unlabeled_data)
                return result.to_dict()
                
            elif operation == "reinforcement_learning":
                experience_data = parameters.get('experience', {})
                result = self.engine.reinforcement_learning(experience_data)
                return result.to_dict()
                
            elif operation == "build_hierarchy":
                result = self.engine.build_knowledge_hierarchy()
                return result.to_dict()
                
            elif operation == "consolidate_knowledge":
                result = self.engine.consolidate_knowledge()
                return result.to_dict()
                
            else:
                return {'success': False, 'error': f'未知操作: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': f'工具调用失败: {str(e)}'}

# 测试代码
if __name__ == "__main__":
    # 创建分层学习引擎实例
    learning_engine = HierarchicalLearningEngine()
    
    # 测试监督学习
    training_data = [
        {
            'features': {'长度': 10, '复杂度': 5, '重要性': 8},
            'label': '重要任务',
            'timestamp': '2024-01-01 10:00:00'
        },
        {
            'features': {'长度': 3, '复杂度': 2, '重要性': 3},
            'label': '简单任务', 
            'timestamp': '2024-01-01 10:05:00'
        }
    ]
    
    result = learning_engine.supervised_learning(training_data)
    print("监督学习结果:")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    # 测试无监督学习
    unlabeled_data = [
        {
            'features': {'特征1': 0.8, '特征2': 0.6, '特征3': 0.9},
            'timestamp': '2024-01-01 11:00:00'
        },
        {
            'features': {'特征1': 0.2, '特征2': 0.3, '特征3': 0.1},
            'timestamp': '2024-01-01 11:05:00'
        }
    ]
    
    result = learning_engine.unsupervised_learning(unlabeled_data)
    print("\n无监督学习结果:")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    # 测试知识层次构建
    result = learning_engine.build_knowledge_hierarchy()
    print("\n知识层次构建结果:")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))