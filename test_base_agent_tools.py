#!/usr/bin/env python3
# @self-expose: {"id": "test_base_agent_tools", "name": "Test Base Agent Tools", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Base Agent Tools功能"]}}
# -*- coding: utf-8 -*-
"""
测试修复后的基类智能体工具调用功能
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

# 尝试导入BaseAgent
print("\n尝试导入BaseAgent...")
try:
    from src.base_agent import BaseAgent
    print("✅ BaseAgent导入成功")
except Exception as e:
    print(f"❌ BaseAgent导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_base_agent_tools():
    """测试基类智能体的工具调用功能"""
    print("=== 测试基类智能体工具调用功能 ===\n")
    
    # 创建测试智能体
    print("1. 创建测试智能体...")
    try:
        agent = BaseAgent('test_agent', 'test_type', 'src/agent_prompts/system_architect_prompt.txt')
        print("✅ 智能体创建成功")
    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return
    
    # 测试工具状态获取
    print("\n2. 测试获取工具状态...")
    try:
        tool_status = agent.tool_integrator.get_tool_status()
        print(f"✅ 工具状态获取成功，共 {len(tool_status)} 个工具可用")
        print("可用工具列表：")
        for tool_name, status in tool_status.items():
            if tool_name in ['file_reading', 'file_writing', 'command_line', 'memory_retrieval']:
                print(f"   - {tool_name}: {status['type']} ({status['module']})")
    except Exception as e:
        print(f"❌ 工具状态获取失败: {e}")
    
    # 测试文件读取工具
    print("\n3. 测试文件读取工具...")
    try:
        # 创建测试文件
        test_file_path = "test_read_file.txt"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文件，用于测试文件读取工具。\n测试内容第二行。")
        
        # 调用文件读取工具
        result = agent.tool_integrator.call_tool(
            tool_name='file_reading',
            parameters={'file_path': test_file_path}
        )
        
        if result['success']:
            print("✅ 文件读取成功")
            print(f"文件内容：\n{result['data']['content']}")
        else:
            print(f"❌ 文件读取失败: {result['error']}")
        
        # 删除测试文件
        os.remove(test_file_path)
    except Exception as e:
        print(f"❌ 文件读取测试失败: {e}")
    
    # 测试文件写入工具
    print("\n4. 测试文件写入工具...")
    try:
        test_file_path = "test_write_file.txt"
        
        # 调用文件写入工具
        result = agent.tool_integrator.call_tool(
            tool_name='file_writing',
            parameters={
                'file_path': test_file_path,
                'content': '这是通过文件写入工具创建的测试文件。\n第二行测试内容。',
                'overwrite': False,
                'enable_assessment': False
            }
        )
        
        if result['success']:
            print("✅ 文件写入成功")
            print(f"写入结果：{result['data']['message']}")
            
            # 验证文件内容
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"文件内容验证：\n{content}")
        else:
            print(f"❌ 文件写入失败: {result['data']['message']}")
        
        # 删除测试文件
        os.remove(test_file_path)
    except Exception as e:
        print(f"❌ 文件写入测试失败: {e}")
    
    # 测试命令行工具
    print("\n5. 测试命令行工具...")
    try:
        # 执行简单命令
        result = agent.tool_integrator.call_tool(
            tool_name='command_line',
            parameters={'command': 'dir', 'timeout': 10}
        )
        
        if result['success']:
            print("✅ 命令执行成功")
            print(f"命令输出：\n{result['data']['stdout'][:500]}...")  # 只显示前500个字符
        else:
            print(f"❌ 命令执行失败: {result['data']['stderr']}")
    except Exception as e:
        print(f"❌ 命令行测试失败: {e}")
    
    # 测试记忆检索工具
    print("\n6. 测试记忆检索工具...")
    try:
        # 先创建一个记忆
        memory_id = agent.create_memory(
            content="这是一个测试记忆，用于测试记忆检索工具。",
            memory_type="test",
            priority="medium",
            tags=["test", "memory_retrieval"]
        )
        print(f"✅ 创建测试记忆成功，记忆ID: {memory_id}")
        
        # 调用记忆检索工具
        result = agent.tool_integrator.call_tool(
            tool_name='memory_retrieval',
            parameters={'query': '测试记忆', 'limit': 3}
        )
        
        if result['success']:
            print("✅ 记忆检索成功")
            print(f"检索到 {len(result['data']['memories'])} 个相关记忆")
        else:
            print(f"❌ 记忆检索失败: {result['error']}")
    except Exception as e:
        print(f"❌ 记忆检索测试失败: {e}")
    
    print("\n=== 基类智能体工具调用测试完成 ===")

if __name__ == "__main__":
    test_base_agent_tools()