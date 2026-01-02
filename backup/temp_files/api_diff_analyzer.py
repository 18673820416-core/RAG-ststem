#!/usr/bin/env python3
# @self-expose: {"id": "api_diff_analyzer", "name": "Api Diff Analyzer", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Api Diff Analyzer功能"]}}
# -*- coding: utf-8 -*-
"""
API接口差异分析脚本
用于分析前后端API接口的不匹配问题
"""

import json
import re
from typing import Dict, List, Set, Tuple

class APIDiffAnalyzer:
    def __init__(self, frontend_file: str, backend_file: str):
        self.frontend_file = frontend_file
        self.backend_file = backend_file
        self.frontend_apis = []
        self.backend_apis = []
        
    def load_data(self):
        """加载前后端API数据"""
        with open(self.frontend_file, 'r', encoding='utf-8') as f:
            self.frontend_apis = json.load(f)
        
        with open(self.backend_file, 'r', encoding='utf-8') as f:
            self.backend_apis = json.load(f)
    
    def normalize_url(self, url: str) -> str:
        """标准化URL路径"""
        # 移除协议和域名
        url = re.sub(r'^https?://[^/]+', '', url)
        # 移除查询参数
        url = re.sub(r'\?.*$', '', url)
        # 标准化路径
        url = url.strip('/')
        # 处理模板字符串
        url = re.sub(r'`\$\{.*?\}', '', url)
        url = re.sub(r"'([^']*)'", lambda m: m.group(1), url)
        url = re.sub(r'this\.\w+Url', 'api/error-report', url)
        url = re.sub(r'this\.apiBase', '', url)
        url = re.sub(r'API_BASE', '', url)
        url = url.strip('/')
        
        # 特殊处理
        if url == 'agents':
            return 'api/agents'
        elif url == 'status':
            return 'api/status'
        elif url == 'history':
            return 'api/chatroom/history'
        elif url == 'message':
            return 'api/chatroom/message'
        elif url == 'summary':
            return 'api/chatroom/summary'
        elif url == 'health':
            return 'api/health'
        elif 'chatroom/history' in url:
            return 'api/chatroom/history'
        elif 'chatroom/message' in url:
            return 'api/chatroom/message'
        
        return url
    
    def analyze_differences(self) -> Dict:
        """分析前后端API差异"""
        self.load_data()
        
        # 构建后端API映射
        backend_map = {}
        for api in self.backend_apis:
            path = api['path'].strip('/')
            if path and not path.startswith('api/'):
                path = f"api/{path}"
            if path and path not in ['api/...', 'api/', '\\\\', '\\']:
                backend_map[path] = {
                    'methods': set(api['methods']),
                    'files': api['files']
                }
        
        # 构建前端API映射
        frontend_map = {}
        for api in self.frontend_apis:
            normalized_url = self.normalize_url(api['url'])
            if normalized_url and not normalized_url.startswith('api/'):
                normalized_url = f"api/{normalized_url}"
            
            if normalized_url and normalized_url not in frontend_map:
                frontend_map[normalized_url] = {
                    'methods': set(api['methods']),
                    'files': api['files']
                }
        
        # 分析差异
        missing_in_backend = []
        missing_in_frontend = []
        method_mismatches = []
        
        # 检查前端有但后端没有的API
        for frontend_path, frontend_info in frontend_map.items():
            if frontend_path not in backend_map:
                missing_in_backend.append({
                    'path': frontend_path,
                    'methods': list(frontend_info['methods']),
                    'files': frontend_info['files']
                })
            else:
                # 检查方法不匹配
                backend_methods = backend_map[frontend_path]['methods']
                frontend_methods = frontend_info['methods']
                
                missing_methods = frontend_methods - backend_methods
                if missing_methods:
                    method_mismatches.append({
                        'path': frontend_path,
                        'frontend_methods': list(frontend_methods),
                        'backend_methods': list(backend_methods),
                        'missing_methods': list(missing_methods),
                        'files': frontend_info['files']
                    })
        
        # 检查后端有但前端没有的API
        for backend_path, backend_info in backend_map.items():
            if backend_path not in frontend_map:
                missing_in_frontend.append({
                    'path': backend_path,
                    'methods': list(backend_info['methods']),
                    'files': backend_info['files']
                })
        
        return {
            'missing_in_backend': missing_in_backend,
            'missing_in_frontend': missing_in_frontend,
            'method_mismatches': method_mismatches,
            'frontend_api_count': len(frontend_map),
            'backend_api_count': len(backend_map)
        }
    
    def generate_report(self, analysis_result: Dict) -> str:
        """生成差异分析报告"""
        report = """# API接口差异分析报告

## 统计概览
- 前端API数量: {frontend_count}
- 后端API数量: {backend_count}

## 问题分析

### 1. 前端调用但后端未实现的API
{missing_backend}

### 2. 后端实现但前端未调用的API
{missing_frontend}

### 3. 方法不匹配的API
{method_mismatches}

## 修复建议
{recommendations}
"""
        
        # 格式化缺失的后端API
        missing_backend_text = ""
        if analysis_result['missing_in_backend']:
            for api in analysis_result['missing_in_backend']:
                missing_backend_text += f"- **{api['path']}** (方法: {', '.join(api['methods'])})\n"
                missing_backend_text += f"  文件: {', '.join(api['files'])}\n\n"
        else:
            missing_backend_text = "无\n"
        
        # 格式化缺失的前端API
        missing_frontend_text = ""
        if analysis_result['missing_in_frontend']:
            for api in analysis_result['missing_in_frontend']:
                missing_frontend_text += f"- **{api['path']}** (方法: {', '.join(api['methods'])})\n"
                missing_frontend_text += f"  文件: {', '.join(api['files'])}\n\n"
        else:
            missing_frontend_text = "无\n"
        
        # 格式化方法不匹配
        method_mismatches_text = ""
        if analysis_result['method_mismatches']:
            for mismatch in analysis_result['method_mismatches']:
                method_mismatches_text += f"- **{mismatch['path']}**\n"
                method_mismatches_text += f"  前端方法: {', '.join(mismatch['frontend_methods'])}\n"
                method_mismatches_text += f"  后端方法: {', '.join(mismatch['backend_methods'])}\n"
                method_mismatches_text += f"  缺失方法: {', '.join(mismatch['missing_methods'])}\n"
                method_mismatches_text += f"  文件: {', '.join(mismatch['files'])}\n\n"
        else:
            method_mismatches_text = "无\n"
        
        # 生成修复建议
        recommendations = self.generate_recommendations(analysis_result)
        
        return report.format(
            frontend_count=analysis_result['frontend_api_count'],
            backend_count=analysis_result['backend_api_count'],
            missing_backend=missing_backend_text,
            missing_frontend=missing_frontend_text,
            method_mismatches=method_mismatches_text,
            recommendations=recommendations
        )
    
    def generate_recommendations(self, analysis_result: Dict) -> str:
        """生成修复建议"""
        recommendations = ""
        
        if analysis_result['missing_in_backend']:
            recommendations += "### 后端需要添加的API端点\n"
            for api in analysis_result['missing_in_backend']:
                recommendations += f"1. **{api['path']}** - 需要实现 {', '.join(api['methods'])} 方法\n"
        
        if analysis_result['method_mismatches']:
            recommendations += "\n### 需要修复的方法不匹配问题\n"
            for mismatch in analysis_result['method_mismatches']:
                recommendations += f"1. **{mismatch['path']}** - 后端需要添加 {', '.join(mismatch['missing_methods'])} 方法实现\n"
        
        if analysis_result['missing_in_frontend']:
            recommendations += "\n### 前端可以考虑调用的后端API\n"
            for api in analysis_result['missing_in_frontend']:
                recommendations += f"1. **{api['path']}** - 已实现 {', '.join(api['methods'])} 方法\n"
        
        if not recommendations:
            recommendations = "前后端API接口匹配良好，无需修复。"
        
        return recommendations
    
    def save_analysis(self, analysis_result: Dict, output_file: str):
        """保存分析结果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        report = self.generate_report(analysis_result)
        with open(output_file.replace('.json', '_report.md'), 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    analyzer = APIDiffAnalyzer(
        'frontend_api_list.json',
        'backend_api_list.json'
    )
    
    print("开始分析前后端API接口差异...")
    
    try:
        analysis_result = analyzer.analyze_differences()
        
        # 保存分析结果
        analyzer.save_analysis(analysis_result, 'api_diff_analysis.json')
        
        print("分析完成！")
        print(f"前端API数量: {analysis_result['frontend_api_count']}")
        print(f"后端API数量: {analysis_result['backend_api_count']}")
        print(f"前端调用但后端未实现的API: {len(analysis_result['missing_in_backend'])}")
        print(f"后端实现但前端未调用的API: {len(analysis_result['missing_in_frontend'])}")
        print(f"方法不匹配的API: {len(analysis_result['method_mismatches'])}")
        
        # 输出关键问题
        if analysis_result['missing_in_backend']:
            print("\n关键问题 - 前端调用但后端未实现的API:")
            for api in analysis_result['missing_in_backend']:
                print(f"  - {api['path']} ({', '.join(api['methods'])})")
        
        if analysis_result['method_mismatches']:
            print("\n关键问题 - 方法不匹配的API:")
            for mismatch in analysis_result['method_mismatches']:
                print(f"  - {mismatch['path']}: 前端需要 {mismatch['missing_methods']}")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")

if __name__ == "__main__":
    main()