#!/usr/bin/env python
# @self-expose: {"id": "test_file_reading_tool", "name": "Test File Reading Tool", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test File Reading Tool功能"]}}
# -*- coding: utf-8 -*-
"""
测试file_reading工具是否能正常工作
"""

import sys
import os
from pathlib import Path

# 添加RAG系统路径
sys.path.insert(0, str(Path("e:/RAG系统")))
sys.path.insert(0, str(Path("e:/RAG系统/src")))

from src.agent_tool_integration import AgentToolIntegration

def test_file_reading_tool():
    """测试file_reading工具"""
    print("=== 测试file_reading工具 ===")
    
    # 初始化工具集成器
    tool_integrator = AgentToolIntegration()
    
    # 先创建一个测试文件
    test_file_path = "e:/RAG系统/test_read.txt"
    test_content = "这是测试文件内容，用于验证file_reading工具是否正常工作。\n测试时间：" + str(datetime.now())
    
    try:
        # 先使用file_writing工具创建测试文件
        write_result = tool_integrator.call_tool(
            tool_name="file_writing",
            parameters={
                "file_path": test_file_path,
                "content": test_content,
                "overwrite": True
            }
        )
        
        print(f"创建测试文件结果: {write_result}")
        
        if write_result.get("success"):
            print("✅ 测试文件创建成功")
            
            # 现在测试file_reading工具
            print("\n开始测试file_reading工具...")
            read_result = tool_integrator.call_tool(
                tool_name="file_reading",
                parameters={
                    "file_path": test_file_path
                }
            )
            
            print(f"读取文件结果: {read_result}")
            
            # 验证结果
            if read_result.get("success"):
                print("✅ file_reading工具调用成功")
                
                # 验证文件内容是否正确
                actual_content = read_result.get('data', {}).get('content', '')
                if test_content in actual_content:
                    print("✅ 文件内容正确")
                    print(f"文件内容: {actual_content}")
                else:
                    print("❌ 文件内容不正确")
                    print(f"预期内容: {test_content}")
                    print(f"实际内容: {actual_content}")
            else:
                print(f"❌ file_reading工具调用失败: {read_result.get('error')}")
                
                # 尝试直接读取文件，看看是否能读取
                print("\n尝试直接读取文件...")
                if os.path.exists(test_file_path):
                    with open(test_file_path, "r", encoding="utf-8") as f:
                        direct_content = f.read()
                    print(f"直接读取成功，文件内容: {direct_content}")
                else:
                    print(f"文件不存在: {test_file_path}")
        else:
            print(f"❌ 测试文件创建失败: {write_result.get('error')}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"\n测试文件已清理: {test_file_path}")
    
    print("=== 测试结束 ===")

if __name__ == "__main__":
    from datetime import datetime
    test_file_reading_tool()