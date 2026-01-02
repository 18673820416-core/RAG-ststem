#!/usr/bin/env python
# @self-expose: {"id": "add_self_exposure_to_missing_files", "name": "添加自曝光注释脚本", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["为缺少自曝光注释的文件添加基本的自曝光注释", "自动检测缺少自曝光注释的文件", "批量添加自曝光注释"]}}
# -*- coding: utf-8 -*-
"""
为缺少自曝光注释的文件添加基本的自曝光注释
"""

import os
import re

def has_self_exposure_comment(file_path):
    """
    检查文件是否有自曝光注释
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否有自曝光注释
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找自曝光注释
        if re.search(r'# @self-expose:', content):
            return True
    except Exception as e:
        print(f"检查文件 {file_path} 时出错: {e}")
    
    return False

def add_self_exposure_comment(file_path):
    """
    为文件添加基本的自曝光注释
    
    Args:
        file_path: 文件路径
    """
    try:
        # 获取文件名（不含扩展名）作为组件ID
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 构建自曝光注释
        self_exposure_comment = f"# @self-expose: {{\"id\": \"{file_name}\", \"name\": \"{file_name.replace('_', ' ').title()}\", \"type\": \"component\", \"version\": \"1.0.0\", \"needs\": {{\"deps\": [], \"resources\": []}}, \"provides\": {{\"capabilities\": [\"{file_name.replace('_', ' ').title()}功能\"]}}}}\n"
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 插入自曝光注释
        if lines and lines[0].startswith('#!/usr/bin/env python'):
            # 如果有shebang行，插入到shebang行之后
            new_lines = [lines[0], self_exposure_comment] + lines[1:]
        else:
            # 否则插入到文件开头
            new_lines = [self_exposure_comment] + lines
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✓ 已添加自曝光注释: {file_path}")
        return True
        
    except Exception as e:
        print(f"为文件 {file_path} 添加自曝光注释失败: {e}")
        return False

def main():
    """
    主函数
    """
    # 要跳过的目录
    skip_dirs = [
        'myenv', 'myenv_stable', '.venv', '__pycache__', 
        'node_modules', '.git', '.idea', 'dist', 'build',
        'tests', 'test', 'backup', 'old_tests'  # 与collect_self_exposures.py保持一致
    ]
    
    # 要跳过的文件类型（非永久文件）- 与collect_self_exposures.py保持一致
    skip_file_patterns = [
        'test_', 'check_', 'fix_', 'analyze_', 'generate_', 
        'get_', 'update_', 'accurate_', 'api_',
        'event_', 'quantum_', 'resource_', 'self_', 'solo_',
        'post_', 'clear_', 'rebuild_', 'clean_'
    ]
    
    # 根目录
    root_dir = '.'
    
    print(f"开始为缺少自曝光注释的文件添加注释，根目录: {root_dir}")
    print("注意：与collect_self_exposures.py使用相同的过滤规则")
    print("=" * 60)
    
    # 统计信息
    total_files = 0
    has_comment_files = 0
    added_comment_files = 0
    skipped_files = 0  # 跟踪跳过的文件数
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk(root_dir):
        # 过滤掉不需要处理的目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                # 检查是否为非永久文件
                is_non_permanent = any(file.startswith(pattern) for pattern in skip_file_patterns)
                if is_non_permanent:
                    skipped_files += 1
                    continue  # 跳过测试文件和临时文件
                
                total_files += 1
                file_path = os.path.join(root, file)
                
                if has_self_exposure_comment(file_path):
                    has_comment_files += 1
                else:
                    if add_self_exposure_comment(file_path):
                        added_comment_files += 1
    
    print("=" * 60)
    print(f"\n处理完成，共处理 {total_files} 个文件")
    print(f"已有自曝光注释: {has_comment_files} 个文件")
    print(f"新增自曝光注释: {added_comment_files} 个文件")
    print(f"剩余未处理: {total_files - has_comment_files - added_comment_files} 个文件")
    print(f"跳过的文件: {skipped_files} 个（测试文件和临时文件）")
    
    # 重新收集自曝光信息
    print("\n重新收集自曝光信息...")
    os.system("python collect_self_exposures.py")
    
    # 重新运行兼容性分析
    print("\n重新运行兼容性分析...")
    os.system("python analyze_compatibility.py")

if __name__ == "__main__":
    main()
