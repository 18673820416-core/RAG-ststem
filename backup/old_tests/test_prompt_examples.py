#!/usr/bin/env python
# @self-expose: {"id": "test_prompt_examples", "name": "Test Prompt Examples", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Prompt Examples功能"]}}
# -*- coding: utf-8 -*-
"""
测试系统提示词中的工具示例代码
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_system_prompt():
    """测试系统提示词中的工具示例代码"""
    
    # 直接读取system_architect_agent.py文件内容
    prompt_file = os.path.join(os.path.dirname(__file__), 'src', 'system_architect_agent.py')
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找系统提示词部分 - 使用三重引号作为标记
    start_marker = 'prompt_template = """'
    end_marker = '"""'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ 未找到系统提示词模板")
        return False
    
    # 查找结束标记（跳过开始标记后的第一个引号）
    start_idx += len(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        print("❌ 未找到系统提示词结束标记")
        return False
    
    # 提取系统提示词内容
    prompt_content = content[start_idx:end_idx]
    
    # 检查关键内容
    checks = [
        ("基础工具使用示例代码", "基础工具示例章节"),
        ("命令行工具", "命令行工具示例"),
        ("文件读写工具", "文件读写示例"),
        ("记忆检索工具", "记忆检索示例"),
        ("网络搜索工具", "网络搜索示例"),
        ("工具使用原则", "工具使用原则"),
        ("command_line", "command_line函数"),
        ("file_reading", "file_reading函数"),
        ("file_writing", "file_writing函数"),
        ("memory_retrieval", "memory_retrieval函数"),
        ("web_search", "web_search函数")
    ]
    
    print("🔍 检查系统提示词中的工具示例代码...")
    print("-" * 50)
    
    all_passed = True
    for check_text, description in checks:
        if check_text in prompt_content:
            print(f"✅ {description}: 存在")
        else:
            print(f"❌ {description}: 缺失")
            all_passed = False
    
    print("-" * 50)
    
    # 检查示例代码的具体内容
    if "基础工具使用示例代码" in prompt_content:
        # 提取示例代码部分
        example_start = prompt_content.find("基础工具使用示例代码")
        example_end = prompt_content.find("工具使用原则", example_start)
        
        if example_start != -1 and example_end != -1:
            example_section = prompt_content[example_start:example_end]
            
            # 检查具体的代码示例
            code_checks = [
                ("dir", "dir命令示例"),
                ("tree", "tree命令示例"),
                ("E:\\RAG系统", "路径示例"),
                ("系统架构设计", "关键词查询示例"),
                ("RAG系统最新技术发展", "搜索内容示例")
            ]
            
            print("\n🔍 检查示例代码具体内容...")
            for code_text, code_desc in code_checks:
                if code_text in example_section:
                    print(f"✅ {code_desc}: 存在")
                else:
                    print(f"❌ {code_desc}: 缺失")
                    all_passed = False
            
            # 检查知识图谱位置信息
            if 'hierarchical_knowledge_graph.json' in example_section:
                print("✅ 知识图谱位置: 存在")
            else:
                print("❌ 知识图谱位置: 缺失")
                all_passed = False
                
            if 'E:\\RAG系统\\data' in example_section:
                print("✅ 知识图谱路径: 存在")
            else:
                print("❌ 知识图谱路径: 缺失")
                all_passed = False
                
            # 检查对话流程配置
            if '前置能力优先' in example_section:
                print("✅ 前置能力配置: 存在")
            else:
                print("❌ 前置能力配置: 缺失")
                all_passed = False
                
            if '工具调用顺序' in example_section:
                print("✅ 工具调用顺序: 存在")
            else:
                print("❌ 工具调用顺序: 缺失")
                all_passed = False
    
    # 统计工具示例代码的完整性
    print("\n📊 工具示例代码完整性统计:")
    print("-" * 50)
    
    # 检查每个工具类别是否有具体的代码示例
    tool_categories = [
        ("命令行工具", "command_line", "dir", "tree"),
        ("文件读写工具", "file_reading", "E:\\\\RAG系统", "系统架构设计"),
        ("记忆检索工具", "memory_retrieval", "人工智能技术", "项目开发"),
        ("网络搜索工具", "web_search", "RAG系统最新技术发展", "人工智能最新进展")
    ]
    
    for category, func, example1, example2 in tool_categories:
        if func in prompt_content and example1 in prompt_content:
            print(f"✅ {category}: 完整示例")
        else:
            print(f"❌ {category}: 示例不完整")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有工具示例代码检查通过！")
        print("✅ 系统提示词已成功添加基础工具使用示例")
        print("✅ LLM现在可以通过示例代码学习工具使用方法")
        print("✅ 解决了LLM缺乏系统命令感知能力的问题")
    else:
        print("⚠️  部分检查未通过，需要进一步完善示例代码")
    
    return all_passed

if __name__ == "__main__":
    test_system_prompt()