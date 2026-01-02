#!/usr/bin/env python
# @self-expose: {"id": "test_slicer_depth_complex", "name": "Test Slicer Depth Complex", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Slicer Depth Complex功能"]}}
# -*- coding: utf-8 -*-
"""
测试记忆切片工具的递归深度（使用复杂文本）
"""

from tools.memory_slicer_tool import MemorySlicerTool

def test_slicer_depth_complex():
    """测试记忆切片工具的递归深度（使用复杂文本）"""
    print("=== 测试记忆切片工具的递归深度（复杂文本） ===")
    
    # 创建切片器实例
    slicer = MemorySlicerTool()
    
    # 查看当前配置
    print(f"当前最大递归深度: {slicer.default_config['max_recursion_depth']}")
    print(f"当前分层阈值: {slicer.default_config['size_thresholds']}")
    print(f"当前最小切片大小: {slicer.default_config['min_slice_size']}")
    
    # 创建复杂测试文本，包含不同的内容和结构
    test_text = ""
    
    # 添加标题
    test_text += "# 测试文档\n\n"
    
    # 添加章节1
    test_text += "## 第一章：介绍\n\n"
    test_text += "这是一个详细的测试文档，用于测试记忆切片工具的递归深度。文档包含多个章节，每个章节有不同的内容和结构。\n\n"
    test_text += "### 1.1 背景\n\n"
    test_text += "随着人工智能技术的发展，RAG系统在知识管理和问答系统中扮演着越来越重要的角色。记忆切片是RAG系统中的关键技术，它能够将长文本分割成适合检索和理解的小片段。\n\n"
    test_text += "### 1.2 目的\n\n"
    test_text += "本测试的目的是验证记忆切片工具的递归深度设置是否合理，确保切片大小适中，既不会过大影响检索效果，也不会过小导致信息碎片化。\n\n"
    
    # 添加章节2
    test_text += "## 第二章：技术原理\n\n"
    test_text += "记忆切片工具基于信息熵驱动的递归分片机制，能够智能地识别文本的逻辑边界，将长文本分割成语义完整的小片段。\n\n"
    test_text += "### 2.1 信息熵计算\n\n"
    test_text += "信息熵是衡量文本信息量的重要指标，计算公式为：H(X) = -∑ p(x) * log₂ p(x)。通过计算文本的信息熵，切片工具能够识别文本的逻辑边界。\n\n"
    test_text += "### 2.2 递归分片\n\n"
    test_text += "切片工具采用递归分片的方式，从顶层开始，逐步将文本分割成更小的片段，直到达到预设的最小切片大小或最大递归深度。\n\n"
    
    # 添加章节3
    test_text += "## 第三章：实验设计\n\n"
    test_text += "本实验采用控制变量法，通过调整递归深度参数，观察切片结果的变化。\n\n"
    test_text += "### 3.1 实验参数\n\n"
    test_text += "- 测试文本长度：约5000字符\n"
    test_text += "- 递归深度：10\n"
    test_text += "- 分层阈值：[1000, 500, 300, 200, 150, 100, 80, 60, 50, 40]\n"
    test_text += "- 最小切片大小：30字符\n\n"
    test_text += "### 3.2 预期结果\n\n"
    test_text += "预期结果是生成大小适中的切片，平均切片大小在50-200字符之间，切片数量在25-100之间。\n\n"
    
    # 添加章节4
    test_text += "## 第四章：结果分析\n\n"
    test_text += "实验结果将从以下几个方面进行分析：\n\n"
    test_text += "1. 切片数量\n"
    test_text += "2. 平均切片大小\n"
    test_text += "3. 最大切片大小\n"
    test_text += "4. 最小切片大小\n"
    test_text += "5. 切片语义完整性\n\n"
    
    # 添加章节5
    test_text += "## 第五章：结论与展望\n\n"
    test_text += "根据实验结果，我们将得出关于递归深度设置的结论，并提出未来的改进方向。\n\n"
    test_text += "### 5.1 结论\n\n"
    test_text += "通过实验，我们验证了递归深度设置对切片结果的影响。适当增加递归深度可以生成更小的切片，但也会增加计算成本。\n\n"
    test_text += "### 5.2 展望\n\n"
    test_text += "未来的改进方向包括：\n"
    test_text += "- 动态调整递归深度\n"
    test_text += "- 基于内容类型的自适应切片\n"
    test_text += "- 结合语义理解的智能切片\n\n"
    
    print(f"\n测试文本长度: {len(test_text)} 字符")
    
    # 执行切片
    slices = slicer.slice_text(test_text, {'source': 'complex_test'})
    
    # 输出切片结果
    print(f"\n切片结果：")
    print(f"- 生成了 {len(slices)} 个切片")
    
    if slices:
        avg_size = sum(len(slice['content']) for slice in slices) / len(slices)
        print(f"- 平均大小：{avg_size:.2f} 字符")
        print(f"- 最大切片大小：{max(len(slice['content']) for slice in slices)} 字符")
        print(f"- 最小切片大小：{min(len(slice['content']) for slice in slices)} 字符")
        
        # 输出前10个切片的信息
        print(f"\n前10个切片信息：")
        for i, slice in enumerate(slices[:10]):
            content = slice['content']
            print(f"切片 {i+1}: 大小 {len(content)} 字符")
            print(f"  内容：{content[:100]}...")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_slicer_depth_complex()