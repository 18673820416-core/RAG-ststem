#!/usr/bin/env python
# @self-expose: {"id": "test_module_loading", "name": "Test Module Loading", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Module Loading功能"]}}
# -*- coding: utf-8 -*-
"""
测试模块加载功能
验证三个核心引擎模块是否能正常加载
"""

import os
import sys

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mesh_thought_engine():
    """测试网状思维引擎加载"""
    try:
        from src.mesh_thought_engine import MeshThoughtEngine, ThoughtNode, AssociationEngine
        print("✓ 网状思维引擎加载成功")
        
        # 测试基本功能
        node1 = ThoughtNode("测试思维节点1", [0.1, 0.2, 0.3])
        node2 = ThoughtNode("测试思维节点2", [0.4, 0.5, 0.6])
        
        association_engine = AssociationEngine()
        relation = association_engine.determine_relation(node1, node2)
        
        print(f"✓ 思维节点关联测试成功: {relation}")
        return True
        
    except Exception as e:
        print(f"✗ 网状思维引擎加载失败: {e}")
        return False

def test_vision_processing_engine():
    """测试视觉处理引擎加载"""
    try:
        from src.vision_processing_engine import VisionProcessingEngine, VisionConfig
        print("✓ 视觉处理引擎加载成功")
        
        # 测试基本功能
        config = VisionConfig()
        vision_engine = VisionProcessingEngine(config)
        
        print(f"✓ 视觉处理引擎初始化成功: {vision_engine.models_loaded}")
        return True
        
    except Exception as e:
        print(f"✗ 视觉处理引擎加载失败: {e}")
        return False

def test_multimodal_fusion_engine():
    """测试多模态融合引擎加载"""
    try:
        from src.multimodal_fusion_engine import MultimodalFusionEngine, FusionConfig
        print("✓ 多模态融合引擎加载成功")
        
        # 测试基本功能
        config = FusionConfig()
        fusion_engine = MultimodalFusionEngine(config)
        
        print(f"✓ 多模态融合引擎初始化成功: {fusion_engine.fusion_models_loaded}")
        return True
        
    except Exception as e:
        print(f"✗ 多模态融合引擎加载失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("RAG系统核心模块加载测试")
    print("=" * 60)
    
    results = []
    
    # 测试网状思维引擎
    results.append(test_mesh_thought_engine())
    print()
    
    # 测试视觉处理引擎
    results.append(test_vision_processing_engine())
    print()
    
    # 测试多模态融合引擎
    results.append(test_multimodal_fusion_engine())
    print()
    
    # 汇总结果
    print("=" * 60)
    print("测试结果汇总:")
    print(f"成功加载模块: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ 所有核心模块加载成功！")
        return True
    else:
        print("✗ 部分模块加载失败，需要检查依赖问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)