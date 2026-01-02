#!/usr/bin/env python3
# @self-expose: {"id": "accurate_api_analysis", "name": "Accurate Api Analysis", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Accurate Api Analysis功能"]}}
# -*- coding: utf-8 -*-
"""
精确的API差异分析脚本
"""

import json
import re

def extract_api_paths_from_frontend():
    """直接从前端文件提取API路径"""
    
    api_paths = []
    
    # 分析chatroom.html
    with open('templates/chatroom.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找API_BASE定义
    api_base_match = re.search(r'const API_BASE\s*=\s*["\']([^"\']+)["\']', content)
    api_base = api_base_match.group(1) if api_base_match else '/api/chatroom'
    
    # 查找fetch调用
    fetch_patterns = [
        (r'fetch\s*\(\s*[`"\']([^`"\']+)[`"\']', 'GET/POST'),
        (r'fetch\s*\(\s*`\$\{API_BASE\}([^`]+)`', 'GET/POST'),
        (r'fetch\s*\(\s*`\$\{this\.apiBase\}([^`]+)`', 'GET/POST'),
    ]
    
    for pattern, method in fetch_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            path = match.group(1)
            # 处理API_BASE路径
            if 'API_BASE' in pattern:
                path = api_base + path
            elif 'this.apiBase' in pattern:
                path = '/api' + path
            
            api_paths.append({
                'path': path,
                'methods': [method],
                'file': 'templates/chatroom.html'
            })
    
    # 分析agent_chatbot.html
    with open('templates/agent_chatbot.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    for pattern, method in fetch_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            path = match.group(1)
            # 处理this.apiBase路径
            if 'this.apiBase' in pattern:
                path = '/api' + path
            
            api_paths.append({
                'path': path,
                'methods': [method],
                'file': 'templates/agent_chatbot.html'
            })
    
    return api_paths

def get_backend_api_paths():
    """获取后端API路径"""
    
    with open('backend_api_list.json', 'r', encoding='utf-8') as f:
        backend_apis = json.load(f)
    
    return {api['path'] for api in backend_apis}

def analyze_api_differences():
    """分析API差异"""
    
    print("开始精确分析API差异...\n")
    
    # 获取前端API路径
    frontend_apis = extract_api_paths_from_frontend()
    frontend_paths = {api['path'] for api in frontend_apis}
    
    # 获取后端API路径
    backend_paths = get_backend_api_paths()
    
    print(f"前端API数量: {len(frontend_paths)}")
    print(f"后端API数量: {len(backend_paths)}")
    
    # 检查差异
    missing_in_backend = frontend_paths - backend_paths
    missing_in_frontend = backend_paths - frontend_paths
    
    print(f"\n前端调用但后端未实现的API ({len(missing_in_backend)}个):")
    for path in sorted(missing_in_backend):
        # 查找对应的文件
        files = [api['file'] for api in frontend_apis if api['path'] == path]
        print(f"  - {path} (来自: {files[0]})")
    
    print(f"\n后端实现但前端未调用的API ({len(missing_in_frontend)}个):")
    for path in sorted(missing_in_frontend):
        print(f"  - {path}")
    
    # 显示前端API的详细信息
    print(f"\n前端API详细信息:")
    for api in frontend_apis:
        print(f"  - {api['path']} ({', '.join(api['methods'])}) - {api['file']}")

if __name__ == "__main__":
    analyze_api_differences()