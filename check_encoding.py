#!/usr/bin/env python
# @self-expose: {"id": "check_encoding", "name": "Check Encoding", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Encoding功能"]}}
# -*- coding: utf-8 -*-
"""
检查文件编码和行尾字符
"""

import sys
import os

# 检查文件是否存在
file_path = 'src/base_agent.py'
if not os.path.exists(file_path):
    print("文件不存在")
    sys.exit(1)

# 读取文件内容
with open(file_path, 'rb') as f:
    content = f.read()

# 检查行尾字符
print("检查行尾字符:")

# 计算不同行尾的数量
cr_count = content.count(b'\r\n')
lf_count = content.count(b'\n') - cr_count
cr_only_count = content.count(b'\r') - cr_count

print(f"  \r\n 行尾数量: {cr_count}")
print(f"  \n  行尾数量: {lf_count}")
print(f"  \r  行尾数量: {cr_only_count}")

# 检查文件编码
print("\n检查文件编码:")
try:
    # 尝试用utf-8解码
    content.decode('utf-8')
    print("  ✓ 文件可以用UTF-8解码")
except UnicodeDecodeError:
    print("  ✗ 文件无法用UTF-8解码")

try:
    # 尝试用gbk解码
    content.decode('gbk')
    print("  ✓ 文件可以用GBK解码")
except UnicodeDecodeError:
    print("  ✗ 文件无法用GBK解码")

# 检查文件大小
print(f"\n文件大小: {len(content)} 字节")

# 检查文件的前几个字符
print("\n文件前20个字符:")
print(f"  {repr(content[:20])}")

# 检查文件的最后几个字符
print("\n文件后20个字符:")
print(f"  {repr(content[-20:])}")
