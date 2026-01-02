#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复并收集所有自曝光注释信息
"""

import os
import re
import json
from pathlib import Path

def fix_and_collect_self_exposures(root_dir, output_file="self_exposures.json"):
    """
    修复并收集所有文件中的自曝光注释信息
    
    Args:
        root_dir: 根目录
        output_file: 输出文件
    
    Returns:
        list: 收集到的自曝光信息列表
    """
    exposures = []
    processed_files = 0
    fixed_files = 0
    collected_files = 0
    
    # 遍历所有Python文件
    for file_path in Path(root_dir).glob('*.py'):
        file_path_str = str(file_path)
        processed_files += 1
        
        try:
            with open(file_path_str, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有自曝光注释
            # 使用更可靠的方式：先找到@self-expose标记，然后提取JSON
            expose_marker = '# @self-expose'
            if expose_marker not in content:
                continue
            
            # 找到@self-expose的位置
            marker_pos = content.find(expose_marker)
            
            # 提取从@self-expose开始到下一个非注释行的内容
            lines = content[marker_pos:].split('\n')
            expose_lines = []
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    break
                expose_lines.append(line)
            
            # 合并行并提取JSON
            expose_content = '\n'.join(expose_lines)
            
            # 清理内容，去除#和空格
            cleaned_lines = []
            for line in expose_content.split('\n'):
                stripped_line = line.strip()
                if stripped_line.startswith('#'):
                    cleaned_line = stripped_line[1:].strip()
                    if cleaned_line:
                        cleaned_lines.append(cleaned_line)
            
            # 合并清理后的行
            cleaned_content = ' '.join(cleaned_lines)
            
            # 提取JSON部分
            # 查找最外层的{}对
            open_brace = cleaned_content.find('{')
            close_brace = cleaned_content.rfind('}')
            
            if open_brace == -1 or close_brace == -1 or open_brace >= close_brace:
                continue
            
            json_str = cleaned_content[open_brace:close_brace+1]
            
            try:
                # 解析JSON
                data = json.loads(json_str)
                
                # 检查并修复字段
                if 'id' not in data:
                    # 使用文件名作为默认ID
                    data['id'] = file_path.stem
                
                if 'name' not in data:
                    # 使用文件名作为默认名称
                    data['name'] = file_path.stem.replace('_', ' ').title()
                
                if 'type' not in data:
                    # 默认类型为component
                    data['type'] = 'component'
                
                if 'version' not in data:
                    # 默认版本为1.0.0
                    data['version'] = '1.0.0'
                
                if 'needs' not in data:
                    # 添加默认的needs字段
                    data['needs'] = {
                        'deps': [],
                        'resources': []
                    }
                
                if 'provides' not in data:
                    # 添加默认的provides字段
                    data['provides'] = {
                        'capabilities': [f"{data.get('name', '未知组件')}功能"]
                    }
                
                # 添加源文件信息
                data['source_file'] = file_path_str
                
                # 添加到收集列表
                exposures.append(data)
                collected_files += 1
                
                # 生成标准化的自曝光注释
                standardized_json = json.dumps(data, ensure_ascii=False)
                standardized_expose = f"# @self-expose: {standardized_json}"
                
                # 替换原有的自曝光注释
                new_content = content.replace(expose_content, standardized_expose)
                
                # 保存修复后的文件
                with open(file_path_str, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                fixed_files += 1
                print(f"✓ 已修复并收集: {file_path.name}")
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON解析失败: {file_path.name}, 错误: {e}")
                continue
                
        except Exception as e:
            print(f"✗ 处理文件失败: {file_path.name}, 错误: {e}")
            continue
    
    # 保存收集到的自曝光信息
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exposures, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！")
    print(f"总文件数: {processed_files}")
    print(f"修复文件数: {fixed_files}")
    print(f"收集文件数: {collected_files}")
    print(f"自曝光信息已保存到: {output_file}")
    
    return exposures

if __name__ == "__main__":
    fix_and_collect_self_exposures('src', 'self_exposures.json')