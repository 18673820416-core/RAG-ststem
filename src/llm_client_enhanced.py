# @self-expose: {"id": "llm_client_enhanced", "name": "Llm Client Enhanced", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Llm Client Enhanced功能"]}}
#!/usr/bin/env python3
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
    """增强版LLM客户端（支持多服务商自动回退）
    
    当前配置：千问（主）+ DEEPSEEK-V3.2（备）
    最新：DeepSeek-V3.2-Speciale (2025.12.01发布)
    - 推理能力：超越GPT-5，持平Gemini-3.0-Pro
    - 竞赛成绩：IMO金牌、IOI金牌
    - 开源协议：MIT（国产AI第一次全面超越国外闭源模型）
    
    架构支持：可扩展到任意LLM服务商（国内外不限）
    未来演化：根据技术趋势调整，不预设固定选型
    """
    
    def __init__(self, provider: str = None, enable_fallback: bool = True):
        self.provider = provider or LLM_CONFIG["default_provider"]
        self.timeout = LLM_CONFIG["timeout"]
        self.max_retries = LLM_CONFIG["max_retries"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]
        self.enable_fallback = enable_fallback
        
        # 获取API密钥
        self.api_key = api_key_manager.get_key(self.provider)
        if not self.api_key:
            # 如果启用回退，尝试使用其他可用服务商
            if self.enable_fallback:
                available = self.get_available_providers()
                if available:
                    self.provider = available[0]
                    self.api_key = api_key_manager.get_key(self.provider)
                    print(f"⚠️ 默认服务商 {provider or LLM_CONFIG['default_provider']} 未配置，切换到 {self.provider}")
                else:
                    raise ValueError(f"未找到任何可用的API密钥，请先使用api_key_tool.py添加")
            else:
                raise ValueError(f"未找到 {self.provider} 的API密钥，请先使用api_key_tool.py添加")
        
        # 设置API端点
        self.endpoint = API_ENDPOINTS.get(self.provider)
        if not self.endpoint:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """聊天补全接口（支持自动回退）"""
        
        # 合并配置参数
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        
        # 尝试使用当前provider
        result = self._try_provider(self.provider, messages, temperature, max_tokens)
        
        # 如果失败且启用回退，尝试其他服务商
        if result is None and self.enable_fallback:
            available_providers = self.get_available_providers()
            for fallback_provider in available_providers:
                if fallback_provider == self.provider:
                    continue  # 跳过当前provider
                
                print(f"⚠️ {self.provider} 调用失败，切换到 {fallback_provider}...")
                result = self._try_provider(fallback_provider, messages, temperature, max_tokens)
                
                if result is not None:
                    print(f"✅ {fallback_provider} 调用成功")
                    # 更新当前provider为成功的fallback
                    self.provider = fallback_provider
                    self.api_key = api_key_manager.get_key(fallback_provider)
                    self.endpoint = API_ENDPOINTS.get(fallback_provider)
                    break
        
        return result
    
    def _try_provider(self, provider: str, messages: List[Dict[str, str]], 
                      temperature: float, max_tokens: int) -> Optional[str]:
        """尝试使用指定provider调用LLM"""
        try:
            # 临时设置provider相关配置
            original_provider = self.provider
            original_key = self.api_key
            original_endpoint = self.endpoint
            
            self.provider = provider
            self.api_key = api_key_manager.get_key(provider)
            self.endpoint = API_ENDPOINTS.get(provider)
            
            if not self.api_key or not self.endpoint:
                return None
            
            # 根据提供商构建请求
            if provider == "deepseek":
                result = self._deepseek_chat(messages, temperature, max_tokens)
            elif provider == "openai":
                result = self._openai_chat(messages, temperature, max_tokens)
            elif provider == "anthropic":
                result = self._anthropic_chat(messages, temperature, max_tokens)
            elif provider == "google":
                result = self._google_chat(messages, temperature, max_tokens)
            elif provider == "qianwen":
                result = self._qianwen_chat(messages, temperature, max_tokens)
            else:
                result = None
            
            # 恢复原始配置（如果失败）
            if result is None:
                self.provider = original_provider
                self.api_key = original_key
                self.endpoint = original_endpoint
            
            return result
            
        except Exception as e:
            print(f"Provider {provider} 调用异常: {e}")
            return None
    
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
    
    def _qianwen_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """字节跳动千问聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "qwen-turbo",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        return self._make_request(headers, data)
    
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
                    error_text = response.text[:200] if len(response.text) > 200 else response.text
                    print(f"❌ {self.provider} API请求失败: {response.status_code} - {error_text}")
                    if attempt == self.max_retries - 1:
                        return None
                    time.sleep(1)  # 短暂等待后重试
                    
            except requests.exceptions.Timeout:
                print(f"⏱️ {self.provider} 请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(1)
                
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 {self.provider} 连接错误: {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {self.provider} 请求异常: {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(1)
        
        return None
    
    def get_available_providers(self) -> List[str]:
        """获取已配置API密钥的可用提供商"""
        available = []
        for provider in API_ENDPOINTS.keys():
            if api_key_manager.get_key(provider):
                available.append(provider)
        return available
    
    def slice_text_with_llm(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用LLM进行智能文本切片"""
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        # 构建切片提示词
        source_info = metadata.get('source', '未知来源')
        
        prompt = f"""请对以下文本进行智能语义切片，确保每个切片语义完整且大小适中：

文本来源：{source_info}
文本内容：
{text}

请按以下要求进行切片：
1. 保持语义完整性，不要在句子中间切断
2. 每个切片大小建议在100-2000字符之间
3. 识别话题转换点作为切片的边界
4. 对于对话文本，按对话轮次进行切片
5. 输出格式为JSON列表，每个元素包含：
   - content: 切片内容
   - boundary_reason: 边界划分理由
   - quality_score: 切片质量评分(0-1)

请输出JSON格式的切片结果："""
        
        try:
            # 调用LLM API
            response = self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            # 解析LLM响应
            slices_data = json.loads(response)
            
            slices = []
            for i, slice_info in enumerate(slices_data):
                slice_content = slice_info.get('content', '').strip()
                if not slice_content:
                    continue
                    
                slices.append({
                    "content": slice_content,
                    "slice_id": f"llm_slice_{i}",
                    "slice_size": len(slice_content),
                    "semantic_quality": slice_info.get('quality_score', 0.5),
                    "metadata": metadata.copy(),
                    "slice_method": "llm",
                    "boundary_reason": slice_info.get('boundary_reason', 'LLM智能划分')
                })
            
            logger.info(f"LLM切片成功，生成 {len(slices)} 个切片")
            return slices
            
        except json.JSONDecodeError as e:
            logger.error(f"解析LLM响应JSON失败: {e}")
            return []
        except Exception as e:
            logger.error(f"LLM切片失败: {e}")
            return []

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