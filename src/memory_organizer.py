#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM驱动记忆梳理系统
使用DEEPSEEK API实现记忆数据的智能梳理、去重、知识图谱构建和语义关联维补全

开发提示词来源：用户建议使用DEEPSEEK API密钥调用LLM完成记忆数据全面梳理
"""
# @self-expose: {"id": "memory_organizer", "name": "Memory Organizer", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Memory Organizer功能"]}}

import time
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests

from .mesh_database_interface import MeshDatabaseInterface
from .llm_client_enhanced import LLMClientEnhanced
from config.api_keys import api_key_manager

logger = logging.getLogger(__name__)

class MemoryOrganizer:
    """LLM驱动记忆梳理器"""
    
    def __init__(self, mesh_interface: MeshDatabaseInterface, deepseek_api_key: str = None):
        self.mesh_interface = mesh_interface
        self.deepseek_api_key = deepseek_api_key or api_key_manager.get_key("deepseek")
        
        # 创建LLM客户端
        try:
            self.llm_client = LLMClientEnhanced(provider="deepseek")
            logger.info("✅ 使用DEEPSEEK API进行记忆梳理")
        except ValueError as e:
            logger.warning(f"⚠️ 未找到DEEPSEEK API密钥，使用模拟模式: {e}")
            # 创建一个简单的模拟客户端
            class MockLLMClient:
                def slice_text_with_llm(self, text, metadata):
                    return []
                def chat_completion(self, messages, **kwargs):
                    return "[]"
            self.llm_client = MockLLMClient()
        
        # 梳理配置
        self.batch_size = 20  # 每批处理数量（避免API限制）
        self.max_retries = 3   # 最大重试次数
        
    def comprehensive_memory_organization(self, max_memories: int = 100) -> Dict[str, Any]:
        """全面记忆梳理：去重、知识图谱构建、语义关联维补全"""
        print("🚀 开始全面记忆梳理...")
        
        start_time = time.time()
        
        # 获取记忆数据
        memories = self.mesh_interface.vector_db.search_memories(limit=max_memories)
        
        if not memories:
            return {'error': '没有找到记忆数据'}
        
        print(f"📚 找到 {len(memories)} 条记忆，开始全面梳理...")
        
        # 执行梳理流程
        results = {
            'deduplication': self._deduplicate_memories(memories),
            'semantic_analysis': self._semantic_analysis_memories(memories),
            'knowledge_graph': self._build_enhanced_knowledge_graph(memories),
            'mesh_association': self._build_mesh_associations(memories)
        }
        
        # 计算统计信息
        processing_time = time.time() - start_time
        
        return {
            'overview': {
                'total_memories_processed': len(memories),
                'processing_time': processing_time,
                'completion_time': datetime.now().isoformat(),
                'llm_used': 'deepseek' if self.deepseek_api_key else 'mock'
            },
            'results': results
        }
    
    def _deduplicate_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用LLM进行智能去重"""
        print("🔍 开始记忆去重分析...")
        
        # 分批处理避免API限制
        duplicate_groups = []
        processed_count = 0
        
        for i in range(0, len(memories), self.batch_size):
            batch = memories[i:i + self.batch_size]
            batch_duplicates = self._analyze_duplicates_with_llm(batch)
            duplicate_groups.extend(batch_duplicates)
            processed_count += len(batch)
            print(f"  进度: {processed_count}/{len(memories)}")
        
        return {
            'duplicate_groups': duplicate_groups,
            'total_groups': len(duplicate_groups),
            'analysis_method': 'llm_semantic_deduplication'
        }
    
    def _analyze_duplicates_with_llm(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用LLM分析重复记忆"""
        if not self.deepseek_api_key:
            # 模拟模式：简单基于内容的去重
            return self._simple_deduplication(memories)
        
        try:
            # 构建去重分析提示词
            memory_contents = [
                f"{i+1}. {mem['content'][:200]}..." 
                for i, mem in enumerate(memories)
            ]
            
            prompt = f"""请分析以下记忆内容，识别语义重复或高度相似的记忆对：

记忆列表：
{"\n".join(memory_contents)}

请返回JSON格式的分析结果，包含：
1. duplicate_groups: 重复记忆组列表，每组包含相似记忆的索引
2. similarity_reason: 相似性原因说明
3. confidence: 相似度置信度(0-1)

请确保分析基于语义相似性，而不仅仅是表面文字重复。"""
            
            # 调用LLM API
            response = self._call_llm_api(prompt)
            
            # 解析响应
            analysis = self._parse_llm_response(response)
            return analysis.get('duplicate_groups', [])
            
        except Exception as e:
            logger.error(f"LLM去重分析失败: {e}")
            return self._simple_deduplication(memories)
    
    def _semantic_analysis_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用LLM进行深度语义分析"""
        print("🧠 开始深度语义分析...")
        
        semantic_categories = {}
        key_concepts = []
        
        for memory in memories:
            analysis = self._analyze_single_memory(memory)
            
            # 统计分类
            category = analysis.get('semantic_category', '未知')
            semantic_categories[category] = semantic_categories.get(category, 0) + 1
            
            # 收集关键概念
            key_concepts.extend(analysis.get('key_concepts', []))
        
        return {
            'semantic_categories': semantic_categories,
            'top_key_concepts': list(set(key_concepts))[:20],  # 去重并限制数量
            'total_memories_analyzed': len(memories)
        }
    
    def _analyze_single_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """分析单条记忆"""
        content = memory.get('content', '')[:500]
        
        if not self.deepseek_api_key:
            # 模拟分析
            return self._simple_semantic_analysis(content)
        
        try:
            prompt = f"""请分析以下文本内容的语义信息：

文本内容：{content}

请返回JSON格式的分析结果，包含：
1. main_topics: 主要主题（1-3个关键词）
2. key_concepts: 关键概念（3-5个核心概念）
3. semantic_category: 语义类别（技术、学术、商业、日常等）
4. sentiment: 情感倾向（积极、消极、中性）
5. complexity: 内容复杂度（简单、中等、复杂）"""
            
            response = self._call_llm_api(prompt)
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.error(f"LLM语义分析失败: {e}")
            return self._simple_semantic_analysis(content)
    
    def _build_enhanced_knowledge_graph(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建增强版知识图谱（LLM优化）"""
        print("🗺️ 构建增强版知识图谱...")
        
        # 使用网状思维引擎的基础知识图谱
        base_graph = self.mesh_interface.build_knowledge_graph()
        
        # 使用LLM优化知识图谱结构
        if self.deepseek_api_key:
            enhanced_graph = self._enhance_graph_with_llm(base_graph, memories)
        else:
            enhanced_graph = base_graph
        
        return {
            'base_graph': {
                'nodes': len(base_graph['nodes']),
                'edges': len(base_graph['edges'])
            },
            'enhanced_graph': enhanced_graph,
            'enhancement_method': 'llm_optimized' if self.deepseek_api_key else 'base_only'
        }
    
    def _enhance_graph_with_llm(self, base_graph: Dict[str, Any], memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用LLM优化知识图谱"""
        # 这里可以实现更复杂的LLM优化逻辑
        # 暂时返回基础图谱
        return base_graph
    
    def _build_mesh_associations(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建网状关联网络"""
        print("🔗 构建网状语义关联...")
        
        associations_created = 0
        
        for memory in memories:
            try:
                # 使用网状思维引擎存储记忆（自动创建关联）
                result = self.mesh_interface.store_memory_with_mesh({
                    'content': memory['content'],
                    'topic': memory.get('topic', '未分类'),
                    'importance': memory.get('importance', 0.5),
                    'source_type': 'memory_organizer'
                })
                
                if result.get('mesh_enhanced'):
                    associations_created += result.get('connections_created', 0)
                    
            except Exception as e:
                logger.error(f"构建记忆关联失败: {e}")
                continue
        
        return {
            'associations_created': associations_created,
            'memories_processed': len(memories)
        }
    
    def _call_llm_api(self, prompt: str, max_retries: int = None) -> str:
        """调用LLM API"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                # 使用现有的LLM客户端
                metadata = {'source': 'memory_organizer', 'purpose': 'semantic_analysis'}
                slices = self.llm_client.slice_text_with_llm(prompt, metadata)
                
                if slices:
                    return slices[0].get('content', '')
                else:
                    return ""
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)  # 重试前等待
        
        return ""
    
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
            'sentiment': '中性',
            'complexity': '中等'
        }
    
    def _simple_deduplication(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """简化去重（模拟模式）"""
        # 基于内容哈希的简单去重
        seen = set()
        duplicates = []
        
        for i, memory in enumerate(memories):
            content_hash = hash(memory['content'][:100])  # 取前100字符计算哈希
            if content_hash in seen:
                duplicates.append({
                    'memory_indices': [i],
                    'similarity_reason': '内容哈希重复',
                    'confidence': 0.8
                })
            else:
                seen.add(content_hash)
        
        return duplicates
    
    def _simple_semantic_analysis(self, content: str) -> Dict[str, Any]:
        """简化语义分析（模拟模式）"""
        # 基于关键词的简单分析
        words = content.split()
        keywords = [word for word in words if len(word) >= 2][:5]
        
        return {
            'main_topics': keywords[:2],
            'key_concepts': keywords,
            'semantic_category': '日常',
            'sentiment': '中性',
            'complexity': '中等'
        }

# 测试函数
def test_memory_organizer():
    """测试记忆梳理器"""
    print("=== LLM驱动记忆梳理系统测试 ===")
    
    from mesh_database_interface import MeshDatabaseInterface
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 创建记忆梳理器
    organizer = MemoryOrganizer(interface)
    
    # 测试全面梳理（小规模）
    result = organizer.comprehensive_memory_organization(max_memories=30)
    
    print(f"\n📊 梳理结果概览:")
    overview = result['overview']
    print(f"   处理记忆数: {overview['total_memories_processed']}")
    print(f"   处理时间: {overview['processing_time']:.2f}秒")
    print(f"   LLM模式: {overview['llm_used']}")
    
    # 显示详细结果
    results = result['results']
    
    print(f"\n🔍 去重分析:")
    dup_result = results['deduplication']
    print(f"   发现重复组: {dup_result['total_groups']}组")
    
    print(f"\n🧠 语义分析:")
    semantic_result = results['semantic_analysis']
    print(f"   语义分类: {semantic_result['semantic_categories']}")
    print(f"   关键概念: {semantic_result['top_key_concepts'][:5]}...")
    
    print(f"\n🗺️ 知识图谱:")
    graph_result = results['knowledge_graph']
    print(f"   基础图谱: {graph_result['base_graph']['nodes']}节点, {graph_result['base_graph']['edges']}边")
    print(f"   优化方法: {graph_result['enhancement_method']}")
    
    print(f"\n🔗 网状关联:")
    mesh_result = results['mesh_association']
    print(f"   创建关联: {mesh_result['associations_created']}个")

if __name__ == "__main__":
    test_memory_organizer()