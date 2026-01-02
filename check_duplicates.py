#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查文件中的重复代码块 - 系统化分析版本"""

import os
from pathlib import Path

def check_file_duplicates(file_path, block_size=15):
    """检查文件中的重复代码块（过滤连续行误报）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    blocks = {}
    for i in range(len(lines) - block_size):
        block = ''.join(lines[i:i+block_size]).strip()
        # 过滤掉太短的块和空行块
        if len(block) < 100 or block.count('\n') < block_size // 2:
            continue
        
        if block in blocks:
            blocks[block].append(i+1)
        else:
            blocks[block] = [i+1]
    
    # 过滤连续行的误报：只保留间隔>5行的重复
    true_duplicates = {}
    for block, positions in blocks.items():
        if len(positions) > 1:
            # 检查是否有非连续的重复
            filtered_positions = [positions[0]]
            for pos in positions[1:]:
                if pos - filtered_positions[-1] > 5:  # 间隔>5行才认为是真正的重复
                    filtered_positions.append(pos)
            
            if len(filtered_positions) > 1:
                true_duplicates[block] = filtered_positions
    
    return true_duplicates, len(lines)

def analyze_by_size_range():
    """按文件大小范围分析重复实现情况"""
    
    ranges = {
        '小文件(<300)': (0, 300),
        '中文件(300-800)': (300, 800),
        '大文件(800-1500)': (800, 1500),
        '超大文件(>1500)': (1500, 999999)
    }
    
    results = {k: {'files': [], 'total_duplicates': 0, 'file_count': 0} for k in ranges}
    
    # 收集所有项目文件
    base_path = Path('e:/RAG系统')
    for dir_name in ['src', 'docs', 'api']:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.rglob('*.py'):
            process_file(file_path, ranges, results)
        for file_path in dir_path.rglob('*.md'):
            process_file(file_path, ranges, results)
    
    # 输出统计报告
    print('\n' + '='*80)
    print('文件大小与重复实现关系分析报告')
    print('='*80)
    
    for range_name in ['小文件(<300)', '中文件(300-800)', '大文件(800-1500)', '超大文件(>1500)']:
        data = results[range_name]
        if data['file_count'] == 0:
            continue
            
        avg_duplicates = data['total_duplicates'] / data['file_count'] if data['file_count'] > 0 else 0
        
        print(f'\n【{range_name}】')
        print(f'  文件数量: {data["file_count"]}')
        print(f'  总重复块: {data["total_duplicates"]}')
        print(f'  平均重复块/文件: {avg_duplicates:.1f}')
        
        # 显示问题最严重的前3个文件
        if data['files']:
            print(f'  \n  问题最严重的文件:')
            sorted_files = sorted(data['files'], key=lambda x: x[1], reverse=True)[:3]
            for fname, dup_count, line_count in sorted_files:
                print(f'    - {fname} ({line_count}行, {dup_count}个重复块)')

def process_file(file_path, ranges, results):
    """处理单个文件"""
    try:
        duplicates, line_count = check_file_duplicates(str(file_path))
        dup_count = len(duplicates)
        
        # 确定文件属于哪个范围
        for range_name, (min_lines, max_lines) in ranges.items():
            if min_lines <= line_count < max_lines:
                results[range_name]['files'].append((file_path.name, dup_count, line_count))
                results[range_name]['total_duplicates'] += dup_count
                results[range_name]['file_count'] += 1
                break
                
    except Exception as e:
        pass  # 忽略读取失败的文件

if __name__ == '__main__':
    analyze_by_size_range()
