#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试千问API密钥并将结果写入文件
"""

import os
import sys
import json
import requests

# 配置
API_KEY = "sk-ca5cbb1572724063ae886b8012aa0541"
ENDPOINT = "https://api.volcengine.com/v3/chat/completions"
RESULTS_FILE = "e:\RAG系统\qianwen_test_results.txt"

def test_qianwen():
    """测试千问API并将结果写入文件"""
    results = []
    results.append("=== 千问API密钥测试结果 ===")
    results.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"API密钥: {API_KEY[:8]}...{API_KEY[-4:]}")
    results.append(f"API端点: {ENDPOINT}")
    results.append("")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "你好，请问1+1等于几？"}
        ],
        "temperature": 0.0,
        "max_tokens": 10
    }
    
    try:
        results.append("发送测试请求...")
        response = requests.post(ENDPOINT, headers=headers, json=data, timeout=30)
        
        results.append(f"响应状态码: {response.status_code}")
        results.append(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            results.append("✅ 千问API调用成功！")
        else:
            results.append("❌ 千问API调用失败")
            
    except Exception as e:
        results.append(f"❌ 测试失败: {e}")
        import traceback
        results.append(f"错误详情: {traceback.format_exc()}")
    
    # 写入结果文件
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
    
    print(f"测试结果已写入文件: {RESULTS_FILE}")
    print("\n".join(results))

if __name__ == "__main__":
    from datetime import datetime
    test_qianwen()
