#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单修复自曝光注释中的JSON格式问题
"""

import os
import re
import json
from pathlib import Path

def simple_fix_self_exposure(file_path):
    """
    简单修复单个文件中的自曝光注释
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否成功修复
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找自曝光注释行
        expose_line_index = -1
        for i, line in enumerate(lines):
            if '# @self-expose' in line:
                expose_line_index = i
                break
        
        if expose_line_index == -1:
            return False
        
        # 获取自曝光注释行
        expose_line = lines[expose_line_index]
        
        # 提取JSON部分
        # 找到第一个{和最后一个}
        open_brace = expose_line.find('{')
        close_brace = expose_line.rfind('}')
        
        if open_brace == -1 or close_brace == -1:
            return False
        
        # 提取JSON字符串
        json_str = expose_line[open_brace:close_brace+1]
        
        try:
            # 解析JSON
            data = json.loads(json_str)
            
            # 检查并修复字段
            if 'provides' not in data:
                data['provides'] = {
                    'capabilities': [f"{data.get('name', '未知组件')}功能"]
                }
            
            # 生成新的JSON字符串
            new_json_str = json.dumps(data, ensure_ascii=False)
            
            # 生成新的注释行
            new_expose_line = f"# @self-expose: {new_json_str}\n"
            
            # 替换旧的注释行
            lines[expose_line_index] = new_expose_line
            
            # 保存修改
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"已修复: {file_path.name}")
            return True
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试手动修复
            # 简单的修复：确保JSON格式正确
            # 这里我们直接重写一个简单的自曝光注释
            simple_data = {
                "id": file_path.stem,
                "name": file_path.stem.replace('_', ' ').title(),
                "type": "component",
                "version": "1.0.0",
                "needs": {
                    "deps": [],
                    "resources": []
                },
                "provides": {
                    "capabilities": [f"{file_path.stem.replace('_', ' ').title()}功能"]
                }
            }
            
            new_json_str = json.dumps(simple_data, ensure_ascii=False)
            new_expose_line = f"# @self-expose: {new_json_str}\n"
            
            lines[expose_line_index] = new_expose_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"已简化修复: {file_path.name}")
            return True
        
    except Exception as e:
        print(f"修复文件 {file_path.name} 时出错: {e}")
        return False

def main():
    """
    修复所有Python文件中的自曝光注释
    """
    src_dir = Path('src')
    fixed_count = 0
    total_count = 0
    
    # 遍历所有Python文件
    for file_path in src_dir.glob('*.py'):
        total_count += 1
        
        if simple_fix_self_exposure(file_path):
            fixed_count += 1
    
    print(f"\n修复完成！")
    print(f"总文件数: {total_count}")
    print(f"修复文件数: {fixed_count}")

if __name__ == "__main__":
    main()