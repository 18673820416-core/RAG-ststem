#!/usr/bin/env python3
# @self-expose: {"id": "add_qianwen_key", "name": "Add Qianwen Key", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Add Qianwen Key功能"]}}
# -*- coding: utf-8 -*-
"""
添加千问API密钥到系统配置
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.api_keys import api_key_manager

def add_qianwen_key():
    """添加千问API密钥"""
    # 用户提供的千问密钥
    qianwen_key = "sk-ca5cbb1572724063ae886b8012aa0541"
    
    print("正在添加千问API密钥...")
    
    try:
        # 添加密钥到配置
        api_key_manager.add_key(
            provider="qianwen",
            api_key=qianwen_key,
            description="用户提供的字节跳动千问API密钥"
        )
        
        # 验证密钥是否添加成功
        if api_key_manager.get_key("qianwen"):
            print("✅ 千问API密钥添加成功！")
            print("密钥已保存到配置文件中")
            
            # 列出所有可用密钥
            print("\n当前可用的LLM提供商:")
            for provider, description in api_key_manager.list_keys().items():
                print(f"  - {provider}: {description}")
            return True
        else:
            print("❌ 千问API密钥添加失败！")
            return False
    except Exception as e:
        print(f"❌ 出错了: {e}")
        return False

if __name__ == "__main__":
    add_qianwen_key()
