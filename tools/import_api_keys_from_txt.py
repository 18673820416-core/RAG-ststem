#!/usr/bin/env python3
# @self-expose: {"id": "import_api_keys_from_txt", "name": "API Keys Import Tool", "type": "tool", "version": "1.0.0", "needs": {"deps": ["config.api_keys"], "resources": []}, "provides": {"capabilities": ["从TXT文件导入API密钥", "支持多种格式", "持久化存储"], "methods": {"parse_line": "解析密钥行", "main": "主导入函数"}}}
# -*- coding: utf-8 -*-
"""
从TXT导入API密钥到系统（写入 config/api_keys.json）
支持格式（每行一条，忽略空行和#注释）：
- provider=sk-xxxx
- provider: sk-xxxx
- provider sk-xxxx
使用方式（PowerShell）：
  python tools/import_api_keys_from_txt.py keys.txt
  python tools/import_api_keys_from_txt.py keys.txt "开发临时密钥"
导入后会持久化到 config/api_keys.json，并可被系统读取。
"""
import sys
import os
import json
from pathlib import Path

try:
    from config.api_keys import APIKeyManager
except Exception as e:
    print(f"导入APIKeyManager失败: {e}")
    sys.exit(1)

def parse_line(line: str):
    # 去除注释
    raw = line.strip()
    if not raw or raw.startswith('#'):
        return None
    # 尝试三种分隔符
    for sep in ['=', ':', ' ']:
        if sep in raw:
            parts = [p.strip() for p in raw.split(sep, 1)]
            if len(parts) == 2 and parts[0] and parts[1]:
                return parts[0], parts[1]
    # 不可解析
    return None

def main():
    if len(sys.argv) < 2:
        print("用法: python tools/import_api_keys_from_txt.py <txt路径> [描述]")
        sys.exit(2)

    txt_path = Path(sys.argv[1])
    description = sys.argv[2] if len(sys.argv) >= 3 else ""

    if not txt_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"TXT文件不存在: {txt_path}"
        }, ensure_ascii=False))
        sys.exit(3)

    manager = APIKeyManager()

    added = []
    skipped = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            parsed = parse_line(line)
            if not parsed:
                skipped.append({"line": idx, "content": line.strip()})
                continue
            provider, key = parsed
            try:
                manager.add_key(provider, key, description)
                added.append({"provider": provider})
            except Exception as e:
                skipped.append({"line": idx, "content": line.strip(), "error": str(e)})

    print(json.dumps({
        "success": True,
        "txt_path": str(txt_path),
        "added_count": len(added),
        "skipped_count": len(skipped),
        "added": added,
        "skipped": skipped,
        "config_file": str(manager.config_file)
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
