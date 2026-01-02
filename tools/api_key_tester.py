#!/usr/bin/env python3
# @self-expose: {"id": "api_key_tester", "name": "API Key Tester Tool", "type": "tool", "version": "1.0.0", "needs": {"deps": ["config.system_config", "src.llm_client_enhanced", "config.api_keys"], "resources": []}, "provides": {"capabilities": ["自动验证API密钥有效性", "支持多提供商测试", "JSON结果输出"], "methods": {"main": "API密钥验证主函数"}}}
# -*- coding: utf-8 -*-
"""
API密钥有效性测试脚本
- 默认使用 config/system_config.py 中的 LLM_CONFIG["default_provider"]
- 可通过命令行参数指定 provider，例如：python tools/api_key_tester.py deepseek
使用方式（PowerShell）：
  python tools/api_key_tester.py
  python tools/api_key_tester.py deepseek
输出：
  - 成功：打印部分模型回复文本
  - 失败：打印错误原因（密钥缺失/端点错误/网络异常等）
"""
import sys
import json
from datetime import datetime

try:
    from config.system_config import LLM_CONFIG
    from src.llm_client_enhanced import LLMClientEnhanced
    from config.api_keys import api_key_manager
except Exception as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

def main():
    provider = None
    if len(sys.argv) >= 2:
        provider = sys.argv[1].strip()
    else:
        provider = LLM_CONFIG.get("default_provider", "deepseek")

    api_key = api_key_manager.get_key(provider)
    if not api_key:
        print(json.dumps({
            "success": False,
            "provider": provider,
            "error": f"未找到提供商 '{provider}' 的API密钥",
            "hint": "请将密钥写入 config/api_keys.json 或用导入脚本添加"
        }, ensure_ascii=False, indent=2))
        sys.exit(2)

    messages = [
        {"role": "system", "content": "你是一个专业的RAG助手，正在执行API密钥有效性自检。"},
        {"role": "user", "content": "你好，请返回一句简短的确认消息，并不要过长。"}
    ]

    try:
        client = LLMClientEnhanced(provider=provider)
        reply = client.chat_completion(messages, max_tokens=64, temperature=0.2)
        if reply:
            print(json.dumps({
                "success": True,
                "provider": provider,
                "timestamp": datetime.now().isoformat(),
                "reply_preview": reply[:200]
            }, ensure_ascii=False, indent=2))
            sys.exit(0)
        else:
            print(json.dumps({
                "success": False,
                "provider": provider,
                "error": "LLM未返回内容",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2))
            sys.exit(3)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "provider": provider,
            "error": f"调用异常: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2))
        sys.exit(4)

if __name__ == "__main__":
    main()
