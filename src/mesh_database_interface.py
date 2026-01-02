#!/usr/bin/env python3
# @self-expose: {"id": "mesh_database_interface", "name": "Mesh Database Interface", "type": "component", "version": "1.5.0", "needs": {"deps": ["induction_engine", "embedding_service"], "resources": []}, "provides": {"capabilities": ["Mesh Database Interface功能", "knowledge_graph.build", "knowledge_graph.time_sequence", "knowledge_graph.causal_edges", "knowledge_graph.global_full_index", "分类记忆库统计与可视化标识", "逻辑链提取与泡泡压缩", "归纳引擎摘要生成", "统一Embedding向量化存储", "单例模式避免重复初始化"]}}
# 网状思维引擎与12维记忆数据库接口
# 实现网状思维引擎与现有向量数据库的集成

import json
import numpy as np
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from .vector_database import VectorDatabase
from .mesh_thought_engine import (
    ThoughtNode, MeshThoughtEngine, 
    ContinuityContextBuilder, NetworkEmpowerment,
    cosine_similarity
)
from tools.induction_engine import summarize_topic, extract_events, batch_process

class MeshDatabaseInterface:
    """网状思维引擎与记忆数据库接口（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式：确保只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        # 避免重复初始化
        if MeshDatabaseInterface._initialized:
            return
        
        self.vector_db = VectorDatabase(db_path)
        # 设置网状思维引擎的持久化存储路径
        mesh_storage_path = "data/mesh_thoughts.json"
        if db_path:
            # 如果提供了数据库路径，使用相同的目录
            import os
            db_dir = os.path.dirname(db_path)
            mesh_storage_path = os.path.join(db_dir, "mesh_thoughts.json")
        
        self.thought_engine = MeshThoughtEngine(storage_path=mesh_storage_path)
        self.empowerment = NetworkEmpowerment(self.thought_engine)
        
        # 标记已初始化
        MeshDatabaseInterface._initialized = True
    
    def store_memory_with_mesh(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用网状思维引擎存储记忆（增强查重功能）"""
        # 提取记忆内容
        content = memory_data.get('content', '')
        topic = memory_data.get('topic', '未分类')
        
        if not content:
            return {'error': '记忆内容不能为空'}
        
        # 使用网状思维引擎处理（自动查重）
        thought_node = self.thought_engine.store_thought(content, {
            'topic': topic,
            'source_type': memory_data.get('source_type', 'unknown'),
            'original_data': memory_data
        })
        
        # 检查是否为重复记忆
        is_duplicate = self._check_memory_duplicate(content, memory_data)
        
        # ✅ 修复：使用统一Embedding服务生成正确维度的向量，而非使用thought_node的简化向量
        from src.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        memory_vector = embedding_service.encode(content)
        
        # 增强记忆数据
        enhanced_memory = memory_data.copy()
        enhanced_memory.update({
            'thought_node_id': thought_node.id,
            'mesh_importance': thought_node.importance,
            'connections_count': len(thought_node.connections),
            'is_duplicate': is_duplicate,
            'mesh_metadata': {
                'stored_at': datetime.now().isoformat(),
                'thought_network_size': self.thought_engine.get_node_count(),
                'duplicate_check': thought_node.metadata.get('duplicate_check', {})
            }
        })
        
        # 如果是重复记忆，记录但不存储到向量数据库
        if is_duplicate:
            return {
                'memory_id': None,
                'thought_node_id': thought_node.id,
                'mesh_enhanced': True,
                'is_duplicate': True,
                'importance': thought_node.importance,
                'connections_created': len(thought_node.connections),
                'message': '检测到重复记忆，已复用现有思维节点'
            }
        
        # 存储到向量数据库
        memory_id = self.vector_db.add_memory(enhanced_memory, memory_vector)
        
        return {
            'memory_id': memory_id,
            'thought_node_id': thought_node.id,
            'mesh_enhanced': True,
            'is_duplicate': False,
            'importance': thought_node.importance,
            'connections_created': len(thought_node.connections)
        }
    
    def search_memories_with_mesh(self, 
                                 query: str = None,
                                 vector: List[float] = None,
                                 topic: str = None,
                                 use_mesh_enhancement: bool = True,
                                 limit: int = 10) -> Dict[str, Any]:
        """使用网状思维引擎增强记忆搜索"""
        
        if use_mesh_enhancement and query:
            # 使用网络赋能增强搜索
            empowerment_result = self.empowerment.empower_llm(query, {
                'search_context': {
                    'topic': topic,
                    'use_mesh': True
                }
            })
            
            # 基于激活的思维网络优化搜索
            enhanced_query = self._enhance_search_query(query, empowerment_result)
            
            # 执行增强搜索
            memories = self.vector_db.search_memories(
                query=enhanced_query,
                vector=vector,
                topic=topic,
                limit=limit * 2  # 获取更多结果用于筛选
            )
            
            # 基于网状思维网络重新排序
            reordered_memories = self._reorder_by_mesh_network(memories, empowerment_result)
            
            return {
                'memories': reordered_memories[:limit],
                'mesh_enhancement': {
                    'original_query': query,
                    'enhanced_query': enhanced_query,
                    'continuity_level': empowerment_result['continuity_level'],
                    'thoughts_activated': len(empowerment_result['activated_network']),
                    'query_node_id': empowerment_result['query_node_id']
                },
                'search_metrics': {
                    'total_found': len(memories),
                    'after_mesh_reordering': len(reordered_memories)
                }
            }
        else:
            # 传统搜索
            memories = self.vector_db.search_memories(
                query=query,
                vector=vector,
                topic=topic,
                limit=limit
            )
            
            return {
                'memories': memories,
                'mesh_enhancement': {'enabled': False},
                'search_metrics': {'total_found': len(memories)}
            }
    
    def _check_memory_duplicate(self, content: str, memory_data: Dict[str, Any]) -> bool:
        """检查记忆是否为重复内容"""
        # 基于内容哈希的精确查重
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 在向量数据库中查找相似记忆
        similar_memories = self.vector_db.search_memories(
            query=content[:100],  # 使用前100个字符作为查询
            limit=5
        )
        
        # 检查是否有完全相同的内容
        for memory in similar_memories:
            if memory.get('content') == content:
                return True
        
        return False
    
    def _enhance_search_query(self, original_query: str, empowerment_result: Dict[str, Any]) -> str:
        """基于网状思维网络增强搜索查询"""
        activated_thoughts = empowerment_result['activated_network']
        
        if not activated_thoughts:
            return original_query
        
        # 提取相关思维的关键词
        related_keywords = []
        for thought in activated_thoughts[:3]:  # 取前3个最相关的
            content = thought['thought_content']
            # 简单的关键词提取（实际应用中应该使用更复杂的方法）
            words = content.split()[:5]  # 取前5个词作为关键词
            related_keywords.extend(words)
        
        # 构建增强查询
        enhanced_parts = [original_query]
        if related_keywords:
            enhanced_parts.extend(related_keywords)
        
        return " ".join(set(enhanced_parts))  # 去重
    
    def _reorder_by_mesh_network(self, memories: List[Dict[str, Any]], 
                                empowerment_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于网状思维网络重新排序记忆结果"""
        if not memories:
            return memories
        
        # 获取查询节点
        query_node_id = empowerment_result.get('query_node_id')
        if not query_node_id or query_node_id not in self.thought_engine.nodes:
            return memories
        
        query_node = self.thought_engine.nodes[query_node_id]
        
        # 计算每个记忆的网状关联分数
        scored_memories = []
        for memory in memories:
            mesh_score = self._calculate_mesh_relevance(memory, query_node)
            
            # 结合原始重要性和网状关联分数
            original_importance = memory.get('importance', 0.5)
            combined_score = original_importance * 0.4 + mesh_score * 0.6
            
            scored_memories.append((memory, combined_score))
        
        # 按综合分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        return [memory for memory, score in scored_memories]
    
    def _calculate_mesh_relevance(self, memory: Dict[str, Any], query_node: ThoughtNode) -> float:
        """计算记忆与查询节点的网状关联度"""
        thought_node_id = memory.get('thought_node_id')
        
        if not thought_node_id or thought_node_id not in self.thought_engine.nodes:
            return 0.0
        
        memory_node = self.thought_engine.nodes[thought_node_id]
        
        # 计算直接相似度
        direct_similarity = cosine_similarity(query_node.vector, memory_node.vector)
        
        # 检查网络连接
        connection_strength = self._get_connection_strength(query_node, memory_node)
        
        # 综合关联分数
        mesh_relevance = direct_similarity * 0.7 + connection_strength * 0.3
        
        return mesh_relevance
    
    def _get_connection_strength(self, node1: ThoughtNode, node2: ThoughtNode) -> float:
        """获取两个节点间的连接强度"""
        # 检查直接连接
        for connection in node1.connections:
            if connection['target_id'] == node2.id:
                return connection['strength']
        
        # 检查间接连接（通过共同邻居）
        common_neighbors = self._find_common_neighbors(node1, node2)
        if common_neighbors:
            return max(conn['strength'] for conn in common_neighbors) * 0.5
        
        return 0.0
    
    def _find_common_neighbors(self, node1: ThoughtNode, node2: ThoughtNode) -> List[Dict[str, Any]]:
        """查找共同邻居节点"""
        common_connections = []
        
        node1_neighbors = {conn['target_id'] for conn in node1.connections}
        node2_neighbors = {conn['target_id'] for conn in node2.connections}
        
        common_neighbor_ids = node1_neighbors.intersection(node2_neighbors)
        
        for neighbor_id in common_neighbor_ids:
            if neighbor_id in self.thought_engine.nodes:
                neighbor = self.thought_engine.nodes[neighbor_id]
                # 获取连接强度（取两个连接中的较小值）
                strength1 = next((conn['strength'] for conn in node1.connections 
                               if conn['target_id'] == neighbor_id), 0)
                strength2 = next((conn['strength'] for conn in node2.connections 
                               if conn['target_id'] == neighbor_id), 0)
                
                common_connections.append({
                    'neighbor_id': neighbor_id,
                    'strength': min(strength1, strength2)
                })
        
        return common_connections
    
    def build_knowledge_graph(self, topic: str = None, max_nodes: int = 5000, 
                            use_multiple_dimensions: bool = True,
                            min_importance: float = 0.05,
                            dynamic_inclusion: bool = True,
                            full_index: bool = False) -> Dict[str, Any]:
        """构建知识图谱（增强版，支持多维度关联和动态纳入）
        
        Args:
            topic: 主题过滤（可选）
            max_nodes: 最大节点数（仅在 full_index=False 时生效）
            use_multiple_dimensions: 是否构建多维关联
            min_importance: 重要性下限
            dynamic_inclusion: 是否动态纳入孤立记忆
            full_index: 是否构建全覆盖索引视图（忽略 max_nodes，只要满足 min_importance 即纳入）
        """
        
        # 获取所有记忆，提高限制以处理大规模数据
        all_memories = self.vector_db.search_memories(limit=200000)  # 增加到足够大的限制
        
        # 过滤重要性低于阈值的记忆
        filtered_memories = [m for m in all_memories if m['importance'] >= min_importance]
        
        # 如果启用动态纳入，自动处理孤立记忆（仅在非全索引模式下使用）
        if dynamic_inclusion and not full_index and len(filtered_memories) < len(all_memories):
            isolated_memories = self._include_isolated_memories(all_memories, filtered_memories)
            filtered_memories.extend(isolated_memories)
        
        # 根据是否为全覆盖索引决定节点选择策略
        if full_index:
            # 全覆盖索引视图：不做抽样，直接使用过滤后的全部记忆
            selected_memories = filtered_memories
        else:
            # 原有抽样逻辑
            if len(filtered_memories) > 100000:
                selected_memories = self._hierarchical_sampling(filtered_memories, max_nodes)
                selected_memories = self._optimize_node_selection(selected_memories, max_nodes)
            elif len(filtered_memories) > 5000:
                selected_memories = self._importance_weighted_sampling(filtered_memories, max_nodes)
            else:
                selected_memories = filtered_memories[:max_nodes]
        
        # 使用选定的记忆构建知识图谱
        memories = selected_memories
        
        # 【分类记忆库统计】统计三个库的记忆数量
        active_count = len([m for m in all_memories if m.get('status', 'active') == 'active'])
        archived_count = len([m for m in all_memories if m.get('status') == 'archived'])
        retired_count = len([m for m in all_memories if m.get('status') == 'retired'])
        
        knowledge_graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'topic': topic or '全局',
                'total_nodes': len(memories),
                'total_available': len(all_memories),
                'coverage_rate': len(memories) / len(all_memories) * 100 if all_memories else 0,
                'build_time': datetime.now().isoformat(),
                'dimensions_used': ['topic', 'importance'] + (['time', 'content_similarity'] if use_multiple_dimensions else []),
                'full_index': full_index,
                # 【分类记忆库统计】三层记忆库的数量分布
                'memory_classification': {
                    'active': active_count,
                    'archived': archived_count,
                    'retired': retired_count
                }
            }
        }

        # 打印构建统计，便于夜间任务成效分析
        print("[知识图谱构建] 主题:", topic or '全局')
        print("[知识图谱构建] 全部记忆数:", len(all_memories))
        print(f"[知识图谱构建] 记忆库分布: 主库(active)={active_count}, 备库(archived)={archived_count}, 淘汰库(retired)={retired_count}")
        print("[知识图谱构建] 本次节点数:", len(memories))
        print("[知识图谱构建] 覆盖率(%)：", knowledge_graph['metadata']['coverage_rate'])
        print("[知识图谱构建] 是否全覆盖索引(full_index):", full_index)
        
        # 添加节点
        for memory in memories:
            thought_node_id = memory.get('thought_node_id')
            node_info = {
                'id': memory['id'],
                'type': 'memory',
                'content': memory['content'][:100] + '...' if len(memory['content']) > 100 else memory['content'],
                'topic': memory['topic'],
                'importance': memory['importance'],
                'confidence': memory['confidence'],
                'timestamp': memory['timestamp'],
                'thought_node_id': thought_node_id,
                # 【分类记忆库标识】添加status字段，用于前端可视化区分三层记忆库
                'status': memory.get('status', 'active'),  # active/archived/retired
                'worldview_version': memory.get('worldview_version'),
                'retire_reason': memory.get('retire_reason')
            }
            
            knowledge_graph['nodes'].append(node_info)
            
            # 如果有关联的思维节点，添加网状连接
            if thought_node_id and thought_node_id in self.thought_engine.nodes:
                thought_node = self.thought_engine.nodes[thought_node_id]
                
                for connection in thought_node.connections:
                    if connection['target_id'] in self.thought_engine.nodes:
                        target_node = self.thought_engine.nodes[connection['target_id']]
                        
                        # 查找目标思维节点关联的记忆
                        target_memories = self.vector_db.search_memories(
                            query=target_node.content[:50], limit=1
                        )
                        
                        if target_memories:
                            edge = {
                                'source': memory['id'],
                                'target': target_memories[0]['id'],
                                'type': connection['type'],
                                'strength': connection['strength'],
                                'relation': 'mesh_connection'
                            }
                            knowledge_graph['edges'].append(edge)
        
        # 事件时间序列边（按timestamp或event_ts）
        try:
            sorted_by_time = sorted(
                [m for m in memories if m.get('timestamp') or m.get('event_ts')],
                key=lambda x: x.get('event_ts') or x.get('timestamp')
            )
            for i in range(len(sorted_by_time)-1):
                src = sorted_by_time[i]['id']
                dst = sorted_by_time[i+1]['id']
                edge = {
                    'source': src,
                    'target': dst,
                    'type': 'time_sequence',
                    'strength': 0.5,
                    'relation': 'temporal_order'
                }
                knowledge_graph['edges'].append(edge)
        except Exception:
            pass

        # 因果关系边（基于cause/effect标签或简单规则）
        for m in memories:
            cause_targets = m.get('causes', []) or m.get('cause', [])
            effect_targets = m.get('effects', []) or m.get('effect', [])
            for t in cause_targets:
                if isinstance(t, str):
                    # 查找目标记忆ID
                    target = next((mem for mem in memories if mem['id'] == t), None)
                    if target:
                        edge = {
                            'source': m['id'],
                            'target': t,
                            'type': 'causal',
                            'strength': 0.7,
                            'relation': 'cause'
                        }
                        knowledge_graph['edges'].append(edge)
            for t in effect_targets:
                if isinstance(t, str):
                    target = next((mem for mem in memories if mem['id'] == t), None)
                    if target:
                        edge = {
                            'source': m['id'],
                            'target': t,
                            'type': 'causal',
                            'strength': 0.7,
                            'relation': 'effect'
                        }
                        knowledge_graph['edges'].append(edge)

        # 如果启用多维度关联，构建额外的连接
        if use_multiple_dimensions:
            self._build_multidimensional_connections(knowledge_graph, memories)
        
        return knowledge_graph
    
    def _hierarchical_sampling(self, memories: List[Dict[str, Any]], max_nodes: int) -> List[Dict[str, Any]]:
        """分层抽样策略：按重要性分层，确保各层次都有代表性样本"""
        
        # 按重要性分层
        high_importance = [m for m in memories if m['importance'] > 0.7]
        medium_importance = [m for m in memories if 0.3 <= m['importance'] <= 0.7]
        low_importance = [m for m in memories if m['importance'] < 0.3]
        
        # 计算各层应该抽取的节点数（按比例分配）
        total_memories = len(memories)
        high_ratio = len(high_importance) / total_memories
        medium_ratio = len(medium_importance) / total_memories
        low_ratio = len(low_importance) / total_memories
        
        # 确保每层至少有一定数量的节点
        high_nodes = max(int(max_nodes * high_ratio), min(1000, len(high_importance)))
        medium_nodes = max(int(max_nodes * medium_ratio), min(2000, len(medium_importance)))
        low_nodes = max(int(max_nodes * low_ratio), min(1000, len(low_importance)))
        
        # 如果总数超过限制，按比例缩减
        total_selected = high_nodes + medium_nodes + low_nodes
        if total_selected > max_nodes:
            scale_factor = max_nodes / total_selected
            high_nodes = int(high_nodes * scale_factor)
            medium_nodes = int(medium_nodes * scale_factor)
            low_nodes = int(low_nodes * scale_factor)
        
        # 从各层抽取节点
        selected_memories = []
        selected_memories.extend(sorted(high_importance, key=lambda x: x['importance'], reverse=True)[:high_nodes])
        selected_memories.extend(sorted(medium_importance, key=lambda x: x['importance'], reverse=True)[:medium_nodes])
        selected_memories.extend(sorted(low_importance, key=lambda x: x['importance'], reverse=True)[:low_nodes])
        
        return selected_memories
    
    def _importance_weighted_sampling(self, memories: List[Dict[str, Any]], max_nodes: int) -> List[Dict[str, Any]]:
        """重要性加权抽样：基于重要性进行概率抽样"""
        
        # 计算重要性权重
        importance_weights = [m['importance'] for m in memories]
        total_weight = sum(importance_weights)
        
        if total_weight == 0:
            # 如果所有重要性都为0，使用均匀抽样
            probabilities = [1.0 / len(memories)] * len(memories)
        else:
            probabilities = [w / total_weight for w in importance_weights]
        
        # 使用重要性加权随机抽样
        import random
        selected_indices = random.choices(range(len(memories)), weights=probabilities, k=max_nodes)
        
        # 去重并转换为记忆列表
        selected_memories = []
        selected_ids = set()
        
        for idx in selected_indices:
            memory = memories[idx]
            if memory['id'] not in selected_ids:
                selected_memories.append(memory)
                selected_ids.add(memory['id'])
        
        # 如果抽样数量不足，补充高重要性记忆
        if len(selected_memories) < max_nodes:
            remaining_slots = max_nodes - len(selected_memories)
            high_importance_memories = sorted(memories, key=lambda x: x['importance'], reverse=True)
            
            for memory in high_importance_memories:
                if memory['id'] not in selected_ids:
                    selected_memories.append(memory)
                    selected_ids.add(memory['id'])
                    remaining_slots -= 1
                    if remaining_slots <= 0:
                        break
        
        return selected_memories
    
    def _optimize_node_selection(self, memories: List[Dict[str, Any]], max_nodes: int) -> List[Dict[str, Any]]:
        """优化节点选择：确保多样性和代表性"""
        
        # 按重要性排序
        sorted_memories = sorted(memories, key=lambda x: x['importance'], reverse=True)
        
        # 选择前max_nodes个高重要性记忆
        selected_memories = sorted_memories[:max_nodes]
        
        # 检查主题多样性
        topics = set()
        for memory in selected_memories:
            topics.add(memory['topic'])
        
        # 如果主题多样性不足，替换一些低重要性但主题不同的记忆
        if len(topics) < 10 and len(sorted_memories) > max_nodes:
            # 寻找不同主题的记忆
            additional_topics = set()
            for memory in sorted_memories[max_nodes:]:
                if memory['topic'] not in topics:
                    additional_topics.add(memory['topic'])
                    if len(additional_topics) >= 5:  # 最多添加5个新主题
                        break
            
            # 替换部分低重要性记忆
            if additional_topics:
                # 找到可以替换的记忆
                replace_count = min(len(additional_topics), max_nodes // 10)  # 替换10%的记忆
                
                for i in range(replace_count):
                    # 从尾部选择要替换的记忆
                    replace_index = max_nodes - 1 - i
                    
                    # 寻找新主题的记忆
                    for j in range(max_nodes, len(sorted_memories)):
                        candidate = sorted_memories[j]
                        if candidate['topic'] in additional_topics:
                            # 替换记忆
                            selected_memories[replace_index] = candidate
                            topics.add(candidate['topic'])
                            additional_topics.discard(candidate['topic'])
                            break
        
        return selected_memories
    
    def _build_multidimensional_connections(self, knowledge_graph: Dict[str, Any], memories: List[Dict[str, Any]]) -> None:
        """构建多维度关联连接"""
        
        # 1. 主题关联：相同主题的记忆建立连接
        topic_groups = {}
        for memory in memories:
            topic = memory['topic']
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(memory)
        
        for topic, group_memories in topic_groups.items():
            if len(group_memories) > 1:
                # 为主题组内的记忆建立连接
                for i in range(len(group_memories)):
                    for j in range(i+1, len(group_memories)):
                        edge = {
                            'source': group_memories[i]['id'],
                            'target': group_memories[j]['id'],
                            'type': 'topic_similarity',
                            'strength': 0.7,  # 主题相似度权重
                            'relation': f'same_topic:{topic}'
                        }
                        knowledge_graph['edges'].append(edge)
        
        # 2. 时间关联：时间相近的记忆建立连接
        # 过滤掉timestamp为空的记忆
        valid_time_memories = [m for m in memories if m.get('timestamp') and m['timestamp'].strip()]
        sorted_memories = sorted(valid_time_memories, key=lambda x: x['timestamp'])
        for i in range(len(sorted_memories) - 1):
            try:
                time_diff = (datetime.fromisoformat(sorted_memories[i+1]['timestamp']) - 
                            datetime.fromisoformat(sorted_memories[i]['timestamp'])).total_seconds()
            except (ValueError, AttributeError):
                continue  # 跳过无效时间戳
            
            # 如果时间差小于1小时，建立时间关联
            if time_diff < 3600:
                edge = {
                    'source': sorted_memories[i]['id'],
                    'target': sorted_memories[i+1]['id'],
                    'type': 'temporal_proximity',
                    'strength': max(0.8 - (time_diff / 3600) * 0.5, 0.3),  # 时间越近强度越高
                    'relation': 'time_sequence'
                }
                knowledge_graph['edges'].append(edge)
        
        # 3. 重要性分层：重要性高的记忆作为中心节点
        high_importance_memories = [m for m in memories if m['importance'] > 0.7]
        medium_importance_memories = [m for m in memories if 0.3 <= m['importance'] <= 0.7]
        
        # 高重要性记忆连接中等重要性记忆
        for high_mem in high_importance_memories:
            for medium_mem in medium_importance_memories:
                # 检查是否已经有连接
                existing_edge = any(e['source'] == high_mem['id'] and e['target'] == medium_mem['id'] 
                                  for e in knowledge_graph['edges'])
                if not existing_edge:
                    edge = {
                        'source': high_mem['id'],
                        'target': medium_mem['id'],
                        'type': 'importance_hierarchy',
                        'strength': 0.6,
                        'relation': 'importance_flow'
                    }
                    knowledge_graph['edges'].append(edge)
        
        # 4. 内容相似度关联（基于向量相似度）
        # 这里简化实现，实际应该使用向量数据库的相似度搜索
        for i in range(len(memories)):
            for j in range(i+1, min(i+10, len(memories))):  # 限制比较范围
                # 简化的内容相似度计算（基于关键词重叠）
                content1 = memories[i]['content'].lower()
                content2 = memories[j]['content'].lower()
                
                words1 = set(content1.split()[:20])  # 取前20个词
                words2 = set(content2.split()[:20])
                
                if words1 and words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                    
                    if similarity > 0.3:  # 相似度阈值
                        edge = {
                            'source': memories[i]['id'],
                            'target': memories[j]['id'],
                            'type': 'content_similarity',
                            'strength': similarity * 0.8,  # 缩放相似度
                            'relation': 'semantic_similarity'
                        }
                        knowledge_graph['edges'].append(edge)
    
    def _include_isolated_memories(self, all_memories: List[Dict[str, Any]], 
                                 included_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """动态纳入孤立记忆到知识图谱"""
        
        # 获取已纳入记忆的ID集合
        included_ids = {m['id'] for m in included_memories}
        
        # 找出未被纳入的记忆
        excluded_memories = [m for m in all_memories if m['id'] not in included_ids]
        
        # 分析孤立记忆的特点，决定是否纳入
        isolated_to_include = []
        
        for memory in excluded_memories:
            # 检查是否为重要记忆（即使重要性较低）
            if self._should_include_isolated_memory(memory, included_memories):
                isolated_to_include.append(memory)
        
        print(f"动态纳入 {len(isolated_to_include)} 个孤立记忆")
        return isolated_to_include
    
    def _should_include_isolated_memory(self, memory: Dict[str, Any], 
                                     included_memories: List[Dict[str, Any]]) -> bool:
        """判断是否应该纳入孤立记忆"""
        
        # 1. 检查是否有明确的主题
        if memory['topic'].strip() and memory['topic'] != 'DS聊天记录':
            return True
        
        # 2. 检查内容长度（较长的内容可能更有价值）
        if len(memory['content']) > 200:
            return True
        
        # 3. 检查是否有特殊标签
        if memory.get('tags') and len(memory['tags']) > 0:
            return True
        
        # 4. 检查是否与已纳入记忆有内容相似性
        for included_memory in included_memories[:50]:  # 检查前50个已纳入记忆
            # 简化的相似度计算
            content1 = memory['content'].lower()
            content2 = included_memory['content'].lower()
            
            words1 = set(content1.split()[:10])
            words2 = set(content2.split()[:10])
            
            if words1 and words2:
                similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                if similarity > 0.4:  # 相似度阈值
                    return True
        
        # 5. 检查时间特征（如果是近期记忆，可能更有价值）
        try:
            from datetime import datetime
            memory_time = datetime.fromisoformat(memory['timestamp'])
            current_time = datetime.now()
            time_diff = (current_time - memory_time).total_seconds()
            
            # 如果是24小时内的记忆，纳入
            if time_diff < 86400:  # 24小时
                return True
        except:
            pass
        
        return False
    
    def extract_logic_chain(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """逻辑链提取：提取关键节点（前提、转折、结论），压缩中间推导过程
        
        Args:
            memories: 记忆列表
            
        Returns:
            logic_chains: 逻辑链列表，每条包含:
                - chain_id: 逻辑链ID
                - memories: 记忆ID列表
                - key_nodes: 关键节点列表（前提/转折/结论）
                - coherence_score: 连贯性得分
                - compressed_summary: 压缩摘要
        """
        logic_chains = []
        visited = set()
        
        for mem in memories:
            if mem['id'] in visited:
                continue
            
            # 构建逻辑链
            chain = [mem]
            visited.add(mem['id'])
            
            # 寻找逻辑相关的后续记忆
            current_mem = mem
            while True:
                next_mem = self._find_logical_successor(current_mem, memories, visited)
                if next_mem:
                    chain.append(next_mem)
                    visited.add(next_mem['id'])
                    current_mem = next_mem
                else:
                    break
            
            if len(chain) >= 1:  # 单个记忆也可以形成逻辑链
                # 提取关键节点（使用归纳引擎）
                key_nodes = self._extract_key_nodes(chain)
                
                # 生成压缩摘要
                full_content = ' '.join([m['content'] for m in chain])
                compressed = summarize_topic(full_content, max_sentences=3, max_chars=280)
                
                logic_chains.append({
                    'chain_id': f"logic_chain_{len(logic_chains)}",
                    'memories': [m['id'] for m in chain],
                    'length': len(chain),
                    'key_nodes': key_nodes,
                    'coherence_score': self._calculate_chain_coherence(chain),
                    'compressed_summary': compressed['topic_summary'],
                    'key_points': compressed['key_points']
                })
        
        print(f"[逻辑链提取] 共提取 {len(logic_chains)} 条逻辑链")
        return logic_chains
    
    def _find_logical_successor(self, current_mem: Dict[str, Any], 
                                all_memories: List[Dict[str, Any]], 
                                visited: set) -> Optional[Dict[str, Any]]:
        """寻找逻辑后继记忆"""
        candidates = []
        
        for mem in all_memories:
            if mem['id'] in visited:
                continue
            
            # 计算逻辑相关性
            score = 0.0
            
            # 1. 主题相同
            if mem['topic'] == current_mem['topic']:
                score += 0.3
            
            # 2. 时间接近（1小时内）
            try:
                time_diff = abs((datetime.fromisoformat(mem['timestamp']) - 
                               datetime.fromisoformat(current_mem['timestamp'])).total_seconds())
                if time_diff < 3600:  # 1小时
                    score += 0.3 * (1 - time_diff / 3600)
            except:
                pass
            
            # 3. 内容相似度（简化版）
            words1 = set(current_mem['content'].lower().split()[:20])
            words2 = set(mem['content'].lower().split()[:20])
            if words1 and words2:
                similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                score += similarity * 0.4
            
            if score > 0.5:  # 阈值
                candidates.append((score, mem))
        
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return None
    
    def _extract_key_nodes(self, chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取逻辑链中的关键节点（前提、转折、结论）"""
        key_nodes = []
        
        if len(chain) == 1:
            # 单个记忆，使用归纳引擎提取关键点
            summary = summarize_topic(chain[0]['content'], max_sentences=2)
            key_nodes.append({
                'type': 'premise',
                'memory_id': chain[0]['id'],
                'content': summary['topic_summary'],
                'importance': chain[0]['importance']
            })
        else:
            # 多个记忆，提取前提、转折、结论
            # 前提：第一个记忆
            premise_summary = summarize_topic(chain[0]['content'], max_sentences=1)
            key_nodes.append({
                'type': 'premise',
                'memory_id': chain[0]['id'],
                'content': premise_summary['topic_summary'],
                'importance': chain[0]['importance']
            })
            
            # 转折：中间重要性最高的记忆
            if len(chain) > 2:
                middle_mem = max(chain[1:-1], key=lambda m: m['importance'])
                turning_summary = summarize_topic(middle_mem['content'], max_sentences=1)
                key_nodes.append({
                    'type': 'turning',
                    'memory_id': middle_mem['id'],
                    'content': turning_summary['topic_summary'],
                    'importance': middle_mem['importance']
                })
            
            # 结论：最后一个记忆
            conclusion_summary = summarize_topic(chain[-1]['content'], max_sentences=1)
            key_nodes.append({
                'type': 'conclusion',
                'memory_id': chain[-1]['id'],
                'content': conclusion_summary['topic_summary'],
                'importance': chain[-1]['importance']
            })
        
        return key_nodes
    
    def _calculate_chain_coherence(self, chain: List[Dict[str, Any]]) -> float:
        """计算逻辑链的连贯性得分"""
        if len(chain) == 1:
            return 1.0
        
        coherence_score = 0.0
        
        # 1. 主题一致性
        topics = [m['topic'] for m in chain]
        if len(set(topics)) == 1:
            coherence_score += 0.4
        else:
            coherence_score += 0.2
        
        # 2. 时间连续性
        try:
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in chain]
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                         for i in range(len(timestamps)-1)]
            avg_diff = sum(time_diffs) / len(time_diffs)
            if avg_diff < 3600:  # 平均1小时内
                coherence_score += 0.3
            elif avg_diff < 86400:  # 平均24小时内
                coherence_score += 0.15
        except:
            pass
        
        # 3. 内容相似度
        total_similarity = 0.0
        count = 0
        for i in range(len(chain)-1):
            words1 = set(chain[i]['content'].lower().split()[:20])
            words2 = set(chain[i+1]['content'].lower().split()[:20])
            if words1 and words2:
                similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                total_similarity += similarity
                count += 1
        
        if count > 0:
            coherence_score += (total_similarity / count) * 0.3
        
        return min(coherence_score, 1.0)
    
    def compress_to_bubble(self, logic_chains: List[Dict[str, Any]], 
                          storage_path: str = "data/logic_bubbles.json") -> Dict[str, Any]:
        """将逻辑链压缩为泡泡存储（精炼关键信息持久化）
        
        Args:
            logic_chains: 逻辑链列表
            storage_path: 泡泡存储路径
            
        Returns:
            压缩结果统计
        """
        import os
        import json
        
        # 读取现有泡泡
        bubbles = []
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    bubbles = json.load(f)
            except:
                bubbles = []
        
        # 为每条逻辑链创建泡泡
        new_bubbles_count = 0
        for chain in logic_chains:
            bubble = {
                'bubble_id': f"bubble_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{chain['chain_id']}",
                'chain_id': chain['chain_id'],
                'timestamp': datetime.now().isoformat(),
                'type': 'logic_chain',
                'compressed_summary': chain['compressed_summary'],
                'key_points': chain['key_points'],
                'key_nodes': chain['key_nodes'],
                'memory_ids': chain['memories'],
                'coherence_score': chain['coherence_score'],
                'metadata': {
                    'chain_length': chain['length'],
                    'creation_time': datetime.now().isoformat()
                }
            }
            bubbles.append(bubble)
            new_bubbles_count += 1
        
        # 保存泡泡
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(bubbles, f, ensure_ascii=False, indent=2)
        
        print(f"[泡泡压缩] 新增 {new_bubbles_count} 个逻辑泡泡，总计 {len(bubbles)} 个")
        print(f"[泡泡压缩] 存储路径: {storage_path}")
        
        return {
            'new_bubbles': new_bubbles_count,
            'total_bubbles': len(bubbles),
            'storage_path': storage_path,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_summaries_with_induction(self, memories: List[Dict[str, Any]], 
                                         batch_size: int = 50) -> List[Dict[str, Any]]:
        """使用归纳引擎对现有文本块进行摘要归纳
        
        Args:
            memories: 记忆列表
            batch_size: 批处理大小
            
        Returns:
            归纳结果列表
        """
        print(f"[归纳引擎] 开始对 {len(memories)} 条记忆进行摘要归纳...")
        
        # 准备批处理数据
        batch_items = [
            {'id': mem['id'], 'text': mem['content']} 
            for mem in memories
        ]
        
        # 分批处理
        all_results = []
        for i in range(0, len(batch_items), batch_size):
            batch = batch_items[i:i+batch_size]
            results = batch_process(batch)
            all_results.extend(results)
            print(f"[归纳引擎] 已处理 {len(all_results)}/{len(batch_items)} 条记忆")
        
        print(f"[归纳引擎] 归纳完成，共生成 {len(all_results)} 条摘要")
        return all_results
     
    def get_mesh_statistics(self) -> Dict[str, Any]:
        """获取网状思维引擎统计信息（包含查重统计）"""
        # 获取查重统计
        duplicate_stats = self.thought_engine.get_duplicate_statistics()
        
        # 获取向量数据库中的重复记忆统计
        all_memories = self.vector_db.search_memories(limit=1000)
        duplicate_memories = [m for m in all_memories if m.get('is_duplicate', False)]
        
        return {
            'thought_engine': {
                'total_nodes': self.thought_engine.get_node_count(),
                'most_important_nodes': [
                    {
                        'id': node.id,
                        'content': node.content[:50] + '...',
                        'importance': node.importance,
                        'connections': len(node.connections)
                    }
                    for node in self.thought_engine.get_most_important_nodes(5)
                ],
                'duplicate_statistics': duplicate_stats
            },
            'vector_database': {
                'total_memories': self.vector_db.get_memory_count(),
                'topics': self.vector_db.get_topics(),
                'duplicate_memories': len(duplicate_memories),
                'unique_memories': len(all_memories) - len(duplicate_memories)
            },
            'integration_metrics': {
                'memories_with_mesh': len([m for m in all_memories 
                                         if m.get('thought_node_id')]),
                'average_importance': np.mean([m.get('importance', 0) 
                                            for m in all_memories[:100]]),
                'duplicate_prevention_rate': len(duplicate_memories) / len(all_memories) if all_memories else 0
            }
        }

def test_mesh_database_interface():
    """测试网状思维数据库接口"""
    print("=== 网状思维数据库接口测试 ===")
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 测试存储记忆
    test_memories = [
        {
            'topic': 'AI技术',
            'content': '深度学习在图像识别领域取得了重大突破',
            'source_type': 'knowledge',
            'importance': 0.8
        },
        {
            'topic': '医疗AI', 
            'content': '人工智能辅助诊断系统提高了医疗效率',
            'source_type': 'research',
            'importance': 0.7
        },
        {
            'topic': '自然语言处理',
            'content': 'Transformer架构彻底改变了NLP领域',
            'source_type': 'technical',
            'importance': 0.9
        }
    ]
    
    for memory in test_memories:
        result = interface.store_memory_with_mesh(memory)
        print(f"存储记忆: {memory['topic']} -> {result}")
    
    # 测试增强搜索
    search_result = interface.search_memories_with_mesh(
        query="人工智能发展",
        use_mesh_enhancement=True,
        limit=5
    )
    
    print(f"\n增强搜索结果:")
    print(f"找到记忆: {len(search_result['memories'])}个")
    print(f"连续性水平: {search_result['mesh_enhancement']['continuity_level']:.3f}")
    
    # 测试知识图谱构建
    knowledge_graph = interface.build_knowledge_graph(topic="AI技术")
    print(f"\n知识图谱统计:")
    print(f"节点数: {len(knowledge_graph['nodes'])}")
    print(f"边数: {len(knowledge_graph['edges'])}")
    
    # 获取统计信息
    stats = interface.get_mesh_statistics()
    print(f"\n系统统计:")
    print(f"思维节点总数: {stats['thought_engine']['total_nodes']}")
    print(f"记忆总数: {stats['vector_database']['total_memories']}")
    
    return interface

if __name__ == "__main__":
    test_mesh_database_interface()