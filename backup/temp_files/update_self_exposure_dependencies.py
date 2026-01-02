#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新自曝光注释中的依赖关系
根据代码实际导入情况，自动更新@self-expose注释中的needs.deps字段
"""

import os
import re
import ast
from pathlib import Path
import json

class DependencyAnalyzer:
    """依赖分析器，用于分析Python文件的依赖关系"""
    
    def __init__(self, base_path="e:\\RAG系统"):
        self.base_path = Path(base_path)
        self.src_path = self.base_path / "src"
    
    def analyze_file_dependencies(self, file_path):
        """分析单个文件的依赖关系"""
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
                    # 检查是否是项目内模块
                    if module.startswith('.'):
                        # 相对导入，需要解析实际模块名
                        file_rel_path = file_path.relative_to(self.src_path)
                        file_dir = str(file_rel_path.parent)
                        
                        # 处理相对路径
                        if module == '.':
                            # 同一目录
                            module_path = file_dir
                        elif module.startswith('..'):
                            # 上级目录
                            levels = len(module) - len(module.lstrip('.'))
                            parent_dir = file_dir
                            for _ in range(levels):
                                parent_dir = os.path.dirname(parent_dir)
                                if parent_dir == '':
                                    break
                            module_path = parent_dir
                            if module[levels:]:
                                module_path = f"{module_path}.{module[levels:]}" if module_path else module[levels:]
                        else:
                            # 子目录
                            module_path = f"{file_dir}.{module[1:]}" if file_dir else module[1:]
                    else:
                        # 绝对导入
                        module_path = module
                    
                    # 添加到项目依赖
                    project_deps.append(module_path)
            
            # 处理直接导入
            for import_name in imports:
                # 检查是否是项目内模块
                if import_name.startswith('src.'):
                    # 移除src.前缀
                    project_deps.append(import_name[4:])
                elif import_name in ['agent_manager', 'agent_discovery_engine', 'tool_review_manager']:
                    # 直接导入的项目内模块
                    project_deps.append(import_name)
            
            # 去重
            project_deps = list(set(project_deps))
            
            # 转换为组件ID格式（移除点，转换为蛇形命名）
            component_deps = []
            for dep in project_deps:
                # 移除src前缀（如果有）
                if dep.startswith('src.'):
                    dep = dep[4:]
                # 转换为组件ID
                component_id = dep.replace('.', '_')
                component_deps.append(component_id)
            
            return component_deps
            
        except Exception as e:
            print(f"分析文件 {file_path} 失败: {e}")
            return []
    
    def update_self_exposure_dependencies(self, file_path):
        """更新文件中的自曝光注释"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找自曝光注释
            self_expose_pattern = r'# @self-expose: (\{[^}]*\})'
            match = re.search(self_expose_pattern, content)
            
            if not match:
                print(f"文件 {file_path} 中未找到自曝光注释")
                return False
            
            # 解析自曝光注释
            self_expose_str = match.group(1)
            try:
                self_expose_data = json.loads(self_expose_str)
            except json.JSONDecodeError as e:
                # 尝试处理多行JSON注释
                self_expose_pattern = r'# @self-expose: (\{[\s\S]*?\})'
                match = re.search(self_expose_pattern, content)
                if match:
                    self_expose_str = match.group(1)
                    self_expose_data = json.loads(self_expose_str)
                else:
                    print(f"文件 {file_path} 的自曝光注释JSON格式错误: {e}")
                    return False
            
            # 分析依赖
            dependencies = self.analyze_file_dependencies(file_path)
            
            # 更新依赖
            if 'needs' not in self_expose_data:
                self_expose_data['needs'] = {}
            if 'deps' not in self_expose_data['needs']:
                self_expose_data['needs']['deps'] = []
            
            self_expose_data['needs']['deps'] = dependencies
            
            # 重新生成自曝光注释
            new_self_expose_str = json.dumps(self_expose_data, ensure_ascii=False)
            new_self_expose_comment = f"# @self-expose: {new_self_expose_str}"
            
            # 更新文件内容
            new_content = re.sub(self_expose_pattern, new_self_expose_comment, content, flags=re.DOTALL)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"已更新文件 {file_path} 的自曝光注释，添加了 {len(dependencies)} 个依赖")
            return True
            
        except Exception as e:
            print(f"更新文件 {file_path} 的自曝光注释失败: {e}")
            return False
    
    def update_all_files(self):
        """更新所有Python文件的自曝光注释"""
        # 遍历所有Python文件
        python_files = list(self.src_path.rglob("*.py"))
        
        print(f"找到 {len(python_files)} 个Python文件")
        
        updated_count = 0
        for file_path in python_files:
            if self.update_self_exposure_dependencies(file_path):
                updated_count += 1
        
        print(f"更新完成，共更新了 {updated_count} 个文件")
        return updated_count

def main():
    """主函数"""
    analyzer = DependencyAnalyzer()
    analyzer.update_all_files()

if __name__ == "__main__":
    main()
