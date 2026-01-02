#!/usr/bin/env python3
# @self-expose: {"id": "test_rewrite_chunks", "name": "Test Rewrite Chunks", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Rewrite Chunks功能"]}}
# -*- coding: utf-8 -*-
"""
测试LLM重写检索文本块功能

开发提示词来源：用户要求确保检索到的文本块在最终输出前被LLM重写
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('e:/RAG系统'))

from src.chat_engine import create_chat_engine

def test_rewrite_retrieved_chunks():
    """
    测试检索文本块重写功能
    """
    print("=== 测试LLM重写检索文本块功能 ===")
    
    # 创建聊天引擎实例
    chat_engine = create_chat_engine()
    
    # 模拟检索到的文本块，包含一些无关内容
    retrieved_text = """
    [IDE命令] ls -la
    [思考过程] 我需要先检查当前目录的文件结构，然后再进行下一步操作。
    [代码示例] def hello():
        print("Hello, world!")
    
    核心信息：RAG系统是一种结合了检索和生成的AI系统，它可以从本地知识库中检索相关信息，然后使用LLM生成回答。RAG系统的主要优势是可以处理最新的信息，而不需要重新训练模型。
    
    [思考过程] 现在我需要将这些信息组织成一个连贯的回答。
    [IDE命令] cd ..
    """
    
    # 模拟用户查询
    query = "什么是RAG系统？"
    
    print("原始检索文本：")
    print(retrieved_text)
    print("\n" + "="*50 + "\n")
    
    # 调用重写方法
    try:
        rewritten_text = chat_engine._rewrite_retrieved_chunks(retrieved_text, query)
        
        print("重写后的文本：")
        print(rewritten_text)
        print("\n" + "="*50 + "\n")
        
        # 检查重写结果
        if "IDE命令" not in rewritten_text and "思考过程" not in rewritten_text and "代码示例" not in rewritten_text:
            print("✅ 测试通过：无关内容已被移除")
        else:
            print("❌ 测试失败：仍包含无关内容")
        
        if "RAG系统" in rewritten_text:
            print("✅ 测试通过：核心信息已保留")
        else:
            print("❌ 测试失败：核心信息丢失")
            
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rewrite_retrieved_chunks()
