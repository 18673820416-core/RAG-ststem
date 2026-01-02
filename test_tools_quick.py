#!/usr/bin/env python
# @self-expose: {"id": "test_tools_quick", "name": "Test Tools Quick", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Tools Quick功能"]}}
# -*- coding: utf-8 -*-
"""快速测试文件读写工具"""

import os
from tools.chat_tools import FileReadingTool, FileWritingTool

# 测试文件读取
print("=== 测试文件读取工具 ===")
# 创建测试文件
with open('test_read_file.txt', 'w', encoding='utf-8') as f:
    f.write("这是测试内容")

reading_tool = FileReadingTool()
content = reading_tool.read_text_file('test_read_file.txt')
print(f"读取结果: {content}")
print(f"类型: {type(content)}")

os.remove('test_read_file.txt')

# 测试文件写入
print("\n=== 测试文件写入工具 ===")
writing_tool = FileWritingTool()
result = writing_tool.write_to_file('test_write_file.txt', '测试写入内容', overwrite=False)
print(f"写入结果: {result}")
print(f"success: {result.get('success')}")
print(f"message: {result.get('message')}")

if os.path.exists('E:\\RAG系统\\test_write_file.txt'):
    print("✅ 文件已创建")
    os.remove('E:\\RAG系统\\test_write_file.txt')
else:
    print("❌ 文件未创建")
