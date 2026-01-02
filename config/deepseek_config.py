#!/usr/bin/env python3
# @self-expose: {"id": "deepseek_config", "name": "Deepseek Config", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Deepseek Config功能"]}}
# -*- coding: utf-8 -*-
"""
DEEPSEEK API配置工具
用于配置和管理DEEPSEEK API密钥

开发提示词来源：用户建议使用已上传的DEEPSEEK API密钥
"""

import os
import json
from typing import Optional
from .api_keys import api_key_manager

class DeepSeekConfig:
    """DEEPSEEK API配置管理器"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.max_tokens = 128000  # 充分利用DeepSeek的128K上下文能力
        self.temperature = 0.3
        
    def setup_api_key(self, api_key: str) -> bool:
        """设置DEEPSEEK API密钥"""
        if not api_key or len(api_key) < 20:
            print("❌ API密钥格式不正确")
            return False
            
        try:
            # 保存到API密钥管理器
            api_key_manager.save_key("deepseek", api_key)
            self.api_key = api_key
            
            print("✅ DEEPSEEK API密钥配置成功")
            print(f"   模型: {self.model}")
            print(f"   端点: {self.base_url}")
            
            # 测试连接
            if self.test_connection():
                print("✅ API连接测试成功")
                return True
            else:
                print("⚠️ API连接测试失败，但密钥已保存")
                return True
                
        except Exception as e:
            print(f"❌ API密钥配置失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试API连接"""
        if not self.api_key:
            print("❌ 未配置API密钥")
            return False
            
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "测试连接"}],
                "max_tokens": 10
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ API响应异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def get_config(self) -> dict:
        """获取完整配置"""
        return {
            "api_key": self.api_key[:10] + "..." if self.api_key else None,
            "base_url": self.base_url,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
    
    def load_saved_key(self) -> bool:
        """加载已保存的API密钥"""
        try:
            saved_key = api_key_manager.get_key("deepseek")
            if saved_key:
                self.api_key = saved_key
                print("✅ 已加载保存的DEEPSEEK API密钥")
                return True
            else:
                print("⚠️ 未找到保存的DEEPSEEK API密钥")
                return False
        except Exception as e:
            print(f"❌ 加载API密钥失败: {e}")
            return False

def setup_deepseek_api():
    """交互式设置DEEPSEEK API"""
    print("=== DEEPSEEK API配置向导 ===")
    
    config = DeepSeekConfig()
    
    # 尝试加载已保存的密钥
    if config.load_saved_key():
        print(f"\n📋 当前配置:")
        current_config = config.get_config()
        for key, value in current_config.items():
            print(f"   {key}: {value}")
        
        choice = input("\n是否重新配置API密钥？(y/N): ").strip().lower()
        if choice != 'y':
            print("✅ 使用现有配置")
            return config
    
    # 输入新密钥
    print("\n🔑 请输入DEEPSEEK API密钥:")
    print("   密钥格式: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    api_key = input("API密钥: ").strip()
    
    if config.setup_api_key(api_key):
        print("\n🎉 DEEPSEEK API配置完成!")
        return config
    else:
        print("\n❌ 配置失败，请检查密钥格式")
        return None

if __name__ == "__main__":
    setup_deepseek_api()