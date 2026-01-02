# @self-expose: {"id": "system_config", "name": "System Config", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["System Config功能"]}}
# RAG系统配置文件

import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = BASE_DIR / "docs"

# 数据库配置
DATABASE_PATH = DATA_DIR / "rag_memory.db"
VECTOR_DIMENSION = 1024  # 向量维度

# 文本嵌入模型配置
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 轻量级模型
MODEL_CACHE_DIR = DATA_DIR / "model_cache"

# 数据源配置
DATA_SOURCES = {
    "browser_cache": {
        "enabled": True,
        "paths": [
            # 浏览器缓存路径（需要根据实际浏览器配置）
            "C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome",
            "C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge",
        ]
    },
    "ide_logs": {
        "enabled": True,
        "paths": [
            # IDE日志路径
            "E:\\AI\\qiusuo-framework\\logs",
            "E:\\灵境\\VCPChat\\logs",
        ]
    },
    "conversation_history": {
        "enabled": True,
        "paths": [
            # 对话历史文件
            "E:\\AI\\docs",
            "E:\\灵境\\docs",
        ]
    }
}

# 检索配置
RETRIEVAL_CONFIG = {
    "top_k": 10,  # 返回结果数量
    "similarity_threshold": 0.7,  # 相似度阈值
    "cache_size": 1000,  # 缓存大小
}

# API密钥配置
from .api_keys import api_key_manager, SUPPORTED_PROVIDERS, API_ENDPOINTS

# LLM配置
LLM_CONFIG = {
    "default_provider": "deepseek",
    "timeout": 30,  # 请求超时时间（秒）
    "max_retries": 3,  # 最大重试次数
    "temperature": 0.7,  # 温度参数
    "max_tokens": 2048,  # 最大输出token数
}

# 确保目录存在
for directory in [DATA_DIR, SRC_DIR, DOCS_DIR, MODEL_CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)