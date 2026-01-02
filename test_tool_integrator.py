#!/usr/bin/env python3
# @self-expose: {"id": "test_tool_integrator", "name": "Test Tool Integrator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Tool Integrator功能"]}}
# -*- coding: utf-8 -*-
"""
直接测试tool_integrator的工具调用功能
"""

import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加项目根目录到Python路径
sys.path.insert(0, current_dir)

# 打印路径信息用于调试
print(f"当前目录: {current_dir}")
print(f"Python路径: {sys.path[:3]}")

# 尝试导入tool_integrator
print("\n尝试导入tool_integrator...")
try:
    from src.agent_tool_integration import get_tool_integrator
    print("✅ tool_integrator导入成功")
except Exception as e:
    print(f"❌ tool_integrator导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试tool_integrator的工具调用功能
def test_tool_integrator():
    """测试tool_integrator的工具调用功能"""
    print("\n=== 测试tool_integrator工具调用功能 ===\n")
    
    # 获取tool_integrator实例
    print("1. 获取tool_integrator实例...")
    try:
        tool_integrator = get_tool_integrator()
        print("✅ tool_integrator实例获取成功")
    except Exception as e:
        print(f"❌ tool_integrator实例获取失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试获取工具状态
    print("\n2. 测试获取工具状态...")
    try:
        tool_status = tool_integrator.get_tool_status()
        print(f"✅ 工具状态获取成功，共 {len(tool_status)} 个工具可用")
        print("可用工具列表：")
        for tool_name, status in tool_status.items():
            if tool_name in ['file_reading', 'file_writing', 'command_line', 'memory_retrieval']:
                print(f"   - {tool_name}: {status['type']} ({status['module']})")
    except Exception as e:
        print(f"❌ 工具状态获取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试文件读取工具
    print("\n3. 测试文件读取工具...")
    try:
        # 创建测试文件
        test_file_path = "test_read_file.txt"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文件，用于测试文件读取工具。\n测试内容第二行。")
        
        # 调用文件读取工具
        result = tool_integrator.call_tool(
            tool_name='file_reading',
            parameters={'file_path': test_file_path}
        )
        
        print(f"工具调用结果: {result}")
        
        # 删除测试文件
        os.remove(test_file_path)
    except Exception as e:
        print(f"❌ 文件读取测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== tool_integrator工具调用测试完成 ===")

if __name__ == "__main__":
    test_tool_integrator()