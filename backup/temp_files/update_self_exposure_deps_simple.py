#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单更新自曝光注释中的依赖关系
使用更可靠的解析方式
"""

import os
import re
import ast
from pathlib import Path
import json

def get_file_dependencies(file_path):
    """获取文件的依赖关系"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析Python代码
        tree = ast.parse(content)
        
        # 提取导入语句
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for name in node.names:
                    from_imports.append((module, name.name))
        
        # 提取项目内的依赖
        project_deps = []
        
        # 处理相对导入
        for module, name in from_imports:
            if module:
                # 只处理相对导入
                if module.startswith('.'):
                    # 相对导入，转换为模块名
                    project_deps.append(module)
        
        # 处理直接导入
        for import_name in imports:
            # 只处理项目内模块
            if import_name in ['agent_manager', 'agent_discovery_engine', 'tool_review_manager']:
                project_deps.append(import_name)
        
        # 去重
        project_deps = list(set(project_deps))
        
        return project_deps
        
    except Exception as e:
        print(f"分析文件 {file_path} 失败: {e}")
        return []

def update_self_exposure(file_path):
    """更新文件的自曝光注释"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找自曝光注释行
        self_expose_line = None
        self_expose_index = -1
        
        for i, line in enumerate(lines):
            if '# @self-expose:' in line:
                self_expose_line = line.strip()
                self_expose_index = i
                break
        
        if self_expose_index == -1:
            print(f"文件 {file_path} 中未找到自曝光注释")
            return False
        
        # 提取JSON部分
        json_str = self_expose_line.split('# @self-expose:')[1].strip()
        
        # 解析JSON
        try:
            self_expose_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"文件 {file_path} 的自曝光注释JSON格式错误: {e}")
            print(f"JSON内容: {json_str}")
            return False
        
        # 获取依赖
        dependencies = get_file_dependencies(file_path)
        
        # 更新依赖
        if 'needs' not in self_expose_data:
            self_expose_data['needs'] = {}
        self_expose_data['needs']['deps'] = dependencies
        
        # 重新生成自曝光注释
        new_json_str = json.dumps(self_expose_data, ensure_ascii=False)
        new_self_expose_line = f"# @self-expose: {new_json_str}\n"
        
        # 更新文件
        lines[self_expose_index] = new_self_expose_line
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"已更新文件 {file_path} 的自曝光注释，添加了 {len(dependencies)} 个依赖")
        return True
        
    except Exception as e:
        print(f"更新文件 {file_path} 的自曝光注释失败: {e}")
        return False

def main():
    """主函数"""
    src_path = Path("e:\\RAG系统\\src")
    
    # 遍历所有Python文件
    python_files = list(src_path.rglob("*.py"))
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    updated_count = 0
    for file_path in python_files:
        if update_self_exposure(file_path):
            updated_count += 1
    
    print(f"更新完成，共更新了 {updated_count} 个文件")

if __name__ == "__main__":
    main()
