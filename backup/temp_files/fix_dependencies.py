#!/usr/bin/env python
# @self-expose: {"id": "fix_dependencies", "name": "修复依赖关系脚本", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["修复文件依赖关系", "更新自曝光注释", "自动分析依赖关系"]}}
# -*- coding: utf-8 -*-
"""
修复依赖关系脚本
为所有文件添加正确的依赖关系
"""

import os
import re
import ast
from pathlib import Path
import json

def analyze_file_dependencies(file_path, src_path):
    """分析文件的实际依赖关系"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析Python代码
        tree = ast.parse(content)
        
        # 提取导入语句
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for name in node.names:
                    from_imports.append((module, name.name))
        
        # 获取当前文件的组件ID
        file_rel_path = file_path.relative_to(src_path)
        file_name = file_rel_path.stem
        current_component_id = file_name
        
        # 提取项目内的依赖
        project_deps = []
        
        # 处理相对导入
        for module, name in from_imports:
            if module and module.startswith('.'):
                # 相对导入
                # 计算实际模块路径
                file_dir = str(file_rel_path.parent)
                levels = len(module) - len(module.lstrip('.'))
                
                # 构建相对路径
                rel_path = file_dir.split(os.sep)
                for _ in range(levels):
                    if rel_path:
                        rel_path.pop()
                
                # 处理模块名
                if module[levels:]:
                    rel_path.extend(module[levels:].split('.'))
                
                # 构建组件ID
                if rel_path:
                    component_id = '_'.join(rel_path)
                    if component_id != current_component_id:
                        project_deps.append(component_id)
        
        # 检查基类继承
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    # 检查是否继承自BaseAgent
                    if isinstance(base, ast.Name) and base.id == 'BaseAgent':
                        project_deps.append('base_agent')
        
        # 去重
        project_deps = list(set(project_deps))
        
        return project_deps
        
    except Exception as e:
        print(f"分析文件 {file_path} 失败: {e}")
        return []

def update_self_exposure(file_path, dependencies):
    """更新文件的自曝光注释"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找自曝光注释行
        self_expose_index = -1
        for i, line in enumerate(lines):
            if '# @self-expose:' in line:
                self_expose_index = i
                break
        
        if self_expose_index == -1:
            print(f"文件 {file_path} 中未找到自曝光注释")
            return False
        
        # 解析自曝光注释
        self_expose_line = lines[self_expose_index].strip()
        json_str = self_expose_line.split('# @self-expose:')[1].strip()
        self_expose_data = json.loads(json_str)
        
        # 更新依赖
        if 'needs' not in self_expose_data:
            self_expose_data['needs'] = {}
        self_expose_data['needs']['deps'] = dependencies
        
        # 重新生成自曝光注释
        new_json_str = json.dumps(self_expose_data, ensure_ascii=False)
        new_self_expose_line = f"# @self-expose: {new_json_str}\n"
        lines[self_expose_index] = new_self_expose_line
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"已更新文件 {file_path} 的自曝光注释，添加了 {len(dependencies)} 个依赖: {', '.join(dependencies)}")
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
        dependencies = analyze_file_dependencies(file_path, src_path)
        if dependencies:
            if update_self_exposure(file_path, dependencies):
                updated_count += 1
    
    print(f"更新完成，共更新了 {updated_count} 个文件")
    
    # 重新收集自曝光信息
    print("\n重新收集自曝光信息...")
    os.system("python collect_self_exposures.py")
    
    # 重新运行兼容性分析
    print("\n重新运行兼容性分析...")
    os.system("python analyze_compatibility.py")

if __name__ == "__main__":
    main()
