#!/usr/bin/env python3
# @self-expose: {"id": "rebuild_knowledge_graph", "name": "Rebuild Knowledge Graph", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Rebuild Knowledge Graph功能"]}}
# -*- coding: utf-8 -*-
"""
知识图谱重建脚本 - 基于先进记忆锚点逻辑

开发提示词来源：记忆锚点_动态知识图谱生成过程.md
核心架构：网状思维引擎 + 主题维度树形结构 + 事件维度编码索引
先进特性：动态反应机制、逻辑链完整性、时间序列、因果关系

⚠️ 重要提醒：此脚本基于先进逻辑，避免使用落后的简单聚类方法
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
import hashlib
import re
from collections import defaultdict

class AdvancedKnowledgeGraphRebuilder:
    """先进知识图谱重建器 - 基于记忆锚点先进逻辑"""
    
    def __init__(self, db_path: str = 'data/rag_memory.db', 
                 graph_path: str = 'data/advanced_hierarchical_knowledge_graph.json'):
        self.db_path = db_path
        self.graph_path = graph_path
        
    def get_all_memories(self) -> List[Dict]:
        """获取所有记忆数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否有记忆数据
        cursor.execute('SELECT COUNT(*) FROM memory_units')
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("⚠️ 向量库为空，需要先收集数据")
            return []
        
        # 获取所有记忆
        cursor.execute('SELECT * FROM memory_units ORDER BY timestamp DESC')
        columns = [desc[0] for desc in cursor.description]
        memories = []
        
        for row in cursor.fetchall():
            memory = dict(zip(columns, row))
            memories.append(memory)
        
        conn.close()
        print(f"✅ 获取到 {len(memories)} 个记忆单元")
        return memories
    
    def build_mesh_thought_engine(self, memories: List[Dict]) -> Dict:
        """构建网状思维引擎（包含事件维度切片）"""
        print("🧠 构建网状思维引擎...")
        
        # 1. 主题维度树形结构构建
        topic_hierarchy = self._build_topic_hierarchy(memories)
        
        # 2. 事件维度编码索引
        event_dimensions = self._encode_event_dimensions(memories)
        
        # 3. 逻辑链完整性分析（包含事件维度切片）
        logic_chains = self._analyze_logic_chains(memories)
        
        # 4. 时间序列关联
        temporal_relations = self._build_temporal_relations(memories)
        
        # 5. 因果关系挖掘
        causal_relations = self._extract_causal_relations(memories)
        
        # 统计事件维度切片信息
        event_slices = []
        event_slice_count = 0
        
        for chain in logic_chains:
            if chain.get('event_dimension', False):
                event_slice_count += 1
                if 'event_slices' in chain:
                    event_slices.extend(chain['event_slices'])
        
        mesh_engine = {
            'topic_hierarchy': topic_hierarchy,
            'event_dimensions': event_dimensions,
            'logic_chains': logic_chains,
            'temporal_relations': temporal_relations,
            'causal_relations': causal_relations,
            'event_slices': event_slices,
            'total_memories': len(memories),
            'event_slices_count': event_slice_count,
            'total_event_slices': len(event_slices),
            'event_dimension_analysis': {
                'large_text_blocks': sum(1 for mem in memories if len(mem.get('content', '')) > 500),
                'sliced_blocks': event_slice_count,
                'slice_types': list(set(slice.get('slice_type', '') for slice in event_slices))
            }
        }
        
        print(f"✅ 网状思维引擎构建完成: {len(logic_chains)} 条逻辑链, {len(temporal_relations)} 个时间关系")
        print(f"📊 事件维度切片: {event_slice_count} 个大型文本块被切片, 共生成 {len(event_slices)} 个事件维度切片")
        return mesh_engine
    
    def _build_topic_hierarchy(self, memories: List[Dict]) -> Dict:
        """构建主题维度树形结构"""
        print("🌳 构建主题维度树形结构...")
        
        # 基于记忆主题构建层次结构
        topic_groups = defaultdict(list)
        for mem in memories:
            topic = mem.get('topic', '未分类')
            topic_groups[topic].append(mem)
        
        # 构建主题层次（全局-主题-子主题三级结构）
        hierarchy = {
            'global': {
                'name': '全局知识图谱',
                'children': {},
                'memories': memories,
                'coverage': len(memories)
            }
        }
        
        # 主题层
        for topic, topic_memories in topic_groups.items():
            # 子主题分析（基于内容关键词）
            subtopics = self._extract_subtopics(topic_memories)
            
            hierarchy['global']['children'][topic] = {
                'name': topic,
                'children': subtopics,
                'memories': topic_memories,
                'coverage': len(topic_memories)
            }
        
        return hierarchy
    
    def _encode_event_dimensions(self, memories: List[Dict]) -> Dict:
        """事件维度编码索引"""
        print("📊 事件维度编码索引...")
        
        event_dimensions = {
            'logic_chain_integrity': [],  # 逻辑链完整性
            'time_sequence': [],          # 时间序列
            'causal_relationships': []   # 因果关系
        }
        
        # 按时间排序记忆
        sorted_memories = sorted(memories, key=lambda x: x.get('timestamp', ''))
        
        # 分析逻辑链完整性
        for i in range(len(sorted_memories) - 1):
            current_mem = sorted_memories[i]
            next_mem = sorted_memories[i + 1]
            
            # 检查逻辑连续性
            logic_score = self._calculate_logic_continuity(current_mem, next_mem)
            if logic_score > 0.3:
                event_dimensions['logic_chain_integrity'].append({
                    'source': current_mem['id'],
                    'target': next_mem['id'],
                    'score': logic_score,
                    'type': 'logic_continuity'
                })
        
        # 构建时间序列
        for i in range(len(sorted_memories) - 1):
            current_mem = sorted_memories[i]
            next_mem = sorted_memories[i + 1]
            
            event_dimensions['time_sequence'].append({
                'source': current_mem['id'],
                'target': next_mem['id'],
                'time_gap': self._calculate_time_gap(current_mem, next_mem),
                'sequence_type': 'temporal'
            })
        
        return event_dimensions
    
    def _analyze_logic_chains(self, memories: List[Dict]) -> List[Dict]:
        """分析逻辑链完整性（包含事件维度二次切片）"""
        logic_chains = []
        
        # 基于内容相似度和时间连续性构建逻辑链
        visited = set()
        
        for mem in memories:
            if mem['id'] in visited:
                continue
            
            # 对大型文本块进行事件维度二次切片
            if len(mem.get('content', '')) > 500:  # 超过500字符的文本块需要二次切片
                event_slices = self._slice_event_dimension(mem)
                if event_slices:
                    # 为每个切片创建逻辑链
                    for slice_data in event_slices:
                        logic_chains.append({
                            'chain_id': f"event_chain_{len(logic_chains)}",
                            'memories': [mem['id']],  # 原始记忆ID
                            'event_slices': [slice_data],
                            'length': 1,
                            'coherence_score': 0.8,
                            'event_dimension': True,
                            'slice_type': slice_data['slice_type'],
                            'sequence_order': slice_data['sequence_order']
                        })
                    visited.add(mem['id'])
                    continue
            
            # 常规逻辑链构建
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
            
            if len(chain) > 1:
                logic_chains.append({
                    'chain_id': f"logic_chain_{len(logic_chains)}",
                    'memories': [m['id'] for m in chain],
                    'length': len(chain),
                    'coherence_score': self._calculate_chain_coherence(chain),
                    'event_dimension': False
                })
        
        return logic_chains
    
    def _slice_event_dimension(self, memory: Dict) -> List[Dict]:
        """对大型文本块进行事件维度二次切片（支持递归分片层级编码）"""
        content = memory.get('content', '')
        
        # 检查是否已经是递归分片的结果（包含slice_id层级编码）
        if 'slice_id' in memory and '.' in memory.get('slice_id', ''):
            # 已经是递归分片结果，直接返回
            return [{
                'slice_id': memory['slice_id'],
                'slice_type': 'recursive_slice',
                'content': content,
                'sequence_order': self._parse_slice_order(memory['slice_id']),
                'keywords': [],
                'original_memory_id': memory['id'],
                'slice_length': len(content),
                'slice_depth': self._parse_slice_depth(memory['slice_id']),
                'hierarchical_path': memory['slice_id']
            }]
        
        if len(content) <= 500:
            return []
        
        slices = []
        
        # 事件维度切片模式：原因、过程、结果、深化等
        event_patterns = {
            'cause': ['因为', '原因', '由于', '背景', '起因'],
            'process': ['过程', '步骤', '方法', '实施', '进行'],
            'deepening': ['深化', '深入', '进一步', '扩展', '发展'],
            'result': ['结果', '结论', '效果', '成果', '影响']
        }
        
        # 基于关键词识别事件维度切片
        for slice_type, keywords in event_patterns.items():
            # 查找包含关键词的段落
            paragraphs = content.split('。')
            relevant_paragraphs = []
            
            for para in paragraphs:
                if any(keyword in para for keyword in keywords):
                    relevant_paragraphs.append(para.strip())
            
            if relevant_paragraphs:
                slice_content = '。'.join(relevant_paragraphs)
                if len(slice_content) > 50:  # 确保切片有足够内容
                    slices.append({
                        'slice_id': f"{memory['id']}_{slice_type}",
                        'slice_type': slice_type,
                        'content': slice_content,
                        'sequence_order': len(slices) + 1,
                        'keywords': keywords,
                        'original_memory_id': memory['id'],
                        'slice_length': len(slice_content)
                    })
        
        # 如果没有找到明确的事件维度，按段落进行智能切片
        if not slices and len(content) > 800:
            paragraphs = content.split('。')
            for i, para in enumerate(paragraphs):
                if len(para.strip()) > 100:  # 只处理有内容的段落
                    slice_type = 'paragraph'
                    if i == 0:
                        slice_type = 'introduction'
                    elif i == len(paragraphs) - 1:
                        slice_type = 'conclusion'
                    
                    slices.append({
                        'slice_id': f"{memory['id']}_{slice_type}_{i}",
                        'slice_type': slice_type,
                        'content': para.strip(),
                        'sequence_order': i + 1,
                        'keywords': [],
                        'original_memory_id': memory['id'],
                        'slice_length': len(para.strip())
                    })
        
        return slices
    
    def _parse_slice_order(self, slice_id: str) -> int:
        """解析切片ID获取顺序编号"""
        if not slice_id:
            return 1
        
        # 层级编码格式：1.2.3 -> 取最后一部分作为顺序
        parts = slice_id.split('.')
        try:
            return int(parts[-1])
        except:
            return 1
    
    def _parse_slice_depth(self, slice_id: str) -> int:
        """解析切片ID获取深度"""
        if not slice_id:
            return 1
        
        parts = slice_id.split('.')
        return len(parts)
    
    def _build_temporal_relations(self, memories: List[Dict]) -> List[Dict]:
        """构建时间序列关联"""
        temporal_relations = []
        
        # 按时间排序
        sorted_memories = sorted(memories, key=lambda x: x.get('timestamp', ''))
        
        for i in range(len(sorted_memories) - 1):
            source_mem = sorted_memories[i]
            target_mem = sorted_memories[i + 1]
            
            temporal_relations.append({
                'source': source_mem['id'],
                'target': target_mem['id'],
                'relation_type': 'temporal_sequence',
                'time_gap': self._calculate_time_gap(source_mem, target_mem),
                'strength': max(0.8 - (self._calculate_time_gap(source_mem, target_mem) / 86400) * 0.5, 0.3)
            })
        
        return temporal_relations
    
    def _extract_causal_relations(self, memories: List[Dict]) -> List[Dict]:
        """提取因果关系"""
        causal_relations = []
        
        # 基于因果关键词和逻辑分析
        causal_keywords = ['因为', '所以', '导致', '引起', '结果', '原因', '因此', '于是']
        
        for i, mem1 in enumerate(memories):
            content1 = mem1.get('content', '').lower()
            
            for j, mem2 in enumerate(memories):
                if i == j:
                    continue
                
                content2 = mem2.get('content', '').lower()
                
                # 检查因果关键词
                causal_score = self._calculate_causal_score(content1, content2, causal_keywords)
                
                if causal_score > 0.4:
                    causal_relations.append({
                        'cause': mem1['id'],
                        'effect': mem2['id'],
                        'score': causal_score,
                        'evidence': 'keyword_analysis'
                    })
        
        return causal_relations
    
    # 辅助方法
    def _extract_subtopics(self, memories: List[Dict]) -> Dict:
        """提取子主题"""
        subtopics = {}
        
        # 基于内容关键词聚类
        keyword_patterns = {
            '技术实现': ['代码', '实现', '开发', '编程'],
            '问题分析': ['问题', '错误', '解决', '调试'],
            '设计讨论': ['设计', '架构', '方案', '规划'],
            '学习研究': ['学习', '研究', '探索', '分析']
        }
        
        for pattern_name, keywords in keyword_patterns.items():
            pattern_memories = []
            for mem in memories:
                content = mem.get('content', '').lower()
                if any(keyword in content for keyword in keywords):
                    pattern_memories.append(mem)
            
            if pattern_memories:
                subtopics[pattern_name] = {
                    'memories': pattern_memories,
                    'coverage': len(pattern_memories)
                }
        
        return subtopics
    
    def _calculate_logic_continuity(self, mem1: Dict, mem2: Dict) -> float:
        """计算逻辑连续性得分"""
        content1 = mem1.get('content', '').lower()
        content2 = mem2.get('content', '').lower()
        
        # 基于关键词重叠和语义连续性
        words1 = set(content1.split()[:20])
        words2 = set(content2.split()[:20])
        
        if not words1 or not words2:
            return 0.0
        
        similarity = len(words1.intersection(words2)) / len(words1.union(words2))
        
        # 时间连续性加成
        time_gap = self._calculate_time_gap(mem1, mem2)
        time_bonus = max(0, 1.0 - time_gap / 3600)  # 1小时内加成
        
        return similarity * 0.7 + time_bonus * 0.3
    
    def _calculate_time_gap(self, mem1: Dict, mem2: Dict) -> float:
        """计算时间间隔（秒）"""
        try:
            time1 = datetime.fromisoformat(mem1.get('timestamp', '').replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(mem2.get('timestamp', '').replace('Z', '+00:00'))
            return abs((time2 - time1).total_seconds())
        except:
            return float('inf')
    
    def _find_logical_successor(self, current_mem: Dict, memories: List[Dict], visited: Set) -> Dict:
        """寻找逻辑后继记忆"""
        best_successor = None
        best_score = 0.0
        
        for mem in memories:
            if mem['id'] in visited or mem['id'] == current_mem['id']:
                continue
            
            score = self._calculate_logic_continuity(current_mem, mem)
            if score > best_score and score > 0.4:
                best_score = score
                best_successor = mem
        
        return best_successor
    
    def _calculate_chain_coherence(self, chain: List[Dict]) -> float:
        """计算逻辑链连贯性得分"""
        if len(chain) < 2:
            return 0.0
        
        total_score = 0.0
        for i in range(len(chain) - 1):
            total_score += self._calculate_logic_continuity(chain[i], chain[i+1])
        
        return total_score / (len(chain) - 1)
    
    def _calculate_causal_score(self, content1: str, content2: str, keywords: List[str]) -> float:
        """计算因果关系得分"""
        score = 0.0
        
        # 检查因果关键词
        for keyword in keywords:
            if keyword in content1 and any(kw in content2 for kw in ['结果', '导致', '引起']):
                score += 0.3
            if keyword in content2 and any(kw in content1 for kw in ['因为', '原因', '由于']):
                score += 0.3
        
        # 语义相似度加成
        words1 = set(content1.split()[:15])
        words2 = set(content2.split()[:15])
        
        if words1 and words2:
            similarity = len(words1.intersection(words2)) / len(words1.union(words2))
            score += similarity * 0.4
        
        return min(score, 1.0)
    
    def build_advanced_knowledge_graph(self, memories: List[Dict]) -> Dict:
        """构建高级知识图谱（支持递归分片层级编码）"""
        print("🚀 构建支持递归分片层级编码的高级知识图谱...")
        
        # 初始化图谱结构
        knowledge_graph = {
            'global_layer': {'nodes': [], 'edges': []},
            'topic_layer': {'nodes': [], 'edges': []},
            'event_layer': {'nodes': [], 'edges': []},
            'hierarchical_layer': {'nodes': [], 'edges': []},  # 新增层级编码层
            'metadata': {
                'total_nodes': 0,
                'total_edges': 0,
                'creation_time': datetime.now().isoformat(),
                'version': '2.1',  # 版本更新
                'hierarchical_support': True
            }
        }
        
        # 构建主题层级
        topic_hierarchy = self._build_topic_hierarchy(memories)
        knowledge_graph['topic_layer']['nodes'] = topic_hierarchy
        
        # 处理每个记忆，构建事件维度切片
        for memory in memories:
            # 构建全局层节点
            global_node = {
                'id': memory['id'],
                'type': 'memory',
                'content': memory.get('content', '')[:200],  # 截取前200字符
                'timestamp': memory.get('timestamp', ''),
                'importance': memory.get('importance', 0),
                'slice_count': 0,
                'hierarchical_depth': 1  # 默认深度为1
            }
            knowledge_graph['global_layer']['nodes'].append(global_node)
            
            # 事件维度切片（支持递归分片）
            event_slices = self._slice_event_dimension(memory)
            memory['slice_count'] = len(event_slices)
            
            for slice_data in event_slices:
                # 构建事件层节点
                event_node = {
                    'id': slice_data['slice_id'],
                    'type': 'event_slice',
                    'slice_type': slice_data['slice_type'],
                    'content': slice_data['content'][:150],
                    'sequence_order': slice_data['sequence_order'],
                    'original_memory_id': memory['id'],
                    'keywords': slice_data.get('keywords', []),
                    'slice_length': slice_data['slice_length'],
                    'slice_depth': slice_data.get('slice_depth', 1),
                    'hierarchical_path': slice_data.get('hierarchical_path', '')
                }
                knowledge_graph['event_layer']['nodes'].append(event_node)
                
                # 构建全局层到事件层的关联
                edge = {
                    'id': f"{memory['id']}_{slice_data['slice_id']}",
                    'source': memory['id'],
                    'target': slice_data['slice_id'],
                    'type': 'contains',
                    'weight': 1.0
                }
                knowledge_graph['global_layer']['edges'].append(edge)
                
                # 如果是递归分片，构建层级编码层
                if 'hierarchical_path' in slice_data and slice_data['hierarchical_path']:
                    self._build_hierarchical_structure(knowledge_graph, slice_data, memory)
        
        # 构建时间序列关联
        temporal_relations = self._build_temporal_relations(memories)
        knowledge_graph['event_layer']['edges'].extend(temporal_relations)
        
        # 构建因果关联
        causal_relations = self._extract_causal_relations(memories)
        knowledge_graph['event_layer']['edges'].extend(causal_relations)
        
        # 构建逻辑链
        logic_chains = self._analyze_logic_chains(memories)
        knowledge_graph['event_layer']['edges'].extend(logic_chains)
        
        # 更新元数据
        knowledge_graph['metadata']['total_nodes'] = (
            len(knowledge_graph['global_layer']['nodes']) +
            len(knowledge_graph['topic_layer']['nodes']) +
            len(knowledge_graph['event_layer']['nodes']) +
            len(knowledge_graph['hierarchical_layer']['nodes'])
        )
        knowledge_graph['metadata']['total_edges'] = (
            len(knowledge_graph['global_layer']['edges']) +
            len(knowledge_graph['topic_layer']['edges']) +
            len(knowledge_graph['event_layer']['edges']) +
            len(knowledge_graph['hierarchical_layer']['edges'])
        )
        
        print(f"✅ 支持递归分片层级编码的高级知识图谱构建完成，共 {knowledge_graph['metadata']['total_nodes']} 个节点，"
              f"{knowledge_graph['metadata']['total_edges']} 条边")
        
        return knowledge_graph
    
    def _build_hierarchical_structure(self, knowledge_graph: Dict, slice_data: Dict, memory: Dict):
        """构建递归分片的层级结构"""
        hierarchical_path = slice_data['hierarchical_path']
        parts = hierarchical_path.split('.')
        
        # 构建层级节点
        for i in range(1, len(parts)):
            parent_id = '.'.join(parts[:i])
            current_id = '.'.join(parts[:i+1])
            
            # 检查是否已存在该层级节点
            existing_nodes = [n for n in knowledge_graph['hierarchical_layer']['nodes'] 
                            if n['id'] == current_id]
            
            if not existing_nodes:
                # 创建层级节点
                hierarchical_node = {
                    'id': current_id,
                    'type': 'hierarchical_slice',
                    'depth': i + 1,
                    'parent_id': parent_id if i > 0 else memory['id'],
                    'sequence_order': int(parts[i]),
                    'content_preview': slice_data['content'][:100] if i == len(parts) - 1 else '',
                    'original_memory_id': memory['id']
                }
                knowledge_graph['hierarchical_layer']['nodes'].append(hierarchical_node)
                
                # 构建层级关联边
                edge = {
                    'id': f"{parent_id}_{current_id}",
                    'source': parent_id,
                    'target': current_id,
                    'type': 'hierarchical_contains',
                    'weight': 1.0 - (i * 0.1)  # 深度越深，权重越低
                }
                knowledge_graph['hierarchical_layer']['edges'].append(edge)
    
    def save_advanced_knowledge_graph(self, graph_data: Dict):
        """保存支持递归分片层级编码的高级知识图谱"""
        print("💾 保存支持递归分片层级编码的高级知识图谱...")
        
        # 创建分层结构（支持层级编码）
        hierarchical_graph = {
            'global_layer': {
                'layer': 'global',
                'name': '全局知识图谱',
                'nodes': graph_data['global_layer']['nodes'],
                'edges': graph_data['global_layer']['edges'],
                'metadata': {
                    'version': graph_data['metadata']['version'],
                    'hierarchical_support': graph_data['metadata']['hierarchical_support'],
                    'build_time': graph_data['metadata']['creation_time'],
                    'total_nodes': len(graph_data['global_layer']['nodes']),
                    'total_edges': len(graph_data['global_layer']['edges'])
                }
            },
            'topic_layer': {
                'layer': 'topic',
                'nodes': graph_data['topic_layer']['nodes'],
                'edges': graph_data['topic_layer']['edges'],
                'metadata': {
                    'total_nodes': len(graph_data['topic_layer']['nodes']),
                    'total_edges': len(graph_data['topic_layer']['edges']),
                    'build_time': graph_data['metadata']['creation_time']
                }
            },
            'event_layer': {
                'layer': 'event',
                'nodes': graph_data['event_layer']['nodes'],
                'edges': graph_data['event_layer']['edges'],
                'metadata': {
                    'total_nodes': len(graph_data['event_layer']['nodes']),
                    'total_edges': len(graph_data['event_layer']['edges']),
                    'build_time': graph_data['metadata']['creation_time']
                }
            },
            'hierarchical_layer': {
                'layer': 'hierarchical',
                'name': '层级编码图谱',
                'nodes': graph_data['hierarchical_layer']['nodes'],
                'edges': graph_data['hierarchical_layer']['edges'],
                'metadata': {
                    'total_nodes': len(graph_data['hierarchical_layer']['nodes']),
                    'total_edges': len(graph_data['hierarchical_layer']['edges']),
                    'max_depth': max([n.get('depth', 1) for n in graph_data['hierarchical_layer']['nodes']]) if graph_data['hierarchical_layer']['nodes'] else 1,
                    'build_time': graph_data['metadata']['creation_time'],
                    'hierarchical_support': True
                }
            }
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        
        with open(self.graph_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchical_graph, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 支持递归分片层级编码的高级知识图谱已保存到: {self.graph_path}")
        
        # 显示统计信息
        stats = graph_data['metadata']
        print(f"📊 递归分片层级编码重建统计:")
        print(f"   总节点数: {stats['total_nodes']}")
        print(f"   总边数: {stats['total_edges']}")
        print(f"   全局层节点: {len(graph_data['global_layer']['nodes'])}")
        print(f"   主题层节点: {len(graph_data['topic_layer']['nodes'])}")
        print(f"   事件层节点: {len(graph_data['event_layer']['nodes'])}")
        print(f"   层级编码层节点: {len(graph_data['hierarchical_layer']['nodes'])}")
        print(f"   最大层级深度: {max([n.get('slice_depth', 1) for n in graph_data['event_layer']['nodes']]) if graph_data['event_layer']['nodes'] else 1}")
        print(f"   层级编码支持: {'已启用' if stats['hierarchical_support'] else '未启用'}")
        print(f"   版本: {stats['version']}")
        print(f"   构建时间: {stats['creation_time']}")
    
    def rebuild_advanced(self):
        """执行先进重建流程（基于记忆锚点先进逻辑）"""
        print("🚀 开始先进知识图谱重建...")
        print("⚠️  使用记忆锚点先进逻辑：网状思维引擎+主题维度树形结构")
        
        # 1. 获取所有记忆
        memories = self.get_all_memories()
        if not memories:
            print("❌ 没有记忆数据，无法重建知识图谱")
            return False
        
        # 2. 构建先进知识图谱
        advanced_graph = self.build_advanced_knowledge_graph(memories)
        
        # 3. 保存先进知识图谱
        self.save_advanced_knowledge_graph(advanced_graph)
        
        print("🎉 先进知识图谱重建完成！")
        return True

def main():
    """主函数 - 使用先进逻辑重建知识图谱"""
    rebuilder = AdvancedKnowledgeGraphRebuilder()
    
    print("=" * 60)
    print("🧠 先进知识图谱重建工具（基于记忆锚点先进逻辑）")
    print("=" * 60)
    print("⚠️  重要提醒：此工具使用先进架构，避免落后逻辑")
    print("📚 参考文档：记忆锚点_动态知识图谱生成过程.md")
    print("-" * 60)
    
    success = rebuilder.rebuild_advanced()
    
    if success:
        print("\n✅ 先进重建成功！知识图谱已与向量库同步")
        print("💡 先进特性已启用：事件维度编码索引、逻辑链完整性分析等")
    else:
        print("\n❌ 重建失败，请检查向量库中是否有数据")

if __name__ == "__main__":
    main()