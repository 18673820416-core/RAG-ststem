#!/usr/bin/env python
# @self-expose: {"id": "test_file_writing", "name": "Test File Writing", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test File Writing功能"]}}
# -*- coding: utf-8 -*-
"""
测试文件写入工具功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent

def test_file_writing_tool():
    """测试文件写入工具功能"""
    print("=== 测试文件写入工具功能 ===")
    
    # 创建智能体实例
    agent = BaseAgent(
        agent_id="test_agent",
        agent_type="test",
        prompt_file="test_prompt.md"
    )
    
    print("智能体创建成功")
    
    # 测试文件写入工具
    print("\n1. 测试文件写入工具:")
    write_response = agent.process_message("请创建一个测试文件，内容为'这是测试文件的内容'")
    print(f"文件写入工具测试响应: {write_response}")
    
    # 检查文件是否创建成功
    test_file_path = "test_output.txt"
    if os.path.exists(test_file_path):
        print(f"\n2. 文件创建成功，内容如下:")
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容: {content}")
        
        # 测试文件读取工具
        print("\n3. 测试文件读取工具:")
        read_response = agent.process_message(f"请读取文件 {test_file_path}")
        print(f"文件读取工具测试响应: {read_response}")
        
        # 清理测试文件
        os.remove(test_file_path)
        print(f"\n4. 测试文件已清理")
    else:
        print(f"\n2. 文件创建失败: {test_file_path} 不存在")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_file_writing_tool()
