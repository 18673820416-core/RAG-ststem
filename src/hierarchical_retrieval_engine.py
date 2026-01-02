#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
层级编码智能检索引擎
开发提示词来源：基于信息熵驱动的递归分片机制需要配套的智能检索功能

核心功能：
1. 层级编码解析和路径分析
2. 基于深度的权重调整
3. 多层级检索结果融合
4. 智能路径推荐和上下文扩展
"""
# @self-expose: {"id": "hierarchical_retrieval_engine", "name": "Hierarchical Retrieval Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Hierarchical Retrieval Engine功能"]}}

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
import re
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

@dataclass
class HierarchicalSlice:
    """层级切片类"""
    slice_id: str
    content: str
    depth: int
    parent_id: Optional[str]
    sequence_order: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        # 自动解析层级路径
        self.hierarchical_path = self.slice_id
        self.parts = self.hierarchical_path.split('.')
    
    def __hash__(self):
        """支持哈希操作，用于set操作"""
        return hash(self.slice_id)
    
    def __eq__(self, other):
        """支持相等比较"""
        if not isinstance(other, HierarchicalSlice):
            return False
        return self.slice_id == other.slice_id
        
    def get_ancestor_ids(self) -> List[str]:
        """获取所有祖先ID"""
        if len(self.parts) <= 1:
            return []
        
        ancestors = []
        for i in range(1, len(self.parts)):
            ancestor_id = '.'.join(self.parts[:i])
            ancestors.append(ancestor_id)
        
        return ancestors
    
    def get_sibling_ids(self, all_slices: List['HierarchicalSlice']) -> List[str]:
        """获取兄弟节点ID"""
        if len(self.parts) <= 1:
            return []
        
        parent_id = '.'.join(self.parts[:-1])
        siblings = []
        
        for slice_obj in all_slices:
            if slice_obj.slice_id == self.slice_id:
                continue
            
            if len(slice_obj.parts) == len(self.parts):
                sibling_parent_id = '.'.join(slice_obj.parts[:-1])
                if sibling_parent_id == parent_id:
                    siblings.append(slice_obj.slice_id)
        
        return siblings

@dataclass
class HierarchicalRetrievalResult:
    """层级检索结果类"""
    query_slice: HierarchicalSlice
    retrieved_slices: List[Tuple[HierarchicalSlice, float]]  # (slice, similarity_score)
    retrieval_method: str
    depth_weights: Dict[int, float]
    context_expansion: List[HierarchicalSlice]
    total_slices_searched: int
    retrieval_time: float
    
    def get_best_matches(self, top_k: int = 5) -> List[HierarchicalSlice]:
        """获取最佳匹配结果"""
        return [item[0] for item in self.retrieved_slices[:top_k]]
    
    def get_results_by_depth(self, depth: int) -> List[Tuple[HierarchicalSlice, float]]:
        """按深度过滤结果"""
        return [(slice_obj, score) for slice_obj, score in self.retrieved_slices 
                if slice_obj.depth == depth]

class HierarchicalRetrievalEngine:
    """层级编码智能检索引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化检索引擎"""
        self.config = config or {}
        self.slice_index: Dict[str, HierarchicalSlice] = {}
        self.embedding_index: Dict[str, List[float]] = {}
        self.hierarchical_structure: Dict[str, List[str]] = defaultdict(list)
        
        # 检索配置
        self.depth_weight_config = self.config.get('depth_weights', {
            1: 1.0,  # 顶层权重最高
            2: 0.8,
            3: 0.6,
            4: 0.4,
            5: 0.2   # 底层权重最低
        })
        
        self.context_expansion_depth = self.config.get('context_expansion_depth', 2)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.3)
        
        logger.info("层级编码智能检索引擎初始化完成")
    
    def index_slice(self, slice_data: HierarchicalSlice) -> bool:
        """索引单个层级切片"""
        try:
            # 添加到索引
            self.slice_index[slice_data.slice_id] = slice_data
            
            # 构建层级结构
            if slice_data.parent_id:
                self.hierarchical_structure[slice_data.parent_id].append(slice_data.slice_id)
            
            logger.info(f"索引层级切片成功: {slice_data.slice_id} (深度: {slice_data.depth})")
            return True
            
        except Exception as e:
            logger.error(f"索引层级切片失败: {e}")
            return False
    
    def batch_index_slices(self, slices: List[HierarchicalSlice]) -> Dict[str, Any]:
        """批量索引层级切片"""
        results = {
            "success_count": 0,
            "failed_count": 0,
            "failed_slices": []
        }
        
        for slice_data in slices:
            if self.index_slice(slice_data):
                results["success_count"] += 1
            else:
                results["failed_count"] += 1
                results["failed_slices"].append(slice_data.slice_id)
        
        logger.info(f"批量索引完成: 成功 {results['success_count']}, 失败 {results['failed_count']}")
        return results
    
    def retrieve(self, 
                 query_slice: HierarchicalSlice,
                 retrieval_method: str = "hierarchical_semantic",
                 max_results: int = 10,
                 include_context: bool = True) -> HierarchicalRetrievalResult:
        """
        执行层级编码智能检索
        
        Args:
            query_slice: 查询切片
            retrieval_method: 检索方法
            max_results: 最大结果数
            include_context: 是否包含上下文扩展
            
        Returns:
            HierarchicalRetrievalResult: 检索结果
        """
        import time
        start_time = time.time()
        
        try:
            # 执行检索
            if retrieval_method == "hierarchical_semantic":
                retrieved_slices = self._hierarchical_semantic_retrieval(query_slice, max_results)
            elif retrieval_method == "path_based":
                retrieved_slices = self._path_based_retrieval(query_slice, max_results)
            elif retrieval_method == "depth_aware":
                retrieved_slices = self._depth_aware_retrieval(query_slice, max_results)
            else:
                raise ValueError(f"不支持的检索方法: {retrieval_method}")
            
            # 上下文扩展
            context_expansion = []
            if include_context:
                context_expansion = self._expand_context(query_slice, retrieved_slices)
            
            retrieval_time = time.time() - start_time
            
            result = HierarchicalRetrievalResult(
                query_slice=query_slice,
                retrieved_slices=retrieved_slices,
                retrieval_method=retrieval_method,
                depth_weights=self.depth_weight_config,
                context_expansion=context_expansion,
                total_slices_searched=len(self.slice_index),
                retrieval_time=retrieval_time
            )
            
            logger.info(f"层级检索完成: 方法={retrieval_method}, 结果数={len(retrieved_slices)}, "
                       f"上下文扩展={len(context_expansion)}, 耗时={retrieval_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"层级检索失败: {e}")
            raise
    
    def _hierarchical_semantic_retrieval(self, 
                                       query_slice: HierarchicalSlice,
                                       max_results: int) -> List[Tuple[HierarchicalSlice, float]]:
        """层级语义检索（考虑深度权重）"""
        similarities = []
        
        for slice_id, slice_data in self.slice_index.items():
            if slice_id == query_slice.slice_id:
                continue  # 跳过查询项本身
            
            # 计算基础相似度
            base_similarity = self._calculate_slice_similarity(query_slice, slice_data)
            
            # 应用深度权重
            depth_weight = self.depth_weight_config.get(slice_data.depth, 0.5)
            weighted_similarity = base_similarity * depth_weight
            
            # 路径相似度加成
            path_similarity_bonus = self._calculate_path_similarity(query_slice, slice_data)
            final_similarity = weighted_similarity + path_similarity_bonus
            
            if final_similarity >= self.similarity_threshold:
                similarities.append((slice_data, final_similarity))
        
        # 按相似度排序并返回前N个结果
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]
    
    def _path_based_retrieval(self, 
                            query_slice: HierarchicalSlice,
                            max_results: int) -> List[Tuple[HierarchicalSlice, float]]:
        """基于路径的检索（优先检索相同路径的切片）"""
        similarities = []
        
        for slice_id, slice_data in self.slice_index.items():
            if slice_id == query_slice.slice_id:
                continue
            
            # 路径匹配度计算
            path_similarity = self._calculate_path_match_score(query_slice, slice_data)
            
            if path_similarity > 0:
                # 路径匹配的切片获得更高权重
                semantic_similarity = self._calculate_slice_similarity(query_slice, slice_data)
                final_similarity = semantic_similarity * (1.0 + path_similarity)
                
                similarities.append((slice_data, final_similarity))
        
        # 如果没有路径匹配的结果，回退到语义检索
        if not similarities:
            return self._hierarchical_semantic_retrieval(query_slice, max_results)
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]
    
    def _depth_aware_retrieval(self, 
                             query_slice: HierarchicalSlice,
                             max_results: int) -> List[Tuple[HierarchicalSlice, float]]:
        """深度感知检索（按深度分层检索）"""
        results_by_depth = {}
        
        # 按深度分组检索
        for depth in sorted(self.depth_weight_config.keys()):
            depth_results = []
            
            for slice_id, slice_data in self.slice_index.items():
                if slice_id == query_slice.slice_id or slice_data.depth != depth:
                    continue
                
                similarity = self._calculate_slice_similarity(query_slice, slice_data)
                if similarity >= self.similarity_threshold:
                    depth_results.append((slice_data, similarity))
            
            # 按深度权重调整
            depth_weight = self.depth_weight_config[depth]
            adjusted_results = [(slice_data, score * depth_weight) 
                              for slice_data, score in depth_results]
            
            results_by_depth[depth] = adjusted_results
        
        # 合并所有深度结果
        all_results = []
        for depth_results in results_by_depth.values():
            all_results.extend(depth_results)
        
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:max_results]
    
    def _calculate_slice_similarity(self, slice_a: HierarchicalSlice, slice_b: HierarchicalSlice) -> float:
        """计算切片相似度（基于内容和元数据）"""
        # 内容相似度
        content_similarity = self._calculate_text_similarity(slice_a.content, slice_b.content)
        
        # 元数据相似度
        metadata_similarity = self._calculate_metadata_similarity(slice_a.metadata, slice_b.metadata)
        
        # 综合相似度
        return 0.7 * content_similarity + 0.3 * metadata_similarity
    
    def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
        """计算文本相似度（基于词频和重叠）"""
        if not text_a or not text_b:
            return 0.0
        
        # 简单的词重叠相似度
        words_a = set(re.findall(r'\w+', text_a.lower()))
        words_b = set(re.findall(r'\w+', text_b.lower()))
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_metadata_similarity(self, metadata_a: Dict, metadata_b: Dict) -> float:
        """计算元数据相似度"""
        if not metadata_a or not metadata_b:
            return 0.0
        
        common_keys = set(metadata_a.keys()) & set(metadata_b.keys())
        if not common_keys:
            return 0.0
        
        similarity_sum = 0.0
        for key in common_keys:
            if metadata_a[key] == metadata_b[key]:
                similarity_sum += 1.0
        
        return similarity_sum / len(common_keys)
    
    def _calculate_path_similarity(self, slice_a: HierarchicalSlice, slice_b: HierarchicalSlice) -> float:
        """计算路径相似度（基于层级路径匹配）"""
        # 计算共同路径长度
        min_length = min(len(slice_a.parts), len(slice_b.parts))
        common_length = 0
        
        for i in range(min_length):
            if slice_a.parts[i] == slice_b.parts[i]:
                common_length += 1
            else:
                break
        
        if common_length == 0:
            return 0.0
        
        # 路径相似度：共同路径越长，相似度越高
        return common_length / max(len(slice_a.parts), len(slice_b.parts))
    
    def _calculate_path_match_score(self, slice_a: HierarchicalSlice, slice_b: HierarchicalSlice) -> float:
        """计算路径匹配分数（用于路径检索）"""
        # 检查是否在同一路径下
        if len(slice_a.parts) > 1 and len(slice_b.parts) > 1:
            # 检查是否有共同的父路径
            parent_a = '.'.join(slice_a.parts[:-1])
            parent_b = '.'.join(slice_b.parts[:-1])
            
            if parent_a == parent_b:
                return 1.0  # 直接兄弟节点
            
            # 检查是否是祖先-后代关系
            if parent_a in slice_b.get_ancestor_ids() or parent_b in slice_a.get_ancestor_ids():
                return 0.8  # 祖先-后代关系
        
        return 0.0
    
    def _expand_context(self, 
                       query_slice: HierarchicalSlice,
                       retrieved_slices: List[Tuple[HierarchicalSlice, float]]) -> List[HierarchicalSlice]:
        """扩展上下文（添加相关切片）"""
        context_slices = set()
        
        # 添加查询切片的上下文
        context_slices.update(self._get_context_slices(query_slice))
        
        # 添加检索结果的上下文
        for slice_data, _ in retrieved_slices[:5]:  # 只处理前5个结果
            context_slices.update(self._get_context_slices(slice_data))
        
        # 转换为列表并去重
        context_list = list(context_slices)
        
        # 确保不包含查询切片本身
        context_list = [slice_obj for slice_obj in context_list 
                       if slice_obj.slice_id != query_slice.slice_id]
        
        return context_list
    
    def _get_context_slices(self, slice_data: HierarchicalSlice) -> Set[HierarchicalSlice]:
        """获取相关上下文切片"""
        context_slices = set()
        
        # 添加祖先切片
        for ancestor_id in slice_data.get_ancestor_ids():
            if ancestor_id in self.slice_index:
                context_slices.add(self.slice_index[ancestor_id])
        
        # 添加兄弟切片
        for sibling_id in slice_data.get_sibling_ids(list(self.slice_index.values())):
            if sibling_id in self.slice_index:
                context_slices.add(self.slice_index[sibling_id])
        
        # 添加直接子切片
        if slice_data.slice_id in self.hierarchical_structure:
            for child_id in self.hierarchical_structure[slice_data.slice_id]:
                if child_id in self.slice_index:
                    context_slices.add(self.slice_index[child_id])
        
        return context_slices
    
    def get_slice_by_id(self, slice_id: str) -> Optional[HierarchicalSlice]:
        """根据ID获取切片"""
        return self.slice_index.get(slice_id)
    
    def get_slices_by_depth(self, depth: int) -> List[HierarchicalSlice]:
        """根据深度获取切片"""
        return [slice_data for slice_data in self.slice_index.values() 
                if slice_data.depth == depth]
    
    def get_hierarchical_path(self, slice_id: str) -> List[str]:
        """获取层级路径"""
        slice_data = self.get_slice_by_id(slice_id)
        if slice_data:
            return slice_data.parts
        return []
    
    def visualize_hierarchy(self, root_slice_id: Optional[str] = None, max_depth: int = 3) -> str:
        """可视化层级结构"""
        if not root_slice_id:
            # 找到根节点（深度为1的节点）
            root_slices = self.get_slices_by_depth(1)
            if not root_slices:
                return "没有找到根节点"
            root_slice_id = root_slices[0].slice_id
        
        def build_tree(node_id: str, current_depth: int) -> str:
            if current_depth > max_depth:
                return ""
            
            node = self.get_slice_by_id(node_id)
            if not node:
                return ""
            
            indent = "  " * (current_depth - 1)
            tree_str = f"{indent}└── {node.slice_id} (深度: {node.depth})\n"
            
            # 添加子节点
            if node_id in self.hierarchical_structure:
                for child_id in self.hierarchical_structure[node_id]:
                    tree_str += build_tree(child_id, current_depth + 1)
            
            return tree_str
        
        return f"层级结构可视化 (根节点: {root_slice_id}):\n" + build_tree(root_slice_id, 1)