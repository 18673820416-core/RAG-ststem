#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复所有自曝光注释中的JSON格式问题
"""

import os
import re
import json
from pathlib import Path

def fix_self_exposure_json(file_path):
    """
    修复单个文件中的自曝光注释JSON格式
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否成功修复
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配所有自曝光注释格式
        # 格式1: # @self-expose: {json内容}
        # 格式2: # @self-expose {json内容}
        pattern = r'# @self-expose(?::)?\s*(\{.*?\})'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False
        
        # 提取JSON字符串
        json_str = match.group(1)
        
        try:
            # 尝试直接解析JSON
            data = json.loads(json_str)
            
            # 检查并修复字段
            if 'provides' not in data:
                data['provides'] = {
                    'capabilities': [f"{data.get('name', '未知组件')}功能"]
                }
            
            # 生成新的JSON字符串
            new_json_str = json.dumps(data, ensure_ascii=False)
            
            # 替换旧的JSON字符串
            new_comment = f"# @self-expose: {new_json_str}"
            new_content = content.replace(match.group(0), new_comment)
            
            # 保存修改
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"已修复: {file_path} - 修复了JSON格式")
            return True
            
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试手动修复JSON格式
            print(f"尝试手动修复: {file_path}")
            
            # 尝试修复常见的JSON格式问题
            # 1. 检查是否缺少右括号
            if json_str.count('{') > json_str.count('}'):
                # 添加缺失的右括号
                fixed_json_str = json_str + '}'
                try:
                    data = json.loads(fixed_json_str)
                    # 检查并修复字段
                    if 'provides' not in data:
                        data['provides'] = {
                            'capabilities': [f"{data.get('name', '未知组件')}功能"]
                        }
                    # 生成新的JSON字符串
                    new_json_str = json.dumps(data, ensure_ascii=False)
                    # 替换旧的JSON字符串
                    new_comment = f"# @self-expose: {new_json_str}"
                    new_content = content.replace(match.group(0), new_comment)
                    # 保存修改
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"已修复: {file_path} - 添加了缺失的右括号")
                    return True
                except:
                    pass
            
            # 2. 尝试使用更宽松的方式提取JSON
            # 查找最外层的{}对
            open_brace = json_str.find('{')
            close_brace = json_str.rfind('}')
            if open_brace != -1 and close_brace != -1:
                extracted_json = json_str[open_brace:close_brace+1]
                try:
                    data = json.loads(extracted_json)
                    # 检查并修复字段
                    if 'provides' not in data:
                        data['provides'] = {
                            'capabilities': [f"{data.get('name', '未知组件')}功能"]
                        }
                    # 生成新的JSON字符串
                    new_json_str = json.dumps(data, ensure_ascii=False)
                    # 替换旧的JSON字符串
                    new_comment = f"# @self-expose: {new_json_str}"
                    new_content = content.replace(match.group(0), new_comment)
                    # 保存修改
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"已修复: {file_path} - 提取了最外层JSON")
                    return True
                except:
                    pass
        
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
            if fix_self_exposure_json(file_path_str):
                fixed_count += 1
    
    print(f"\n修复完成！")
    print(f"总文件数: {total_count}")
    print(f"包含自曝光注释的文件数: {fixed_count}")
    print(f"已修复的文件数: {fixed_count}")

if __name__ == "__main__":
    main()