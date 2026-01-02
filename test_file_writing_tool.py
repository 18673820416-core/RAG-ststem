#!/usr/bin/env python
# @self-expose: {"id": "test_file_writing_tool", "name": "Test File Writing Tool", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test File Writing Tool功能"]}}
# -*- coding: utf-8 -*-
"""
测试file_writing工具是否能正常工作
"""

import sys
import os
from pathlib import Path

# 添加RAG系统路径
sys.path.insert(0, str(Path("e:/RAG系统")))
sys.path.insert(0, str(Path("e:/RAG系统/src")))

from src.agent_tool_integration import AgentToolIntegration

def test_file_writing_tool():
    """测试file_writing工具"""
    print("=== 测试file_writing工具 ===")
    
    # 初始化工具集成器
    tool_integrator = AgentToolIntegration()
    
    # 测试参数
    test_file_path = "e:/RAG系统/test_output.txt"
    test_content = "这是测试文件内容，用于验证file_writing工具是否正常工作。\n测试时间：" + str(datetime.now())
    
    try:
        # 调用file_writing工具
        result = tool_integrator.call_tool(
            tool_name="file_writing",
            parameters={
                "file_path": test_file_path,
                "content": test_content,
                "overwrite": True
            }
        )
        
        print(f"工具调用结果: {result}")
        
        # 验证结果
        if result.get("success"):
            print("✅ file_writing工具调用成功")
            
            # 验证文件是否创建成功
            if os.path.exists(test_file_path):
                print(f"✅ 文件已成功创建: {test_file_path}")
                
                # 验证文件内容是否正确
                with open(test_file_path, "r", encoding="utf-8") as f:
                    actual_content = f.read()
                    
                if test_content in actual_content:
                    print("✅ 文件内容正确")
                    print(f"文件内容: {actual_content}")
                else:
                    print("❌ 文件内容不正确")
                    print(f"预期内容: {test_content}")
                    print(f"实际内容: {actual_content}")
            else:
                print(f"❌ 文件未创建: {test_file_path}")
        else:
            print(f"❌ file_writing工具调用失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== 测试结束 ===")

if __name__ == "__main__":
    from datetime import datetime
    test_file_writing_tool()