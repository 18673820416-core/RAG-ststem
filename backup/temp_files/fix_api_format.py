#!/usr/bin/env python3
# @self-expose: {"id": "fix_api_format", "name": "Fix Api Format", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Fix Api Format功能"]}}
# -*- coding: utf-8 -*-
"""
修复前端API列表格式，使其与后端API列表格式一致
"""

import json
import re

def normalize_frontend_url(url):
    """标准化前端URL格式"""
    # 移除模板字符串标记
    url = url.replace('`', '').replace('${', '').replace('}', '')
    
    # 移除引号
    url = url.replace("'", "").replace('"', '')
    
    # 处理完整的URL
    if url.startswith('http'):
        # 提取路径部分
        match = re.search(r'/api(/.*)', url)
        if match:
            return match.group(1)
    
    # 处理相对路径
    if not url.startswith('/'):
        # 检查是否是API_BASE相关的路径
        if 'API_BASE' in url:
            # 提取路径部分
            match = re.search(r'API_BASE(/.*)', url)
            if match:
                return '/api/chatroom' + match.group(1)
        elif 'this.apiBase' in url:
            # 提取路径部分
            match = re.search(r'this\.apiBase(/.*)', url)
            if match:
                return '/api' + match.group(1)
        else:
            # 简单的相对路径，添加/api前缀
            return '/api/' + url
    
    return url

def fix_frontend_api_list():
    """修复前端API列表"""
    
    # 读取原始前端API列表
    with open('frontend_api_list.json', 'r', encoding='utf-8') as f:
        frontend_apis = json.load(f)
    
    # 修复每个API的URL
    fixed_apis = []
    for api in frontend_apis:
        fixed_api = api.copy()
        original_url = api['url']
        
        # 标准化URL
        normalized_url = normalize_frontend_url(original_url)
        
        # 特殊处理：API_BASE相关的路径
        if 'API_BASE' in original_url:
            # 提取路径部分
            match = re.search(r'API_BASE(/.*)', original_url.replace('`', '').replace('${', '').replace('}', ''))
            if match:
                normalized_url = '/api/chatroom' + match.group(1)
        
        # 处理this.apiBase相关的路径
        elif 'this.apiBase' in original_url:
            # 提取路径部分
            match = re.search(r'this\.apiBase(/.*)', original_url.replace('`', '').replace('${', '').replace('}', ''))
            if match:
                normalized_url = '/api' + match.group(1)
        
        # 处理简单的相对路径
        elif not original_url.startswith('/') and not original_url.startswith('http'):
            normalized_url = '/api/' + original_url
        
        fixed_api['path'] = normalized_url
        fixed_apis.append(fixed_api)
    
    # 保存修复后的前端API列表
    with open('frontend_api_list_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_apis, f, ensure_ascii=False, indent=2)
    
    print(f"修复了 {len(fixed_apis)} 个前端API")
    
    # 显示修复前后的对比
    print("\n修复前后对比:")
    for i, (orig, fixed) in enumerate(zip(frontend_apis, fixed_apis)):
        print(f"{i+1}. {orig['url']} -> {fixed['path']}")

def analyze_api_differences():
    """分析API差异"""
    
    # 读取修复后的前端API列表
    with open('frontend_api_list_fixed.json', 'r', encoding='utf-8') as f:
        frontend_apis = json.load(f)
    
    # 读取后端API列表
    with open('backend_api_list.json', 'r', encoding='utf-8') as f:
        backend_apis = json.load(f)
    
    # 提取路径集合
    frontend_paths = {api['path'] for api in frontend_apis}
    backend_paths = {api['path'] for api in backend_apis}
    
    print(f"\n前端API数量: {len(frontend_paths)}")
    print(f"后端API数量: {len(backend_paths)}")
    
    # 检查差异
    missing_in_backend = frontend_paths - backend_paths
    missing_in_frontend = backend_paths - frontend_paths
    
    print(f"\n前端调用但后端未实现的API ({len(missing_in_backend)}个):")
    for path in sorted(missing_in_backend):
        print(f"  - {path}")
    
    print(f"\n后端实现但前端未调用的API ({len(missing_in_frontend)}个):")
    for path in sorted(missing_in_frontend):
        print(f"  - {path}")

if __name__ == "__main__":
    print("开始修复前端API列表格式...")
    fix_frontend_api_list()
    print("\n分析API差异...")
    analyze_api_differences()