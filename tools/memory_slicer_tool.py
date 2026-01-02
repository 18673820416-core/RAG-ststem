#!/usr/bin/env python3
# @self-expose: {"id": "memory_slicer_tool", "name": "多层次自适应分片工具", "type": "tool", "version": "2.3.0", "needs": {"deps": ["src.memory_bubble_manager", "src.cognitive_engines.memory_reconstruction_engine"], "resources": []}, "provides": {"capabilities": ["多层次自适应分片策略", "信息熵递归分片", "LLM精炼改写", "困惑度复合分片", "层级编码管理", "分片失败泡泡记录", "智能阈值范围优化", "自适应递归深度调整", "LLM重构有效性校验"], "methods": ["slice_text", "parse_slice_id", "get_slice_hierarchy", "hierarchical_retrieval"]}}
# -*- coding: utf-8 -*-
"""
记忆切片管理工具 - 多层次自适应分片策略

开发提示词来源：用户提出的"逻辑切片工具和事件二次切片工具统一打包成一个切片工具，
注册在工具箱里，专门负责记忆的切片管理"

重要原理记录：多层次自适应分片策略（2025年12月3日优化）
核心理念：成本与质量的梯度平衡，从低成本的纯算法分片到高成本的LLM辅助分片

分片流程（四层梯度）：
【第一层】信息熵递归分片（无LLM调用）
    ↓ 成功 → 完成
    ↓ 失败（达到最大递归深度）
【第二层】文本预处理 + LLM精炼改写 + 再次递归分片
    ↓ 成功 → 完成
    ↓ 失败
【第三层】困惑度计算 + 复合分片（需LLM）
    ↓ 成功 → 完成
    ↓ 失败
【第四层】强制分片 + 记录问题到泡泡

技术原理：
- 信息熵计算：H(X) = -∑ p(x) * log₂ p(x)，用于检测逻辑边界
- 困惑度估算：基于n-gram模型的简化困惑度计算（无需完整LLM）
- 层级编码：点分隔符（1, 1.1, 1.1.1）保持逻辑链结构
- 泡泡记录：分片失败时记录文件名、尝试方法、失败原因、优化建议
"""

import logging
import re
import math
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)

class MemorySlicerTool:
    """记忆切片管理工具 - 多层次自适应分片策略"""
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = Path(base_path)
        
        # 默认配置 - 多层次自适应分片策略
        self.default_config = {
            # 分层阈值：只有大切片才会被进一步分割
            'size_thresholds': [1000, 700, 500, 300, 200],
            'max_recursion_depth': 10,  # 最大递归深度
            'min_slice_size': 50,      # 最小切片大小
            'quality_threshold': 0.7,   # 切片质量阈值
            'enable_entropy_analysis': True,  # 启用信息熵分析
            'enable_semantic_evaluation': True,  # 启用语义质量评估
            'enable_hierarchical_encoding': True,  # 启用层级编码
            'enable_llm_refinement': True,  # 启用LLM精炼改写
            'enable_perplexity_analysis': True,  # 启用困惑度分析
            'enable_bubble_logging': True,  # 启用泡泡记录
        }
        
        # 初始化记忆泡泡管理器（用于记录分片失败）
        self.bubble_manager = None
        try:
            from src.memory_bubble_manager import MemoryBubbleManager
            self.bubble_manager = MemoryBubbleManager(agent_id="memory_slicer_tool")
            logger.info("泡泡管理器初始化成功")
        except Exception as e:
            logger.warning(f"泡泡管理器初始化失败，将跳过泡泡记录: {e}")
        
        # 初始化记忆重构引擎（用于LLM精炼改写）
        self.reconstruction_engine = None
        try:
            from src.cognitive_engines.memory_reconstruction_engine import MemoryReconstructionEngine
            self.reconstruction_engine = MemoryReconstructionEngine()
            logger.info("记忆重构引擎初始化成功")
        except Exception as e:
            logger.warning(f"记忆重构引擎初始化失败，将跳过LLM精炼: {e}")
        
        logger.info("记忆切片管理工具初始化完成（多层次自适应分片策略）")
    
    def slice_text(self, text: str, metadata: Dict[str, Any] = None, 
                   config: Dict[str, Any] = None, source_file: str = None) -> List[Dict[str, Any]]:
        """
        多层次自适应分片策略：从低成本算法分片到高成本LLM辅助分片
        
        Args:
            text: 待切片的文本内容
            metadata: 元数据信息
            config: 切片配置参数
            source_file: 源文件名（用于泡泡记录）
            
        Returns:
            切片结果列表，包含内容和元信息，包含层级编码
        """
        
        if not text or not text.strip():
            logger.warning("切片文本为空")
            return []
        
        # 合并配置
        merged_config = {**self.default_config, **(config or {})}
        
        # 🔧 优化：自适应递归与阈值调整（针对所有文本长度）
        try:
            if merged_config.get('adaptive_recursion', True):
                length = len(text)
                
                # 根据文本长度动态调整递归深度
                if length < 1000:
                    # 小文本：不需要递归，直接返回
                    merged_config['max_recursion_depth'] = 3
                elif length < 5000:
                    # 中等文本：适度递归（5层足够）
                    merged_config['max_recursion_depth'] = 5
                elif length < 50000:
                    # 较大文本：需要8-10层递归
                    merged_config['max_recursion_depth'] = max(merged_config.get('max_recursion_depth', 10), 8)
                elif length < 200000:
                    # 超大文本：增加3层
                    extra_depth = 3
                    merged_config['max_recursion_depth'] = max(merged_config.get('max_recursion_depth', 10), 10 + extra_depth)
                    if isinstance(merged_config.get('size_thresholds'), list) and merged_config['size_thresholds']:
                        merged_config['size_thresholds'] = [min(t + 300, 3000) for t in merged_config['size_thresholds']]
                else:
                    # 巨大文本：增加5层
                    extra_depth = 5
                    merged_config['max_recursion_depth'] = max(merged_config.get('max_recursion_depth', 10), 10 + extra_depth)
                    if isinstance(merged_config.get('size_thresholds'), list) and merged_config['size_thresholds']:
                        merged_config['size_thresholds'] = [min(t + 300, 3000) for t in merged_config['size_thresholds']]
                    # 大文本时适度放宽质量阈值，避免全量被过滤
                    if merged_config.get('quality_threshold', 0.7) > 0.6:
                        merged_config['quality_threshold'] = 0.6
        except Exception:
            pass
        
        # 分片尝试记录
        attempt_log = {
            'source_file': source_file or 'unknown',
            'text_length': len(text),
            'attempts': [],
            'success': False,
            'final_method': None
        }
        
        try:
            logger.info(f"开始多层次自适应分片，文本长度: {len(text)} 字符")
            
            # 【第一层】信息熵递归分片（无LLM调用）
            logger.info("【第一层】尝试信息熵递归分片...")
            attempt_log['attempts'].append('第一层：信息熵递归分片')
            
            recursive_slices, success = self._try_entropy_recursive_slice(
                text=text,
                metadata=metadata,
                config=merged_config
            )
            
            if success and recursive_slices:
                logger.info(f"【第一层】信息熵递归分片成功，生成 {len(recursive_slices)} 个切片")
                attempt_log['success'] = True
                attempt_log['final_method'] = '第一层：信息熵递归分片'
                return self._finalize_slices(recursive_slices, merged_config, attempt_log)
            
            logger.warning("【第一层】信息熵递归分片失败，进入第二层")
            
            # 【第二层】文本预处理 + LLM精炼改写 + 再次递归分片
            if merged_config['enable_llm_refinement'] and self.reconstruction_engine:
                logger.info("【第二层】尝试LLM精炼改写 + 递归分片...")
                attempt_log['attempts'].append('第二层：LLM精炼改写 + 递归分片')
                
                refined_slices, success = self._try_llm_refinement_slice(
                    text=text,
                    metadata=metadata,
                    config=merged_config
                )
                
                if success and refined_slices:
                    logger.info(f"【第二层】LLM精炼改写分片成功，生成 {len(refined_slices)} 个切片")
                    attempt_log['success'] = True
                    attempt_log['final_method'] = '第二层：LLM精炼改写 + 递归分片'
                    return self._finalize_slices(refined_slices, merged_config, attempt_log)
                
                logger.warning("【第二层】LLM精炼改写分片失败，进入第三层")
            
            # 【第三层】困惑度计算 + 复合分片
            if merged_config['enable_perplexity_analysis']:
                logger.info("【第三层】尝试困惑度复合分片...")
                attempt_log['attempts'].append('第三层：困惑度复合分片')
                
                perplexity_slices, success = self._try_perplexity_compound_slice(
                    text=text,
                    metadata=metadata,
                    config=merged_config
                )
                
                if success and perplexity_slices:
                    logger.info(f"【第三层】困惑度复合分片成功，生成 {len(perplexity_slices)} 个切片")
                    attempt_log['success'] = True
                    attempt_log['final_method'] = '第三层：困惑度复合分片'
                    return self._finalize_slices(perplexity_slices, merged_config, attempt_log)
                
                logger.warning("【第三层】困惑度复合分片失败，进入第四层")
            
            # 【第四层】强制分片 + 记录问题到泡泡
            logger.warning("【第四层】所有智能分片方法失败，执行强制分片")
            attempt_log['attempts'].append('第四层：强制分片（兜底）')
            
            forced_slices = self._force_slice_and_log(
                text=text,
                metadata=metadata,
                config=merged_config,
                attempt_log=attempt_log
            )
            
            attempt_log['success'] = len(forced_slices) > 0
            attempt_log['final_method'] = '第四层：强制分片（兜底）'
            
            return self._finalize_slices(forced_slices, merged_config, attempt_log)
            
        except Exception as e:
            logger.error(f"记忆切片完全失败: {e}")
            attempt_log['error'] = str(e)
            self._log_failure_to_bubble(attempt_log)
            return []
    
    # =========================================================================
    # 多层次分片策略方法
    # =========================================================================
    
    def _try_entropy_recursive_slice(self, text: str, metadata: Dict[str, Any], 
                                     config: Dict[str, Any]) -> tuple:
        """第一层：信息熵递归分片（无LLM调用）
        
        Returns:
            (slices, success): 切片结果和成功标志
        """
        try:
            # 执行递归分片
            slices = self._recursive_slice(
                text=text,
                metadata=metadata,
                config=config,
                current_depth=0,
                parent_id=""
            )
            
            if not slices:
                return [], False
            
            # 检查是否有切片是由于达到最大递归深度而强制生成的
            has_max_depth_slices = any(
                slice_data.get('slice_method') == 'recursive_max_depth' 
                for slice_data in slices
            )
            
            if has_max_depth_slices:
                logger.warning("检测到达到最大递归深度的切片，第一层分片认为失败")
                return slices, False
            
            return slices, True
            
        except Exception as e:
            logger.error(f"第一层信息熵递归分片失败: {e}")
            return [], False
    
    def _try_llm_refinement_slice(self, text: str, metadata: Dict[str, Any], 
                                  config: Dict[str, Any]) -> tuple:
        """第二层：LLM精炼改写 + 再次递归分片
        
        Returns:
            (slices, success): 切片结果和成功标志
        """
        try:
            if not self.reconstruction_engine:
                logger.warning("LLM重构引擎未初始化，跳过第二层")
                return [], False
            
            logger.info("使用LLM进行文本精炼改写...")
            
            # 调用记忆重构引擎进行文本精炼
            reconstruction_result = self.reconstruction_engine.reconstruct_memory(
                memory_content=text,
                context=metadata or {}
            )
            
            # 🔧 修复：正确判定重构是否有效
            # 原逻辑：if refined_text == text → 失败（错误！）
            # 新逻辑：检查以下条件
            refined_text = reconstruction_result.get('reconstructed_content', '')
            confidence = reconstruction_result.get('confidence', 0.0)
            should_delete = reconstruction_result.get('should_delete', False)
            
            # 判定条件：
            # 1. 不应该删除
            # 2. 有效内容（非空且长度合理）
            # 3. 可信度达标（>70%）
            if should_delete:
                logger.warning(f"LLM重构建议删除此记忆：{reconstruction_result.get('delete_reason', '未知')}")
                return [], False
            
            if not refined_text or len(refined_text.strip()) < 20:
                logger.warning("LLM精炼返回无效内容（过短或为空）")
                return [], False
            
            if confidence < 0.7:
                logger.warning(f"LLM精炼可信度不足：{confidence:.2%} < 70%")
                return [], False
            
            logger.info(f"LLM精炼完成，原文本 {len(text)} 字符 -> 精炼后 {len(refined_text)} 字符，可信度: {confidence:.2%}")
            
            # 对精炼后的文本再次执行递归分片
            slices = self._recursive_slice(
                text=refined_text,
                metadata=metadata,
                config=config,
                current_depth=0,
                parent_id=""
            )
            
            if not slices:
                return [], False
            
            # 标记切片经过LLM精炼
            for slice_data in slices:
                slice_data['llm_refined'] = True
                slice_data['original_text_length'] = len(text)
                slice_data['refined_text_length'] = len(refined_text)
            
            return slices, True
            
        except Exception as e:
            logger.error(f"第二层LLM精炼改写分片失败: {e}")
            return [], False
    
    def _try_perplexity_compound_slice(self, text: str, metadata: Dict[str, Any], 
                                       config: Dict[str, Any]) -> tuple:
        """第三层：困惑度计算 + 复合分片
        
        Returns:
            (slices, success): 切片结果和成功标志
        """
        try:
            logger.info("计算文本困惑度，查找困惑度变化点...")
            
            # 计算困惑度分割点
            perplexity_split_points = self._find_perplexity_boundaries(text, config)
            
            if not perplexity_split_points:
                logger.warning("未找到有效的困惑度分割点")
                return [], False
            
            # 基于困惑度分割点进行分片
            slices = []
            start_pos = 0
            
            for i, split_point in enumerate(perplexity_split_points):
                end_pos = split_point
                segment = text[start_pos:end_pos].strip()
                
                if len(segment) >= config['min_slice_size']:
                    slice_id = f"{i + 1}"
                    slices.append({
                        'content': segment,
                        'slice_id': slice_id,
                        'slice_depth': 0,
                        'parent_id': '',
                        'slice_method': 'perplexity_compound',
                        'entropy': self._calculate_entropy(segment),
                        'perplexity': self._calculate_perplexity(segment)
                    })
                
                start_pos = end_pos
            
            # 处理剩余文本
            if start_pos < len(text):
                remaining = text[start_pos:].strip()
                if len(remaining) >= config['min_slice_size']:
                    slices.append({
                        'content': remaining,
                        'slice_id': f"{len(slices) + 1}",
                        'slice_depth': 0,
                        'parent_id': '',
                        'slice_method': 'perplexity_compound',
                        'entropy': self._calculate_entropy(remaining),
                        'perplexity': self._calculate_perplexity(remaining)
                    })
            
            if not slices:
                return [], False
            
            logger.info(f"困惑度复合分片生成 {len(slices)} 个切片")
            return slices, True
            
        except Exception as e:
            logger.error(f"第三层困惑度复合分片失败: {e}")
            return [], False
    
    def _force_slice_and_log(self, text: str, metadata: Dict[str, Any], 
                            config: Dict[str, Any], attempt_log: Dict) -> List[Dict[str, Any]]:
        """第四层：强制分片 + 记录问题到泡泡
        
        Returns:
            强制分片结果
        """
        logger.warning("执行强制分片作为兜底策略")
        
        # 执行简单的强制分片
        slices = []
        max_size = config['size_thresholds'][0] if config['size_thresholds'] else 1000
        
        start = 0
        slice_index = 0
        
        while start < len(text):
            end = min(start + max_size, len(text))
            
            # 尝试在句子边界处分割
            if end < len(text):
                sentence_end = text.rfind('。', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('.', start, end)
                
                if sentence_end != -1 and sentence_end > start + max_size * 0.5:
                    end = sentence_end + 1
            
            segment = text[start:end].strip()
            
            if segment:
                slices.append({
                    'content': segment,
                    'slice_id': f"{slice_index + 1}",
                    'slice_depth': 0,
                    'parent_id': '',
                    'slice_method': 'forced_fallback',
                    'entropy': self._calculate_entropy(segment),
                    'warning': '此切片通过强制分片生成，可能破坏逻辑完整性'
                })
                slice_index += 1
            
            start = end
        
        # 记录失败到泡泡
        self._log_failure_to_bubble(attempt_log)
        
        return slices
    
    def _recursive_slice(self, text: str, metadata: Dict[str, Any], 
                        config: Dict[str, Any], current_depth: int, 
                        parent_id: str) -> List[Dict[str, Any]]:
        """
        递归分片核心方法 - 基于信息熵驱动的递归分片机制
        
        Args:
            text: 待分片文本
            metadata: 元数据
            config: 配置参数
            current_depth: 当前递归深度
            parent_id: 父级切片ID
            
        Returns:
            分片结果列表，包含层级编码
        """
        
        # 检查递归深度限制
        if current_depth >= config['max_recursion_depth']:
            logger.warning(f"达到最大递归深度 {current_depth}，将当前文本作为最终切片")
            # 当达到最大递归深度时，将当前文本作为一个切片返回，而不是空列表
            slice_id = self._generate_slice_id(parent_id, current_depth, 0)
            return [{
                'content': text,
                'slice_id': slice_id,
                'slice_depth': current_depth,
                'parent_id': parent_id,
                'slice_method': 'recursive_max_depth',
                'entropy': self._calculate_entropy(text)
            }]
        
        # 获取当前层级的阈值
        if current_depth < len(config['size_thresholds']):
            current_threshold = config['size_thresholds'][current_depth]
        else:
            # 如果深度超过阈值列表长度，使用最后一个阈值
            current_threshold = config['size_thresholds'][-1]
        
        min_size = config['min_slice_size']
        
        # 如果文本长度小于等于当前阈值，直接返回
        if len(text) <= current_threshold:
            slice_id = self._generate_slice_id(parent_id, current_depth, 0)
            return [{
                'content': text,
                'slice_id': slice_id,
                'slice_depth': current_depth,
                'parent_id': parent_id,
                'slice_method': 'recursive_final',
                'entropy': self._calculate_entropy(text)
            }]
        
        # 信息熵检测：计算文本的信息熵
        entropy = self._calculate_entropy(text)
        
        # 如果信息熵较低（内容单一），直接返回
        if entropy < 2.0 and len(text) <= current_threshold * 1.5:
            slice_id = self._generate_slice_id(parent_id, current_depth, 0)
            return [{
                'content': text,
                'slice_id': slice_id,
                'slice_depth': current_depth,
                'parent_id': parent_id,
                'slice_method': 'recursive_low_entropy',
                'entropy': entropy
            }]
        
        # 基于信息熵和逻辑边界进行分片
        slices = []
        
        # 1. 查找最佳分割点
        split_points = self._find_optimal_split_points(text, current_threshold, entropy)
        
        if not split_points:
            # 如果没有找到合适的分割点，尝试强制分割
            split_points = self._force_split_by_size(text, current_threshold)
        
        # 2. 基于分割点进行分片
        start_pos = 0
        for i, split_point in enumerate(split_points):
            end_pos = split_point
            segment = text[start_pos:end_pos]
            
            if len(segment) >= min_size:
                slice_id = self._generate_slice_id(parent_id, current_depth, i)
                
                # 递归分片子片段
                child_slices = self._recursive_slice(
                    text=segment,
                    metadata=metadata,
                    config=config,
                    current_depth=current_depth + 1,
                    parent_id=slice_id
                )
                
                slices.extend(child_slices)
            
            start_pos = end_pos
        
        # 处理剩余文本
        if start_pos < len(text):
            remaining_text = text[start_pos:]
            if len(remaining_text) >= min_size:
                slice_id = self._generate_slice_id(parent_id, current_depth, len(split_points))
                
                child_slices = self._recursive_slice(
                    text=remaining_text,
                    metadata=metadata,
                    config=config,
                    current_depth=current_depth + 1,
                    parent_id=slice_id
                )
                
                slices.extend(child_slices)
        
        return slices
    
    def _generate_slice_id(self, parent_id: str, depth: int, index: int) -> str:
        """生成层级编码的切片ID"""
        if not parent_id:
            return f"{index + 1}"  # 第一层：1, 2, 3...
        else:
            return f"{parent_id}.{index + 1}"  # 子层：1.1, 1.2, 2.1...
    
    def parse_slice_id(self, slice_id: str) -> Dict[str, Any]:
        """
        解析层级编码，提取层级信息
        
        Args:
            slice_id: 层级编码的切片ID
            
        Returns:
            包含层级信息的字典
        """
        if not slice_id:
            return {'depth': 0, 'path': [], 'is_root': True}
        
        parts = slice_id.split('.')
        depth = len(parts)
        
        return {
            'depth': depth,
            'path': [int(part) for part in parts],
            'is_root': depth == 1,
            'parent_id': '.'.join(parts[:-1]) if depth > 1 else "",
            'level': parts[-1],
            'full_path': slice_id
        }
    
    def get_slice_hierarchy(self, slices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建切片层级结构
        
        Args:
            slices: 切片列表
            
        Returns:
            层级结构字典
        """
        hierarchy = {}
        
        for slice_data in slices:
            slice_id = slice_data.get('slice_id', '')
            if not slice_id:
                continue
                
            parsed = self.parse_slice_id(slice_id)
            
            # 构建层级路径
            current_level = hierarchy
            for level in parsed['path'][:-1]:
                if str(level) not in current_level:
                    current_level[str(level)] = {'children': {}, 'slices': []}
                current_level = current_level[str(level)]['children']
            
            # 添加当前切片
            current_level_key = str(parsed['path'][-1])
            if current_level_key not in current_level:
                current_level[current_level_key] = {'children': {}, 'slices': []}
            
            current_level[current_level_key]['slices'].append(slice_data)
        
        return hierarchy
    
    def hierarchical_retrieval(self, query: str, slices: List[Dict[str, Any]], 
                              top_k: int = 10) -> List[Dict[str, Any]]:
        """
        基于层级编码的智能检索
        
        Args:
            query: 查询文本
            slices: 切片列表
            top_k: 返回结果数量
            
        Returns:
            排序后的检索结果
        """
        # 1. 计算每个切片的相似度
        scored_slices = []
        
        for slice_data in slices:
            content = slice_data.get('content', '')
            
            # 简单的文本相似度计算（可以替换为更复杂的语义相似度算法）
            similarity = self._calculate_text_similarity(query, content)
            
            # 考虑层级深度权重：深层切片权重更高
            slice_id = slice_data.get('slice_id', '')
            parsed = self.parse_slice_id(slice_id)
            depth_weight = 1.0 + (parsed['depth'] * 0.1)  # 每层增加10%权重
            
            # 考虑语义质量权重
            quality_weight = slice_data.get('semantic_quality', 0.5)
            
            # 综合得分
            final_score = similarity * depth_weight * quality_weight
            
            scored_slices.append({
                'slice_data': slice_data,
                'similarity': similarity,
                'depth_weight': depth_weight,
                'quality_weight': quality_weight,
                'final_score': final_score
            })
        
        # 2. 按得分排序
        scored_slices.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 3. 返回top_k结果
        return [item['slice_data'] for item in scored_slices[:top_k]]
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的词频相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _find_optimal_split_points(self, text: str, threshold: int, entropy: float) -> List[int]:
        """基于信息熵和逻辑边界查找最佳分割点"""
        
        split_points = []
        
        # 逻辑边界模式
        boundary_patterns = [
            r'[。！？!?]\s*\n',  # 句子结束+换行
            r'[。！？!?]\s{2,}',  # 句子结束+多个空格
            r'\n\s*\n',         # 空行
            r'##\s+',            # 标题标记
            r'\d+\.\s+',        # 数字标题
        ]
        
        # 查找所有逻辑边界
        boundaries = []
        for pattern in boundary_patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                boundaries.append(match.end())
        
        boundaries = sorted(set(boundaries))
        
        # 滑动窗口分析信息熵变化
        window_size = min(100, len(text) // 10)
        entropy_changes = []
        
        for i in range(window_size, len(text) - window_size, window_size // 2):
            prev_window = text[max(0, i - window_size):i]
            next_window = text[i:min(len(text), i + window_size)]
            
            prev_entropy = self._calculate_entropy(prev_window)
            next_entropy = self._calculate_entropy(next_window)
            
            entropy_change = abs(next_entropy - prev_entropy)
            entropy_changes.append((i, entropy_change))
        
        # 选择信息熵变化最大的点作为候选分割点
        entropy_changes.sort(key=lambda x: x[1], reverse=True)
        candidate_points = [point for point, _ in entropy_changes[:5]]
        
        # 合并逻辑边界和熵变化点
        all_candidates = sorted(set(boundaries + candidate_points))
        
        # 选择满足阈值要求的分割点（优化版）
        current_pos = 0
        for candidate in all_candidates:
            segment_length = candidate - current_pos
            
            # 🔧 修复：放宽阈值范围，从±30%改为±50%，避免合理分割被拒绝
            # 原逻辑：threshold * 0.7 ~ 1.3（700-1300）对2151字符的文本会失败
            # 新逻辑：threshold * 0.5 ~ 2.0（500-2000）更合理
            min_acceptable = threshold * 0.5  # 最小50%
            max_acceptable = threshold * 2.0  # 最大200%
            
            if segment_length >= min_acceptable and segment_length <= max_acceptable:
                split_points.append(candidate)
                current_pos = candidate
            elif segment_length > max_acceptable:
                # 如果段长仍然过大，智能添加中间点
                # 优先选择逻辑边界，如果没有则均分
                mid_boundary = self._find_nearest_boundary(text, current_pos, candidate)
                if mid_boundary:
                    split_points.append(mid_boundary)
                    current_pos = mid_boundary
                else:
                    mid_point = current_pos + segment_length // 2
                    split_points.append(mid_point)
                    current_pos = mid_point
        
        return split_points
    
    def _find_nearest_boundary(self, text: str, start: int, end: int) -> Optional[int]:
        """在指定范围内查找最近的逻辑边界"""
        middle = (start + end) // 2
        search_range = (end - start) // 4  # 在中点±25%范围内查找
        
        search_start = max(start, middle - search_range)
        search_end = min(end, middle + search_range)
        
        # 在中点附近查找逻辑边界
        boundary_patterns = [
            r'[。！？!?]\s*\n',  # 句子结束+换行（优先级最高）
            r'\n\s*\n',         # 空行
            r'[。！？!?]',       # 句子结束
        ]
        
        best_boundary = None
        min_distance = float('inf')
        
        for pattern in boundary_patterns:
            for match in re.finditer(pattern, text[search_start:search_end]):
                boundary_pos = search_start + match.end()
                distance = abs(boundary_pos - middle)
                
                if distance < min_distance:
                    min_distance = distance
                    best_boundary = boundary_pos
        
        return best_boundary
    
    def _force_split_by_size(self, text: str, threshold: int) -> List[int]:
        """基于大小强制分割"""
        split_points = []
        
        current_pos = 0
        while current_pos < len(text):
            next_pos = current_pos + threshold
            
            if next_pos >= len(text):
                break
            
            # 尝试在句子边界附近分割
            sentence_end = text.rfind('。', current_pos, next_pos)
            if sentence_end != -1 and sentence_end > current_pos + threshold * 0.5:
                split_points.append(sentence_end + 1)  # 包括句号
                current_pos = sentence_end + 1
            else:
                # 如果没有找到句子边界，在空格处分割
                space_pos = text.rfind(' ', current_pos, next_pos)
                if space_pos != -1 and space_pos > current_pos + threshold * 0.5:
                    split_points.append(space_pos + 1)
                    current_pos = space_pos + 1
                else:
                    # 强制在阈值位置分割
                    split_points.append(next_pos)
                    current_pos = next_pos
        
        return split_points
    
    def _split_large_segment(self, segment: str, max_size: int) -> List[str]:
        """分割过大的文本段"""
        
        if len(segment) <= max_size:
            return [segment]
        
        # 尝试在句子边界分割
        sentence_pattern = r'[。！？!?]\s*'
        sentences = re.split(sentence_pattern, segment)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # 添加标点符号
            sentence_with_punct = sentence + "。"
            
            if len(current_chunk) + len(sentence_with_punct) <= max_size:
                current_chunk += sentence_with_punct
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence_with_punct
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # 如果仍然过大，强制分割
        if len(chunks) == 0 or any(len(chunk) > max_size * 1.5 for chunk in chunks):
            chunks = [segment[i:i+max_size] for i in range(0, len(segment), max_size)]
        
        return chunks
    
    def _optimize_slices_by_entropy(self, slices: List[Dict[str, Any]], 
                                  config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于信息熵优化分片"""
        
        if not config['enable_entropy_analysis']:
            return slices
        
        optimized_slices = []
        
        for slice_data in slices:
            content = slice_data['content']
            
            # 计算信息熵
            entropy = self._calculate_entropy(content)
            
            # 基于信息熵决定是否需要进一步分割
            if entropy > 4.0 and len(content) > config['max_slice_size'] * 0.8:
                # 高信息熵且长度接近上限，考虑分割
                sub_slices = self._split_by_entropy(content, config)
                
                for i, sub_content in enumerate(sub_slices):
                    sub_slice_data = slice_data.copy()
                    sub_slice_data['content'] = sub_content
                    sub_slice_data['entropy'] = self._calculate_entropy(sub_content)
                    sub_slice_data['slice_method'] = 'entropy_optimized'
                    sub_slice_data['slice_level'] = 'optimized'
                    optimized_slices.append(sub_slice_data)
            else:
                slice_data['entropy'] = entropy
                slice_data['slice_method'] = 'logic_boundary_only'
                optimized_slices.append(slice_data)
        
        return optimized_slices
    
    def _calculate_entropy(self, text: str) -> float:
        """计算文本信息熵 H(X) = -∑ p(x) * log₂ p(x)"""
        
        if not text:
            return 0.0
        
        # 计算字符频率
        char_freq = {}
        total_chars = len(text)
        
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        # 计算熵
        entropy = 0.0
        for count in char_freq.values():
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_perplexity(self, text: str, n: int = 2) -> float:
        """计算文本困惑度（基于n-gram的简化实现，无需LLM）
        
        困惑度公式：Perplexity = 2^H(X)
        这里使用简化的n-gram模型估算
        
        Args:
            text: 文本内容
            n: n-gram的n值（默认2-gram）
            
        Returns:
            困惑度值
        """
        if not text or len(text) < n:
            return 0.0
        
        try:
            # 构建n-gram
            ngrams = []
            for i in range(len(text) - n + 1):
                ngram = text[i:i+n]
                ngrams.append(ngram)
            
            if not ngrams:
                return 0.0
            
            # 计算n-gram频率
            ngram_freq = Counter(ngrams)
            total_ngrams = len(ngrams)
            
            # 计算交叉熵
            cross_entropy = 0.0
            for count in ngram_freq.values():
                probability = count / total_ngrams
                if probability > 0:
                    cross_entropy -= probability * math.log2(probability)
            
            # 困惑度 = 2^(交叉熵)
            perplexity = math.pow(2, cross_entropy)
            
            return perplexity
            
        except Exception as e:
            logger.error(f"计算困惑度失败: {e}")
            return 0.0
    
    def _find_perplexity_boundaries(self, text: str, config: Dict[str, Any]) -> List[int]:
        """基于困惑度变化查找分割边界
        
        Args:
            text: 文本内容
            config: 配置参数
            
        Returns:
            分割点位置列表
        """
        if len(text) < 200:
            return []
        
        # 滑动窗口大小
        window_size = min(100, len(text) // 10)
        step_size = window_size // 2
        
        # 计算每个窗口的困惑度
        perplexity_values = []
        
        for i in range(0, len(text) - window_size + 1, step_size):
            window_text = text[i:i+window_size]
            perplexity = self._calculate_perplexity(window_text)
            perplexity_values.append((i, perplexity))
        
        if len(perplexity_values) < 3:
            return []
        
        # 查找困惑度变化大的位置
        split_points = []
        threshold = config['size_thresholds'][0] if config['size_thresholds'] else 1000
        
        for i in range(1, len(perplexity_values) - 1):
            prev_perplexity = perplexity_values[i-1][1]
            curr_perplexity = perplexity_values[i][1]
            next_perplexity = perplexity_values[i+1][1]
            
            # 计算困惑度变化率
            perplexity_change = abs(curr_perplexity - prev_perplexity) + abs(next_perplexity - curr_perplexity)
            
            # 如果变化率较大，且满足长度要求，添加分割点
            if perplexity_change > 5.0:  # 困惑度变化阈值
                position = perplexity_values[i][0]
                
                # 检查是否满足最小间隔
                if not split_points or position - split_points[-1] >= threshold * 0.5:
                    split_points.append(position)
        
        return split_points
    
    def _finalize_slices(self, slices: List[Dict[str, Any]], 
                        config: Dict[str, Any], 
                        attempt_log: Dict) -> List[Dict[str, Any]]:
        """完成切片后处理：质量评估、过滤、添加元信息
        
        Args:
            slices: 原始切片列表
            config: 配置参数
            attempt_log: 尝试日志
            
        Returns:
            处理后的切片列表
        """
        # 语义质量评估
        if config['enable_semantic_evaluation']:
            evaluated_slices = self._evaluate_semantic_quality(slices)
            logger.info("语义质量评估完成")
        else:
            evaluated_slices = slices
        
        # 质量过滤
        if config['quality_threshold'] > 0:
            filtered_slices = [
                slice_data for slice_data in evaluated_slices 
                if slice_data.get('semantic_quality', 0) >= config['quality_threshold']
            ]
            logger.info(f"质量过滤: {len(evaluated_slices)} -> {len(filtered_slices)} 个切片")
            # 若全部被过滤，放宽为返回未过滤的评估切片（避免切片结果为空导致早停）
            final_slices = filtered_slices if filtered_slices else evaluated_slices
            relaxed = filtered_slices == []
        else:
            final_slices = evaluated_slices
            relaxed = False
        
        # 添加工具信息和重要性评估
        for i, slice_data in enumerate(final_slices):
            slice_data['slicer_tool'] = 'memory_slicer'
            slice_data['slice_timestamp'] = datetime.now().isoformat()
            slice_data['slice_config'] = {
                'method': attempt_log.get('final_method', 'unknown'),
                'attempts': len(attempt_log.get('attempts', [])),
                'thresholds': config['size_thresholds'],
                'quality_filter_relaxed': relaxed
            }
            
            # 如果切片缺少importance字段，则基于语义质量计算重要性
            if 'importance' not in slice_data:
                semantic_quality = slice_data.get('semantic_quality', 0.5)
                content = slice_data.get('content', '')
                importance = self._calculate_slice_importance(content, semantic_quality)
                slice_data['importance'] = importance
        
        logger.info(f"记忆切片完成，共生成 {len(final_slices)} 个高质量切片")
        return final_slices
    
    def _log_failure_to_bubble(self, attempt_log: Dict):
        """记录分片失败信息到泡泡
        
        Args:
            attempt_log: 尝试日志，包含文件名、尝试方法、失败原因等
        """
        if not self.bubble_manager or not self.default_config['enable_bubble_logging']:
            return
        
        try:
            # 构建泡泡内容
            bubble_content = f"""
分片失败记录

文件名: {attempt_log.get('source_file', 'unknown')}
文本长度: {attempt_log.get('text_length', 0)} 字符

尝试的方法：
{chr(10).join(f'- {method}' for method in attempt_log.get('attempts', []))}

最终使用方法: {attempt_log.get('final_method', '未知')}
是否成功: {'\u6210\u529f' if attempt_log.get('success') else '\u5931\u8d25'}

优化建议：
1. 检查文本结构是否异常（如过长、缺乏逻辑边界等）
2. 考虑调整size_thresholds配置
3. 如果多LLM精炼失败，检查记忆重构引擎配置
4. 如果困惑度分片失败，检查文本是否具有明显的主题转换
"""
            
            if 'error' in attempt_log:
                bubble_content += f"\n\n错误信息: {attempt_log['error']}"
            
            # 记录到泡泡
            bubble_id = self.bubble_manager.quick_note(
                category="分片问题",
                content=bubble_content,
                context={
                    'source_file': attempt_log.get('source_file'),
                    'text_length': attempt_log.get('text_length'),
                    'attempts': attempt_log.get('attempts'),
                    'final_method': attempt_log.get('final_method')
                },
                priority="high" if not attempt_log.get('success') else "normal"
            )
            
            logger.info(f"分片失败信息已记录到泡泡: {bubble_id}")
            
        except Exception as e:
            logger.error(f"记录分片失败信息到泡泡失败: {e}")
    
    def _split_by_entropy(self, text: str, config: Dict[str, Any]) -> List[str]:
        """基于信息熵进行分割"""
        
        # 在信息熵变化较大的位置进行分割
        window_size = min(100, len(text) // 10)
        entropy_values = []
        
        # 计算滑动窗口的信息熵
        for i in range(0, len(text) - window_size + 1, window_size // 2):
            window_text = text[i:i+window_size]
            entropy = self._calculate_entropy(window_text)
            entropy_values.append((i, entropy))
        
        # 找到熵值变化较大的位置作为分割点
        split_points = [0]
        for i in range(1, len(entropy_values) - 1):
            prev_entropy = entropy_values[i-1][1]
            curr_entropy = entropy_values[i][1]
            next_entropy = entropy_values[i+1][1]
            
            # 计算熵值变化率
            entropy_change = abs(curr_entropy - prev_entropy) + abs(next_entropy - curr_entropy)
            
            if entropy_change > 1.0:  # 变化阈值
                split_points.append(entropy_values[i][0])
        
        split_points.append(len(text))
        
        # 基于分割点进行分割
        chunks = []
        for i in range(len(split_points) - 1):
            start = split_points[i]
            end = split_points[i + 1]
            chunk = text[start:end]
            if len(chunk) >= config['min_slice_size']:
                chunks.append(chunk)
        
        return chunks
    
    def _evaluate_semantic_quality(self, slices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """评估切片语义质量"""
        
        evaluated_slices = []
        
        for slice_data in slices:
            content = slice_data['content']
            
            # 基于多个指标评估语义质量
            quality_score = self._calculate_semantic_quality(content)
            
            slice_data['semantic_quality'] = quality_score
            evaluated_slices.append(slice_data)
        
        return evaluated_slices
    
    def _calculate_semantic_quality(self, content: str) -> float:
        """计算语义质量分数"""
        
        if not content:
            return 0.0
        
        # 1. 信息熵因子
        entropy = self._calculate_entropy(content)
        entropy_factor = min(1.0, entropy / 6.0)  # 假设最大熵为6
        
        # 2. 长度因子
        length = len(content)
        if 200 <= length <= 1500:
            length_factor = 0.9
        elif length > 1500:
            length_factor = 0.7
        else:
            length_factor = 0.5
        
        # 3. 结构完整性因子
        has_complete_sentences = any(marker in content for marker in ['。', '！', '？', '.', '!', '?'])
        structure_factor = 0.8 if has_complete_sentences else 0.4
        
        # 4. 词汇多样性因子
        unique_words = len(set(re.findall(r'[\w\u4e00-\u9fff]+', content)))
        total_words = len(re.findall(r'[\w\u4e00-\u9fff]+', content))
        diversity_factor = unique_words / max(1, total_words)
        
        # 综合质量分数
        quality = (entropy_factor * 0.3 + length_factor * 0.25 + 
                  structure_factor * 0.25 + diversity_factor * 0.2)
        
        return min(1.0, max(0.0, quality))
    
    def _calculate_slice_importance(self, content: str, semantic_quality: float) -> float:
        """计算切片重要性"""
        
        # 基础重要性基于语义质量
        base_importance = semantic_quality
        
        # 长度因子：适中长度的内容更重要
        content_length = len(content)
        if 100 <= content_length <= 2000:
            length_factor = 0.8
        elif content_length > 2000:
            # 过长内容可能包含冗余信息
            length_factor = 0.6
        else:
            # 过短内容信息量不足
            length_factor = 0.4
        
        # 信息密度因子：基于独特字符比例
        unique_chars = len(set(content))
        density_factor = min(1.0, unique_chars / max(1, content_length) * 2)
        
        # 结构完整性因子：检查是否有完整的句子结构
        has_complete_structure = any(marker in content for marker in ['。', '！', '？', '.', '!', '?'])
        structure_factor = 0.9 if has_complete_structure else 0.6
        
        # 综合重要性计算
        importance = base_importance * 0.4 + length_factor * 0.2 + density_factor * 0.2 + structure_factor * 0.2
        
        return min(1.0, max(0.1, importance))
    
    def slice_file(self, file_path: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        对文件内容进行切片
        
        Args:
            file_path: 文件路径
            config: 切片配置
            
        Returns:
            切片结果列表
        """
        
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return []
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"文件内容为空: {file_path}")
                return []
            
            # 构建元数据
            metadata = {
                'source_type': 'file',
                'source_path': file_path,
                'file_name': full_path.name,
                'file_size': len(content)
            }
            
            # 调用文本切片
            slices = self.slice_text(content, metadata, config)
            
            logger.info(f"文件切片完成: {file_path} -> {len(slices)} 个切片")
            return slices
            
        except Exception as e:
            logger.error(f"文件切片失败 {file_path}: {e}")
            return []
    
    def batch_slice_files(self, file_pattern: str = "*.txt", 
                         config: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量切片多个文件
        
        Args:
            file_pattern: 文件匹配模式
            config: 切片配置
            
        Returns:
            文件名到切片列表的映射
        """
        
        results = {}
        
        try:
            # 查找匹配的文件
            matched_files = list(self.base_path.rglob(file_pattern))
            
            if not matched_files:
                logger.warning(f"未找到匹配的文件: {file_pattern}")
                return results
            
            logger.info(f"找到 {len(matched_files)} 个匹配文件，开始批量切片")
            
            for file_path in matched_files:
                relative_path = str(file_path.relative_to(self.base_path))
                
                # 切片当前文件
                slices = self.slice_file(relative_path, config)
                results[relative_path] = slices
                
                logger.info(f"文件切片完成: {relative_path} -> {len(slices)} 个切片")
            
            logger.info(f"批量切片完成，共处理 {len(results)} 个文件")
            return results
            
        except Exception as e:
            logger.error(f"批量切片失败: {e}")
            return {}

# 兼容性接口，保持与原有代码一致
def create_memory_slicer() -> MemorySlicerTool:
    """创建记忆切片器实例"""
    return MemorySlicerTool()