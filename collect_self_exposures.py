#!/usr/bin/env python
# @self-expose: {"id": "collect_self_exposures", "name": "收集自曝光信息脚本", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["收集所有文件的自曝光信息", "解析自曝光注释", "生成自曝光信息汇总文件"]}}
# -*- coding: utf-8 -*-
"""
收集所有文件的自我申明，集中存储
"""

import os
import re
import json

def parse_self_exposure(file_path, max_lines=50):
    """
    解析文件头部的自我申明注释
    
    Args:
        file_path: 文件路径
        max_lines: 读取的最大行数
        
    Returns:
        dict: 解析后的自我申明数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到自曝光注释的位置，支持Python和HTML格式
        expose_start = content.find('# @self-expose')
        if expose_start == -1:
            # 尝试HTML注释格式
            expose_start = content.find('<!-- @self-expose')
            if expose_start == -1:
                return None
        
        # 从@self-expose开始查找第一个{
        brace_start = content.find('{', expose_start)
        if brace_start == -1:
            return None
        
        # 使用计数器跟踪{和}的数量，找到完整的JSON对象
        brace_count = 0
        brace_end = -1
        for i in range(brace_start, len(content)):
            char = content[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    brace_end = i
                    break
        
        if brace_end == -1:
            return None
        
        # 提取完整的JSON字符串
        json_str = content[brace_start:brace_end+1]
        
        try:
            # 解析JSON
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"解析JSON失败: {file_path}, 错误: {e}")
            print(f"原始JSON: {json_str}")
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
    
    # 如果所有尝试都失败，返回None
    return None

def collect_self_exposures(root_dir, output_file="self_exposures.json"):
    """
    收集所有文件的自我申明，集中存储
    
    Args:
        root_dir: 根目录
        output_file: 输出文件
    """
    exposures = []
    processed_files = 0
    matched_files = 0
    missing_files = []  # 记录缺少自曝光信息的文件
    
    # 要跳过的目录
    skip_dirs = [
        'myenv', 'myenv_stable', '.venv', '__pycache__', 
        'node_modules', '.git', '.idea', 'dist', 'build',
        'tests', 'test', 'backup', 'old_tests'
    ]
    
    # 要跳过的文件类型（非永久文件）
    skip_file_patterns = [
        'test_', 'check_', 'fix_', 'analyze_', 'generate_', 
        'get_', 'update_', 'accurate_', 'api_',
        'event_', 'quantum_', 'resource_', 'self_', 'solo_',
        'post_', 'clear_', 'rebuild_', 'clean_'
    ]
    
    print(f"开始收集自曝光信息，根目录: {root_dir}")
    print("=" * 60)
    
    for root, dirs, files in os.walk(root_dir):
        # 过滤掉不需要处理的目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            # 支持Python和HTML文件
            if file.endswith(('.py', '.html')):
                # 检查是否为非永久文件
                is_non_permanent = any(file.startswith(pattern) for pattern in skip_file_patterns)
                if not is_non_permanent:
                    processed_files += 1
                    file_path = os.path.join(root, file)
                    exposure = parse_self_exposure(file_path)
                    if exposure:
                        matched_files += 1
                        exposure['source_file'] = file_path
                        exposures.append(exposure)
                        print(f"✓ 找到自曝光信息: {file_path}")
                    else:
                        # 【主动报错】记录缺少自曝光信息的文件
                        missing_files.append(file_path)
                        print(f"✗ 缺少自曝光信息: {file_path}")
    
    print("=" * 60)
    print(f"\n收集完成，共处理 {processed_files} 个文件，找到 {matched_files} 个自曝光信息")
    
    # 【主动报错】如果有文件缺少自曝光信息，输出警告
    if missing_files:
        print(f"\n⚠️  警告：发现 {len(missing_files)} 个文件缺少自曝光信息！")
        print("=" * 60)
        print("缺失自曝光信息的文件列表：")
        for missing_file in missing_files:
            print(f"  - {missing_file}")
        print("=" * 60)
        print("\n根据自曝光协议，所有组件文件都应该包含自曝光声明。")
        print("建议运行：python add_self_exposure_to_missing_files.py")
        print("=" * 60)
        
        # 触发二级报错机制
        try:
            from src.error_reporting import report_component_error
            from datetime import datetime
            
            component_error = {
                "error_id": f"collect_self_exposures-missing-{datetime.now().isoformat()}",
                "level": "component",
                "type": "SelfExposureMissingError",
                "message": f"发现 {len(missing_files)} 个文件缺少自曝光信息",
                "timestamp": datetime.now().isoformat(),
                "component": "collect_self_exposures",
                "function": "collect_self_exposures",
                "file_path": __file__,
                "line_number": 0,
                "stack_trace": "self-exposure collection",
                "context": {
                    "total_files": processed_files,
                    "matched_files": matched_files,
                    "missing_files": missing_files,
                    "missing_count": len(missing_files)
                },
                "severity": "warning"
            }
            report_component_error(component_error)
            print("\n✓ 错误已上报到二级报错系统")
        except Exception as e:
            print(f"\n✗ 无法上报到二级报错系统: {e}")
    else:
        print("\n✓ 所有文件都包含自曝光信息！")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exposures, f, ensure_ascii=False, indent=2)
    
    print(f"\n自曝光信息已保存到: {output_file}")
    
    # 生成组件-文件组织关系图谱（知识图谱）
    try:
        root_dir = os.path.abspath(root_dir)
        id_index = {e.get('id') for e in exposures if isinstance(e, dict)}
        graph_nodes = []
        graph_edges = []
        total_files = 0
        for e in exposures:
            if not isinstance(e, dict):
                continue
            comp_id = e.get('id')
            comp_name = e.get('name')
            comp_type = e.get('type')
            comp_ver = e.get('version')
            # 组件节点
            if comp_id:
                graph_nodes.append({
                    'id': comp_id,
                    'type': comp_type or 'component',
                    'name': comp_name or comp_id,
                    'version': comp_ver or ''
                })
            # 文件节点与包含关系
            src_file = e.get('source_file')
            if src_file:
                total_files += 1
                file_node_id = f"file:{src_file}"
                graph_nodes.append({
                    'id': file_node_id,
                    'type': 'file',
                    'path': src_file
                })
                if comp_id:
                    graph_edges.append({
                        'source': comp_id,
                        'target': file_node_id,
                        'relation': 'contains'
                    })
            # 依赖关系
            needs = e.get('needs') or {}
            dep_list = needs.get('deps') or []
            for dep in dep_list:
                target_id = dep if dep in id_index else f"component_dep:{dep}"
                if comp_id:
                    graph_edges.append({
                        'source': comp_id,
                        'target': target_id,
                        'relation': 'depends_on'
                    })
        component_graph = {
            'nodes': graph_nodes,
            'edges': graph_edges,
            'metadata': {
                'build_time': __import__('datetime').datetime.now().isoformat(),
                'total_components': len([n for n in graph_nodes if n.get('type') != 'file']),
                'total_files': total_files
            }
        }
        # 写入到data目录
        data_dir = os.path.join(root_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        graph_path = os.path.join(data_dir, 'component_graph.json')
        with open(graph_path, 'w', encoding='utf-8') as gf:
            json.dump(component_graph, gf, ensure_ascii=False, indent=2)
        print(f"组件-文件组织关系图谱已生成: {graph_path}")
    except Exception as ge:
        print(f"生成组件知识图谱失败: {ge}")
    
    return exposures

# 使用示例
if __name__ == "__main__":
    collect_self_exposures('.', 'self_exposures.json')
