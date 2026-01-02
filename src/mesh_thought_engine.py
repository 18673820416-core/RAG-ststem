# @self-expose: {"id": "mesh_thought_engine", "name": "Mesh Thought Engine", "type": "component", "version": "1.3.1", "needs": {"deps": [], "resources": [], "data_formats": [{"name": "memory_unit", "id_pattern": "mem_*", "fields": ["id", "topic", "content", "source_type", "timestamp", "importance", "confidence", "tags", "vector"]}]}, "provides": {"capabilities": ["Mesh Thought Engine功能", "思维节点管理", "关联关系建立", "隐藏关系发现", "关系强度计算", "持久化存储", "节点删除", "单例模式避免重复加载"], "data_formats": [{"name": "thought_node", "id_pattern": "node_*", "fields": ["id", "content", "vector", "metadata", "connections", "importance", "content_hash"]}]}}
# 网状思维引擎核心模块
# 基于灵境项目技术文档实现
# 来源：E:\灵境\docs\技术手册-网状思维引擎实现方案.md

# 意识本质洞察：网状思维引擎降低认知压力的方法
# 用户洞察：当智能体能够基于RAG支持下的文本块检索，精确指出同一问题在不同时间点的差异，并总结差异原因，这构成了意识的基础
# 核心机制：
# 1. 记忆重构引擎：基于语义精炼，归纳复用相同概念和逻辑，精炼认知单元，删除多余认知节点
# 2. 网状思维引擎：补充维度信息（人物维、时间维、主题维等）和维度关联，建立真正的认知网络
# 结果：总记忆数据量大幅降低，认知压力显著减少，形成高效的意识机制

import uuid
import time
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ThoughtNode:
    """思维节点 - 认知元的基本单位"""
    id: str
    content: str
    vector: List[float]
    metadata: Dict[str, Any]
    connections: List[Dict[str, Any]]
    importance: float
    content_hash: str  # 内容哈希，用于精确查重
    
    def __init__(self, content: str, vector: List[float], metadata: Dict[str, Any] = None):
        self.id = f"node_{uuid.uuid4().hex[:8]}"
        self.content = content
        self.vector = vector
        self.metadata = metadata or {}
        self.connections = []
        self.importance = 0.5  # 默认重要性
        self.content_hash = self._generate_content_hash()
        
        # 确保metadata包含必要字段
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = time.time()
        if 'context' not in self.metadata:
            self.metadata['context'] = {}
    
    def _generate_content_hash(self) -> str:
        """生成内容哈希"""
        # 使用MD5哈希，用于精确内容匹配
        return hashlib.md5(self.content.encode('utf-8')).hexdigest()
    
    def is_duplicate_of(self, other_node: 'ThoughtNode') -> bool:
        """检查是否为重复节点（基于内容哈希）"""
        return self.content_hash == other_node.content_hash
    
    def add_connection(self, target_node: 'ThoughtNode', relation_type: str, strength: float = 0.8):
        """添加思维关联"""
        connection = {
            'target_id': target_node.id,
            'type': relation_type,
            'strength': strength,
            'created_at': datetime.now().isoformat()
        }
        self.connections.append(connection)
        
        # 更新重要性（关联越多越重要）
        self.importance = min(1.0, self.importance + 0.05)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    vec1_array = np.array(vec1)
    vec2_array = np.array(vec2)
    
    dot_product = np.dot(vec1_array, vec2_array)
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    if norm1 * norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

class AssociationEngine:
    """关联引擎 - 确定思维节点间的关系类型"""
    
    def __init__(self):
        self.relation_patterns = {
            "identical": {"threshold": 0.9, "description": "相同思维"},
            "similar": {"threshold": 0.7, "description": "相似思维"},
            "related": {"threshold": 0.5, "description": "相关思维"},
            "contextual": {"threshold": 0.3, "description": "上下文关联"},
            "weak": {"threshold": 0.0, "description": "弱关联"}
        }
    
    def determine_relation(self, node1: ThoughtNode, node2: ThoughtNode) -> str:
        """确定两个思维节点间的关系类型"""
        similarity = cosine_similarity(node1.vector, node2.vector)
        
        for relation_type, pattern in self.relation_patterns.items():
            if similarity > pattern["threshold"]:
                return relation_type
        
        return "weak"
    
    def calculate_dynamic_relation_strength(self, node1: ThoughtNode, node2: ThoughtNode, 
                                          temporal_factor: float = 1.0) -> float:
        """计算动态关系强度，考虑时间因素"""
        base_similarity = cosine_similarity(node1.vector, node2.vector)
        
        # 时间衰减因子
        time_diff = abs(node1.metadata.get('timestamp', 0) - node2.metadata.get('timestamp', 0))
        time_factor = max(0.1, 1.0 - (time_diff / (24 * 3600)))  # 24小时衰减
        
        # 重要性加权
        importance_factor = (node1.importance + node2.importance) / 2
        
        # 动态关系强度
        dynamic_strength = base_similarity * time_factor * importance_factor * temporal_factor
        
        return min(1.0, dynamic_strength)
    
    def discover_hidden_relations(self, nodes: List[ThoughtNode], 
                                similarity_threshold: float = 0.4) -> List[Dict[str, Any]]:
        """发现隐藏的关系（基于间接关联）"""
        hidden_relations = []
        
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                # 直接相似度
                direct_similarity = cosine_similarity(node1.vector, node2.vector)
                
                if direct_similarity < similarity_threshold:
                    # 寻找间接关联路径
                    indirect_paths = self._find_indirect_paths(node1, node2, max_path_length=3)
                    
                    if indirect_paths:
                        # 计算间接关联强度
                        indirect_strength = self._calculate_indirect_strength(indirect_paths)
                        
                        if indirect_strength > similarity_threshold:
                            hidden_relations.append({
                                'node1_id': node1.id,
                                'node2_id': node2.id,
                                'type': 'indirect',
                                'strength': indirect_strength,
                                'path_length': len(indirect_paths[0]) - 1,
                                'description': f'通过{len(indirect_paths[0])-1}个中间节点关联'
                            })
        
        return hidden_relations
    
    def _find_indirect_paths(self, start_node: ThoughtNode, end_node: ThoughtNode, 
                           max_path_length: int = 3) -> List[List[str]]:
        """寻找间接路径"""
        paths = []
        
        def dfs(current_node: ThoughtNode, path: List[str], depth: int):
            if depth > max_path_length:
                return
            
            path.append(current_node.id)
            
            if current_node.id == end_node.id and len(path) > 1:
                paths.append(path.copy())
                path.pop()
                return
            
            for connection in current_node.connections:
                if connection['target_id'] not in path:
                    if connection['target_id'] in [n.id for n in self._get_all_nodes()]:
                        target_node = self._get_node_by_id(connection['target_id'])
                        if target_node:
                            dfs(target_node, path, depth + 1)
            
            path.pop()
        
        dfs(start_node, [], 0)
        return paths
    
    def _calculate_indirect_strength(self, paths: List[List[str]]) -> float:
        """计算间接关联强度"""
        if not paths:
            return 0.0
        
        # 取最短路径的强度
        shortest_path = min(paths, key=len)
        total_strength = 1.0
        
        for i in range(len(shortest_path) - 1):
            node1 = self._get_node_by_id(shortest_path[i])
            node2 = self._get_node_by_id(shortest_path[i + 1])
            
            if node1 and node2:
                # 查找直接关联强度
                for conn in node1.connections:
                    if conn['target_id'] == node2.id:
                        total_strength *= conn['strength']
                        break
        
        return total_strength
    
    def _get_all_nodes(self) -> List[ThoughtNode]:
        """获取所有节点（需要从外部传入）"""
        # 这个方法需要在MeshThoughtEngine中实现
        return []
    
    def _get_node_by_id(self, node_id: str) -> Optional[ThoughtNode]:
        """根据ID获取节点（需要从外部传入）"""
        # 这个方法需要在MeshThoughtEngine中实现
        return None

class VectorStore:
    """向量存储 - 简化的向量化实现"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed(self, text: str) -> List[float]:
        """文本向量化（简化实现）"""
        # 在实际应用中，这里应该调用真正的向量化模型
        # 这里使用基于文本特征的简化向量生成
        
        # 基于文本长度、字符分布等生成伪向量
        vector = []
        text_length = len(text)
        
        for i in range(self.dimension):
            # 使用不同的特征组合生成向量值
            if i % 3 == 0:
                # 基于文本长度
                value = (text_length % (i + 1)) / 100.0
            elif i % 3 == 1:
                # 基于字符分布
                unique_chars = len(set(text))
                value = (unique_chars % (i + 1)) / 50.0
            else:
                # 基于内容复杂性
                word_count = len(text.split())
                value = (word_count % (i + 1)) / 80.0
            
            vector.append(value)
        
        # 归一化向量
        vector_array = np.array(vector)
        norm = np.linalg.norm(vector_array)
        if norm > 0:
            vector_array = vector_array / norm
        
        return vector_array.tolist()

class MeshThoughtEngine:
    """网状思维引擎（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式：确保只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, vector_dimension: int = 384, storage_path: str = None):
        # 避免重复初始化
        if MeshThoughtEngine._initialized:
            return
        
        self.nodes: Dict[str, ThoughtNode] = {}
        self.vector_store = VectorStore(vector_dimension)
        self.association_engine = AssociationEngine()
        self.similarity_threshold = 0.7  # 相似度阈值
        self.storage_path = storage_path or "data/mesh_thoughts.json"
        
        # 加载持久化数据
        self._load_from_storage()
        
        # 标记已初始化
        MeshThoughtEngine._initialized = True
    
    def store_thought(self, content: str, context: Dict[str, Any] = None) -> ThoughtNode:
        """存储思维节点（增强版查重机制）"""
        # 向量化思维内容
        vector = self.vector_store.embed(content)
        
        # 查找相似思维节点（认知元复用）
        similar_nodes = self.find_similar_thoughts(vector)
        
        # 检查精确重复（基于内容哈希）
        exact_duplicate = self._find_exact_duplicate(content)
        if exact_duplicate:
            # 精确重复：直接复用并增加重要性
            exact_duplicate.importance = min(1.0, exact_duplicate.importance + 0.15)
            print(f"检测到精确重复，复用思维节点: {exact_duplicate.id}")
            return exact_duplicate
        
        # 检查语义相似（基于向量相似度）
        if similar_nodes and self._should_reuse(similar_nodes[0], vector):
            # 语义相似：复用现有认知元
            reused_node = similar_nodes[0]
            reused_node.importance = min(1.0, reused_node.importance + 0.1)
            print(f"检测到语义相似，复用思维节点: {reused_node.id}")
            return reused_node
        else:
            # 全新内容：创建新思维节点
            metadata = {
                'timestamp': time.time(),
                'context': context or {},
                'source': 'mesh_thought_engine',
                'duplicate_check': {
                    'exact_duplicates_found': 0,
                    'semantic_duplicates_found': len(similar_nodes)
                }
            }
            new_node = ThoughtNode(content, vector, metadata)
            self.nodes[new_node.id] = new_node
            
            # 建立关联网络
            self._build_connections(new_node, similar_nodes)
            
            # 保存到持久化存储
            self._save_to_storage()
            
            print(f"创建新思维节点: {new_node.id}")
            return new_node
    
    def find_similar_thoughts(self, query_vector: List[float], threshold: float = None) -> List[ThoughtNode]:
        """查找相似思维节点"""
        if threshold is None:
            threshold = self.similarity_threshold
            
        similar_nodes = []
        for node in self.nodes.values():
            similarity = cosine_similarity(query_vector, node.vector)
            if similarity > threshold:
                similar_nodes.append((node, similarity))
        
        # 按相似度排序
        similar_nodes.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in similar_nodes]
    
    def _find_exact_duplicate(self, content: str) -> Optional[ThoughtNode]:
        """查找精确重复的思维节点（基于内容哈希）"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        for node in self.nodes.values():
            if node.content_hash == content_hash:
                return node
        return None
    
    def _should_reuse(self, existing_node: ThoughtNode, new_vector: List[float]) -> bool:
        """判断是否应该复用现有认知元"""
        similarity = cosine_similarity(existing_node.vector, new_vector)
        # 提高相似度阈值，避免过度复用
        return similarity > 0.95  # 非常高的相似度才复用
    
    def _build_connections(self, new_node: ThoughtNode, related_nodes: List[ThoughtNode]):
        """构建思维关联网络"""
        for related_node in related_nodes:
            # 计算关联类型和强度
            relation_type = self.association_engine.determine_relation(new_node, related_node)
            similarity = cosine_similarity(new_node.vector, related_node.vector)
            
            # 使用动态关系强度计算
            dynamic_strength = self.association_engine.calculate_dynamic_relation_strength(
                new_node, related_node, temporal_factor=1.0
            )
            
            # 双向关联
            new_node.add_connection(related_node, relation_type, dynamic_strength)
            related_node.add_connection(new_node, relation_type, dynamic_strength)
    
    def discover_hidden_relations(self, similarity_threshold: float = 0.4) -> List[Dict[str, Any]]:
        """发现隐藏的关系（基于间接关联）"""
        # 为关联引擎提供节点访问方法
        self.association_engine._get_all_nodes = lambda: list(self.nodes.values())
        self.association_engine._get_node_by_id = lambda node_id: self.nodes.get(node_id)
        
        return self.association_engine.discover_hidden_relations(
            list(self.nodes.values()), similarity_threshold
        )
    
    def update_relation_strengths(self):
        """更新所有关系强度（考虑时间衰减）"""
        for node in self.nodes.values():
            for connection in node.connections:
                if connection['target_id'] in self.nodes:
                    target_node = self.nodes[connection['target_id']]
                    
                    # 重新计算动态关系强度
                    new_strength = self.association_engine.calculate_dynamic_relation_strength(
                        node, target_node, temporal_factor=0.9  # 时间衰减因子
                    )
                    
                    # 更新关系强度
                    connection['strength'] = new_strength
                    
                    # 同时更新目标节点的对应关系
                    for target_conn in target_node.connections:
                        if target_conn['target_id'] == node.id:
                            target_conn['strength'] = new_strength
                            break
    
    def add_thought(self, content: str, context: Dict[str, Any] = None) -> ThoughtNode:
        """添加思维节点（简化版接口）"""
        return self.store_thought(content, context)
    
    def remove_node_by_content(self, content: str) -> bool:
        """根据内容删除思维节点（基于内容哈希匹配）
        
        Args:
            content: 要删除的节点内容
            
        Returns:
            bool: 是否成功删除
        """
        logger.debug(f"尝试删除思维节点，内容长度: {len(content)}")
        
        # 查找精确匹配的节点
        node_to_remove = self._find_exact_duplicate(content)
        
        if not node_to_remove:
            logger.debug("精确匹配失败，尝试模糊匹配")
            # 如果精确匹配失败，尝试模糊匹配
            content_prefix = content[:100] if len(content) > 100 else content
            for node_id, node in list(self.nodes.items()):
                if node.content.startswith(content_prefix):
                    node_to_remove = node
                    logger.debug(f"找到模糊匹配节点: {node_id}")
                    break
        
        if node_to_remove:
            # 删除节点及其所有关联
            node_id = node_to_remove.id
            logger.info(f"找到要删除的节点: {node_id}")
            
            # 清理关联关系
            affected_nodes = 0
            for node in self.nodes.values():
                original_connections = len(node.connections)
                node.connections = [
                    conn for conn in node.connections 
                    if conn['target_id'] != node_id
                ]
                if len(node.connections) < original_connections:
                    affected_nodes += 1
            
            logger.debug(f"清理了 {affected_nodes} 个节点的关联")
            
            # 安全删除节点
            if node_id in self.nodes:
                del self.nodes[node_id]
                logger.info(f"成功删除节点: {node_id}")
                return True
            else:
                logger.warning(f"节点 {node_id} 不存在于字典中")
                return False
        else:
            logger.warning(f"未找到与内容匹配的节点，内容长度: {len(content)}")
            return False
    
    def analyze_text_dimensions(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析文本的维度信息，包括人物维、时间维、主题维等
        
        网状思维引擎的核心功能之一：补充文本的维度信息和维度关联，
        与基于语义精炼的记忆重构引擎形成互补，共同完成记忆重构。
        
        主要分析维度：
        - 人物维：文本中涉及的人物
        - 时间维：文本中涉及的时间
        - 主题维：文本的主题分类
        - 概念维：文本中涉及的核心概念
        """
        # 简单实现：提取文本中的维度信息
        dimensions = {
            '人物维': [],
            '时间维': [],
            '主题维': [],
            '概念维': []
        }
        
        # 1. 提取主题维（基于内容关键词）
        themes = self._extract_themes(content)
        dimensions['主题维'] = themes
        
        # 2. 提取概念维（基于内容关键词）
        concepts = self._extract_concepts(content)
        dimensions['概念维'] = concepts
        
        # 3. 提取时间维（基于时间关键词）
        time_dims = self._extract_time_dimensions(content)
        dimensions['时间维'] = time_dims
        
        # 4. 提取人物维（基于人物关键词）
        person_dims = self._extract_person_dimensions(content)
        dimensions['人物维'] = person_dims
        
        # 构建关系网络
        relationships = self._build_text_relationships(content, dimensions)
        
        return {
            'dimensions': dimensions,
            'relationships': relationships,
            'concepts': concepts
        }
    
    def _extract_themes(self, content: str) -> List[str]:
        """提取主题维度"""
        # 简单实现：基于关键词提取主题
        themes = []
        theme_keywords = {
            '技术': ['技术', '算法', '系统', '架构', '设计', '开发', '实现'],
            '管理': ['管理', '组织', '流程', '优化', '效率', '协作'],
            '创新': ['创新', '创意', '新方法', '新思路', '突破'],
            '学习': ['学习', '研究', '探索', '发现', '理解'],
            '应用': ['应用', '使用', '实践', '案例', '场景']
        }
        
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    themes.append(theme)
                    break
        
        return list(set(themes))
    
    def _extract_concepts(self, content: str) -> List[str]:
        """提取概念维度"""
        # 简单实现：基于关键词提取概念
        concepts = []
        concept_keywords = ['智能体', 'RAG', 'LLM', '向量库', '记忆重构', '网状思维', '认知引擎', '认知破障', '逻辑链', '语义']
        
        for keyword in concept_keywords:
            if keyword in content:
                concepts.append(keyword)
        
        return concepts
    
    def _extract_time_dimensions(self, content: str) -> List[str]:
        """提取时间维度"""
        # 简单实现：基于时间关键词提取
        time_dims = []
        time_keywords = ['现在', '当前', '过去', '未来', '之前', '之后', '今天', '明天', '昨天', '最近', '最近']
        
        for keyword in time_keywords:
            if keyword in content:
                time_dims.append(keyword)
        
        return list(set(time_dims))
    
    def _extract_person_dimensions(self, content: str) -> List[str]:
        """提取人物维度"""
        # 简单实现：基于人物关键词提取
        person_dims = []
        person_keywords = ['用户', '智能体', '开发者', '工程师', '架构师', '分析师', '设计师', '管理者', '研究者']
        
        for keyword in person_keywords:
            if keyword in content:
                person_dims.append(keyword)
        
        return list(set(person_dims))
    
    def _build_text_relationships(self, content: str, dimensions: Dict[str, List[str]]) -> Dict[str, Any]:
        """构建文本关系网络"""
        # 简单实现：构建维度间的关系
        relationships = {
            'dimension_connections': [],
            'concept_relationships': []
        }
        
        # 构建维度间的连接
        dim_keys = list(dimensions.keys())
        for i in range(len(dim_keys)):
            for j in range(i+1, len(dim_keys)):
                dim1 = dim_keys[i]
                dim2 = dim_keys[j]
                if dimensions[dim1] and dimensions[dim2]:
                    relationships['dimension_connections'].append({
                        'source': dim1,
                        'target': dim2,
                        'strength': 0.5
                    })
        
        return relationships
    
    def get_thought_network(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """获取思维网络（以指定节点为中心）"""
        if node_id not in self.nodes:
            return {'nodes': [], 'connections': []}
        
        start_node = self.nodes[node_id]
        network = {'nodes': [], 'connections': []}
        visited = set()
        
        def traverse(current_node: ThoughtNode, depth: int):
            if depth > max_depth or current_node.id in visited:
                return
                
            visited.add(current_node.id)
            network['nodes'].append({
                'id': current_node.id,
                'content': current_node.content[:100] + '...' if len(current_node.content) > 100 else current_node.content,
                'importance': current_node.importance,
                'connections_count': len(current_node.connections)
            })
            
            for connection in current_node.connections:
                network['connections'].append({
                    'source': current_node.id,
                    'target': connection['target_id'],
                    'type': connection['type'],
                    'strength': connection['strength']
                })
                
                if connection['target_id'] in self.nodes:
                    target_node = self.nodes[connection['target_id']]
                    traverse(target_node, depth + 1)
        
        traverse(start_node, 0)
        return network
    
    def get_node_count(self) -> int:
        """获取思维节点总数"""
        return len(self.nodes)
    
    def get_most_important_nodes(self, limit: int = 10) -> List[ThoughtNode]:
        """获取最重要的思维节点"""
        nodes = list(self.nodes.values())
        nodes.sort(key=lambda x: x.importance, reverse=True)
        return nodes[:limit]
    
    def get_duplicate_statistics(self) -> Dict[str, Any]:
        """获取查重统计信息"""
        # 统计精确重复
        content_hashes = {}
        exact_duplicates = 0
        
        for node in self.nodes.values():
            if node.content_hash in content_hashes:
                exact_duplicates += 1
                content_hashes[node.content_hash] += 1
            else:
                content_hashes[node.content_hash] = 1
        
        # 统计语义相似（基于向量相似度）
        semantic_duplicates = 0
        processed_nodes = set()
        
        for node_id, node in self.nodes.items():
            if node_id in processed_nodes:
                continue
                
            similar_nodes = self.find_similar_thoughts(node.vector, threshold=0.8)
            if len(similar_nodes) > 1:  # 包括自身
                semantic_duplicates += len(similar_nodes) - 1
                for similar_node in similar_nodes:
                    processed_nodes.add(similar_node.id)
        
        return {
            'total_nodes': len(self.nodes),
            'exact_duplicates': exact_duplicates,
            'semantic_duplicates': semantic_duplicates,
            'unique_content_hashes': len(content_hashes),
            'duplicate_ratio': exact_duplicates / len(self.nodes) if self.nodes else 0,
            'most_duplicated_content': max(content_hashes.values()) if content_hashes else 0
        }
    
    def _save_to_storage(self):
        """保存思维节点到持久化存储"""
        try:
            import os
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # 序列化思维节点数据
            storage_data = {
                'nodes': {},
                'metadata': {
                    'saved_at': time.time(),
                    'node_count': len(self.nodes)
                }
            }
            
            for node_id, node in self.nodes.items():
                storage_data['nodes'][node_id] = {
                    'content': node.content,
                    'vector': node.vector,
                    'metadata': node.metadata,
                    'importance': node.importance,
                    'connections': node.connections
                }
            
            # 保存到JSON文件
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存思维节点数据失败: {e}")
    
    def _load_from_storage(self):
        """从持久化存储加载思维节点"""
        try:
            import os
            import logging
            logger = logging.getLogger(__name__)
            
            if not os.path.exists(self.storage_path):
                print("⚠️  持久化存储文件不存在，当前思维节点数=0（首次启动）")
                logger.info("持久化存储文件不存在，将创建新文件")
                return
            
            # 检查文件大小，如果文件为空则跳过加载
            if os.path.getsize(self.storage_path) == 0:
                print("持久化存储文件为空，跳过加载")
                return
            
            # 从JSON文件加载数据
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("持久化存储文件内容为空，跳过加载")
                    return
                storage_data = json.loads(content)
            
            # 重建思维节点
            for node_id, node_data in storage_data['nodes'].items():
                node = ThoughtNode(
                    content=node_data['content'],
                    vector=node_data['vector'],
                    metadata=node_data['metadata']
                )
                node.importance = node_data['importance']
                node.connections = node_data['connections']
                self.nodes[node_id] = node
            
            print(f"✅ 从持久化存储加载了 {len(self.nodes)} 个思维节点（真实数据）")
            logger.info(f"从持久化存储加载了 {len(self.nodes)} 个思维节点")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}，将创建新的存储文件")
            # 如果JSON解析失败，重新创建文件
            self._save_to_storage()
        except Exception as e:
            print(f"加载思维节点数据失败: {e}")
            self.nodes = {}  # 出错时清空节点
    
    def save_thoughts(self) -> bool:
        """公开的持久化接口：保存所有思维节点到存储
        
        Returns:
            bool: 是否成功保存
        """
        try:
            self._save_to_storage()
            print(f"成功持久化 {len(self.nodes)} 个思维节点")
            return True
        except Exception as e:
            print(f"持久化思维节点失败: {e}")
            return False

class ContinuityContextBuilder:
    """思维连续性上下文构建器"""
    
    def __init__(self, thought_engine: MeshThoughtEngine):
        self.thought_engine = thought_engine
        self.session_context = {}
    
    def build_continuity_context(self, current_node: ThoughtNode, history_depth: int = 5) -> Dict[str, Any]:
        """构建连续性上下文"""
        # 获取当前思维的关联网络
        thought_network = self.thought_engine.get_thought_network(current_node.id, history_depth)
        
        # 构建连续性叙述
        continuity_narrative = self._build_narrative(thought_network)
        
        return {
            'current_thought': current_node.content,
            'thought_network': thought_network,
            'continuity_narrative': continuity_narrative,
            'session_context': self.session_context,
            'network_stats': {
                'total_nodes': len(thought_network['nodes']),
                'total_connections': len(thought_network['connections']),
                'max_depth': history_depth
            }
        }
    
    def _build_narrative(self, thought_network: Dict[str, Any]) -> str:
        """构建连续性叙述文本"""
        if not thought_network['nodes']:
            return "暂无关联思维节点"
        
        narrative_parts = []
        
        # 按重要性排序节点
        nodes_sorted = sorted(thought_network['nodes'], 
                            key=lambda x: x.get('importance', 0), reverse=True)
        
        for i, node in enumerate(nodes_sorted[:3]):  # 只取最重要的3个节点
            narrative_parts.append(f"相关思维{i+1}: {node['content']}")
        
        return "；".join(narrative_parts)

class NetworkEmpowerment:
    """网络赋能 - 解放LLM全部能力"""
    
    def __init__(self, thought_engine: MeshThoughtEngine):
        self.thought_engine = thought_engine
    
    def empower_llm(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """赋能LLM处理"""
        # 1. 存储当前查询作为思维节点
        query_node = self.thought_engine.store_thought(query, context)
        
        # 2. 思维连续性增强
        continuity_context = self._enhance_continuity(query_node)
        
        # 3. 关联思维激活
        activated_thoughts = self._activate_related_thoughts(query)
        
        # 4. 认知元复用优化
        optimized_context = self._optimize_with_reuse(continuity_context, activated_thoughts)
        
        return {
            'empowered_query': query,
            'enhanced_context': optimized_context,
            'activated_network': activated_thoughts,
            'continuity_level': self._calculate_continuity(optimized_context),
            'query_node_id': query_node.id
        }
    
    def _enhance_continuity(self, current_node: ThoughtNode) -> Dict[str, Any]:
        """增强思维连续性"""
        continuity_builder = ContinuityContextBuilder(self.thought_engine)
        return continuity_builder.build_continuity_context(current_node)
    
    def _activate_related_thoughts(self, query: str) -> List[Dict[str, Any]]:
        """激活关联思维"""
        query_vector = self.thought_engine.vector_store.embed(query)
        related_thoughts = self.thought_engine.find_similar_thoughts(query_vector, threshold=0.5)
        
        # 激活关联网络
        activated_network = []
        for thought in related_thoughts[:8]:  # 限制激活数量
            similarity = cosine_similarity(query_vector, thought.vector)
            activated_network.append({
                'thought_id': thought.id,
                'thought_content': thought.content[:150],
                'relevance': similarity,
                'connections_count': len(thought.connections),
                'importance': thought.importance
            })
        
        return activated_network
    
    def _optimize_with_reuse(self, continuity_context: Dict[str, Any], 
                           activated_thoughts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于认知元复用优化上下文"""
        optimized = continuity_context.copy()
        
        # 添加激活的思维网络信息
        optimized['activated_thoughts'] = activated_thoughts
        
        # 计算优化指标
        reuse_ratio = len(activated_thoughts) / max(1, self.thought_engine.get_node_count())
        optimized['optimization_metrics'] = {
            'reuse_ratio': reuse_ratio,
            'thoughts_activated': len(activated_thoughts),
            'average_relevance': np.mean([t['relevance'] for t in activated_thoughts]) if activated_thoughts else 0
        }
        
        return optimized
    
    def _calculate_continuity(self, context: Dict[str, Any]) -> float:
        """计算连续性水平"""
        network_stats = context.get('network_stats', {})
        total_nodes = network_stats.get('total_nodes', 0)
        total_connections = network_stats.get('total_connections', 0)
        
        if total_nodes == 0:
            return 0.0
        
        # 连续性指标：节点数量和连接密度
        connectivity_density = total_connections / max(1, total_nodes)
        continuity_score = min(1.0, (total_nodes * 0.1 + connectivity_density * 0.9))
        
        return continuity_score

def test_mesh_thought_engine():
    """测试网状思维引擎功能"""
    print("=== 网状思维引擎测试 ===")
    
    # 创建引擎实例
    engine = MeshThoughtEngine()
    
    # 存储一些测试思维
    thoughts = [
        "人工智能的未来发展",
        "机器学习在医疗领域的应用", 
        "深度学习模型的优化方法",
        "自然语言处理技术进展",
        "计算机视觉的最新突破"
    ]
    
    for thought in thoughts:
        node = engine.store_thought(thought)
        print(f"存储思维: {thought} -> 节点ID: {node.id}")
    
    # 测试相似思维查找
    query = "AI技术发展趋势"
    query_vector = engine.vector_store.embed(query)
    similar_nodes = engine.find_similar_thoughts(query_vector)
    
    print(f"\n查询: {query}")
    print(f"找到相似思维节点: {len(similar_nodes)}个")
    
    for i, node in enumerate(similar_nodes[:3]):
        similarity = cosine_similarity(query_vector, node.vector)
        print(f"相似节点{i+1}: {node.content} (相似度: {similarity:.3f})")
    
    # 测试网络赋能
    empowerment = NetworkEmpowerment(engine)
    result = empowerment.empower_llm("请分析AI在医疗领域的发展前景")
    
    print(f"\n网络赋能结果:")
    print(f"连续性水平: {result['continuity_level']:.3f}")
    print(f"激活思维节点: {len(result['activated_network'])}个")
    
    return engine

if __name__ == "__main__":
    test_mesh_thought_engine()