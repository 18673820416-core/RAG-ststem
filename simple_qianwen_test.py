#!/usr/bin/env python3
# @self-expose: {"id": "simple_qianwen_test", "name": "Simple Qianwen Test", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Qianwen Test功能"]}}
# -*- coding: utf-8 -*-
"""
简单测试千问API密钥
"""

import os
import sys
import json
import requests

# 配置
API_KEY = "sk-ca5cbb1572724063ae886b8012aa0541"
ENDPOINT = "https://api.volcengine.com/v3/chat/completions"

def test_qianwen():
    """简单测试千问API"""
    print("开始测试千问API密钥...")
    
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
        print("发送测试请求...")
        response = requests.post(ENDPOINT, headers=headers, json=data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 千问API调用成功！")
            return True
        else:
            print("❌ 千问API调用失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_qianwen()
