# @self-expose: {"id": "llm_client", "name": "Llm Client", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Llm Client功能"]}}
# LLM客户端模块

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

import os

class LLMConfig:
    """LLM配置类"""
    
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None):
        self.api_key = api_key or os.getenv('LLM_API_KEY')
        self.api_base = api_base or os.getenv('LLM_API_BASE', 'https://cloud.siliconflow.cn/v1')
        self.model = model or os.getenv('LLM_MODEL', 'deepseek-ai/DeepSeek-V3')
        self.max_tokens = 2000
        self.temperature = 0.3
        self.timeout = 30

class LLMClient:
    """LLM客户端"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.session = requests.Session()
        
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = self._make_request(
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            return False
    
    def slice_text_with_llm(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用LLM进行智能文本切片"""
        
        # 构建切片提示词
        prompt = self._build_slice_prompt(text, metadata)
        
        try:
            # 调用LLM API
            response = self._make_request(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            # 解析LLM响应
            return self._parse_slice_response(response, text, metadata)
            
        except Exception as e:
            logger.error(f"LLM切片失败: {e}")
            # 返回空列表，让备用方案接管
            return []
    
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int) -> Dict[str, Any]:
        """发送API请求"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.session.post(
            f"{self.config.api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=self.config.timeout
        )
        
        if response.status_code != 200:
            error_msg = f"API请求失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()
    
    def _build_slice_prompt(self, text: str, metadata: Dict[str, Any]) -> str:
        """构建切片提示词"""
        
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
        
        return prompt
    
    def _parse_slice_response(self, response: Dict[str, Any], original_text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析LLM切片响应"""
        
        try:
            # 提取LLM回复内容
            content = response['choices'][0]['message']['content']
            
            # 尝试解析JSON
            slices_data = json.loads(content)
            
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
            raise Exception(f"LLM响应格式错误: {e}")
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            raise

class MockLLMClient:
    """模拟LLM客户端（用于测试和备用）"""
    
    def __init__(self):
        self.available = True
    
    def test_connection(self) -> bool:
        """模拟连接测试"""
        return True
    
    def slice_text_with_llm(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """模拟LLM切片（使用规则方法）"""
        # 这里可以集成我们之前实现的规则切片方法
        # 暂时返回空列表，让备用方案接管
        return []

def create_llm_client(api_key: str = "", use_mock: bool = False) -> LLMClient:
    """创建LLM客户端"""
    
    if use_mock or not api_key:
        logger.info("使用模拟LLM客户端")
        return MockLLMClient()
    
    config = LLMConfig(
        api_key=api_key,
        model="gpt-3.5-turbo"  # 可以尝试不同的模型
    )
    
    client = LLMClient(config)
    
    # 测试连接
    if client.test_connection():
        logger.info("LLM客户端连接成功")
        return client
    else:
        logger.warning("LLM客户端连接失败，使用模拟客户端")
        return MockLLMClient()

def test_llm_client():
    """测试LLM客户端"""
    
    # 使用模拟客户端进行测试
    client = create_llm_client(use_mock=True)
    
    test_text = """
今天我们来讨论RAG系统的设计。RAG系统应该基于意识=认知=记忆=意义的循环等式。

首先，我们需要建立记忆系统化的基础框架。这个框架应该简单实用，避免过度设计。
"""
    
    metadata = {"source": "test"}
    
    try:
        slices = client.slice_text_with_llm(test_text, metadata)
        print(f"模拟切片结果: {len(slices)} 个切片")
    except Exception as e:
        print(f"切片测试失败: {e}")

if __name__ == "__main__":
    test_llm_client()