#!/usr/bin/env python
# @self-expose: {"id": "test_slicer_depth", "name": "Test Slicer Depth", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Slicer Depth功能"]}}
# -*- coding: utf-8 -*-
"""
测试记忆切片工具的递归深度
"""

from tools.memory_slicer_tool import MemorySlicerTool

def test_slicer_depth():
    """测试记忆切片工具的递归深度"""
    print("=== 测试记忆切片工具的递归深度 ===")
    
    # 创建切片器实例
    slicer = MemorySlicerTool()
    
    # 查看当前配置
    print(f"当前最大递归深度: {slicer.default_config['max_recursion_depth']}")
    print(f"当前分层阈值: {slicer.default_config['size_thresholds']}")
    print(f"当前最小切片大小: {slicer.default_config['min_slice_size']}")
    
    # 创建测试文本
    test_text = '这是一个测试文本，用于测试记忆切片工具的递归深度。' * 100
    print(f"\n测试文本长度: {len(test_text)} 字符")
    
    # 执行切片
    slices = slicer.slice_text(test_text, {'source': 'test'})
    
    # 输出切片结果
    print(f"\n切片结果：")
    print(f"- 生成了 {len(slices)} 个切片")
    
    if slices:
        avg_size = sum(len(slice['content']) for slice in slices) / len(slices)
        print(f"- 平均大小：{avg_size:.2f} 字符")
        print(f"- 最大切片大小：{max(len(slice['content']) for slice in slices)} 字符")
        print(f"- 最小切片大小：{min(len(slice['content']) for slice in slices)} 字符")
        
        # 输出前5个切片的信息
        print(f"\n前5个切片信息：")
        for i, slice in enumerate(slices[:5]):
            content = slice['content']
            print(f"切片 {i+1}: 大小 {len(content)} 字符")
            print(f"  内容：{content[:100]}...")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_slicer_depth()