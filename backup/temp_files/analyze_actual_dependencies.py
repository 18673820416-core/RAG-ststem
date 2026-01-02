#!/usr/bin/env python
# @self-expose: {"id": "analyze_actual_dependencies", "name": "实际依赖关系分析脚本", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["分析文件的实际依赖关系", "更新自曝光注释中的依赖关系", "自动收集和更新依赖信息"]}}
# -*- coding: utf-8 -*-
"""
实际依赖关系分析脚本
更准确地识别组件间的依赖关系
"""

import os
import re
import ast
from pathlib import Path
import json

def get_component_id_from_module(module_name):
    """从模块名获取组件ID"""
    # 处理相对导入
    if module_name.startswith('.'):
        # 相对导入，转换为组件ID
        # 移除点号
        module_name = module_name.replace('.', '')
    
    # 处理模块路径
    module_name = module_name.replace('.', '_')
    
    return module_name

def analyze_file_dependencies(file_path, src_path):
    """分析文件的实际依赖关系"""
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
        
        # 获取当前文件的组件ID
        file_rel_path = file_path.relative_to(src_path)
        file_name = file_rel_path.stem
        current_component_id = file_name
        
        # 处理相对导入
        for module, name in from_imports:
            if module:
                # 相对导入
                if module.startswith('.'):
                    # 计算实际模块路径
                    file_dir = str(file_rel_path.parent)
                    
                    # 处理相对路径
                    levels = len(module) - len(module.lstrip('.'))
                    parent_dir = file_dir
                    for _ in range(levels):
                        parent_dir = os.path.dirname(parent_dir)
                        if parent_dir == '':
                            break
                    
                    # 构建模块名
                    if module[levels:]:
                        module_path = f"{parent_dir}.{module[levels:]}" if parent_dir else module[levels:]
                    else:
                        module_path = parent_dir
                    
                    # 转换为组件ID
                    if module_path:
                        # 处理子模块导入，如 from .agent_manager import get_agent_manager
                        # 只取模块名，忽略具体导入的函数
                        module_parts = module_path.split('.')
                        for i in range(1, len(module_parts) + 1):
                            partial_module = '.'.join(module_parts[:i])
                            # 转换为组件ID
                            component_id = partial_module.replace('.', '_')
                            if component_id != current_component_id:
                                project_deps.append(component_id)
                    else:
                        # 同一目录下的模块
                        if name != current_component_id:
                            project_deps.append(name)
                # 绝对导入，但属于项目内模块
                elif module.startswith('src.'):
                    # 移除src前缀
                    module_path = module[4:]
                    component_id = module_path.replace('.', '_')
                    if component_id != current_component_id:
                        project_deps.append(component_id)
        
        # 处理直接导入
        for import_name in imports:
            # 检查是否是项目内模块
            if import_name in ['agent_manager', 'agent_discovery_engine', 'tool_review_manager', 'base_agent']:
                if import_name != current_component_id:
                    project_deps.append(import_name)
        
        # 检查基类继承
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    # 检查是否继承自BaseAgent
                    if isinstance(base, ast.Name) and base.id == 'BaseAgent':
                        project_deps.append('base_agent')
                    # 检查是否继承自其他项目内类
                    elif isinstance(base, ast.Attribute) and hasattr(base.value, 'id'):
                        # 如 class MyAgent(agent_manager.AgentManager):
                        dep_id = base.value.id.lower()
                        if dep_id != current_component_id:
                            project_deps.append(dep_id)
        
        # 去重
        project_deps = list(set(project_deps))
        
        return project_deps
        
    except Exception as e:
        print(f"分析文件 {file_path} 失败: {e}")
        return []

def update_self_exposure_dependencies(file_path, src_path):
    """更新文件的自曝光注释中的依赖关系"""
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
        
        # 分析依赖
        dependencies = analyze_file_dependencies(file_path, src_path)
        
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
        if update_self_exposure_dependencies(file_path, src_path):
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
