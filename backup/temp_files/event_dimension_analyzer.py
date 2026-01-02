#!/usr/bin/env python3
# @self-expose: {"id": "event_dimension_analyzer", "name": "Event Dimension Analyzer", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Event Dimension Analyzer功能"]}}
# -*- coding: utf-8 -*-
"""
事件维度分析器 - 针对大型文本块进行事件维度二次切片
基于用户反馈：事件维是指某个具体事件的的原因、过程、结果，比如DOCS文件夹中的双模态构架这个文本，
原则上讲他是一个完整的逻辑链，如此庞大的文本块，如何查询？
这个时候，是不是应该对他进行第二次切片，将文本切分成原因，转进，深化，结果，等基于事件的具体逻辑分部来向量化，
然后用事件维的序列号，将他们穿起来才是一个完整的逻辑链？

开发提示词来源：用户对事件维度缺失的质疑和具体建议
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime

class EventDimensionAnalyzer:
    """事件维度分析器 - 实现大型文本块的二次切片和逻辑链串联"""
    
    def __init__(self):
        # 事件维度切片模式
        self.event_patterns = {
            'cause': {
                'keywords': ['因为', '原因', '由于', '背景', '起因', '基于', '考虑到', '鉴于'],
                'description': '事件的原因和背景',
                'priority': 1
            },
            'process': {
                'keywords': ['过程', '步骤', '方法', '实施', '进行', '操作', '执行', '开展'],
                'description': '事件的发展过程',
                'priority': 2
            },
            'deepening': {
                'keywords': ['深化', '深入', '进一步', '扩展', '发展', '提升', '优化', '改进'],
                'description': '事件的深化和发展',
                'priority': 3
            },
            'result': {
                'keywords': ['结果', '结论', '效果', '成果', '影响', '成效', '收获', '总结'],
                'description': '事件的结果和影响',
                'priority': 4
            },
            'challenge': {
                'keywords': ['困难', '挑战', '问题', '障碍', '难点', '瓶颈', '局限'],
                'description': '事件中的挑战和问题',
                'priority': 2.5
            },
            'solution': {
                'keywords': ['解决', '方案', '对策', '措施', '办法', '策略', '途径'],
                'description': '事件的解决方案',
                'priority': 2.7
            }
        }
        
        # 逻辑连接词
        self.logical_connectors = [
            '首先', '其次', '然后', '接着', '随后', '最后', '总之', '综上所述',
            '一方面', '另一方面', '此外', '另外', '同时', '而且', '并且'
        ]
    
    def analyze_large_text_block(self, content: str, memory_id: str) -> Dict:
        """分析大型文本块的事件维度结构"""
        if len(content) <= 500:
            return self._create_simple_analysis(content, memory_id)
        
        print(f"🔍 分析大型文本块: {memory_id} (长度: {len(content)} 字符)")
        
        # 1. 进行事件维度切片
        event_slices = self._slice_by_event_dimension(content, memory_id)
        
        # 2. 构建逻辑链
        logic_chain = self._build_logic_chain(event_slices, memory_id)
        
        # 3. 分析事件维度完整性
        dimension_completeness = self._analyze_dimension_completeness(event_slices)
        
        return {
            'memory_id': memory_id,
            'content_length': len(content),
            'event_slices': event_slices,
            'logic_chain': logic_chain,
            'dimension_completeness': dimension_completeness,
            'analysis_time': datetime.now().isoformat(),
            'total_slices': len(event_slices),
            'has_event_dimension': len(event_slices) > 1
        }
    
    def _slice_by_event_dimension(self, content: str, memory_id: str) -> List[Dict]:
        """基于事件维度进行文本切片"""
        slices = []
        
        # 首先尝试按事件维度关键词切片
        for dimension, pattern_info in self.event_patterns.items():
            dimension_slices = self._extract_dimension_slices(
                content, dimension, pattern_info, memory_id
            )
            slices.extend(dimension_slices)
        
        # 如果没有找到明确的事件维度，按段落进行智能切片
        if not slices:
            slices = self._slice_by_paragraphs(content, memory_id)
        
        # 按优先级排序
        slices.sort(key=lambda x: self.event_patterns.get(x['dimension'], {}).get('priority', 99))
        
        # 为每个切片分配序列号
        for i, slice_data in enumerate(slices):
            slice_data['sequence_id'] = f"{memory_id}_event_{i+1:02d}"
            slice_data['sequence_order'] = i + 1
        
        return slices
    
    def _extract_dimension_slices(self, content: str, dimension: str, 
                                 pattern_info: Dict, memory_id: str) -> List[Dict]:
        """提取特定事件维度的切片"""
        slices = []
        keywords = pattern_info['keywords']
        
        # 按句子分割
        sentences = re.split(r'[。！？；]', content)
        
        current_slice = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 检查是否包含该维度的关键词
            if any(keyword in sentence for keyword in keywords):
                if current_slice:
                    # 保存当前切片
                    slice_content = '。'.join(current_slice)
                    if len(slice_content) > 30:  # 确保有足够内容
                        slices.append({
                            'slice_id': f"{memory_id}_{dimension}_{len(slices)+1}",
                            'dimension': dimension,
                            'content': slice_content,
                            'keywords_found': [k for k in keywords if k in sentence],
                            'slice_length': len(slice_content),
                            'description': pattern_info['description']
                        })
                    current_slice = []
                
                current_slice.append(sentence)
            elif current_slice:
                current_slice.append(sentence)
        
        # 处理最后一个切片
        if current_slice:
            slice_content = '。'.join(current_slice)
            if len(slice_content) > 30:
                slices.append({
                    'slice_id': f"{memory_id}_{dimension}_{len(slices)+1}",
                    'dimension': dimension,
                    'content': slice_content,
                    'keywords_found': [],
                    'slice_length': len(slice_content),
                    'description': pattern_info['description']
                })
        
        return slices
    
    def _slice_by_paragraphs(self, content: str, memory_id: str) -> List[Dict]:
        """按段落进行智能切片"""
        slices = []
        
        # 按段落分割
        paragraphs = content.split('\n\n')
        if len(paragraphs) == 1:
            paragraphs = content.split('。')
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para or len(para) < 50:
                continue
            
            # 智能判断段落类型
            dimension = self._classify_paragraph(para, i, len(paragraphs))
            
            slices.append({
                'slice_id': f"{memory_id}_para_{i+1:02d}",
                'dimension': dimension,
                'content': para,
                'keywords_found': [],
                'slice_length': len(para),
                'description': f'第{i+1}段落 - {self._get_dimension_description(dimension)}'
            })
        
        return slices
    
    def _classify_paragraph(self, paragraph: str, index: int, total: int) -> str:
        """智能分类段落的事件维度"""
        # 开头段落通常是原因/背景
        if index == 0:
            return 'cause'
        # 结尾段落通常是结果/总结
        elif index == total - 1:
            return 'result'
        # 中间段落根据内容判断
        else:
            content_lower = paragraph.lower()
            
            for dimension, pattern_info in self.event_patterns.items():
                if any(keyword in content_lower for keyword in pattern_info['keywords']):
                    return dimension
            
            # 默认分类为过程
            return 'process'
    
    def _get_dimension_description(self, dimension: str) -> str:
        """获取维度描述"""
        return self.event_patterns.get(dimension, {}).get('description', '未知维度')
    
    def _build_logic_chain(self, event_slices: List[Dict], memory_id: str) -> Dict:
        """构建事件维度的逻辑链"""
        if not event_slices:
            return {'chain_id': f'{memory_id}_chain', 'slices': [], 'completeness': 0.0}
        
        # 计算逻辑链完整性
        completeness = self._calculate_chain_completeness(event_slices)
        
        # 构建逻辑连接
        connections = []
        for i in range(len(event_slices) - 1):
            connections.append({
                'from': event_slices[i]['slice_id'],
                'to': event_slices[i+1]['slice_id'],
                'relation': 'logical_sequence',
                'strength': 0.8
            })
        
        return {
            'chain_id': f'{memory_id}_event_chain',
            'slices': [s['slice_id'] for s in event_slices],
            'connections': connections,
            'completeness': completeness,
            'total_connections': len(connections),
            'dimension_sequence': [s['dimension'] for s in event_slices]
        }
    
    def _calculate_chain_completeness(self, event_slices: List[Dict]) -> float:
        """计算逻辑链完整性得分"""
        # 检查是否包含核心事件维度
        core_dimensions = ['cause', 'process', 'result']
        found_dimensions = set(s['dimension'] for s in event_slices)
        
        completeness = 0.0
        
        # 基础完整性（核心维度）
        for dim in core_dimensions:
            if dim in found_dimensions:
                completeness += 0.2
        
        # 逻辑顺序完整性
        if len(event_slices) >= 3:
            completeness += 0.2
        
        # 维度多样性加分
        if len(found_dimensions) >= 3:
            completeness += 0.2
        
        return min(completeness, 1.0)
    
    def _analyze_dimension_completeness(self, event_slices: List[Dict]) -> Dict:
        """分析事件维度完整性"""
        dimensions_present = set(s['dimension'] for s in event_slices)
        
        return {
            'total_dimensions': len(dimensions_present),
            'dimensions_present': list(dimensions_present),
            'core_dimensions_missing': [d for d in ['cause', 'process', 'result'] 
                                      if d not in dimensions_present],
            'completeness_score': self._calculate_chain_completeness(event_slices),
            'recommendation': self._generate_recommendation(dimensions_present)
        }
    
    def _generate_recommendation(self, dimensions_present: set) -> str:
        """生成改进建议"""
        missing_core = [d for d in ['cause', 'process', 'result'] if d not in dimensions_present]
        
        if not missing_core:
            return "事件维度完整，逻辑链清晰"
        elif len(missing_core) == 1:
            return f"建议补充{missing_core[0]}维度的内容"
        else:
            return f"建议补充{', '.join(missing_core)}等核心维度的内容"
    
    def _create_simple_analysis(self, content: str, memory_id: str) -> Dict:
        """为小型文本块创建简单分析"""
        return {
            'memory_id': memory_id,
            'content_length': len(content),
            'event_slices': [{
                'slice_id': f'{memory_id}_single',
                'dimension': 'single',
                'content': content,
                'slice_length': len(content),
                'description': '单一文本块'
            }],
            'logic_chain': {
                'chain_id': f'{memory_id}_single_chain',
                'slices': [f'{memory_id}_single'],
                'completeness': 1.0
            },
            'dimension_completeness': {
                'total_dimensions': 1,
                'completeness_score': 1.0,
                'recommendation': '文本较小，无需事件维度切片'
            },
            'has_event_dimension': False
        }

# 使用示例
def test_event_dimension_analyzer():
    """测试事件维度分析器"""
    analyzer = EventDimensionAnalyzer()
    
    # 模拟大型文本块（类似双模态构架的文本）
    test_content = """
    双模态构架的研究背景是基于当前人工智能发展的迫切需求。随着深度学习技术的快速发展，单一模态的AI系统在处理复杂现实世界任务时表现出明显的局限性。传统的单模态方法往往只能处理特定类型的数据，如图像、文本或语音，而无法有效整合多源信息。这种局限性在需要综合判断的复杂场景中尤为突出。
    
    基于这一背景，我们决定探索多模态融合的技术路径。研究过程分为几个关键阶段：首先，我们对现有的多模态技术方案进行了全面分析，包括早期的特征级融合方法和近年来的端到端深度学习模型。在这个过程中，我们发现数据对齐是多模态融合的核心挑战之一。不同模态的数据在时间、空间和语义层面往往存在不一致性，这给有效的特征融合带来了困难。
    
    针对数据对齐的挑战，我们设计了一种基于注意力机制的双模态融合架构。该架构的核心思想是通过自适应的权重分配来实现模态间的动态对齐。具体实施过程中，我们首先构建了基础的双流网络结构，分别处理不同模态的输入数据。然后，我们引入了跨模态注意力模块，该模块能够自动学习模态间的相关性，并生成对齐的特征表示。
    
    在深化研究阶段，我们对架构进行了多次优化。一个重要改进是引入了分层注意力机制，使得模型能够在不同粒度上进行模态对齐。另一个关键优化是加入了模态缺失处理机制，确保在某个模态数据不可用时系统仍能稳定运行。这些优化显著提升了架构的鲁棒性和实用性。
    
    实施过程中遇到了诸多技术挑战。最大的困难是训练数据的稀缺性和质量不一致问题。为了解决这个问题，我们开发了数据增强策略和半监督学习方法。此外，计算资源的限制也给我们带来了挑战，迫使我们设计更高效的网络结构和训练策略。
    
    最终的实验结果表明，我们提出的双模态构架在多个评估指标上都有显著提升。在图像-文本匹配任务中，准确率比基线方法提高了15%；在视频理解任务中，F1分数提升了12%。更重要的是，架构展现出了良好的泛化能力，在不同领域的数据集上都取得了稳定表现。这些成果为后续的多模态研究提供了重要参考和技术基础。
    
    总结来说，双模态构架的研究不仅解决了当前AI系统的局限性，还为未来更复杂的多模态应用奠定了基础。这项工作的成功实施证明了多模态融合在提升AI系统性能方面的巨大潜力，同时也为相关领域的研究者提供了可借鉴的技术路线。
    """
    
    result = analyzer.analyze_large_text_block(test_content, "test_memory_001")
    
    print("📋 事件维度分析结果:")
    print(f"文本块ID: {result['memory_id']}")
    print(f"文本长度: {result['content_length']} 字符")
    print(f"切片数量: {len(result['event_slices'])}")
    print(f"逻辑链完整性: {result['logic_chain']['completeness']:.1%}")
    
    print("\n🔍 事件维度切片详情:")
    for slice_data in result['event_slices']:
        print(f"  - {slice_data['dimension']}: {slice_data['description']}")
        print(f"    内容: {slice_data['content'][:100]}...")
        print(f"    长度: {slice_data['slice_length']} 字符")
    
    print(f"\n💡 改进建议: {result['dimension_completeness']['recommendation']}")

if __name__ == "__main__":
    test_event_dimension_analyzer()