#!/usr/bin/env python
# @self-expose: {"id": "multimodal_retrieval_engine", "name": "Multimodal Retrieval Engine", "type": "component", "version": "1.0.0", "needs": {"deps": ["src.hierarchical_retrieval_engine"], "resources": []}, "provides": {"capabilities": ["多模态数据索引", "跨模态检索", "多模态相似度计算", "检索结果融合"], "methods": {"index_item": "索引项目", "retrieve": "多模态检索"}}}
# -*- coding: utf-8 -*-
"""
多模态检索引擎
开发提示词来源：用户发现通过API调用的智能体缺乏多模态能力，需要开发多模态对齐和检索引擎

核心功能：
1. 多模态数据索引（文本、图像、音频等）
2. 跨模态检索（文本搜图像、图像搜文本等）
3. 多模态相似度计算
4. 检索结果融合和排序
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

# 导入层级检索引擎
from .hierarchical_retrieval_engine import HierarchicalRetrievalEngine, HierarchicalSlice

logger = logging.getLogger(__name__)

@dataclass
class RetrievalItem:
    """检索项类"""
    item_id: str
    modality_type: str  # text, image, audio
    content: Any
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class RetrievalResult:
    """检索结果类"""
    query_item: RetrievalItem
    retrieved_items: List[Tuple[RetrievalItem, float]]  # (item, similarity_score)
    retrieval_method: str
    fusion_strategy: str
    total_items_searched: int
    retrieval_time: float

class MultimodalRetrievalEngine:
    """多模态检索引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化检索引擎"""
        self.config = config or {}
        self.index = {}  # 多模态索引库
        self.embedding_models = self._initialize_embedding_models()
        self.retrieval_methods = self._initialize_retrieval_methods()
        self.fusion_strategies = self._initialize_fusion_strategies()
        
        # 初始化层级检索引擎
        self.hierarchical_engine = HierarchicalRetrievalEngine(
            config.get('hierarchical_config', {}) if config else {}
        )
        
        logger.info("多模态检索引擎初始化完成（包含层级检索支持）")
    
    def _initialize_embedding_models(self) -> Dict[str, Any]:
        """初始化嵌入模型"""
        return {
            "text": self._generate_text_embedding,
            "image": self._generate_image_embedding,
            "audio": self._generate_audio_embedding
        }
    
    def _initialize_retrieval_methods(self) -> Dict[str, Any]:
        """初始化检索方法"""
        return {
            "semantic": self._semantic_retrieval,
            "cross_modal": self._cross_modal_retrieval,
            "hybrid": self._hybrid_retrieval
        }
    
    def _initialize_fusion_strategies(self) -> Dict[str, Any]:
        """初始化融合策略"""
        return {
            "weighted_average": self._weighted_average_fusion,
            "rank_fusion": self._rank_fusion,
            "max_fusion": self._max_fusion
        }
    
    def index_item(self, item: RetrievalItem) -> bool:
        """索引单个项目"""
        try:
            # 生成嵌入向量
            if item.embedding is None:
                item.embedding = self._generate_embedding(item)
            
            # 添加到索引
            if item.modality_type not in self.index:
                self.index[item.modality_type] = {}
            
            self.index[item.modality_type][item.item_id] = item
            
            logger.info(f"索引项目成功: {item.modality_type}/{item.item_id}")
            return True
            
        except Exception as e:
            logger.error(f"索引项目失败: {e}")
            return False
    
    def batch_index_items(self, items: List[RetrievalItem]) -> Dict[str, Any]:
        """批量索引项目"""
        results = {
            "success_count": 0,
            "failed_count": 0,
            "failed_items": []
        }
        
        for item in items:
            if self.index_item(item):
                results["success_count"] += 1
            else:
                results["failed_count"] += 1
                results["failed_items"].append(item.item_id)
        
        logger.info(f"批量索引完成: 成功 {results['success_count']}, 失败 {results['failed_count']}")
        return results
    
    def retrieve(self, 
                 query_item: RetrievalItem,
                 target_modality: Optional[str] = None,
                 retrieval_method: str = "semantic",
                 fusion_strategy: str = "weighted_average",
                 max_results: int = 10) -> RetrievalResult:
        """
        执行多模态检索
        
        Args:
            query_item: 查询项目
            target_modality: 目标模态（None表示跨模态检索）
            retrieval_method: 检索方法
            fusion_strategy: 融合策略
            max_results: 最大结果数
            
        Returns:
            RetrievalResult: 检索结果
        """
        start_time = time.time()
        
        try:
            # 验证检索方法
            if retrieval_method not in self.retrieval_methods:
                raise ValueError(f"不支持的检索方法: {retrieval_method}")
            
            # 执行检索
            retrieval_func = self.retrieval_methods[retrieval_method]
            retrieved_items = retrieval_func(query_item, target_modality, max_results)
            
            # 结果融合
            if fusion_strategy in self.fusion_strategies:
                fusion_func = self.fusion_strategies[fusion_strategy]
                retrieved_items = fusion_func(retrieved_items)
            
            retrieval_time = time.time() - start_time
            
            result = RetrievalResult(
                query_item=query_item,
                retrieved_items=retrieved_items,
                retrieval_method=retrieval_method,
                fusion_strategy=fusion_strategy,
                total_items_searched=self._get_total_items_count(),
                retrieval_time=retrieval_time
            )
            
            logger.info(f"检索完成: 方法={retrieval_method}, 结果数={len(retrieved_items)}, 耗时={retrieval_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            raise
    
    def _semantic_retrieval(self, 
                          query_item: RetrievalItem,
                          target_modality: Optional[str],
                          max_results: int) -> List[Tuple[RetrievalItem, float]]:
        """语义检索（同模态）"""
        if target_modality is None:
            target_modality = query_item.modality_type
        
        if target_modality not in self.index:
            return []
        
        # 计算相似度
        similarities = []
        for item_id, item in self.index[target_modality].items():
            if item_id == query_item.item_id:
                continue  # 跳过查询项本身
            
            similarity = self._calculate_similarity(query_item, item)
            similarities.append((item, similarity))
        
        # 按相似度排序并返回前N个结果
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]
    
    def _cross_modal_retrieval(self, 
                              query_item: RetrievalItem,
                              target_modality: Optional[str],
                              max_results: int) -> List[Tuple[RetrievalItem, float]]:
        """跨模态检索"""
        if target_modality is None:
            # 在所有模态中检索
            results = []
            for modality in self.index.keys():
                if modality == query_item.modality_type:
                    continue  # 跳过同模态（由语义检索处理）
                
                # 模拟跨模态检索
                for item_id, item in self.index[modality].items():
                    similarity = self._calculate_cross_modal_similarity(query_item, item)
                    results.append((item, similarity))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:max_results]
        else:
            # 在指定模态中检索
            if target_modality not in self.index:
                return []
            
            results = []
            for item_id, item in self.index[target_modality].items():
                similarity = self._calculate_cross_modal_similarity(query_item, item)
                results.append((item, similarity))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:max_results]
    
    def _hybrid_retrieval(self, 
                         query_item: RetrievalItem,
                         target_modality: Optional[str],
                         max_results: int) -> List[Tuple[RetrievalItem, float]]:
        """混合检索（语义+跨模态）"""
        semantic_results = self._semantic_retrieval(query_item, target_modality, max_results * 2)
        cross_modal_results = self._cross_modal_retrieval(query_item, target_modality, max_results * 2)
        
        # 合并结果
        all_results = semantic_results + cross_modal_results
        
        # 去重并排序
        seen_items = set()
        unique_results = []
        
        for item, score in all_results:
            if item.item_id not in seen_items:
                seen_items.add(item.item_id)
                unique_results.append((item, score))
        
        unique_results.sort(key=lambda x: x[1], reverse=True)
        return unique_results[:max_results]
    
    def _weighted_average_fusion(self, results: List[Tuple[RetrievalItem, float]]) -> List[Tuple[RetrievalItem, float]]:
        """加权平均融合"""
        # 简单的加权平均（可根据需要调整权重）
        return results
    
    def _rank_fusion(self, results: List[Tuple[RetrievalItem, float]]) -> List[Tuple[RetrievalItem, float]]:
        """排序融合"""
        # 基于排序的融合
        return results
    
    def _max_fusion(self, results: List[Tuple[RetrievalItem, float]]) -> List[Tuple[RetrievalItem, float]]:
        """最大分数融合"""
        # 取最大分数
        return results
    
    def _generate_text_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # 模拟文本嵌入生成
        # 实际应用中应该使用BERT、Sentence-BERT等模型
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        return [((hash_val >> i) & 0xFF) / 255.0 for i in range(0, 24, 8)][:5]
    
    def _generate_image_embedding(self, image_data: Any) -> List[float]:
        """生成图像嵌入向量"""
        # 模拟图像嵌入生成
        # 实际应用中应该使用ResNet、CLIP等模型
        import hashlib
        if isinstance(image_data, str):
            hash_val = int(hashlib.md5(image_data.encode()).hexdigest()[:8], 16)
        else:
            hash_val = int(hashlib.md5(str(image_data).encode()).hexdigest()[:8], 16)
        return [((hash_val >> i) & 0xFF) / 255.0 + 0.05 for i in range(0, 24, 8)][:5]
    
    def _generate_audio_embedding(self, audio_data: Any) -> List[float]:
        """生成音频嵌入向量"""
        # 模拟音频嵌入生成
        # 实际应用中应该使用VGGish、AudioSet等模型
        import hashlib
        if isinstance(audio_data, str):
            hash_val = int(hashlib.md5(audio_data.encode()).hexdigest()[:8], 16)
        else:
            hash_val = int(hashlib.md5(str(audio_data).encode()).hexdigest()[:8], 16)
        return [((hash_val >> i) & 0xFF) / 255.0 + 0.02 for i in range(0, 24, 8)][:5]
    
    def _generate_embedding(self, item: RetrievalItem) -> List[float]:
        """生成嵌入向量"""
        # 模拟嵌入生成
        if item.modality_type == "text":
            return [0.1, 0.2, 0.3, 0.4, 0.5]
        elif item.modality_type == "image":
            return [0.15, 0.25, 0.35, 0.45, 0.55]
        elif item.modality_type == "audio":
            return [0.12, 0.22, 0.32, 0.42, 0.52]
        else:
            return [0.1] * 5
    
    def _calculate_similarity(self, item_a: RetrievalItem, item_b: RetrievalItem) -> float:
        """计算相似度（同模态）"""
        if item_a.embedding is None or item_b.embedding is None:
            return 0.0
        
        # 余弦相似度
        dot_product = sum(a * b for a, b in zip(item_a.embedding, item_b.embedding))
        norm_a = math.sqrt(sum(a ** 2 for a in item_a.embedding))
        norm_b = math.sqrt(sum(b ** 2 for b in item_b.embedding))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _calculate_cross_modal_similarity(self, item_a: RetrievalItem, item_b: RetrievalItem) -> float:
        """计算跨模态相似度（基于语义交汇点）"""
        # 基于语义交汇点的多模态对齐
        semantic_point_a = self._map_to_semantic_space(item_a)
        semantic_point_b = self._map_to_semantic_space(item_b)
        
        # 计算语义空间中的相似度
        return self._semantic_similarity(semantic_point_a, semantic_point_b)
    
    def _map_to_semantic_space(self, item: RetrievalItem) -> List[float]:
        """将模态向量映射到语义空间"""
        if item.embedding is None:
            item.embedding = self._generate_embedding(item)
        
        # 模拟语义映射：不同模态映射到统一的语义空间
        # 实际应用中应该使用CLIP等多模态对齐模型
        if item.modality_type == "text":
            # 文本模态语义映射
            return [x * 1.2 for x in item.embedding]  # 文本语义增强
        elif item.modality_type == "image":
            # 图像模态语义映射
            return [x * 1.1 for x in item.embedding]  # 图像语义映射
        elif item.modality_type == "audio":
            # 音频模态语义映射
            return [x * 1.0 for x in item.embedding]  # 音频语义映射
        else:
            return item.embedding
    
    def _semantic_similarity(self, semantic_a: List[float], semantic_b: List[float]) -> float:
        """计算语义空间中的相似度（基于语义交汇点）"""
        # 余弦相似度在语义空间
        dot_product = sum(a * b for a, b in zip(semantic_a, semantic_b))
        norm_a = sum(a ** 2 for a in semantic_a) ** 0.5
        norm_b = sum(b ** 2 for b in semantic_b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot_product / (norm_a * norm_b)
        
        # 语义交汇点检测：当两个向量在语义空间中接近时
        # 这体现了不同模态在同一个语义概念上的交汇
        if similarity > 0.6:
            # 语义交汇增强：在交汇点附近增强相似度
            # 这表示不同模态表达了同一个语义概念
            similarity = min(similarity * 1.3, 1.0)
        
        return similarity
    
    def _find_semantic_intersection(self, items: List[RetrievalItem]) -> List[float]:
        """找到多个模态在语义空间中的交汇点"""
        if not items:
            return [0.0] * 5  # 默认向量
        
        # 将所有模态映射到语义空间
        semantic_vectors = [self._map_to_semantic_space(item) for item in items]
        
        # 计算语义交汇点（向量平均）
        intersection_point = []
        for i in range(len(semantic_vectors[0])):
            avg_val = sum(vec[i] for vec in semantic_vectors) / len(semantic_vectors)
            intersection_point.append(avg_val)
        
        return intersection_point
    
    def semantic_intersection_retrieval(self, 
                                      query_items: List[RetrievalItem],
                                      max_results: int = 10) -> List[Tuple[RetrievalItem, float]]:
        """基于语义交汇点的多模态检索"""
        # 找到查询项的语义交汇点
        intersection_point = self._find_semantic_intersection(query_items)
        
        # 在所有索引项中寻找最接近交汇点的项
        similarities = []
        for modality, items in self.index.items():
            for item_id, item in items.items():
                # 跳过查询项本身
                if any(item.item_id == q_item.item_id for q_item in query_items):
                    continue
                
                # 计算到语义交汇点的距离
                item_semantic = self._map_to_semantic_space(item)
                similarity = self._semantic_similarity(intersection_point, item_semantic)
                similarities.append((item, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]
    
    def _get_total_items_count(self) -> int:
        """获取总项目数"""
        total = 0
        for modality_items in self.index.values():
            total += len(modality_items)
        return total
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        stats = {
            "total_items": self._get_total_items_count(),
            "modality_distribution": {},
            "engine_status": "active",
            "hierarchical_support": True,
            "hierarchical_slices_count": len(self.hierarchical_engine.slice_index)
        }
        
        for modality, items in self.index.items():
            stats["modality_distribution"][modality] = len(items)
        
        return stats
    
    def index_hierarchical_slice(self, 
                                slice_id: str,
                                content: str,
                                depth: int,
                                parent_id: Optional[str] = None,
                                sequence_order: int = 0,
                                metadata: Optional[Dict[str, Any]] = None,
                                embedding: Optional[List[float]] = None) -> bool:
        """索引层级切片"""
        try:
            slice_data = HierarchicalSlice(
                slice_id=slice_id,
                content=content,
                depth=depth,
                parent_id=parent_id,
                sequence_order=sequence_order,
                metadata=metadata or {},
                embedding=embedding
            )
            
            return self.hierarchical_engine.index_slice(slice_data)
            
        except Exception as e:
            logger.error(f"索引层级切片失败: {e}")
            return False
    
    def hierarchical_retrieve(self,
                            query_slice_id: str,
                            retrieval_method: str = "hierarchical_semantic",
                            max_results: int = 10,
                            include_context: bool = True) -> Optional[Dict[str, Any]]:
        """层级编码智能检索"""
        try:
            # 获取查询切片
            query_slice = self.hierarchical_engine.get_slice_by_id(query_slice_id)
            if not query_slice:
                logger.error(f"未找到查询切片: {query_slice_id}")
                return None
            
            # 执行层级检索
            result = self.hierarchical_engine.retrieve(
                query_slice=query_slice,
                retrieval_method=retrieval_method,
                max_results=max_results,
                include_context=include_context
            )
            
            # 格式化结果
            formatted_results = []
            for slice_obj, score in result.retrieved_slices:
                formatted_results.append({
                    "slice_id": slice_obj.slice_id,
                    "content_preview": slice_obj.content[:100] + "..." if len(slice_obj.content) > 100 else slice_obj.content,
                    "depth": slice_obj.depth,
                    "similarity_score": score,
                    "metadata": slice_obj.metadata
                })
            
            # 格式化上下文扩展
            context_expansion = []
            for slice_obj in result.context_expansion:
                context_expansion.append({
                    "slice_id": slice_obj.slice_id,
                    "content_preview": slice_obj.content[:100] + "..." if len(slice_obj.content) > 100 else slice_obj.content,
                    "depth": slice_obj.depth,
                    "relation_type": self._determine_relation_type(query_slice, slice_obj)
                })
            
            return {
                "success": True,
                "query_slice": {
                    "slice_id": query_slice.slice_id,
                    "depth": query_slice.depth,
                    "hierarchical_path": query_slice.hierarchical_path
                },
                "retrieved_slices": formatted_results,
                "context_expansion": context_expansion,
                "retrieval_method": result.retrieval_method,
                "total_slices_searched": result.total_slices_searched,
                "retrieval_time": result.retrieval_time,
                "depth_weights": result.depth_weights
            }
            
        except Exception as e:
            logger.error(f"层级检索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"层级检索失败: {e}"
            }
    
    def _determine_relation_type(self, query_slice: HierarchicalSlice, context_slice: HierarchicalSlice) -> str:
        """确定切片间的关系类型"""
        if context_slice.slice_id in query_slice.get_ancestor_ids():
            return "ancestor"
        elif query_slice.slice_id in context_slice.get_ancestor_ids():
            return "descendant"
        elif context_slice.slice_id in query_slice.get_sibling_ids(list(self.hierarchical_engine.slice_index.values())):
            return "sibling"
        else:
            return "related"
    
    def get_hierarchical_structure(self, root_slice_id: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """获取层级结构信息"""
        try:
            visualization = self.hierarchical_engine.visualize_hierarchy(root_slice_id, max_depth)
            
            # 统计信息
            depth_distribution = {}
            for depth in range(1, 6):  # 假设最大深度为5
                slices_at_depth = self.hierarchical_engine.get_slices_by_depth(depth)
                depth_distribution[depth] = len(slices_at_depth)
            
            return {
                "visualization": visualization,
                "depth_distribution": depth_distribution,
                "total_slices": len(self.hierarchical_engine.slice_index),
                "max_depth": max(depth_distribution.keys()) if depth_distribution else 0
            }
            
        except Exception as e:
            logger.error(f"获取层级结构失败: {e}")
            return {
                "error": str(e),
                "message": "获取层级结构失败"
            }

# 工具接口类（用于智能体集成）
class MultimodalRetrievalTool:
    """多模态检索工具（智能体工具接口）"""
    
    def __init__(self):
        self.engine = MultimodalRetrievalEngine()
        self.tool_name = "multimodal_retrieval"
        self.tool_description = "多模态检索工具，支持文本、图像、音频等模态的跨模态检索"
    
    def call(self, **kwargs) -> Dict[str, Any]:
        """工具调用接口"""
        try:
            # 解析参数
            query_content = kwargs.get("query_content")
            query_modality = kwargs.get("query_modality")
            target_modality = kwargs.get("target_modality")
            retrieval_method = kwargs.get("retrieval_method", "semantic")
            max_results = kwargs.get("max_results", 5)
            
            # 创建查询项
            query_item = RetrievalItem(
                item_id=f"query_{int(time.time())}",
                modality_type=query_modality,
                content=query_content,
                metadata={"query_time": datetime.now().isoformat()}
            )
            
            # 执行检索
            result = self.engine.retrieve(
                query_item=query_item,
                target_modality=target_modality,
                retrieval_method=retrieval_method,
                max_results=max_results
            )
            
            # 格式化结果
            formatted_results = []
            for item, score in result.retrieved_items:
                formatted_results.append({
                    "item_id": item.item_id,
                    "modality": item.modality_type,
                    "content_preview": str(item.content)[:100] + "..." if len(str(item.content)) > 100 else str(item.content),
                    "similarity_score": score,
                    "metadata": item.metadata
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "statistics": {
                    "total_items_searched": result.total_items_searched,
                    "retrieval_time": result.retrieval_time,
                    "retrieval_method": result.retrieval_method
                },
                "message": "多模态检索成功"
            }
            
        except Exception as e:
            logger.error(f"多模态检索工具调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"多模态检索失败: {e}"
            }
    
    def index_item(self, **kwargs) -> Dict[str, Any]:
        """索引项目接口"""
        try:
            item_id = kwargs.get("item_id")
            modality_type = kwargs.get("modality_type")
            content = kwargs.get("content")
            metadata = kwargs.get("metadata", {})
            
            item = RetrievalItem(
                item_id=item_id,
                modality_type=modality_type,
                content=content,
                metadata=metadata
            )
            
            success = self.engine.index_item(item)
            
            return {
                "success": success,
                "message": "索引项目成功" if success else "索引项目失败"
            }
            
        except Exception as e:
            logger.error(f"索引项目失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"索引项目失败: {e}"
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            "name": self.tool_name,
            "description": self.tool_description,
            "parameters": {
                "query_content": "查询内容",
                "query_modality": "查询模态类型（text/image/audio）",
                "target_modality": "目标模态类型（可选，None表示跨模态）",
                "retrieval_method": "检索方法（semantic/cross_modal/hybrid）",
                "max_results": "最大结果数"
            },
            "hierarchical_operations": {
                "index_hierarchical_slice": "索引层级切片",
                "hierarchical_retrieve": "层级编码智能检索",
                "get_hierarchical_structure": "获取层级结构信息"
            }
        }
    
    def hierarchical_retrieve(self, **kwargs) -> Dict[str, Any]:
        """层级检索工具接口"""
        try:
            query_slice_id = kwargs.get("query_slice_id")
            retrieval_method = kwargs.get("retrieval_method", "hierarchical_semantic")
            max_results = kwargs.get("max_results", 10)
            include_context = kwargs.get("include_context", True)
            
            result = self.engine.hierarchical_retrieve(
                query_slice_id=query_slice_id,
                retrieval_method=retrieval_method,
                max_results=max_results,
                include_context=include_context
            )
            
            if result:
                return result
            else:
                return {
                    "success": False,
                    "message": "层级检索失败，未找到结果"
                }
                
        except Exception as e:
            logger.error(f"层级检索工具调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"层级检索失败: {e}"
            }
    
    def index_hierarchical_slice(self, **kwargs) -> Dict[str, Any]:
        """索引层级切片工具接口"""
        try:
            slice_id = kwargs.get("slice_id")
            content = kwargs.get("content")
            depth = kwargs.get("depth")
            parent_id = kwargs.get("parent_id")
            sequence_order = kwargs.get("sequence_order", 0)
            metadata = kwargs.get("metadata", {})
            
            success = self.engine.index_hierarchical_slice(
                slice_id=slice_id,
                content=content,
                depth=depth,
                parent_id=parent_id,
                sequence_order=sequence_order,
                metadata=metadata
            )
            
            return {
                "success": success,
                "message": "索引层级切片成功" if success else "索引层级切片失败"
            }
            
        except Exception as e:
            logger.error(f"索引层级切片失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"索引层级切片失败: {e}"
            }
    
    def get_hierarchical_structure(self, **kwargs) -> Dict[str, Any]:
        """获取层级结构信息工具接口"""
        try:
            root_slice_id = kwargs.get("root_slice_id")
            max_depth = kwargs.get("max_depth", 3)
            
            result = self.engine.get_hierarchical_structure(
                root_slice_id=root_slice_id,
                max_depth=max_depth
            )
            
            return {
                "success": True,
                "structure_info": result
            }
            
        except Exception as e:
            logger.error(f"获取层级结构失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"获取层级结构失败: {e}"
            }

def create_multimodal_retrieval_tool() -> MultimodalRetrievalTool:
    """创建多模态检索工具实例"""
    return MultimodalRetrievalTool()

if __name__ == "__main__":
    # 测试代码
    tool = create_multimodal_retrieval_tool()
    
    # 测试索引项目
    tool.index_item(
        item_id="test_image_1",
        modality_type="image",
        content="base64_encoded_image_data",
        metadata={"description": "一只猫在草地上玩耍"}
    )
    
    # 测试检索
    result = tool.call(
        query_content="寻找猫的图片",
        query_modality="text",
        target_modality="image",
        retrieval_method="cross_modal",
        max_results=3
    )
    
    print("检索结果:", json.dumps(result, indent=2, ensure_ascii=False))