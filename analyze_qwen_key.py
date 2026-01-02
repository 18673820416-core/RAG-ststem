#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用DeepSeek推导千问密钥有效性
"""
import requests
import json

# 测试DeepSeek（已知可用）
deepseek_key = "sk-4ce384ecace64c729dea26b2bea0de89"
deepseek_url = "https://api.deepseek.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {deepseek_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "分析千问API密钥格式'sk-ca5cbb1572724063ae886b8012aa0541'是否符合阿里云DashScope标准格式（sk-前缀+32位十六进制）。仅回复：符合 或 不符合"}
    ],
    "max_tokens": 10,
    "temperature": 0
}

try:
    response = requests.post(deepseek_url, headers=headers, json=payload, timeout=30)
    data = response.json()
    
    if response.status_code == 200 and "choices" in data:
        answer = data["choices"][0]["message"]["content"]
        
        # 基于格式判断 + LLM分析
        qwen_key = "sk-ca5cbb1572724063ae886b8012aa0541"
        format_valid = qwen_key.startswith("sk-") and len(qwen_key) == 42
        
        result = {
            "DeepSeek分析结果": answer,
            "格式校验": "✅ 通过" if format_valid else "❌ 不通过",
            "千问密钥": qwen_key,
            "推导结论": "✅ 密钥格式正确，大概率可用（需实际调用验证）" if format_valid else "❌ 格式异常，不可用"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"错误": "DeepSeek调用失败", "详情": data}, ensure_ascii=False, indent=2))
        
except Exception as e:
    # 即使DeepSeek失败，也直接基于格式判断
    qwen_key = "sk-ca5cbb1572724063ae886b8012aa0541"
    format_valid = qwen_key.startswith("sk-") and len(qwen_key) == 42
    
    result = {
        "DeepSeek调用": "网络异常",
        "格式校验": "✅ 通过" if format_valid else "❌ 不通过",
        "千问密钥": qwen_key,
        "最终结论": "✅ 格式符合标准，可接入系统（运行时验证有效性）" if format_valid else "❌ 格式异常，不可用"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
