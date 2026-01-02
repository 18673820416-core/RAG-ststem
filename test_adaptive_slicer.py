#!/usr/bin/env python
# @self-expose: {"id": "test_adaptive_slicer", "name": "多层次自适应分片策略测试", "type": "test", "version": "1.0.0", "needs": {"deps": ["tools.memory_slicer_tool"], "resources": []}, "provides": {"capabilities": ["验证四层分片流程", "测试信息熵分片", "测试LLM精炼", "测试困惑度计算", "测试泡泡记录", "测试层级编码"], "test_cases": ["test_entropy_slice_success", "test_llm_refinement_needed", "test_perplexity_analysis", "test_bubble_logging", "test_hierarchical_encoding"]}}
# -*- coding: utf-8 -*-
"""
测试多层次自适应分片策略
验证四层分片流程的正确性
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tools.memory_slicer_tool import MemorySlicerTool

def test_entropy_slice_success():
    """测试第一层：信息熵递归分片成功"""
    print("\n" + "="*70)
    print("测试第一层：信息熵递归分片（成功案例）")
    print("="*70)
    
    slicer = MemorySlicerTool()
    
    # 创建一个中等长度、结构良好的文本
    test_text = """
    第一部分：系统架构设计
    本系统采用微服务架构，包含用户服务、订单服务和支付服务三个核心模块。
    用户服务负责用户注册、登录和权限管理。订单服务处理订单创建、查询和更新。
    支付服务集成第三方支付平台，完成支付处理和对账功能。
    
    第二部分：技术选型
    后端采用Python Flask框架，数据库使用PostgreSQL，缓存层使用Redis。
    前端使用React框架，状态管理采用Redux。消息队列使用RabbitMQ处理异步任务。
    
    第三部分：部署方案
    系统部署在AWS云平台，使用Docker容器化部署。
    通过Kubernetes进行容器编排，实现自动扩缩容。采用Nginx作为负载均衡器。
    """ * 2  # 重复2次，增加长度但保持结构
    
    slices = slicer.slice_text(text=test_text, metadata={'source': 'test'}, source_file='test_success.txt')
    
    print(f"\n切片结果：")
    print(f"- 生成切片数: {len(slices)}")
    if slices:
        print(f"- 切片方法: {slices[0].get('slice_config', {}).get('method', 'unknown')}")
        print(f"- 尝试次数: {slices[0].get('slice_config', {}).get('attempts', 0)}")
        
        print(f"\n前3个切片信息：")
        for i, slice_data in enumerate(slices[:3]):
            print(f"\n切片 {i+1}:")
            print(f"  ID: {slice_data.get('slice_id')}")
            print(f"  深度: {slice_data.get('slice_depth')}")
            print(f"  方法: {slice_data.get('slice_method')}")
            print(f"  长度: {len(slice_data.get('content', ''))} 字符")
            print(f"  质量: {slice_data.get('semantic_quality', 0):.2f}")

def test_llm_refinement_needed():
    """测试第二层：LLM精炼改写（需要LLM的情况）"""
    print("\n" + "="*70)
    print("测试第二层：LLM精炼改写（模拟需要LLM的情况）")
    print("="*70)
    
    slicer = MemorySlicerTool()
    
    # 创建一个超长且缺乏明显逻辑边界的文本（模拟第一层失败）
    # 这里用重复文本模拟
    base_text = "这是一段很长的文本" * 200
    test_text = base_text + " " + base_text + " " + base_text
    
    print(f"文本长度: {len(test_text)} 字符")
    
    # 注意：由于没有实际的LLM，这里可能会退化到第四层
    slices = slicer.slice_text(text=test_text, metadata={'source': 'test'}, source_file='test_llm_needed.txt')
    
    print(f"\n切片结果：")
    print(f"- 生成切片数: {len(slices)}")
    if slices:
        print(f"- 切片方法: {slices[0].get('slice_config', {}).get('method', 'unknown')}")
        print(f"- 尝试次数: {slices[0].get('slice_config', {}).get('attempts', 0)}")

def test_perplexity_analysis():
    """测试第三层：困惑度复合分片"""
    print("\n" + "="*70)
    print("测试困惑度计算功能")
    print("="*70)
    
    slicer = MemorySlicerTool()
    
    # 测试困惑度计算
    text1 = "这是一段正常的文本，包含完整的句子结构。"
    text2 = "abcdefghijklmnopqrstuvwxyz" * 10
    text3 = "的的的的的的的的的的的的的的的的的的的的"
    
    perp1 = slicer._calculate_perplexity(text1)
    perp2 = slicer._calculate_perplexity(text2)
    perp3 = slicer._calculate_perplexity(text3)
    
    print(f"\n困惑度测试结果：")
    print(f"- 正常文本: {perp1:.2f}")
    print(f"- 随机字符: {perp2:.2f}")
    print(f"- 重复文本: {perp3:.2f}")
    
    print(f"\n解释：")
    print(f"- 困惑度越高，文本越\"难以预测\"（信息越丰富）")
    print(f"- 重复文本困惑度最低（容易预测）")
    print(f"- 随机字符困惑度最高（完全无法预测）")

def test_bubble_logging():
    """测试泡泡记录功能"""
    print("\n" + "="*70)
    print("测试泡泡记录功能")
    print("="*70)
    
    slicer = MemorySlicerTool()
    
    # 创建一个会失败的场景（空文本或极短文本）
    test_text = "短"
    
    slices = slicer.slice_text(text=test_text, metadata={'source': 'test'}, source_file='test_bubble.txt')
    
    print(f"\n切片结果：")
    print(f"- 生成切片数: {len(slices)}")
    
    # 检查泡泡目录
    bubble_dir = Path("data/memory_bubbles/memory_slicer_tool")
    if bubble_dir.exists():
        bubbles = list(bubble_dir.glob("*.json"))
        print(f"\n泡泡记录：")
        print(f"- 泡泡数量: {len(bubbles)}")
        if bubbles:
            import json
            latest_bubble = max(bubbles, key=lambda p: p.stat().st_mtime)
            with open(latest_bubble, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            print(f"- 最新泡泡类别: {bubble_data.get('category')}")
            print(f"- 最新泡泡优先级: {bubble_data.get('priority')}")
            print(f"- 最新泡泡内容预览: {bubble_data.get('content', '')[:100]}...")
    else:
        print(f"\n未找到泡泡目录，可能泡泡管理器未初始化")

def test_hierarchical_encoding():
    """测试层级编码功能"""
    print("\n" + "="*70)
    print("测试层级编码功能")
    print("="*70)
    
    slicer = MemorySlicerTool()
    
    # 测试层级编码解析
    test_ids = ["1", "1.1", "1.1.1", "1.1.2", "1.2", "2", "2.1"]
    
    print(f"\n层级编码解析测试：")
    for slice_id in test_ids:
        parsed = slicer.parse_slice_id(slice_id)
        print(f"\nID: {slice_id}")
        print(f"  深度: {parsed['depth']}")
        print(f"  路径: {parsed['path']}")
        print(f"  是否根节点: {parsed['is_root']}")
        print(f"  父ID: {parsed['parent_id']}")

if __name__ == "__main__":
    print("="*70)
    print("多层次自适应分片策略测试")
    print("="*70)
    
    try:
        # 测试1：第一层成功
        test_entropy_slice_success()
        
        # 测试2：需要LLM精炼
        test_llm_refinement_needed()
        
        # 测试3：困惑度分析
        test_perplexity_analysis()
        
        # 测试4：泡泡记录
        test_bubble_logging()
        
        # 测试5：层级编码
        test_hierarchical_encoding()
        
        print("\n" + "="*70)
        print("所有测试完成！")
        print("="*70)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
