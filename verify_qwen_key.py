#!/usr/bin/env python3
# @self-expose: {"id": "verify_qwen_key", "name": "Verify Qwen Key", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Verify Qwen Key功能"]}}
# -*- coding: utf-8 -*-
"""
直接验证千问密钥并输出结论
"""
import requests
import json

def test_qwen_key(api_key):
    """测试千问密钥并返回明确结论"""
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        # 判断是否成功
        if response.status_code == 200 and "choices" in data:
            content = data["choices"][0]["message"]["content"]
            return {
                "结论": "✅ 密钥可用",
                "状态码": response.status_code,
                "回复内容": content,
                "provider": "qwen",
                "endpoint": url
            }
        else:
            return {
                "结论": "❌ 密钥不可用",
                "状态码": response.status_code,
                "错误信息": data.get("error", {}).get("message", str(data)),
                "provider": "qwen",
                "endpoint": url
            }
    except requests.exceptions.RequestException as e:
        return {
            "结论": "❌ 网络请求失败",
            "错误类型": type(e).__name__,
            "错误详情": str(e)
        }
    except Exception as e:
        return {
            "结论": "❌ 验证异常",
            "错误类型": type(e).__name__,
            "错误详情": str(e)
        }

if __name__ == "__main__":
    api_key = "sk-ca5cbb1572724063ae886b8012aa0541"
    result = test_qwen_key(api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))
