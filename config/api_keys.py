# @self-expose: {"id": "api_keys", "name": "Api Keys", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Api Keys功能"]}}
# API密钥管理配置
# 来源：用户对话中提到的API密钥保存需求，用于未来聊天机器人调用LLM

import os
from pathlib import Path
from typing import Dict, Optional

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self, config_file: str = "api_keys.json"):
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / "config" / config_file
        self.keys: Dict[str, str] = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """从配置文件加载API密钥"""
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.keys = json.load(f)
            except Exception as e:
                print(f"加载API密钥配置失败: {e}")
                self.keys = {}
    
    def save_keys(self) -> None:
        """保存API密钥到配置文件"""
        import json
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, ensure_ascii=False, indent=2)
            print(f"API密钥已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存API密钥失败: {e}")
    
    def add_key(self, provider: str, api_key: str, description: str = "") -> None:
        """添加API密钥"""
        key_info = {
            "key": api_key,
            "description": description,
            "added_time": str(os.path.getctime(self.config_file) if self.config_file.exists() else "")
        }
        self.keys[provider] = key_info
        self.save_keys()
    
    def get_key(self, provider: str) -> Optional[str]:
        """获取指定提供商的API密钥"""
        if provider in self.keys:
            return self.keys[provider].get("key")
        return None
    
    def list_keys(self) -> Dict[str, str]:
        """列出所有可用的API密钥（仅显示提供商名称）"""
        return {provider: info.get("description", "") for provider, info in self.keys.items()}
    
    def remove_key(self, provider: str) -> bool:
        """移除指定提供商的API密钥"""
        if provider in self.keys:
            del self.keys[provider]
            self.save_keys()
            return True
        return False

# 全局API密钥管理器实例
api_key_manager = APIKeyManager()

# 支持的LLM提供商
SUPPORTED_PROVIDERS = {
    "deepseek": "DeepSeek AI",
    "openai": "OpenAI",
    "anthropic": "Anthropic Claude",
    "google": "Google AI",
    "azure": "Azure OpenAI",
    "siliconflow": "硅基流动",
    "zhipu": "智谱AI",
    "baidu": "百度文心一言",
    "qianwen": "字节跳动千问"
}

# 默认API端点配置
API_ENDPOINTS = {
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "google": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
    "qianwen": "https://api.volcengine.com/v3/chat/completions"
}