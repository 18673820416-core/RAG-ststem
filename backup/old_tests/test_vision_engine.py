#!/usr/bin/env python
# @self-expose: {"id": "test_vision_engine", "name": "Test Vision Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Vision Engine功能"]}}
# -*- coding: utf-8 -*-
"""
视觉处理引擎测试脚本
测试视觉处理引擎的基本功能
"""

import os
import sys
import numpy as np
from pathlib import Path

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

def test_vision_engine():
    """测试视觉处理引擎"""
    try:
        # 导入视觉处理引擎
        from src.vision_processing_engine import VisionProcessingEngine
        
        # 创建引擎实例
        vision_engine = VisionProcessingEngine()
        print("✓ 视觉处理引擎初始化成功")
        
        # 测试图像加载功能
        # 创建一个简单的测试图像（模拟）
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        print("✓ 测试图像创建成功")
        
        # 测试特征提取
        features = vision_engine.extract_features(test_image)
        print("✓ 特征提取功能正常")
        print(f"  提取的特征: {list(features.keys())}")
        
        # 测试对象检测
        objects = vision_engine.detect_objects(test_image)
        print("✓ 对象检测功能正常")
        print(f"  检测到的对象数量: {len(objects)}")
        
        # 测试工具集成
        from src.agent_tool_integration import get_tool_integrator
        
        tool_integrator = get_tool_integrator()
        
        # 测试工具调用
        result = tool_integrator.call_tool('VisionProcessingEngine', {
            'operation': 'extract_features',
            'image_path': None,
            'base64_data': None
        })
        
        if result['success']:
            print("✓ 工具集成调用成功")
        else:
            print(f"✗ 工具集成调用失败: {result['error']}")
        
        print("\n🎯 视觉处理引擎测试完成！")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print("请检查依赖库是否安装: pip install opencv-python numpy")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def test_vision_tool_integration():
    """测试视觉处理工具集成"""
    try:
        from src.agent_tool_integration import get_tool_integrator
        
        tool_integrator = get_tool_integrator()
        
        # 获取可用工具列表
        available_tools = tool_integrator.get_available_tools()
        print("可用工具列表:")
        for tool in available_tools:
            print(f"  - {tool}")
        
        # 检查视觉处理工具状态
        tool_status = tool_integrator.get_tool_status()
        if 'VisionProcessingEngine' in tool_status:
            print("✓ 视觉处理工具已正确集成")
        else:
            print("✗ 视觉处理工具未找到")
            
    except Exception as e:
        print(f"✗ 工具集成测试失败: {e}")

if __name__ == "__main__":
    print("开始测试视觉处理引擎...")
    print("=" * 50)
    
    test_vision_engine()
    
    print("\n" + "=" * 50)
    print("开始测试工具集成...")
    print("=" * 50)
    
    test_vision_tool_integration()
    
    print("\n" + "=" * 50)
    print("测试完成！")