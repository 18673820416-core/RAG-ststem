#!/usr/bin/env python
# @self-expose: {"id": "check_syntax", "name": "Check Syntax", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Syntax功能"]}}
# -*- coding: utf-8 -*-
"""
检查base_agent.py文件的语法和内容
"""

import sys
import os
import ast

# 检查文件是否存在
file_path = 'src/base_agent.py'
if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
    sys.exit(1)

# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.splitlines()

print(f"文件总行数: {len(lines)}")
print()

# 检查报告的错误行
print("检查报告的错误行:")

# 检查行390
if len(lines) >= 390:
    print(f"行390: {repr(lines[389])}")
    print(f"行391: {repr(lines[390])}")
    print(f"行392: {repr(lines[391])}")
else:
    print("行390不存在")

print()

# 检查行400
if len(lines) >= 400:
    print(f"行400: {repr(lines[399])}")
    print(f"行401: {repr(lines[400])}")
    print(f"行402: {repr(lines[401])}")
else:
    print("行400不存在")

print()

# 检查行1977
if len(lines) >= 1977:
    print(f"行1977: {repr(lines[1976])}")
else:
    print("行1977不存在")

print()

# 检查文件语法
print("检查文件语法:")
try:
    ast.parse(content)
    print("✓ 文件语法正确")
except SyntaxError as e:
    print(f"✗ 文件语法错误: {e}")
    print(f"  错误位置: 行 {e.lineno}, 列 {e.offset}")
    print(f"  错误行: {repr(lines[e.lineno-1])}")

print()

# 运行Python -m py_compile检查
print("使用Python编译器检查:")
try:
    import py_compile
    py_compile.compile(file_path)
    print("✓ 编译检查通过")
except py_compile.PyCompileError as e:
    print(f"✗ 编译检查失败: {e}")
