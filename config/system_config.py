# @self-expose: {"id": "system_config", "name": "System Config", "type": "component", "version": "1.1.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["System Config功能", "User Preferences"]}}
# RAG系统配置文件

import os
import json
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = BASE_DIR / "docs"

# 数据库配置
DATABASE_PATH = DATA_DIR / "rag_memory.db"

# Embedding配置
EMBEDDING_CONFIG = {
    # 默认使用的embedding provider（开发环境：local；生产可切到qianwen）
    "default_provider": "local",  # 可选: "local", "qianwen", "openai"

    # 本地模型配置（开发环境推荐）
    "local": {
        "model_name": "all-MiniLM-L6-v2",
        "dimension": 384,
        "cache_dir": str(DATA_DIR / "model_cache")
    },

    # 千问API配置（生产环境推荐）
    "qianwen": {
        "model_name": "text-embedding-v3",
        "dimension": 1024,
        "api_key_env": "QWEN_API_KEY",  # 从环境变量或api_keys.json读取
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "batch_size": 25,
        "max_retries": 3,
        "timeout": 30
    },

    # OpenAI配置（可选）
    "openai": {
        "model_name": "text-embedding-3-small",
        "dimension": 1536,
        "api_key_env": "OPENAI_API_KEY"
    },

    # 故障转移顺序
    "fallback_order": ["qianwen", "local"]
}

# 向量维度（根据provider自动调整）
VECTOR_DIMENSION = EMBEDDING_CONFIG[EMBEDDING_CONFIG["default_provider"]]["dimension"]

# 文本嵌入模型配置（保留旧字段以兼容历史代码，不再直接使用）
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 轻量级模型
MODEL_CACHE_DIR = DATA_DIR / "model_cache"

# 用户偏好（从data/user_preferences.json加载，默认中文深度思考）
USER_PREFERENCES_DEFAULT = {
    "language": {
        "deep_thinking": "zh",
        "explanation": "zh",
        "code_identifiers": "en",
        "switch_on_request": True
    }
}

def _deep_merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        r = dict(a or {})
        for k, v in b.items():
            r[k] = _deep_merge((a or {}).get(k), v) if (a or {}).get(k) is not None else v
        return r
    return b if b is not None else a

def load_user_preferences():
    try:
        pref_path = DATA_DIR / "user_preferences.json"
        if pref_path.exists():
            with open(pref_path, 'r', encoding='utf-8') as f:
                user_prefs = json.load(f) or {}
            return _deep_merge(USER_PREFERENCES_DEFAULT, user_prefs)
    except Exception:
        pass
    return USER_PREFERENCES_DEFAULT

USER_PREFERENCES = load_user_preferences()

# 交互日志配置（本地持久化）
LOG_INTERACTIONS = True
INTERACTION_LOG_DIR = DATA_DIR / "interactions"
INTERACTION_RETENTION_DAYS = 30

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
            "E:\\rag系统\\docs",  # 添加当前项目的docs文件夹
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
    "default_provider": "qianwen",  # 切换到千问作为默认提供商
    "timeout": 60,  # 请求超时时间（秒），增加到60秒
    "max_retries": 5,  # 最大重试次数，增加到5次
    "temperature": 0.7,  # 温度参数
    "max_tokens": 8192,  # DeepSeek API支持的最大token数
}

# 确保目录存在
for directory in [DATA_DIR, SRC_DIR, DOCS_DIR, MODEL_CACHE_DIR, INTERACTION_LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)