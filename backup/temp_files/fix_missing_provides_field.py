#!/usr/bin/env python
# @self-expose: {"id": "fix_missing_provides_field", "name": "Fix Missing Provides Field", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Fix Missing Provides Field功能"]}}
# -*- coding: utf-8 -*-
"""
修复所有自曝光注释中缺失的provides字段
"""

import os
import re
import json
from pathlib import Path

def fix_missing_provides_field(file_path):
    """
    修复单个文件中自曝光注释缺失的provides字段
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否成功修复
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配自曝光注释
        pattern = r'(# @self-expose(?::)?\s*(?:\{.*?\}))'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False
        
        # 提取JSON字符串
        comment = match.group(1)
        json_str_match = re.search(r'\{(.*?)\}', comment, re.DOTALL)
        
        if not json_str_match:
            return False
        
        json_str = json_str_match.group(0)
        
        try:
            # 解析JSON
            data = json.loads(json_str)
            
            # 检查是否缺少provides字段
            if 'provides' not in data:
                # 添加默认的provides字段
                data['provides'] = {
                    'capabilities': [f"{data.get('name', '未知组件')}功能"]
                }
                
                # 生成新的JSON字符串
                new_json_str = json.dumps(data, ensure_ascii=False)
                
                # 替换旧的JSON字符串
                new_comment = comment.replace(json_str, new_json_str)
                new_content = content.replace(comment, new_comment)
                
                # 保存修改
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"已修复: {file_path} - 添加了provides字段")
                return True
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，跳过此文件
            return False
        
        return False
        
    except Exception as e:
        print(f"修复文件 {file_path} 时出错: {e}")
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
        file_path_str = str(file_path)
        total_count += 1
        
        # 检查文件是否包含自曝光注释
        with open(file_path_str, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        if '@self-expose' in file_content:
            if fix_missing_provides_field(file_path_str):
                fixed_count += 1
    
    print(f"\n修复完成！")
    print(f"总文件数: {total_count}")
    print(f"包含自曝光注释的文件数: {fixed_count}")
    print(f"已修复的文件数: {fixed_count}")

if __name__ == "__main__":
    main()