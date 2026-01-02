#!/usr/bin/env python
# @self-expose: {"id": "get_all_python_files", "name": "Get All Python Files", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Get All Python Files功能"]}}
# -*- coding: utf-8 -*-
"""
获取所有Python文件的列表
"""

import os
from pathlib import Path

def get_all_python_files(root_dir):
    """
    获取指定目录下所有Python文件的列表
    
    Args:
        root_dir: 根目录
    
    Returns:
        list: Python文件路径列表
    """
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                python_files.append(str(file_path))
    return python_files

def main():
    """
    主函数
    """
    root_dir = 'src'
    python_files = get_all_python_files(root_dir)
    
    # 保存到文件
    with open('python_files_list.txt', 'w', encoding='utf-8') as f:
        for file_path in python_files:
            f.write(f"{file_path}\n")
    
    print(f"找到 {len(python_files)} 个Python文件")
    print("文件列表已保存到 python_files_list.txt")

if __name__ == "__main__":
    main()