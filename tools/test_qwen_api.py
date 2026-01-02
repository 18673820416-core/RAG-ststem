#!/usr/bin/env python3
# @self-expose: {"id": "test_qwen_api", "name": "Qwen API Tester Tool", "type": "tool", "version": "1.0.0", "needs": {"deps": ["requests"], "resources": []}, "provides": {"capabilities": ["千问API有效性测试", "OpenAI兼容模式支持", "原生端点回退"], "methods": {"test_openai_compat": "OpenAI兼容模式测试", "test_native": "原生模式测试", "main": "主测试函数"}}}
# -*- coding: utf-8 -*-
"""
千问(Qwen/DashScope) API密钥有效性测试脚本
- 优先使用 OpenAI 兼容端点：https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
- 若失败，回退使用原生端点：https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
使用：
  python tools/test_qwen_api.py <api_key>
  python tools/test_qwen_api.py   # 从 config/api_keys.json 读取 'qwen' 或 'dashscope'
输出：成功/失败的JSON结果及回复预览/错误原因
"""
import sys
import json
from datetime import datetime
import requests
from pathlib import Path

OPENAI_COMPAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
NATIVE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
DEFAULT_MODEL = "qwen-plus"  # 可按需调整，例如 qwen2.5-7b-chat

def load_key_from_config():
    try:
        cfg = Path(__file__).parent.parent / "config" / "api_keys.json"
        if not cfg.exists():
            return None
        data = json.loads(cfg.read_text(encoding="utf-8"))
        # 依次尝试 qwen / dashscope
        for prov in ("qwen", "dashscope"):
            if prov in data and isinstance(data[prov], dict):
                key = data[prov].get("key")
                if key:
                    return key
        return None
    except Exception:
        return None


def test_openai_compat(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个RAG系统自检助手。"},
            {"role": "user", "content": "请仅回复：OK"}
        ],
        "max_tokens": 64,
        "temperature": 0.0
    }
    resp = requests.post(OPENAI_COMPAT_URL, headers=headers, json=payload, timeout=30)
    data = resp.json()
    if resp.status_code == 200 and "choices" in data and data["choices"]:
        content = data["choices"][0]["message"]["content"]
        return True, content
    return False, data


def test_native(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "input": {"messages": [
            {"role": "system", "content": "你是一个RAG系统自检助手。"},
            {"role": "user", "content": "请仅回复：OK"}
        ]},
        "parameters": {"result_format": "text", "max_tokens": 64, "temperature": 0.0}
    }
    resp = requests.post(NATIVE_URL, headers=headers, json=payload, timeout=30)
    data = resp.json()
    # 原生接口的返回格式不同，尝试提取text
    if resp.status_code == 200:
        # 可能返回结构包含 output / choices 等，按常见结构尝试提取文本
        text = None
        if isinstance(data, dict):
            if "output" in data and isinstance(data["output"], dict):
                text = data["output"].get("text")
            if not text and "choices" in data and data["choices"]:
                ch0 = data["choices"][0]
                if isinstance(ch0, dict):
                    text = ch0.get("message", {}).get("content") or ch0.get("text")
        if text:
            return True, text
    return False, data


def main():
    api_key = None
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        api_key = sys.argv[1].strip()
    else:
        api_key = load_key_from_config()

    if not api_key:
        print(json.dumps({
            "success": False,
            "provider": "qwen",
            "error": "未提供API密钥，且配置文件未找到 'qwen'/'dashscope' 密钥",
            "hint": "请传入参数或将密钥写入 config/api_keys.json"
        }, ensure_ascii=False, indent=2))
        sys.exit(2)

    try:
        ok, result = test_openai_compat(api_key)
        if ok:
            print(json.dumps({
                "success": True,
                "provider": "qwen",
                "endpoint": OPENAI_COMPAT_URL,
                "timestamp": datetime.now().isoformat(),
                "reply_preview": str(result)[:200]
            }, ensure_ascii=False, indent=2))
            sys.exit(0)
        # 回退原生
        ok2, result2 = test_native(api_key)
        if ok2:
            print(json.dumps({
                "success": True,
                "provider": "qwen",
                "endpoint": NATIVE_URL,
                "timestamp": datetime.now().isoformat(),
                "reply_preview": str(result2)[:200]
            }, ensure_ascii=False, indent=2))
            sys.exit(0)
        # 两者皆失败
        print(json.dumps({
            "success": False,
            "provider": "qwen",
            "error": "调用失败",
            "details": result2,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2))
        sys.exit(3)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "provider": "qwen",
            "error": f"异常: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2))
        sys.exit(4)

if __name__ == "__main__":
    main()
