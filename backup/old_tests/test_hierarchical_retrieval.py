#!/usr/bin/env python
# @self-expose: {"id": "test_hierarchical_retrieval", "name": "Test Hierarchical Retrieval", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Hierarchical Retrieval功能"]}}
# -*- coding: utf-8 -*-
"""
层级编码智能检索功能测试脚本
开发提示词来源：基于信息熵驱动的递归分片机制需要配套的智能检索功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.multimodal_retrieval_engine import create_multimodal_retrieval_tool
import json

def test_hierarchical_retrieval():
    """测试层级检索功能"""
    print("=== 层级编码智能检索功能测试 ===\n")
    
    # 创建检索工具
    tool = create_multimodal_retrieval_tool()
    
    # 测试数据：模拟层级编码的切片
    test_slices = [
        {
            "slice_id": "1",
            "content": "人工智能的基本概念和发展历程",
            "depth": 1,
            "parent_id": None,
            "sequence_order": 1,
            "metadata": {"topic": "人工智能", "category": "基础概念"}
        },
        {
            "slice_id": "1.1",
            "content": "机器学习是人工智能的重要分支，主要研究如何让计算机从数据中学习",
            "depth": 2,
            "parent_id": "1",
            "sequence_order": 1,
            "metadata": {"topic": "机器学习", "category": "技术分支"}
        },
        {
            "slice_id": "1.2",
            "content": "深度学习是机器学习的一个子领域，使用神经网络进行特征学习",
            "depth": 2,
            "parent_id": "1",
            "sequence_order": 2,
            "metadata": {"topic": "深度学习", "category": "技术分支"}
        },
        {
            "slice_id": "1.1.1",
            "content": "监督学习是机器学习的一种方法，使用标注数据进行训练",
            "depth": 3,
            "parent_id": "1.1",
            "sequence_order": 1,
            "metadata": {"topic": "监督学习", "category": "学习方法"}
        },
        {
            "slice_id": "1.1.2",
            "content": "无监督学习不需要标注数据，主要发现数据中的内在结构",
            "depth": 3,
            "parent_id": "1.1",
            "sequence_order": 2,
            "metadata": {"topic": "无监督学习", "category": "学习方法"}
        },
        {
            "slice_id": "2",
            "content": "自然语言处理是人工智能的重要应用领域",
            "depth": 1,
            "parent_id": None,
            "sequence_order": 2,
            "metadata": {"topic": "自然语言处理", "category": "应用领域"}
        },
        {
            "slice_id": "2.1",
            "content": "文本分类是自然语言处理的基本任务之一",
            "depth": 2,
            "parent_id": "2",
            "sequence_order": 1,
            "metadata": {"topic": "文本分类", "category": "基础任务"}
        }
    ]
    
    print("1. 索引测试切片数据...")
    for slice_data in test_slices:
        result = tool.index_hierarchical_slice(**slice_data)
        if result["success"]:
            print(f"   ✓ 索引成功: {slice_data['slice_id']}")
        else:
            print(f"   ✗ 索引失败: {slice_data['slice_id']} - {result.get('error', '未知错误')}")
    
    print("\n2. 测试层级结构可视化...")
    structure_result = tool.get_hierarchical_structure()
    if structure_result["success"]:
        structure_info = structure_result["structure_info"]
        print("   层级结构可视化:")
        print(structure_info.get("visualization", "可视化失败"))
        print("   深度分布:", structure_info.get("depth_distribution", {}))
    else:
        print("   获取层级结构失败:", structure_result.get("error", "未知错误"))
    
    print("\n3. 测试层级语义检索...")
    retrieval_result = tool.hierarchical_retrieve(
        query_slice_id="1.1",
        retrieval_method="hierarchical_semantic",
        max_results=5,
        include_context=True
    )
    
    if retrieval_result["success"]:
        print("   检索成功!")
        print(f"   查询切片: {retrieval_result['query_slice']}")
        print(f"   检索方法: {retrieval_result['retrieval_method']}")
        print(f"   检索耗时: {retrieval_result['retrieval_time']:.3f}s")
        print(f"   搜索切片总数: {retrieval_result['total_slices_searched']}")
        
        print("\n   检索结果:")
        for i, result in enumerate(retrieval_result['retrieved_slices'], 1):
            print(f"   {i}. ID: {result['slice_id']}, 深度: {result['depth']}, "
                  f"相似度: {result['similarity_score']:.3f}")
            print(f"      内容: {result['content_preview']}")
        
        print("\n   上下文扩展:")
        for i, context in enumerate(retrieval_result['context_expansion'], 1):
            print(f"   {i}. ID: {context['slice_id']}, 深度: {context['depth']}, "
                  f"关系: {context['relation_type']}")
    else:
        print("   检索失败:", retrieval_result.get("error", "未知错误"))
    
    print("\n4. 测试路径检索...")
    path_retrieval_result = tool.hierarchical_retrieve(
        query_slice_id="1.1",
        retrieval_method="path_based",
        max_results=3,
        include_context=False
    )
    
    if path_retrieval_result["success"]:
        print("   路径检索成功!")
        print("   检索结果:")
        for i, result in enumerate(path_retrieval_result['retrieved_slices'], 1):
            print(f"   {i}. ID: {result['slice_id']}, 相似度: {result['similarity_score']:.3f}")
    else:
        print("   路径检索失败:", path_retrieval_result.get("error", "未知错误"))
    
    print("\n5. 测试深度感知检索...")
    depth_retrieval_result = tool.hierarchical_retrieve(
        query_slice_id="1.1",
        retrieval_method="depth_aware",
        max_results=4,
        include_context=True
    )
    
    if depth_retrieval_result["success"]:
        print("   深度感知检索成功!")
        print("   深度权重配置:", depth_retrieval_result['depth_weights'])
        print("   检索结果:")
        for i, result in enumerate(depth_retrieval_result['retrieved_slices'], 1):
            print(f"   {i}. ID: {result['slice_id']}, 深度: {result['depth']}, "
                  f"相似度: {result['similarity_score']:.3f}")
    else:
        print("   深度感知检索失败:", depth_retrieval_result.get("error", "未知错误"))
    
    print("\n6. 测试工具统计信息...")
    stats = tool.engine.get_index_statistics()
    print("   索引统计信息:")
    print(f"   总项目数: {stats['total_items']}")
    print(f"   层级支持: {stats['hierarchical_support']}")
    print(f"   层级切片数: {stats['hierarchical_slices_count']}")
    print(f"   模态分布: {stats['modality_distribution']}")
    
    print("\n=== 测试完成 ===")
    return True

def test_integration_with_memory_slicer():
    """测试与内存分片工具的集成"""
    print("\n=== 测试与内存分片工具集成 ===\n")
    
    try:
        # 导入内存分片工具
        from tools.memory_slicer_tool import MemorySlicerTool
        
        # 创建内存分片工具实例
        memory_slicer = MemorySlicerTool()
        
        # 测试文本
        test_text = """
        人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。
        机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习。
        深度学习是机器学习的一个子集，它使用神经网络来模拟人脑的学习过程。
        自然语言处理是人工智能的一个重要应用领域，专注于计算机与人类语言之间的交互。
        """
        
        print("1. 使用内存分片工具进行递归分片...")
        slice_result = memory_slicer.slice_text(
            text=test_text,
            config={
                'max_recursion_depth': 3,
                'min_slice_size': 50,
                'size_thresholds': [500, 200, 100]
            }
        )
        
        if slice_result and len(slice_result) > 0:
            print(f"   分片成功! 生成切片数: {len(slice_result)}")
            
            # 创建检索工具
            tool = create_multimodal_retrieval_tool()
            
            # 索引分片结果
            print("2. 索引分片结果到层级检索引擎...")
            indexed_count = 0
            for slice_data in slice_result:
                # 提取层级信息
                slice_id = slice_data.get('slice_id', '')
                content = slice_data.get('content', '')
                metadata = slice_data.get('metadata', {})
                
                # 解析深度
                depth = len(slice_id.split('.')) if '.' in slice_id else 1
                parent_id = '.'.join(slice_id.split('.')[:-1]) if '.' in slice_id else None
                
                # 索引切片
                result = tool.index_hierarchical_slice(
                    slice_id=slice_id,
                    content=content,
                    depth=depth,
                    parent_id=parent_id,
                    metadata=metadata
                )
                
                if result["success"]:
                    indexed_count += 1
            
            print(f"   索引成功: {indexed_count} 个切片")
            
            # 测试检索
            if indexed_count > 0:
                print("3. 测试检索功能...")
                # 选择一个切片进行检索
                sample_slice = slice_result['slices'][0]
                retrieval_result = tool.hierarchical_retrieve(
                    query_slice_id=sample_slice['slice_id'],
                    max_results=3
                )
                
                if retrieval_result["success"]:
                    print("   检索成功!")
                    print(f"   检索到 {len(retrieval_result['retrieved_slices'])} 个相关切片")
                else:
                    print("   检索失败:", retrieval_result.get('error', '未知错误'))
            
        else:
            print("   分片失败:", slice_result.get('error', '未知错误'))
            
    except ImportError as e:
        print(f"   导入内存分片工具失败: {e}")
        print("   请确保 memory_slicer_tool.py 文件存在")
    except Exception as e:
        print(f"   集成测试失败: {e}")
    
    print("\n=== 集成测试完成 ===")

if __name__ == "__main__":
    # 运行基本测试
    test_hierarchical_retrieval()
    
    # 运行集成测试
    test_integration_with_memory_slicer()
    
    print("\n所有测试完成!")