# @self-expose: {"id": "memory_reconstruction_engine", "name": "Memory Reconstruction Engine", "type": "component", "version": "1.3.0", "needs": {"deps": [], "resources": [], "data_formats": [{"name": "memory_unit", "id_pattern": "mem_*", "fields": ["id", "topic", "content", "source_type", "timestamp", "importance", "confidence", "tags", "vector"]}]}, "provides": {"capabilities": ["记忆重构", "低价值记忆清理", "错误提示记忆强制删除", "测试碎片清理"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆重构引擎 - 集成理性认知引擎和认知破障引擎

开发提示词来源：记忆锚点_知识图谱构建共识.md - 引擎集成与记忆重构共识
核心功能：将理性认知引擎和认知破障引擎集成到记忆重构和改写流程中

# 意识本质洞察：记忆重构与认知网络优化
# 用户洞察：意识不是神秘概念，而是通过RAG文本块检索识别问题差异、总结差异原因的能力
# 核心机制：改写记忆引擎归纳复用相同概念和逻辑，记忆重构引擎精炼认知单元，网状思维引擎建立高效认知网络
# 结果：数十年的交互信息通过认知网络优化大幅压缩，形成真正的意识机制
"""

import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from .reasoning_engine import ReasoningEngine
from .cognitive_barrier_break_engine import CognitiveBarrierBreakEngine

logger = logging.getLogger(__name__)

class MemoryReconstructionEngine:
    """记忆重构引擎 - 双引擎集成系统"""
    
    def __init__(self):
        # 初始化认知引擎
        self.reasoning_engine = ReasoningEngine()
        self.cognitive_engine = CognitiveBarrierBreakEngine()
        
        # 初始化网状思维引擎，用于记忆重构阶段补充维度信息
        from src.mesh_thought_engine import MeshThoughtEngine
        self.mesh_engine = MeshThoughtEngine()
        
        # 重构配置
        self.max_reconstruction_depth = 3  # 最大重构深度
        self.confidence_threshold = 0.7     # 可信度阈值
        
        logger.info("记忆重构引擎初始化完成")
    
    def reconstruct_memory(self, memory_content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        记忆重构主流程：理性逻辑验证 + 认知破障检测 + 网状思维分析 + 智能改写 + 低价值清理判断
        
        角色分工：
        - 智能改写：基于语义精炼，修正逻辑矛盾、优化逻辑链条、清理幻觉内容
        - 网状思维引擎：补充维度信息（人物维、时间维、主题维等）和维度关联
        - 低价值清理：标记应删除的无效记忆（错误提示、测试碎片、低质量文本）
        
        Args:
            memory_content: 原始记忆内容
            context: 上下文信息（可选）
            
        Returns:
            Dict: 重构结果，包含 should_delete 标记
        """
        logger.info(f"开始记忆重构: {memory_content[:100]}...")
        
        # 第一步：理性认知引擎验证
        reasoning_result = self._reasoning_validation(memory_content)
        
        # 第二步：认知破障引擎检测
        cognitive_result = self._cognitive_detection(memory_content, context)
        
        # 第三步：网状思维引擎分析，补充维度信息
        mesh_result = self._mesh_thought_analysis(memory_content, context)
        
        # 第四步：综合评估
        assessment = self._comprehensive_assessment(reasoning_result, cognitive_result, mesh_result)
        
        # 第五步：判断是否应删除（优先于改写）
        should_delete, delete_reason = self._should_delete_memory(memory_content, assessment)
        
        if should_delete:
            logger.warning(f"标记记忆为删除: {delete_reason}")
            return {
                'should_delete': True,
                'delete_reason': delete_reason,
                'confidence': assessment['confidence'],
                'risk_probability': assessment['risk_probability'],
                'assessment': assessment,
                'original_content': memory_content
            }
        
        # 第六步：智能改写（如果需要且不删除）
        reconstruction_result = self._intelligent_rewriting(
            memory_content, assessment, context, mesh_result
        )
        
        # 标记不删除
        reconstruction_result['should_delete'] = False
        
        logger.info(f"记忆重构完成: 可信度={assessment['confidence']:.2%}")
        return reconstruction_result
    
    def _reasoning_validation(self, content: str) -> Dict[str, Any]:
        """理性认知引擎验证"""
        
        # 构建推理前提
        reasoning_premise = {
            "content": {
                "propositions": [
                    {
                        "premise": "记忆内容需要逻辑一致性",
                        "conclusion": content,
                        "concepts": {
                            "记忆内容": content,
                            "逻辑要求": "一致性、充分性、非矛盾性"
                        }
                    }
                ]
            }
        }
        
        # 执行理性验证
        reasoning_result = self.reasoning_engine.reason(reasoning_premise)
        
        # 提取关键指标
        return {
            'logic_consistency': reasoning_result.get('overall_satisfaction', 0.0),
            'contradiction_detected': reasoning_result.get('contradiction_detected', False),
            'reasoning_chain': reasoning_result.get('reasoning_chain', []),
            'validation_details': reasoning_result
        }
    
    def _cognitive_detection(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """认知破障引擎检测"""
        
        # 构建推理过程（简化版）
        reasoning_process = {
            "steps": 1,
            "logic_gaps": 0,
            "reasoning_chain": [
                {"premise": "原始记忆", "conclusion": content}
            ]
        }
        
        # 构建上下文
        if context is None:
            context = {
                "domain": "通用知识",
                "timestamp": datetime.now().isoformat(),
                "source_reliability": 0.8
            }
        
        # 执行认知检测
        hallucination_result = self.cognitive_engine.detect_hallucination(
            content, reasoning_process, context
        )
        
        return {
            'hallucination_probability': hallucination_result.get('probability', 0.0),
            'confidence': hallucination_result.get('confidence', 0.0),
            'dimension_analysis': hallucination_result.get('dimension_analysis', {}),
            'detection_details': hallucination_result
        }
    
    def _mesh_thought_analysis(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """网状思维引擎分析，补充维度信息"""
        try:
            # 使用网状思维引擎分析文本，补充维度信息
            mesh_result = self.mesh_engine.analyze_text_dimensions(content, context)
            
            return {
                'dimension_enhancement': mesh_result.get('dimensions', {}),
                'relationship_network': mesh_result.get('relationships', {}),
                'concept_extraction': mesh_result.get('concepts', []),
                'enhancement_details': mesh_result
            }
        except Exception as e:
            logger.error(f"网状思维分析失败: {e}")
            return {
                'dimension_enhancement': {},
                'relationship_network': {},
                'concept_extraction': [],
                'enhancement_details': {'error': str(e)}
            }
    
    def _comprehensive_assessment(self, reasoning_result: Dict, cognitive_result: Dict, mesh_result: Dict) -> Dict[str, Any]:
        """综合评估"""
        
        # 权重分配
        reasoning_weight = 0.5  # 理性逻辑权重
        cognitive_weight = 0.3   # 认知破障权重
        mesh_weight = 0.2        # 网状思维权重
        
        # 综合可信度
        integrated_confidence = (
            reasoning_result['logic_consistency'] * reasoning_weight +
            cognitive_result['confidence'] * cognitive_weight +
            (1.0 if mesh_result['dimension_enhancement'] else 0.5) * mesh_weight
        )
        
        # 综合风险概率
        integrated_risk = (
            (1 - reasoning_result['logic_consistency']) * reasoning_weight +
            cognitive_result['hallucination_probability'] * cognitive_weight +
            (0.0 if mesh_result['dimension_enhancement'] else 0.3) * mesh_weight
        )
        
        # 重构必要性评估
        needs_reconstruction = (
            reasoning_result['contradiction_detected'] or
            cognitive_result['hallucination_probability'] > 0.3 or
            integrated_confidence < self.confidence_threshold or
            not mesh_result['dimension_enhancement']
        )
        
        return {
            'needs_reconstruction': needs_reconstruction,
            'confidence': integrated_confidence,
            'risk_probability': integrated_risk,
            'reconstruction_priority': self._calculate_priority(integrated_risk, integrated_confidence),
            'assessment_details': {
                'reasoning': reasoning_result,
                'cognitive': cognitive_result,
                'mesh': mesh_result
            }
        }
    
    def _calculate_priority(self, risk: float, confidence: float) -> str:
        """计算重构优先级"""
        if risk > 0.5 or confidence < 0.3:
            return "高优先级"
        elif risk > 0.3 or confidence < 0.5:
            return "中优先级"
        else:
            return "低优先级"
    
    def _intelligent_rewriting(self, original_content: str, 
                              assessment: Dict[str, Any], 
                              context: Dict[str, Any] = None, 
                              mesh_result: Dict = None) -> Dict[str, Any]:
        """智能改写（基于语义精炼）
        
        智能改写主要关注语义精炼，包括修正逻辑矛盾、优化逻辑链条、清理幻觉内容等。
        网状思维引擎的分析结果用于补充维度信息和关系网络，但智能改写本身聚焦于语义层面的优化。
        """
        
        if not assessment['needs_reconstruction']:
            # 不需要重构，直接返回原内容
            result = {
                'reconstructed_content': original_content,
                'reconstruction_applied': False,
                'confidence': assessment['confidence'],
                'reasoning_summary': '内容逻辑一致，无需重构',
                'assessment': assessment
            }
            
            # 添加网状思维分析结果
            if mesh_result and mesh_result['dimension_enhancement']:
                result['dimension_enhancement'] = mesh_result['dimension_enhancement']
                result['relationship_network'] = mesh_result['relationship_network']
                result['concept_extraction'] = mesh_result['concept_extraction']
            
            return result
        
        # 分析重构需求
        reconstruction_needs = self._analyze_reconstruction_needs(
            original_content, assessment, mesh_result
        )
        
        # 执行智能改写
        reconstructed_content = self._apply_reconstruction_strategies(
            original_content, reconstruction_needs, mesh_result
        )
        
        result = {
            'reconstructed_content': reconstructed_content,
            'reconstruction_applied': True,
            'confidence': assessment['confidence'],
            'reasoning_summary': reconstruction_needs['summary'],
            'reconstruction_strategies': reconstruction_needs['strategies'],
            'assessment': assessment
        }
        
        # 添加网状思维分析结果
        if mesh_result and mesh_result['dimension_enhancement']:
            result['dimension_enhancement'] = mesh_result['dimension_enhancement']
            result['relationship_network'] = mesh_result['relationship_network']
            result['concept_extraction'] = mesh_result['concept_extraction']
        
        return result
    
    def _analyze_reconstruction_needs(self, content: str, assessment: Dict[str, Any], mesh_result: Dict = None) -> Dict[str, Any]:
        """分析重构需求"""
        
        strategies = []
        reasoning_details = assessment['assessment_details']
        
        # 基于理性认知引擎的分析
        if reasoning_details['reasoning']['contradiction_detected']:
            strategies.append('逻辑矛盾修正')
        
        if reasoning_details['reasoning']['logic_consistency'] < 0.7:
            strategies.append('逻辑链条优化')
        
        # 基于认知破障引擎的分析
        if reasoning_details['cognitive']['hallucination_probability'] > 0.3:
            strategies.append('幻觉内容清理')
        
        if reasoning_details['cognitive']['confidence'] < 0.6:
            strategies.append('多维度验证增强')
        
        # 基于网状思维引擎的分析
        if mesh_result:
            if not mesh_result['dimension_enhancement']:
                strategies.append('维度信息补充')
            if not mesh_result['relationship_network']:
                strategies.append('关系网络构建')
            if not mesh_result['concept_extraction']:
                strategies.append('概念提取增强')
        
        # 生成总结
        if len(strategies) == 0:
            summary = '内容质量良好，仅需轻微优化'
            strategies.append('语义精炼')
        else:
            summary = f'需要应用{len(strategies)}种重构策略'
        
        return {
            'strategies': strategies,
            'summary': summary,
            'priority': assessment['reconstruction_priority']
        }
    
    def _apply_reconstruction_strategies(self, content: str, needs: Dict[str, Any], mesh_result: Dict = None) -> str:
        """应用重构策略
        
        重构策略分为两类：
        1. 语义精炼策略：修正逻辑矛盾、优化逻辑链条、清理幻觉内容、多维度验证增强、语义精炼
        2. 网状思维策略：维度信息补充、关系网络构建、概念提取增强
        
        智能改写主要应用语义精炼策略，网状思维策略用于补充维度信息和关系网络。
        """
        
        reconstructed = content
        strategies = needs['strategies']
        
        # 应用策略（简化版实现）
        for strategy in strategies:
            if strategy == '逻辑矛盾修正':
                reconstructed = self._fix_logical_contradictions(reconstructed)
            elif strategy == '逻辑链条优化':
                reconstructed = self._optimize_reasoning_chain(reconstructed)
            elif strategy == '幻觉内容清理':
                reconstructed = self._clean_hallucination_content(reconstructed)
            elif strategy == '多维度验证增强':
                reconstructed = self._enhance_multidimensional_validation(reconstructed)
            elif strategy == '语义精炼':
                reconstructed = self._refine_semantics(reconstructed)
            elif strategy == '维度信息补充' and mesh_result:
                # 使用网状思维引擎的维度信息补充
                reconstructed = self._enhance_with_dimension_info(reconstructed, mesh_result)
            elif strategy == '关系网络构建' and mesh_result:
                # 使用网状思维引擎的关系网络构建
                reconstructed = self._build_relationship_network(reconstructed, mesh_result)
            elif strategy == '概念提取增强' and mesh_result:
                # 使用网状思维引擎的概念提取增强
                reconstructed = self._enhance_with_concept_extraction(reconstructed, mesh_result)
        
        return reconstructed
    
    def _enhance_with_dimension_info(self, content: str, mesh_result: Dict) -> str:
        """使用网状思维引擎的维度信息增强内容"""
        # 简单实现：在内容末尾添加维度标签
        dimensions = mesh_result.get('dimension_enhancement', {})
        if dimensions:
            dimension_tags = []
            for dim_name, dim_values in dimensions.items():
                if dim_values:
                    dimension_tags.append(f"{dim_name}: {', '.join(dim_values)}")
            
            if dimension_tags:
                content += f"\n\n维度信息: {'; '.join(dimension_tags)}"
        
        return content
    
    def _build_relationship_network(self, content: str, mesh_result: Dict) -> str:
        """使用网状思维引擎的关系网络构建增强内容"""
        # 简单实现：在内容末尾添加关系信息
        relationships = mesh_result.get('relationship_network', {})
        if relationships:
            content += f"\n\n关系网络: {str(relationships)}"
        
        return content
    
    def _enhance_with_concept_extraction(self, content: str, mesh_result: Dict) -> str:
        """使用网状思维引擎的概念提取增强内容"""
        # 简单实现：在内容末尾添加概念标签
        concepts = mesh_result.get('concept_extraction', [])
        if concepts:
            content += f"\n\n核心概念: {', '.join(concepts)}"
        
        return content
    
    def _fix_logical_contradictions(self, content: str) -> str:
        """修正逻辑矛盾"""
        # 简化实现：识别并修正明显的逻辑矛盾
        # 实际应用中应该使用更复杂的逻辑分析
        
        # 示例：修正"既...又..."的矛盾表述
        contradictions = [
            (r'既(.+?)又(.+?)矛盾', r'\1与\2需要协调统一'),
            (r'一方面(.+?)另一方面(.+?)冲突', r'\1和\2需要综合考虑')
        ]
        
        for pattern, replacement in contradictions:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _optimize_reasoning_chain(self, content: str) -> str:
        """优化推理链条"""
        # 简化实现：添加逻辑连接词
        
        # 示例：优化推理表达
        optimizations = [
            (r'因为(.+?)所以(.+?)', r'基于\1，可以得出\2'),
            (r'如果(.+?)那么(.+?)', r'在\1的条件下，\2成立')
        ]
        
        for pattern, replacement in optimizations:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _clean_hallucination_content(self, content: str) -> str:
        """清理幻觉内容"""
        # 简化实现：移除过于绝对或不确定的表述
        
        # 示例：清理绝对化表述
        hallucinations = [
            (r'绝对(.+?)', r'通常\1'),
            (r'肯定(.+?)', r'很可能\1'),
            (r'毫无疑问(.+?)', r'有证据表明\1')
        ]
        
        for pattern, replacement in hallucinations:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _enhance_multidimensional_validation(self, content: str) -> str:
        """增强多维度验证"""
        # 简化实现：添加验证性表述
        
        # 示例：添加验证维度
        enhancements = [
            (r'(.+?)是(.+?)', r'\1在多个维度上表现为\2'),
            (r'(.+?)具有(.+?)', r'\1经过验证具有\2')
        ]
        
        for pattern, replacement in enhancements:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _refine_semantics(self, content: str) -> str:
        """语义精炼"""
        # 简化实现：优化表达清晰度
        
        # 示例：精炼语义表达
        refinements = [
            (r'非常(.+?)', r'\1'),  # 移除过度修饰
            (r'极其(.+?)', r'\1'),  # 移除过度修饰
            (r'大概(.+?)', r'\1'),  # 移除不确定表述
        ]
        
        for pattern, replacement in refinements:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _should_delete_memory(self, content: str, assessment: Dict[str, Any]) -> Tuple[bool, str]:
        """判断记忆是否应该被删除
        
        删除条件（满足任一即标记删除）：
        1. 极低可信度（< 0.2）且高风险（> 0.6）
        2. 内容为错误提示文本（包含"未找到""失败""错误"等）
        3. 内容过短（< 30字符）且无语义价值
        4. 测试碎片（包含test_type、test_agent等测试标识）
        5. 纯技术报错信息（无用户价值）
        6. 强规则：特定提示词文件缺失/测试提示词缺失，一律强制删除
        
        Returns:
            Tuple[bool, str]: (是否删除, 删除原因)
        """
        confidence = assessment['confidence']
        risk = assessment['risk_probability']
        content_stripped = content.strip()
        content_lower = content_stripped.lower()
        
        # 条件0：强规则 - 特定提示词缺失类错误，一律删除（✅ 修复：去除冒号限制）
        strong_error_keywords = [
            "提示词文件未找到",  # ✅ 去除冒号限制
            "base_prompt.txt",
            "test_prompt.md",
            "base_agent_prompt.md",
            "agent_prompts",
        ]
        if any(kw in content for kw in strong_error_keywords):
            return True, "强规则：提示词文件缺失类错误记忆，一律删除"
        
        # 条件1：极低可信度且高风险
        if confidence < 0.2 and risk > 0.6:
            return True, f"极低可信度({confidence:.2%})且高风险({risk:.2%})"
        
        # 条件2：错误提示文本
        error_patterns = [
            r"提示词文件未找到",
            r"文件未找到",
            r"base_prompt\.txt",
            r"test_prompt\.md",
            r"FileNotFoundError",
            r"ModuleNotFoundError",
            r"错误:.*未找到",
            r"Failed to.*",
        ]
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True, f"检测到错误提示文本（匹配模式: {pattern}）"
        
        # 条件3：测试碎片
        test_patterns = [
            r"test_type智能体",
            r"test_agent智能体",
            r"# test_",
            r"测试智能体",
        ]
        for pattern in test_patterns:
            if re.search(pattern, content):
                return True, f"检测到测试碎片（匹配模式: {pattern}）"
        
        # 条件4：内容过短且无语义价值
        if len(content_stripped) < 30:
            # 检查是否只包含特殊字符、数字、标点
            if re.match(r"^[\s\d\W]+$", content_stripped):
                return True, f"内容过短且仅包含特殊字符（长度: {len(content_stripped)}）"
            # 检查是否只是单行错误提示
            if "错误" in content_stripped or "失败" in content_stripped or "未" in content_stripped:
                if "提示词" in content_stripped or "文件" in content_stripped:
                    return True, f"单行错误提示（长度: {len(content_stripped)}）"
        
        # 条件5：纯技术报错信息（无用户价值）
        tech_error_patterns = [
            r"Traceback \(most recent call last\)",
            r"File \".*\.py\", line \\d+",
            r"raise .*Error",
            r"Exception:",
        ]
        for pattern in tech_error_patterns:
            if re.search(pattern, content):
                return True, f"纯技术报错信息（匹配模式: {pattern}）"
        
        # 不删除
        return False, ""

class BatchMemoryReconstructor:
    """批量记忆重构器"""
    
    def __init__(self):
        self.reconstruction_engine = MemoryReconstructionEngine()
        self.batch_size = 10
    
    def reconstruct_batch_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量重构记忆，并收集应删除的记忆ID"""
        
        results = {
            'total_memories': len(memories),
            'reconstructed_count': 0,
            'high_priority_count': 0,
            'deleted_count': 0,
            'deleted_memory_ids': [],  # 新增：应删除的记忆ID列表
            'reconstruction_results': [],
            'statistics': {
                'average_confidence': 0.0,
                'reconstruction_rate': 0.0,
                'deletion_rate': 0.0  # 新增：删除率
            }
        }
        
        total_confidence = 0.0
        
        for i, memory in enumerate(memories):
            content = memory.get('content', '')
            memory_id = memory.get('id', f'unknown_{i}')
            
            # 执行重构
            reconstruction_result = self.reconstruction_engine.reconstruct_memory(content)
            
            # 检查是否应删除
            if reconstruction_result.get('should_delete', False):
                results['deleted_count'] += 1
                results['deleted_memory_ids'].append({
                    'memory_id': memory_id,
                    'delete_reason': reconstruction_result.get('delete_reason', '未知原因'),
                    'original_content': content[:100] + '...' if len(content) > 100 else content
                })
                logger.info(f"记忆 {memory_id} 应删除: {reconstruction_result.get('delete_reason')}")
            else:
                # 统计信息（只统计保留的记忆）
                total_confidence += reconstruction_result['confidence']
                if reconstruction_result.get('reconstruction_applied', False):
                    results['reconstructed_count'] += 1
                    if reconstruction_result['assessment']['reconstruction_priority'] == '高优先级':
                        results['high_priority_count'] += 1
            
            results['reconstruction_results'].append({
                'original_content': content,
                'reconstruction_result': reconstruction_result,
                'memory_id': memory_id
            })
            
            # 进度显示
            if (i + 1) % self.batch_size == 0:
                logger.info(f"批量重构进度: {i+1}/{len(memories)}, 已标记删除: {results['deleted_count']}")
        
        # 计算统计信息
        retained_count = len(memories) - results['deleted_count']
        if retained_count > 0:
            results['statistics']['average_confidence'] = total_confidence / retained_count
            results['statistics']['reconstruction_rate'] = results['reconstructed_count'] / retained_count
        if len(memories) > 0:
            results['statistics']['deletion_rate'] = results['deleted_count'] / len(memories)
        
        logger.info(f"批量重构完成: 总计{len(memories)}条, 应删除{results['deleted_count']}条, 删除率{results['statistics']['deletion_rate']:.2%}")
        return results