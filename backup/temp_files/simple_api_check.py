#!/usr/bin/env python3
# @self-expose: {"id": "simple_api_check", "name": "Simple Api Check", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Api Check功能"]}}
# -*- coding: utf-8 -*-
"""
简单直接的API检查脚本
"""

import json
import re

def check_frontend_apis():
    """检查前端实际调用的API"""
    
    print("检查前端实际调用的API...\n")
    
    # 读取chatroom.html
    with open('templates/chatroom.html', 'r', encoding='utf-8') as f:
        chatroom_content = f.read()
    
    # 查找API_BASE定义
    api_base_match = re.search(r'const API_BASE\s*=\s*["\']([^"\']+)["\']', chatroom_content)
    api_base = api_base_match.group(1) if api_base_match else '/api/chatroom'
    print(f"API_BASE定义: {api_base}")
    
    # 查找实际的fetch调用
    fetch_calls = []
    
    # 查找所有fetch调用
    fetch_pattern = r'fetch\s*\(\s*([`"\'][^`"\']+[`"\']|`\$\{API_BASE\}[^`]+`|`\$\{this\.apiBase\}[^`]+`)'
    matches = re.finditer(fetch_pattern, chatroom_content)
    
    for match in matches:
        url = match.group(1)
        
        # 处理模板字符串
        if url.startswith('`${API_BASE}'):
            path = url.replace('`${API_BASE}', api_base).replace('`', '')
        elif url.startswith('`${this.apiBase}'):
            path = url.replace('`${this.apiBase}', '/api').replace('`', '')
        else:
            # 处理普通字符串
            path = url.strip('`"\'')
        
        # 移除查询参数
        if '?' in path:
            path = path.split('?')[0]
        
        fetch_calls.append(path)
    
    # 读取agent_chatbot.html
    with open('templates/agent_chatbot.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # 查找agent_chatbot.html中的fetch调用
    matches = re.finditer(fetch_pattern, index_content)
    for match in matches:
        url = match.group(1)
        
        # 处理模板字符串
        if url.startswith('`${this.apiBase}'):
            path = url.replace('`${this.apiBase}', '/api').replace('`', '')
        else:
            # 处理普通字符串
            path = url.strip('`"\'')
        
        # 移除查询参数
        if '?' in path:
            path = path.split('?')[0]
        
        fetch_calls.append(path)
    
    # 去重
    unique_fetch_calls = list(set(fetch_calls))
    
    print(f"前端实际调用的API ({len(unique_fetch_calls)}个):")
    for call in sorted(unique_fetch_calls):
        print(f"  - {call}")
    
    return unique_fetch_calls

def check_backend_apis():
    """检查后端已实现的API"""
    
    with open('backend_api_list.json', 'r', encoding='utf-8') as f:
        backend_apis = json.load(f)
    
    backend_paths = {api['path'] for api in backend_apis}
    
    print(f"\n后端已实现的API ({len(backend_paths)}个):")
    for path in sorted(backend_paths):
        print(f"  - {path}")
    
    return backend_paths

def check_differences():
    """检查差异"""
    
    frontend_apis = check_frontend_apis()
    backend_apis = check_backend_apis()
    
    # 转换为集合
    frontend_set = set(frontend_apis)
    backend_set = set(backend_apis)
    
    # 检查差异
    missing_in_backend = frontend_set - backend_set
    missing_in_frontend = backend_set - frontend_set
    
    print(f"\n前端调用但后端未实现的API ({len(missing_in_backend)}个):")
    for path in sorted(missing_in_backend):
        print(f"  - {path}")
    
    print(f"\n后端实现但前端未调用的API ({len(missing_in_frontend)}个):")
    for path in sorted(missing_in_frontend):
        print(f"  - {path}")
    
    return missing_in_backend, missing_in_frontend

if __name__ == "__main__":
    missing_backend, missing_frontend = check_differences()
    
    print("\n" + "="*50)
    print("修复建议:")
    print("="*50)
    
    if missing_backend:
        print("\n需要在后端添加以下API端点:")
        for path in sorted(missing_backend):
            print(f"  - {path}")
    
    if missing_frontend:
        print("\n前端可以考虑调用以下后端API:")
        for path in sorted(missing_frontend):
            print(f"  - {path}")