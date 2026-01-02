#!/usr/bin/env python3
# @self-expose: {"id": "write_qianwen_key", "name": "Write Qianwen Key", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Write Qianwen Key功能"]}}
# -*- coding: utf-8 -*-
"""
直接将千问API密钥写入配置文件
"""

import os
import json

# 配置文件路径
config_file = "e:\RAG系统\config\api_keys.json"

# 用户提供的千问密钥
qianwen_key = "sk-ca5cbb1572724063ae886b8012aa0541"

# 读取现有配置
config = {}
if os.path.exists(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"读取现有配置失败，将创建新配置: {e}")
        config = {}

# 添加千问密钥
config['qianwen'] = {
    "key": qianwen_key,
    "description": "用户提供的字节跳动千问API密钥",
    "added_time": "2025-12-03"
}

# 写入配置文件
try:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 千问API密钥已成功写入配置文件: {config_file}")
    print(f"当前配置的提供商: {list(config.keys())}")
    print("\n配置文件内容:")
    with open(config_file, 'r', encoding='utf-8') as f:
        print(f.read())
except Exception as e:
    print(f"❌ 写入配置文件失败: {e}")
