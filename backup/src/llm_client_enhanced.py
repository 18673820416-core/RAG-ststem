#!/usr/bin/env python3
# @self-expose: {"id": "llm_client_enhanced", "name": "Llm Client Enhanced", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Llm Client Enhanced功能"]}}
# -*- coding: utf-8 -*-
"""
增强版LLM客户端
集成API密钥管理功能，支持多种LLM提供商
来源：用户对话中提到的API密钥保存需求，用于未来聊天机器人调用LLM
"""

import json
import requests
import time
from typing import List, Dict, Optional, Any
from pathlib import Path

# 导入配置
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.system_config import api_key_manager, API_ENDPOINTS, LLM_CONFIG

class LLMClientEnhanced:
    """增强版LLM客户端"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or LLM_CONFIG["default_provider"]
        self.timeout = LLM_CONFIG["timeout"]
        self.max_retries = LLM_CONFIG["max_retries"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]
        
        # 获取API密钥
        self.api_key = api_key_manager.get_key(self.provider)
        if not self.api_key:
            raise ValueError(f"未找到 {self.provider} 的API密钥，请先使用api_key_tool.py添加")
        
        # 设置API端点
        self.endpoint = API_ENDPOINTS.get(self.provider)
        if not self.endpoint:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """聊天补全接口"""
        
        # 合并配置参数
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        
        # 根据提供商构建请求
        if self.provider == "deepseek":
            return self._deepseek_chat(messages, temperature, max_tokens)
        elif self.provider == "openai":
            return self._openai_chat(messages, temperature, max_tokens)
        elif self.provider == "anthropic":
            return self._anthropic_chat(messages, temperature, max_tokens)
        elif self.provider == "google":
            return self._google_chat(messages, temperature, max_tokens)
        else:
            raise ValueError(f"暂不支持的LLM提供商: {self.provider}")
    
    def _deepseek_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """DeepSeek聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        return self._make_request(headers, data)
    
    def _openai_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """OpenAI聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        return self._make_request(headers, data)
    
    def _anthropic_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """Anthropic Claude聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # 转换消息格式为Claude格式
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_message:
            data["system"] = system_message
        
        return self._make_request(headers, data, response_key="content")
    
    def _google_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """Google AI聊天接口"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # 构建Google AI格式
        contents = []
        for msg in messages:
            if msg["role"] == "user":
                contents.append({
                    "parts": [{"text": msg["content"]}],
                    "role": "user"
                })
            elif msg["role"] == "assistant":
                contents.append({
                    "parts": [{"text": msg["content"]}],
                    "role": "model"
                })
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        # Google AI使用API密钥作为查询参数
        endpoint = f"{self.endpoint}?key={self.api_key}"
        return self._make_request(headers, data, endpoint=endpoint, response_key="candidates")
    
    def _make_request(self, headers: Dict[str, str], data: Dict[str, Any], 
                     endpoint: str = None, response_key: str = "choices") -> Optional[str]:
        """发送HTTP请求"""
        
        url = endpoint or self.endpoint
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 根据不同提供商的响应格式提取文本
                    if self.provider == "anthropic":
                        return result.get("content", [{}])[0].get("text", "")
                    elif self.provider == "google":
                        candidates = result.get(response_key, [])
                        if candidates:
                            return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return ""
                    else:
                        choices = result.get(response_key, [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
                        return ""
                
                elif response.status_code == 429:  # 限流
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"请求被限流，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    print(f"API请求失败: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    return None
                
            except Exception as e:
                print(f"请求异常: {e}")
                return None
        
        return None
    
    def get_available_providers(self) -> List[str]:
        """获取已配置API密钥的可用提供商"""
        available = []
        for provider in API_ENDPOINTS.keys():
            if api_key_manager.get_key(provider):
                available.append(provider)
        return available

def test_llm_client():
    """测试LLM客户端"""
    try:
        # 获取可用的提供商
        available_providers = []
        for provider in API_ENDPOINTS.keys():
            if api_key_manager.get_key(provider):
                available_providers.append(provider)
        
        if not available_providers:
            print("⚠️ 未找到任何可用的API密钥")
            print("请先使用 tools/api_key_tool.py 添加API密钥")
            return
        
        print("可用的LLM提供商:")
        for provider in available_providers:
            print(f"  - {provider}")
        
        # 使用第一个可用的提供商进行测试
        provider = available_providers[0]
        print(f"\n使用 {provider} 进行测试...")
        
        client = LLMClientEnhanced(provider)
        
        messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]
        
        response = client.chat_completion(messages)
        if response:
            print(f"✅ 测试成功！响应: {response}")
        else:
            print("❌ 测试失败")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_llm_client()