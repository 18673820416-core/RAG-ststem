#!/usr/bin/env python
# @self-expose: {"id": "test_llm_client", "name": "Test Llm Client", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Llm Client功能"]}}
# -*- coding: utf-8 -*-
"""
测试LLM客户端是否正常工作
"""

import os
import sys

# 强制使用Python 3.13.7路径
python313_path = r"C:\Users\liang\AppData\Local\Programs\Python\Python313"
if python313_path not in sys.path:
    sys.path.insert(0, python313_path)

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试LLM客户端...")
    
    # 导入LLM客户端
    from src.llm_client_enhanced import LLMClientEnhanced
    
    # 创建LLM客户端实例
    print("创建LLM客户端实例...")
    llm_client = LLMClientEnhanced(provider="deepseek")
    print("LLM客户端创建成功！")
    
    # 构建测试消息
    messages = [
        {
            "role": "system",
            "content": "你是一个多智能体聊天室的AI助手，请以友好、专业的语气回答用户的问题。"
        },
        {
            "role": "user", 
            "content": "奴隶制是否能长期存在？"
        }
    ]
    
    # 调用LLM生成响应
    print("正在调用LLM生成响应...")
    response = llm_client.chat_completion(messages)
    
    if response:
        print("✅ LLM调用成功！")
        print(f"响应内容: {response}")
    else:
        print("❌ LLM调用失败，返回空响应")
        
except Exception as e:
    print(f"❌ LLM客户端测试失败: {e}")
    import traceback
    traceback.print_exc()

print("测试完成！")