#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多模态融合引擎
实现智能体系统的多模态信息融合能力
支持视觉、音频、文本等多模态数据的融合处理
"""

# @self-expose: {"id": "multimodal_fusion_engine", "name": "多模态融合引擎", "type": "tool", "version": "2.0.0", "needs": {"deps": ["numpy"], "resources": ["融合配置对象", "结果对象"]}, "provides": {"capabilities": ["初始化融合模型", "早期融合（特征级）", "晚期融合（决策级）", "混合融合", "提取文本特征", "提取图像特征", "提取音频特征", "特征归一化", "特征拼接", "计算融合置信度", "计算模态贡献度", "加权融合", "计算总体置信度", "生成最终决策", "融合混合结果", "计算混合置信度", "综合融合分析", "生成融合摘要", "支持多种融合策略", "支持置信度阈值配置", "支持智能体集成"]}, "exclusive_caller": "data_collector_agent", "usage_scenarios": ["数据收集师融合多模态信息提取结构化数据", "融合网页文本+图片+视频的综合内容"], "architecture_role": "分离式多模态架构核心组件", "design_principle": "验证'非原生多模态LLM + 多模态引擎'能否等效原生多模态LLM"}

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

class FusionConfig:
    """多模态融合配置类"""
    
    def __init__(self):
        self.fusion_methods = ['early_fusion', 'late_fusion', 'hybrid_fusion']
        self.feature_dimensions = {
            'text': 768,
            'image': 512,
            'audio': 128
        }
        self.fusion_weights = {
            'text': 0.4,
            'image': 0.3,
            'audio': 0.3
        }
        self.confidence_threshold = 0.6

class FusionResult:
    """融合结果类"""
    
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

class MultimodalFusionEngine:
    """多模态融合引擎核心类"""
    
    def __init__(self, config: FusionConfig = None):
        self.config = config or FusionConfig()
        self.fusion_models_loaded = False
        self._initialize_fusion_models()
    
    def _initialize_fusion_models(self):
        """初始化融合模型"""
        try:
            # 创建模型目录
            model_dir = Path("models/fusion")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # 标记模型已加载
            self.fusion_models_loaded = True
            print("多模态融合引擎初始化成功")
            
        except Exception as e:
            print(f"融合模型初始化失败: {e}")
            self.fusion_models_loaded = False
    
    def early_fusion(self, modalities: Dict[str, Any]) -> Dict[str, Any]:
        """早期融合：在特征级别融合多模态数据"""
        try:
            # 提取各模态特征
            features = {}
            
            for modality, data in modalities.items():
                if modality == 'text':
                    features[modality] = self._extract_text_features(data)
                elif modality == 'image':
                    features[modality] = self._extract_image_features(data)
                elif modality == 'audio':
                    features[modality] = self._extract_audio_features(data)
            
            # 特征归一化
            normalized_features = self._normalize_features(features)
            
            # 特征拼接
            fused_features = self._concatenate_features(normalized_features)
            
            # 计算融合置信度
            confidence = self._calculate_fusion_confidence(normalized_features)
            
            return {
                'fusion_method': 'early_fusion',
                'fused_features': fused_features.tolist(),
                'feature_dimensions': len(fused_features),
                'confidence': confidence,
                'modality_contributions': self._calculate_modality_contributions(normalized_features)
            }
            
        except Exception as e:
            print(f"早期融合失败: {e}")
            return {'error': f'早期融合失败: {str(e)}'}
    
    def late_fusion(self, modality_results: Dict[str, Any]) -> Dict[str, Any]:
        """晚期融合：在决策级别融合多模态结果"""
        try:
            # 提取各模态的决策结果
            decisions = {}
            confidences = {}
            
            for modality, result in modality_results.items():
                if 'decision' in result and 'confidence' in result:
                    decisions[modality] = result['decision']
                    confidences[modality] = result['confidence']
            
            if not decisions:
                return {'error': '没有有效的决策结果可用于融合'}
            
            # 加权融合
            weighted_decisions = self._weighted_fusion(decisions, confidences)
            
            # 计算融合置信度
            overall_confidence = self._calculate_overall_confidence(confidences)
            
            # 生成融合决策
            final_decision = self._generate_final_decision(weighted_decisions)
            
            return {
                'fusion_method': 'late_fusion',
                'final_decision': final_decision,
                'overall_confidence': overall_confidence,
                'modality_decisions': decisions,
                'modality_confidences': confidences,
                'weighted_decisions': weighted_decisions
            }
            
        except Exception as e:
            print(f"晚期融合失败: {e}")
            return {'error': f'晚期融合失败: {str(e)}'}
    
    def hybrid_fusion(self, modalities: Dict[str, Any], modality_results: Dict[str, Any]) -> Dict[str, Any]:
        """混合融合：结合早期和晚期融合"""
        try:
            # 早期融合
            early_result = self.early_fusion(modalities)
            
            # 晚期融合
            late_result = self.late_fusion(modality_results)
            
            # 融合两种融合结果
            hybrid_result = self._fuse_hybrid_results(early_result, late_result)
            
            return {
                'fusion_method': 'hybrid_fusion',
                'early_fusion': early_result,
                'late_fusion': late_result,
                'hybrid_result': hybrid_result,
                'confidence': self._calculate_hybrid_confidence(early_result, late_result)
            }
            
        except Exception as e:
            print(f"混合融合失败: {e}")
            return {'error': f'混合融合失败: {str(e)}'}
    
    def _extract_text_features(self, text_data: Any) -> np.ndarray:
        """提取文本特征（简化版）"""
        try:
            # 简化的文本特征提取
            if isinstance(text_data, str):
                # 基于文本长度和词汇特征的简化表示
                text_length = len(text_data)
                word_count = len(text_data.split())
                avg_word_length = text_length / max(word_count, 1)
                
                # 创建特征向量
                features = np.array([text_length, word_count, avg_word_length])
                
                # 扩展到标准维度
                if len(features) < self.config.feature_dimensions['text']:
                    padding = np.zeros(self.config.feature_dimensions['text'] - len(features))
                    features = np.concatenate([features, padding])
                
                return features[:self.config.feature_dimensions['text']]
            
            elif isinstance(text_data, dict) and 'features' in text_data:
                # 如果已经提供了特征
                features = np.array(text_data['features'])
                return features[:self.config.feature_dimensions['text']]
            
            else:
                return np.zeros(self.config.feature_dimensions['text'])
                
        except Exception as e:
            print(f"文本特征提取失败: {e}")
            return np.zeros(self.config.feature_dimensions['text'])
    
    def _extract_image_features(self, image_data: Any) -> np.ndarray:
        """提取图像特征（简化版）"""
        try:
            # 简化的图像特征提取
            if isinstance(image_data, dict) and 'features' in image_data:
                # 如果已经提供了特征
                features = np.array(image_data['features'])
                return features[:self.config.feature_dimensions['image']]
            
            else:
                # 返回随机特征（实际应用中应该使用CNN等提取真实特征）
                return np.random.randn(self.config.feature_dimensions['image'])
                
        except Exception as e:
            print(f"图像特征提取失败: {e}")
            return np.zeros(self.config.feature_dimensions['image'])
    
    def _extract_audio_features(self, audio_data: Any) -> np.ndarray:
        """提取音频特征（简化版）"""
        try:
            # 简化的音频特征提取
            if isinstance(audio_data, dict) and 'features' in audio_data:
                # 如果已经提供了特征
                features = np.array(audio_data['features'])
                return features[:self.config.feature_dimensions['audio']]
            
            else:
                # 返回随机特征（实际应用中应该使用MFCC等提取真实特征）
                return np.random.randn(self.config.feature_dimensions['audio'])
                
        except Exception as e:
            print(f"音频特征提取失败: {e}")
            return np.zeros(self.config.feature_dimensions['audio'])
    
    def _normalize_features(self, features: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """特征归一化"""
        normalized = {}
        
        for modality, feature in features.items():
            if len(feature) > 0:
                # 归一化到0-1范围
                min_val = np.min(feature)
                max_val = np.max(feature)
                
                if max_val > min_val:
                    normalized[modality] = (feature - min_val) / (max_val - min_val)
                else:
                    normalized[modality] = feature
            else:
                normalized[modality] = feature
        
        return normalized
    
    def _concatenate_features(self, normalized_features: Dict[str, np.ndarray]) -> np.ndarray:
        """特征拼接"""
        concatenated = []
        
        for modality in ['text', 'image', 'audio']:
            if modality in normalized_features:
                concatenated.append(normalized_features[modality])
        
        if concatenated:
            return np.concatenate(concatenated)
        else:
            return np.array([])
    
    def _calculate_fusion_confidence(self, normalized_features: Dict[str, np.ndarray]) -> float:
        """计算融合置信度"""
        if not normalized_features:
            return 0.0
        
        # 基于特征质量和多样性计算置信度
        confidence_scores = []
        
        for modality, feature in normalized_features.items():
            if len(feature) > 0:
                # 特征质量：非零特征的比例
                non_zero_ratio = np.sum(feature != 0) / len(feature)
                
                # 特征多样性：标准差
                diversity = np.std(feature) if len(feature) > 1 else 0.0
                
                # 综合置信度
                modality_confidence = (non_zero_ratio + diversity) / 2
                confidence_scores.append(modality_confidence)
        
        if confidence_scores:
            return float(np.mean(confidence_scores))
        else:
            return 0.0
    
    def _calculate_modality_contributions(self, normalized_features: Dict[str, np.ndarray]) -> Dict[str, float]:
        """计算各模态贡献度"""
        contributions = {}
        total_contribution = 0.0
        
        for modality, feature in normalized_features.items():
            if len(feature) > 0:
                # 基于特征能量计算贡献度
                energy = np.sum(feature**2)
                contributions[modality] = energy
                total_contribution += energy
        
        # 归一化贡献度
        if total_contribution > 0:
            for modality in contributions:
                contributions[modality] /= total_contribution
        
        return contributions
    
    def _weighted_fusion(self, decisions: Dict[str, Any], confidences: Dict[str, float]) -> Dict[str, float]:
        """加权融合"""
        weighted = {}
        
        # 计算总权重
        total_weight = sum(confidences.values())
        
        if total_weight > 0:
            for modality, decision in decisions.items():
                weight = confidences[modality] / total_weight
                
                # 根据决策类型进行加权
                if isinstance(decision, (int, float)):
                    weighted[modality] = decision * weight
                elif isinstance(decision, dict):
                    # 对于字典类型的决策，递归处理
                    weighted[modality] = self._weight_dict_decision(decision, weight)
                else:
                    weighted[modality] = decision
        
        return weighted
    
    def _weight_dict_decision(self, decision: Dict[str, Any], weight: float) -> Dict[str, Any]:
        """加权字典决策"""
        weighted_decision = {}
        
        for key, value in decision.items():
            if isinstance(value, (int, float)):
                weighted_decision[key] = value * weight
            elif isinstance(value, dict):
                weighted_decision[key] = self._weight_dict_decision(value, weight)
            else:
                weighted_decision[key] = value
        
        return weighted_decision
    
    def _calculate_overall_confidence(self, confidences: Dict[str, float]) -> float:
        """计算总体置信度"""
        if not confidences:
            return 0.0
        
        # 基于各模态置信度的加权平均
        weights = self.config.fusion_weights
        total_confidence = 0.0
        total_weight = 0.0
        
        for modality, confidence in confidences.items():
            weight = weights.get(modality, 0.0)
            total_confidence += confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_confidence / total_weight
        else:
            return np.mean(list(confidences.values())) if confidences else 0.0
    
    def _generate_final_decision(self, weighted_decisions: Dict[str, Any]) -> Any:
        """生成最终决策"""
        if not weighted_decisions:
            return None
        
        # 简单的决策融合：取平均值或多数投票
        numeric_decisions = []
        
        for decision in weighted_decisions.values():
            if isinstance(decision, (int, float)):
                numeric_decisions.append(decision)
        
        if numeric_decisions:
            return np.mean(numeric_decisions)
        else:
            # 如果无法数值化，返回第一个决策
            return list(weighted_decisions.values())[0]
    
    def _fuse_hybrid_results(self, early_result: Dict[str, Any], late_result: Dict[str, Any]) -> Dict[str, Any]:
        """融合混合结果"""
        try:
            hybrid_result = {
                'early_fusion_features': early_result.get('fused_features', []),
                'late_fusion_decision': late_result.get('final_decision', None),
                'combined_confidence': (early_result.get('confidence', 0) + late_result.get('overall_confidence', 0)) / 2
            }
            
            return hybrid_result
            
        except Exception as e:
            print(f"混合结果融合失败: {e}")
            return {'error': f'混合结果融合失败: {str(e)}'}
    
    def _calculate_hybrid_confidence(self, early_result: Dict[str, Any], late_result: Dict[str, Any]) -> float:
        """计算混合融合置信度"""
        early_confidence = early_result.get('confidence', 0)
        late_confidence = late_result.get('overall_confidence', 0)
        
        return (early_confidence + late_confidence) / 2
    
    def fuse_modalities(self, fusion_method: str, modalities: Dict[str, Any] = None, 
                       modality_results: Dict[str, Any] = None) -> FusionResult:
        """多模态融合主方法"""
        try:
            if fusion_method not in self.config.fusion_methods:
                return FusionResult(success=False, error=f"不支持的融合方法: {fusion_method}")
            
            if fusion_method == 'early_fusion' and modalities:
                result = self.early_fusion(modalities)
            elif fusion_method == 'late_fusion' and modality_results:
                result = self.late_fusion(modality_results)
            elif fusion_method == 'hybrid_fusion' and modalities and modality_results:
                result = self.hybrid_fusion(modalities, modality_results)
            else:
                return FusionResult(success=False, error="缺少必要的模态数据")
            
            if 'error' in result:
                return FusionResult(success=False, error=result['error'])
            
            return FusionResult(success=True, data=result)
            
        except Exception as e:
            return FusionResult(success=False, error=f"多模态融合失败: {str(e)}")

class MultimodalFusionTool:
    """多模态融合工具类（用于智能体集成）"""
    
    def __init__(self):
        self.engine = MultimodalFusionEngine()
        self.tool_name = "MultimodalFusionEngine"
        self.tool_description = "多模态融合引擎，支持视觉、音频、文本等多模态数据的融合处理"
        self.tool_usage = "用于融合多模态信息，提高智能体对复杂场景的理解能力"
    
    def call(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用多模态融合工具"""
        try:
            if operation == "fuse_modalities":
                fusion_method = parameters.get('fusion_method', 'hybrid_fusion')
                modalities = parameters.get('modalities', {})
                modality_results = parameters.get('modality_results', {})
                
                result = self.engine.fuse_modalities(fusion_method, modalities, modality_results)
                return result.to_dict()
                
            elif operation == "early_fusion":
                modalities = parameters.get('modalities', {})
                result = self.engine.early_fusion(modalities)
                return {'success': True, 'data': result}
                
            elif operation == "late_fusion":
                modality_results = parameters.get('modality_results', {})
                result = self.engine.late_fusion(modality_results)
                return {'success': True, 'data': result}
                
            elif operation == "hybrid_fusion":
                modalities = parameters.get('modalities', {})
                modality_results = parameters.get('modality_results', {})
                result = self.engine.hybrid_fusion(modalities, modality_results)
                return {'success': True, 'data': result}
                
            else:
                return {'success': False, 'error': f'未知操作: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': f'工具调用失败: {str(e)}'}

# 测试代码
if __name__ == "__main__":
    # 创建多模态融合引擎实例
    fusion_engine = MultimodalFusionEngine()
    
    # 测试早期融合
    test_modalities = {
        'text': '这是一个测试文本',
        'image': {'features': [0.1, 0.2, 0.3, 0.4, 0.5]},
        'audio': {'features': [0.6, 0.7, 0.8, 0.9, 1.0]}
    }
    
    result = fusion_engine.early_fusion(test_modalities)
    print("早期融合结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试晚期融合
    test_modality_results = {
        'text': {'decision': 'positive', 'confidence': 0.8},
        'image': {'decision': 'negative', 'confidence': 0.6},
        'audio': {'decision': 'positive', 'confidence': 0.7}
    }
    
    result = fusion_engine.late_fusion(test_modality_results)
    print("\n晚期融合结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))