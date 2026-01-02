#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能体工具集成系统
"""

# @self-expose: {"id": "test_tool_integration", "name": "Test Tool Integration", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Tool Integration功能"]}}

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tool_integration():
    """测试工具集成系统"""
    try:
        import agent_tool_integration
        
        print("=" * 60)
        print("智能体工具集成系统测试")
        print("=" * 60)
        
        # 获取工具集成器实例
        integrator = agent_tool_integration.get_tool_integrator()
        
        # 获取可用工具列表
        available_tools = integrator.get_available_tools()
        
        print("\n✅ 可用工具列表:")
        for i, tool in enumerate(available_tools, 1):
            print(f"  {i}. {tool}")
        
        # 获取工具状态
        tool_status = integrator.get_tool_status()
        
        print("\n✅ 工具状态信息:")
        for tool_name, info in tool_status.items():
            print(f"  {tool_name}:")
            print(f"    类型: {info.get('type', 'Unknown')}")
            print(f"    模块: {info.get('module', 'Unknown')}")
            print(f"    可用: {info.get('available', False)}")
        
        # 测试多模态引擎
        print("\n✅ 多模态引擎测试:")
        multimodal_engines = [
            'MultimodalAlignmentEngine',
            'MultimodalRetrievalEngine', 
            'VisionProcessingEngine',
            'AudioProcessingEngine',
            'MultimodalFusionEngine'
        ]
        
        for engine_name in multimodal_engines:
            if engine_name in available_tools:
                print(f"  ✓ {engine_name} - 已集成")
            else:
                print(f"  ✗ {engine_name} - 未找到")
        
        # 测试认知引擎
        print("\n✅ 认知引擎测试:")
        cognitive_engines = [
            'AbductiveReasoningEngine',
            'HierarchicalLearningEngine'
        ]
        
        for engine_name in cognitive_engines:
            if engine_name in available_tools:
                print(f"  ✓ {engine_name} - 已集成")
            else:
                print(f"  ✗ {engine_name} - 未找到")
        
        # 测试工具调用
        print("\n✅ 工具调用测试:")
        test_tools = ['VisionProcessingEngine', 'AudioProcessingEngine']
        
        for tool_name in test_tools:
            if tool_name in available_tools:
                tool_instance = integrator.get_tool(tool_name)
                if tool_instance:
                    print(f"  ✓ {tool_name} - 工具实例获取成功")
                    
                    # 测试工具调用
                    try:
                        if tool_name == 'VisionProcessingEngine':
                            result = integrator.call_tool(tool_name, {
                                'operation': 'analyze_image',
                                'image_path': 'test_image.jpg'
                            })
                        elif tool_name == 'AudioProcessingEngine':
                            result = integrator.call_tool(tool_name, {
                                'operation': 'analyze_audio',
                                'audio_path': 'test_audio.wav'
                            })
                        
                        print(f"    工具调用结果: {result.get('success', False)}")
                        
                    except Exception as e:
                        print(f"    工具调用异常: {e}")
                else:
                    print(f"  ✗ {tool_name} - 工具实例获取失败")
            else:
                print(f"  ✗ {tool_name} - 工具未注册")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tool_integration()
    sys.exit(0 if success else 1)