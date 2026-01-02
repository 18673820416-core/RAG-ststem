#!/usr/bin/env python
# @self-expose: {"id": "test_slicer_depth_long", "name": "Test Slicer Depth Long", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Slicer Depth Long功能"]}}
# -*- coding: utf-8 -*-
"""
测试记忆切片工具的递归深度（使用长文本）
"""

from tools.memory_slicer_tool import MemorySlicerTool

def test_slicer_depth_long():
    """测试记忆切片工具的递归深度（使用长文本）"""
    print("=== 测试记忆切片工具的递归深度（长文本） ===")
    
    # 创建切片器实例
    slicer = MemorySlicerTool()
    
    # 查看当前配置
    print(f"当前最大递归深度: {slicer.default_config['max_recursion_depth']}")
    print(f"当前分层阈值: {slicer.default_config['size_thresholds']}")
    print(f"当前最小切片大小: {slicer.default_config['min_slice_size']}")
    
    # 创建长测试文本，确保超过第一层阈值（1000字符）
    base_text = "这是一个详细的测试段落，用于测试记忆切片工具的递归深度。这个段落包含了丰富的内容，涵盖了多个主题和知识点。随着递归深度的增加，切片工具应该能够将长文本分割成更小的片段。"
    # 重复多次，确保总长度超过1000字符
    test_text = base_text * 12  # 约1008字符
    
    print(f"\n测试文本长度: {len(test_text)} 字符")
    
    # 执行切片
    slices = slicer.slice_text(test_text, {'source': 'long_test'})
    
    # 输出切片结果
    print(f"\n切片结果：")
    print(f"- 生成了 {len(slices)} 个切片")
    
    if slices:
        avg_size = sum(len(slice['content']) for slice in slices) / len(slices)
        print(f"- 平均大小：{avg_size:.2f} 字符")
        print(f"- 最大切片大小：{max(len(slice['content']) for slice in slices)} 字符")
        print(f"- 最小切片大小：{min(len(slice['content']) for slice in slices)} 字符")
        
        # 输出所有切片的信息
        print(f"\n所有切片信息：")
        for i, slice in enumerate(slices):
            content = slice['content']
            print(f"切片 {i+1}: 大小 {len(content)} 字符")
            print(f"  内容：{content[:100]}...")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_slicer_depth_long()