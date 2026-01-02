#!/usr/bin/env python
# @self-expose: {"id": "backend_api_analyzer", "name": "Backend Api Analyzer", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Backend Api Analyzer功能"]}}
# -*- coding: utf-8 -*-
"""
后端API接口统计脚本
用于分析Python服务器文件中的API接口实现
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Any

class BackendAPIAnalyzer:
    """后端API接口分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.api_endpoints = []
    
    def analyze_python_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """分析单个Python文件中的API接口"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST分析Python代码
            tree = ast.parse(content)
            
            # 查找类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否是HTTP请求处理器类
                    if self._is_http_handler_class(node):
                        endpoints.extend(self._analyze_handler_class(node, content, file_path))
            
            # 使用正则表达式作为备用方法
            endpoints.extend(self._regex_analysis(content, file_path))
            
        except Exception as e:
            print(f"分析文件 {file_path} 时出错: {e}")
            
        return endpoints
    
    def _is_http_handler_class(self, class_node: ast.ClassDef) -> bool:
        """判断是否是HTTP请求处理器类"""
        # 检查类名是否包含Handler或Controller
        class_name = class_node.name.lower()
        if 'handler' in class_name or 'controller' in class_name:
            return True
        
        # 检查是否有do_GET或do_POST方法
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith('do_'):
                    return True
        
        return False
    
    def _analyze_handler_class(self, class_node: ast.ClassDef, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """分析HTTP处理器类中的API端点"""
        endpoints = []
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                # 分析do_GET和do_POST方法
                if item.name in ['do_GET', 'do_POST']:
                    endpoints.extend(self._analyze_do_method(item, content, file_path))
        
        return endpoints
    
    def _analyze_do_method(self, method_node: ast.FunctionDef, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """分析do_GET或do_POST方法中的API端点"""
        endpoints = []
        
        # 获取方法源代码
        method_lines = content.split('\n')[method_node.lineno-1:method_node.end_lineno]
        method_code = '\n'.join(method_lines)
        
        # 查找路径匹配模式
        path_patterns = [
            # if path == '/api/...'
            r"if\s+path\s*==\s*['\"]([^'\"]+)['\"]",
            # elif path == '/api/...'
            r"elif\s+path\s*==\s*['\"]([^'\"]+)['\"]",
            # path.startswith('/api/')
            r"path\.startswith\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        ]
        
        for pattern in path_patterns:
            matches = re.finditer(pattern, method_code, re.DOTALL)
            for match in matches:
                endpoint = {
                    'file': str(file_path.relative_to(self.project_root)),
                    'line': method_node.lineno + self._get_line_offset(method_code, match.start()),
                    'method': method_node.name.replace('do_', '').upper(),
                    'path': match.group(1),
                    'response_type': 'application/json',  # 默认响应类型
                    'implementation': '已实现'
                }
                
                # 提取更多信息
                self._extract_endpoint_details(method_code, match, endpoint)
                
                endpoints.append(endpoint)
        
        return endpoints
    
    def _get_line_offset(self, code: str, position: int) -> int:
        """获取字符位置在代码块中的行偏移"""
        return code[:position].count('\n')
    
    def _extract_endpoint_details(self, method_code: str, match: re.Match, endpoint: Dict[str, Any]):
        """提取端点的详细信息"""
        # 查找send_response调用
        response_match = re.search(r"self\.send_response\s*\(\s*(\d+)\s*\)", method_code)
        if response_match:
            endpoint['status_code'] = int(response_match.group(1))
        
        # 查找Content-Type
        content_type_match = re.search(r"Content-type['\"]\s*:\s*['\"]([^'\"]+)['\"]", method_code)
        if content_type_match:
            endpoint['response_type'] = content_type_match.group(1)
        
        # 检查是否有异常处理
        if 'try:' in method_code and 'except:' in method_code:
            endpoint['error_handling'] = True
        else:
            endpoint['error_handling'] = False
    
    def _regex_analysis(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """使用正则表达式进行补充分析"""
        endpoints = []
        
        # 查找路径匹配模式
        path_patterns = [
            # if path == '/api/...'
            r"if\s+path\s*==\s*['\"]([^'\"]+)['\"]",
            # elif path == '/api/...'
            r"elif\s+path\s*==\s*['\"]([^'\"]+)['\"]",
            # path.startswith('/api/')
            r"path\.startswith\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        ]
        
        for pattern in path_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                # 确定HTTP方法
                method = 'GET'
                context_start = max(0, match.start() - 100)
                context = content[context_start:match.end()]
                if 'do_POST' in context:
                    method = 'POST'
                
                endpoint = {
                    'file': str(file_path.relative_to(self.project_root)),
                    'line': content[:match.start()].count('\n') + 1,
                    'method': method,
                    'path': match.group(1),
                    'response_type': 'application/json',
                    'implementation': '已实现'
                }
                
                endpoints.append(endpoint)
        
        return endpoints
    
    def find_python_files(self) -> List[Path]:
        """查找项目中的所有Python文件"""
        python_files = []
        for ext in ['*.py']:
            python_files.extend(self.project_root.rglob(ext))
        
        # 过滤掉venv和__pycache__目录
        python_files = [f for f in python_files 
                       if 'venv' not in str(f) and '__pycache__' not in str(f)]
        
        return python_files
    
    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目的后端API接口"""
        print("开始分析后端API接口...")
        
        python_files = self.find_python_files()
        print(f"找到 {len(python_files)} 个Python文件")
        
        all_endpoints = []
        for python_file in python_files:
            print(f"分析文件: {python_file.relative_to(self.project_root)}")
            endpoints = self.analyze_python_file(python_file)
            all_endpoints.extend(endpoints)
        
        # 按路径分组统计
        path_groups = {}
        for endpoint in all_endpoints:
            path = endpoint['path']
            if path not in path_groups:
                path_groups[path] = []
            path_groups[path].append(endpoint)
        
        # 生成统计报告
        report = {
            'total_files': len(python_files),
            'total_endpoints': len(all_endpoints),
            'unique_paths': len(path_groups),
            'endpoints_by_file': {},
            'paths_summary': {}
        }
        
        # 按文件统计
        for endpoint in all_endpoints:
            file = endpoint['file']
            if file not in report['endpoints_by_file']:
                report['endpoints_by_file'][file] = []
            report['endpoints_by_file'][file].append(endpoint)
        
        # 路径摘要
        for path, endpoints in path_groups.items():
            methods = list(set(endpoint['method'] for endpoint in endpoints))
            files = list(set(endpoint['file'] for endpoint in endpoints))
            
            report['paths_summary'][path] = {
                'endpoint_count': len(endpoints),
                'methods': methods,
                'files': files,
                'sample_endpoint': endpoints[0] if endpoints else None
            }
        
        return {
            'report': report,
            'detailed_endpoints': all_endpoints
        }
    
    def save_report(self, analysis_result: Dict[str, Any], output_file: str):
        """保存分析报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"分析报告已保存到: {output_file}")

def main():
    """主函数"""
    project_root = r"E:\RAG系统"
    
    analyzer = BackendAPIAnalyzer(project_root)
    result = analyzer.analyze_project()
    
    # 输出摘要信息
    report = result['report']
    print(f"\n=== 后端API接口分析报告 ===")
    print(f"分析文件数量: {report['total_files']}")
    print(f"API端点总数: {report['total_endpoints']}")
    print(f"唯一路径数量: {report['unique_paths']}")
    
    print(f"\n=== 路径统计 ===")
    for path, summary in report['paths_summary'].items():
        print(f"路径: {path}")
        print(f"  端点数量: {summary['endpoint_count']}")
        print(f"  方法: {', '.join(summary['methods'])}")
        print(f"  文件: {', '.join(summary['files'])}")
        print()
    
    # 保存详细报告
    output_file = os.path.join(project_root, 'backend_api_analysis.json')
    analyzer.save_report(result, output_file)
    
    # 生成后端API清单
    backend_apis = []
    for path, summary in report['paths_summary'].items():
        backend_apis.append({
            'path': path,
            'methods': summary['methods'],
            'response_format': 'JSON',
            'files': summary['files']
        })
    
    backend_api_file = os.path.join(project_root, 'backend_api_list.json')
    with open(backend_api_file, 'w', encoding='utf-8') as f:
        json.dump(backend_apis, f, ensure_ascii=False, indent=2)
    print(f"后端API清单已保存到: {backend_api_file}")

if __name__ == "__main__":
    main()