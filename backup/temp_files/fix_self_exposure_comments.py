#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复所有文件中的自曝光注释格式
将所有注释转换为统一的格式：# @self-expose: {json内容}
"""

import os
import re
import json
from pathlib import Path

def fix_self_exposure_comment(file_path):
    """
    修复单个文件中的自曝光注释格式
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否成功修复
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配所有可能的自曝光注释格式
        # 格式1: # @self-expose
        # {json内容}
        pattern1 = r'# @self-expose\s*\n(\{[\s\S]*?^\s*\})'
        # 格式2: # @self-expose
        # # {json内容}
        pattern2 = r'# @self-expose\s*\n(#\s*\{[\s\S]*?^#\s*\})'
        # 格式3: # @self-expose {json内容}
        pattern3 = r'# @self-expose\s*(\{[\s\S]*?\})'
        # 格式4: # @self-expose: {json内容} (已经是正确格式)
        pattern4 = r'# @self-expose:\s*(\{[\s\S]*?\})'
        
        # 检查文件是否包含自曝光注释
        if not any(re.search(p, content, re.MULTILINE) for p in [pattern1, pattern2, pattern3, pattern4]):
            return False
        
        # 处理格式1: # @self-expose\n{json内容}
        match = re.search(pattern1, content, re.MULTILINE)
        if match:
            json_str = match.group(1)
            # 清理json字符串
            cleaned_json = json_str.strip()
            # 转换为单行格式
            new_comment = f"# @self-expose: {cleaned_json}"
            content = content.replace(match.group(0), new_comment)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        # 处理格式2: # @self-expose\n# {json内容}
        match = re.search(pattern2, content, re.MULTILINE)
        if match:
            json_str = match.group(1)
            # 清理每行开头的#和空格
            lines = json_str.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.startswith('#'):
                    cleaned_line = line[1:].strip()
                    if cleaned_line:
                        cleaned_lines.append(cleaned_line)
                else:
                    cleaned_lines.append(line.strip())
            cleaned_json = '\n'.join(cleaned_lines)
            # 转换为单行格式
            new_comment = f"# @self-expose: {cleaned_json}"
            content = content.replace(match.group(0), new_comment)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        # 处理格式3: # @self-expose {json内容}
        match = re.search(pattern3, content)
        if match:
            json_str = match.group(1)
            # 转换为正确格式
            new_comment = f"# @self-expose: {json_str}"
            content = content.replace(match.group(0), new_comment)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        # 格式4已经是正确格式，无需处理
        return False
        
    except Exception as e:
        print(f"修复文件 {file_path} 时出错: {e}")
        return False

def main():
    """
    修复所有Python文件中的自曝光注释格式
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
            content = f.read()
        
        if '@self-expose' in content:
            if fix_self_exposure_comment(file_path_str):
                fixed_count += 1
                print(f"已修复: {file_path.name}")
            else:
                print(f"无需修复: {file_path.name}")
    
    print(f"\n修复完成！")
    print(f"总文件数: {total_count}")
    print(f"包含自曝光注释的文件数: {fixed_count}")
    print(f"已修复的文件数: {fixed_count}")

if __name__ == "__main__":
    main()