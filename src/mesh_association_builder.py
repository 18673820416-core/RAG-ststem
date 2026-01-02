#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网状思维引擎关联构建器
通过LLM协作实现记忆数据库的语义关联维补全

开发提示词来源：用户建议使用LLM协作遍历记忆数据库实现语义关联维补全
"""
# @self-expose: {"id": "mesh_association_builder", "name": "Mesh Association Builder", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Mesh Association Builder功能"]}}

import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .mesh_database_interface import MeshDatabaseInterface
from .llm_client_enhanced import LLMClientEnhanced

class MeshAssociationBuilder:
    """网状思维关联构建器 - LLM协作版本"""
    
    def __init__(self, mesh_interface: MeshDatabaseInterface, llm_client: LLMClientEnhanced = None):
        self.mesh_interface = mesh_interface
        
        # 创建或使用提供的LLM客户端
        if llm_client is None:
            # 使用模拟客户端进行测试
            try:
                self.llm_client = LLMClientEnhanced(provider="deepseek")
            except ValueError:
                # 创建一个简单的模拟客户端
                class MockLLMClient:
                    def slice_text_with_llm(self, text, metadata):
                        return []
                    def chat_completion(self, messages, **kwargs):
                        return "[]"
                self.llm_client = MockLLMClient()
        else:
            self.llm_client = llm_client
            
        self.batch_size = 100  # 每批处理数量
        
    def build_complete_association_network(self, max_memories: int = 1000) -> Dict[str, Any]:
        """构建完整的关联网络（LLM协作）"""
        print("🚀 开始构建完整的语义关联网络...")
        
        # 获取记忆数据
        memories = self.mesh_interface.vector_db.search_memories(limit=max_memories)
        
        if not memories:
            return {'error': '没有找到记忆数据'}
        
        print(f"📚 找到 {len(memories)} 条记忆，开始语义关联分析...")
        
        stats = {
            'total_processed': 0,
            'thought_nodes_created': 0,
            'thought_nodes_reused': 0,
            'associations_created': 0,
            'processing_time': 0
        }
        
        start_time = time.time()
        
        # 分批处理记忆
        for i in range(0, len(memories), self.batch_size):
            batch = memories[i:i + self.batch_size]
            batch_stats = self._process_memory_batch(batch, i // self.batch_size + 1)
            
            # 更新统计信息
            stats['total_processed'] += batch_stats['processed']
            stats['thought_nodes_created'] += batch_stats['nodes_created']
            stats['thought_nodes_reused'] += batch_stats['nodes_reused']
            stats['associations_created'] += batch_stats['associations']
            
            print(f"✅ 批次 {i//self.batch_size + 1} 完成: "
                  f"处理 {batch_stats['processed']} 条记忆, "
                  f"创建 {batch_stats['nodes_created']} 个思维节点")
        
        stats['processing_time'] = time.time() - start_time
        
        # 构建知识图谱
        knowledge_graph = self.mesh_interface.build_knowledge_graph()
        
        return {
            'association_stats': stats,
            'knowledge_graph': {
                'nodes': len(knowledge_graph['nodes']),
                'edges': len(knowledge_graph['edges'])
            },
            'completion_time': datetime.now().isoformat()
        }
    
    def _process_memory_batch(self, memories: List[Dict[str, Any]], batch_num: int) -> Dict[str, Any]:
        """处理一批记忆数据"""
        batch_stats = {
            'processed': 0,
            'nodes_created': 0,
            'nodes_reused': 0,
            'associations': 0
        }
        
        for memory in memories:
            try:
                # 检查是否已有思维节点关联
                if memory.get('thought_node_id'):
                    batch_stats['nodes_reused'] += 1
                    continue
                
                # 使用LLM分析记忆内容
                analysis_result = self._analyze_memory_with_llm(memory)
                
                # 基于分析结果创建或复用思维节点
                thought_result = self.mesh_interface.store_memory_with_mesh({
                    'content': memory['content'],
                    'topic': memory.get('topic', '未分类'),
                    'source_type': 'association_builder',
                    'importance': memory.get('importance', 0.5),
                    'llm_analysis': analysis_result
                })
                
                if thought_result.get('mesh_enhanced'):
                    if 'thought_node_id' in thought_result:
                        batch_stats['nodes_created'] += 1
                    batch_stats['associations'] += thought_result.get('connections_created', 0)
                
                batch_stats['processed'] += 1
                
                # 进度显示
                if batch_stats['processed'] % 10 == 0:
                    print(f"  进度: {batch_stats['processed']}/{len(memories)}")
                
            except Exception as e:
                print(f"❌ 处理记忆失败: {e}")
                continue
        
        return batch_stats
    
    def _analyze_memory_with_llm(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM分析记忆内容（语义理解）"""
        content = memory.get('content', '')[:500]  # 限制长度
        
        if not self.llm_client or not hasattr(self.llm_client, 'slice_text_with_llm'):
            # 如果没有LLM客户端或客户端不支持语义分析，使用简化分析
            return self._simple_semantic_analysis(content)
        
        try:
            # 使用现有的LLM切片功能进行语义分析
            metadata = {
                'source': 'association_builder',
                'purpose': 'semantic_analysis'
            }
            
            # 调用LLM进行智能分析
            slices = self.llm_client.slice_text_with_llm(content, metadata)
            
            if slices:
                # 使用第一个切片的内容进行分析
                slice_content = slices[0].get('content', content)
                return self._analyze_slice_content(slice_content)
            else:
                # 如果切片失败，使用简化分析
                return self._simple_semantic_analysis(content)
            
        except Exception as e:
            print(f"LLM分析失败，使用简化分析: {e}")
            return self._simple_semantic_analysis(content)
    
    def _analyze_slice_content(self, content: str) -> Dict[str, Any]:
        """分析切片内容（基于LLM切片结果）"""
        # 基于切片内容进行语义分析
        keywords = self._extract_keywords(content)
        
        return {
            'main_topics': keywords[:3],
            'key_concepts': keywords[:5],
            'semantic_category': self._categorize_content(content),
            'related_suggestions': keywords[3:6] if len(keywords) > 6 else [],
            'analysis_method': 'llm_slice_based'
        }
    
    def _simple_semantic_analysis(self, content: str) -> Dict[str, Any]:
        """简化语义分析（无LLM时使用）"""
        # 基于关键词的简单分析
        keywords = self._extract_keywords(content)
        
        return {
            'main_topics': keywords[:3],
            'key_concepts': keywords[:5],
            'semantic_category': self._categorize_content(content),
            'related_suggestions': keywords[3:6] if len(keywords) > 6 else [],
            'analysis_method': 'keyword_based'
        }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词（简化实现）"""
        # 中文停用词（简化版）
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '给', '可以', '通过', '这个', '这样', '已经', '现在', '因为', '所以', '但是', '如果', '然后', '而且', '或者', '虽然', '尽管', '即使', '为了', '由于', '因此', '然而', '不过', '总之', '例如', '比如', '特别', '尤其', '非常', '比较', '相对', '绝对', '完全', '彻底', '基本', '主要', '重要', '关键', '核心', '根本', '本质', '实质', '实际', '真正', '确实', '的确', '肯定', '一定', '必须', '需要', '应该', '应当', '可以', '能够', '可能', '也许', '大概', '大约', '左右', '上下', '前后', '先后', '先后顺序', '首先', '其次', '最后', '总之', '综上所述', '总的来说', '总而言之', '简而言之', '换句话说', '也就是说', '实际上', '事实上', '本质上', '从本质上讲', '从根本上说', '总的来说', '总体而言', '一般而言', '通常情况下', '一般来说', '大多数情况下', '少数情况下', '个别情况下', '特殊情况下', '正常情况下', '异常情况下', '紧急情况下', '危险情况下', '安全情况下', '稳定情况下', '不稳定情况下', '平衡状态下', '不平衡状态下', '对称状态下', '不对称状态下', '均匀状态下', '不均匀状态下', '连续状态下', '不连续状态下', '离散状态下', '连续离散状态下'}
        
        # 简单分词和关键词提取
        words = content.split()
        keywords = []
        
        for word in words:
            if (len(word) >= 2 and 
                word not in stop_words and 
                not word.isdigit() and
                word not in keywords):
                keywords.append(word)
        
        return keywords[:10]  # 限制数量
    
    def _categorize_content(self, content: str) -> str:
        """内容分类（简化实现）"""
        tech_keywords = {'技术', '科技', '人工智能', 'AI', '机器学习', '深度学习', '算法', '编程', '代码', '软件', '硬件', '网络', '数据', '数据库'}
        academic_keywords = {'研究', '学术', '论文', '科学', '理论', '实验', '分析', '方法', '模型', '框架', '概念', '定义'}
        
        content_words = set(content.split())
        
        if tech_keywords.intersection(content_words):
            return '技术'
        elif academic_keywords.intersection(content_words):
            return '学术'
        else:
            return '日常'
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 如果解析失败，返回默认结构
        return {
            'main_topics': ['未知'],
            'key_concepts': ['未知'],
            'semantic_category': '未知',
            'related_suggestions': [],
            'analysis_method': 'llm_fallback'
        }

# 测试函数
def test_association_builder():
    """测试关联构建器"""
    print("=== 网状思维关联构建器测试 ===")
    
    from mesh_database_interface import MeshDatabaseInterface
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 创建构建器（无LLM客户端）
    builder = MeshAssociationBuilder(interface)
    
    # 测试构建关联网络（小规模）
    result = builder.build_complete_association_network(max_memories=50)
    
    print(f"\n📊 关联构建结果:")
    print(f"  处理记忆总数: {result['association_stats']['total_processed']}")
    print(f"  创建思维节点: {result['association_stats']['thought_nodes_created']}")
    print(f"  复用思维节点: {result['association_stats']['thought_nodes_reused']}")
    print(f"  创建关联数: {result['association_stats']['associations_created']}")
    print(f"  处理时间: {result['association_stats']['processing_time']:.2f}秒")
    print(f"  知识图谱: {result['knowledge_graph']['nodes']}节点, {result['knowledge_graph']['edges']}边")

if __name__ == "__main__":
    test_association_builder()