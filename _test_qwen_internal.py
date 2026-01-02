#!/usr/bin/env python3
# @self-expose: {"id": "_test_qwen_internal", "name": " Test Qwen Internal", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": [" Test Qwen Internal功能"]}}
# -*- coding: utf-8 -*-
"""内部调用千问验证并输出结果"""
import json
import sys
from datetime import datetime
import requests

api_key = "sk-ca5cbb1572724063ae886b8012aa0541"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen-plus",
    "messages": [
        {"role": "system", "content": "你是一个RAG系统自检助手。"},
        {"role": "user", "content": "请仅回复：OK"}
    ],
    "max_tokens": 64,
    "temperature": 0.0
}

try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    result = {
        "status_code": resp.status_code,
        "response_json": resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text,
        "timestamp": datetime.now().isoformat()
    }
    with open("e:/RAG系统/qwen_validation_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    error_result = {
        "error": str(e),
        "timestamp": datetime.now().isoformat()
    }
    with open("e:/RAG系统/qwen_validation_result.json", "w", encoding="utf-8") as f:
        json.dump(error_result, f, ensure_ascii=False, indent=2)
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
