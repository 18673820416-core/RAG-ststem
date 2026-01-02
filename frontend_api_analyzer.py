#!/usr/bin/env python
# @self-expose: {"id": "frontend_api_analyzer", "name": "Frontend Api Analyzer", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Frontend Api Analyzer功能"]}}
# -*- coding: utf-8 -*-
"""
前端API调用统计脚本
用于分析前端HTML/JavaScript文件中的API调用模式
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

class FrontendAPIAnalyzer:
    """前端API调用分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.api_calls = []
        
    def analyze_html_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """分析单个HTML文件中的API调用"""
        api_calls = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配fetch API调用
            fetch_patterns = [
                # fetch('/api/...')
                r"fetch\s*\(\s*['\"]([^'\"]+)['\"]",
                # fetch(`${apiBase}/...`)
                r"fetch\s*\(\s*`\$\{.*?\}/([^`]+)`",
                # fetch(url, {method: 'POST', ...})
                r"fetch\s*\(\s*([^,]+)\s*,\s*\{[^}]*method\s*:\s*['\"]([^'\"]+)['\"][^}]*\}",
            ]
            
            for pattern in fetch_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    api_call = {
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': self._get_line_number(content, match.start()),
                        'method': 'GET',  # 默认方法
                        'url': '',
                        'headers': {},
                        'body': None
                    }
                    
                    if len(match.groups()) >= 2:
                        # 匹配到URL和方法
                        api_call['url'] = match.group(1)
                        api_call['method'] = match.group(2).upper()
                    else:
                        # 只匹配到URL
                        api_call['url'] = match.group(1)
                        
                    # 尝试提取更多信息
                    self._extract_api_details(content, match, api_call)
                    
                    api_calls.append(api_call)
                    
        except Exception as e:
            print(f"分析文件 {file_path} 时出错: {e}")
            
        return api_calls
    
    def _get_line_number(self, content: str, position: int) -> int:
        """获取字符位置对应的行号"""
        return content[:position].count('\n') + 1
    
    def _extract_api_details(self, content: str, match: re.Match, api_call: Dict[str, Any]):
        """提取API调用的详细信息"""
        # 查找fetch调用的完整上下文
        start_pos = max(0, match.start() - 200)
        end_pos = min(len(content), match.end() + 200)
        context = content[start_pos:end_pos]
        
        # 提取headers
        headers_match = re.search(r"headers\s*:\s*\{([^}]+)\}", context)
        if headers_match:
            headers_content = headers_match.group(1)
            # 解析headers对象
            header_pairs = re.findall(r"(['\"]?)([^'\":]+)\1\s*:\s*['\"]([^'\"]+)['\"]", headers_content)
            for _, key, value in header_pairs:
                api_call['headers'][key.strip()] = value
        
        # 提取body
        body_match = re.search(r"body\s*:\s*([^,}\n]+)", context)
        if body_match:
            body_content = body_match.group(1).strip()
            if body_content.startswith('JSON.stringify'):
                # 解析JSON.stringify调用
                json_match = re.search(r"JSON\.stringify\s*\(\s*([^)]+)\)", body_content)
                if json_match:
                    api_call['body'] = f"JSON: {json_match.group(1)}"
            else:
                api_call['body'] = body_content
    
    def find_html_files(self) -> List[Path]:
        """查找项目中的所有HTML文件"""
        html_files = []
        for ext in ['*.html', '*.htm']:
            html_files.extend(self.project_root.rglob(ext))
        return html_files
    
    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目的前端API调用"""
        print("开始分析前端API调用...")
        
        html_files = self.find_html_files()
        print(f"找到 {len(html_files)} 个HTML文件")
        
        all_api_calls = []
        for html_file in html_files:
            print(f"分析文件: {html_file.relative_to(self.project_root)}")
            api_calls = self.analyze_html_file(html_file)
            all_api_calls.extend(api_calls)
        
        # 按URL分组统计
        url_groups = {}
        for api_call in all_api_calls:
            url = api_call['url']
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(api_call)
        
        # 生成统计报告
        report = {
            'total_files': len(html_files),
            'total_api_calls': len(all_api_calls),
            'unique_endpoints': len(url_groups),
            'api_calls_by_file': {},
            'endpoints_summary': {}
        }
        
        # 按文件统计
        for api_call in all_api_calls:
            file = api_call['file']
            if file not in report['api_calls_by_file']:
                report['api_calls_by_file'][file] = []
            report['api_calls_by_file'][file].append(api_call)
        
        # 端点摘要
        for url, calls in url_groups.items():
            methods = list(set(call['method'] for call in calls))
            files = list(set(call['file'] for call in calls))
            
            report['endpoints_summary'][url] = {
                'call_count': len(calls),
                'methods': methods,
                'files': files,
                'sample_call': calls[0] if calls else None
            }
        
        return {
            'report': report,
            'detailed_calls': all_api_calls
        }
    
    def save_report(self, analysis_result: Dict[str, Any], output_file: str):
        """保存分析报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"分析报告已保存到: {output_file}")

def main():
    """主函数"""
    project_root = r"E:\RAG系统"
    
    analyzer = FrontendAPIAnalyzer(project_root)
    result = analyzer.analyze_project()
    
    # 输出摘要信息
    report = result['report']
    print(f"\n=== 前端API调用分析报告 ===")
    print(f"分析文件数量: {report['total_files']}")
    print(f"API调用总数: {report['total_api_calls']}")
    print(f"唯一端点数量: {report['unique_endpoints']}")
    
    print(f"\n=== 端点统计 ===")
    for url, summary in report['endpoints_summary'].items():
        print(f"端点: {url}")
        print(f"  调用次数: {summary['call_count']}")
        print(f"  方法: {', '.join(summary['methods'])}")
        print(f"  文件: {', '.join(summary['files'])}")
        print()
    
    # 保存详细报告
    output_file = os.path.join(project_root, 'frontend_api_analysis.json')
    analyzer.save_report(result, output_file)
    
    # 生成前端API清单
    frontend_apis = []
    for url, summary in report['endpoints_summary'].items():
        frontend_apis.append({
            'url': url,
            'methods': summary['methods'],
            'expected_response': '待分析',
            'files': summary['files']
        })
    
    frontend_api_file = os.path.join(project_root, 'frontend_api_list.json')
    with open(frontend_api_file, 'w', encoding='utf-8') as f:
        json.dump(frontend_apis, f, ensure_ascii=False, indent=2)
    print(f"前端API清单已保存到: {frontend_api_file}")

if __name__ == "__main__":
    main()