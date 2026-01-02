# 千问Embedding模型集成方案

> 📅 2025-12-04
> 🎯 目标：集成千问Embedding模型，支持多模型切换

---

## 一、千问Embedding模型介绍

### 可选模型对比

| 模型 | 维度 | 大小 | 性能 | 适用场景 |
|-----|------|------|------|---------|
| **text-embedding-v3** | 1024 | API调用 | ⭐⭐⭐⭐⭐ | 生产环境（推荐）|
| **text-embedding-v2** | 1536 | API调用 | ⭐⭐⭐⭐ | 高精度检索 |
| **bge-large-zh-v1.5** | 1024 | 1.3GB | ⭐⭐⭐⭐ | 本地部署（中文） |
| **all-MiniLM-L6-v2** | 384 | 90MB | ⭐⭐⭐ | 轻量级（当前） |

### 千问API Embedding优势
1. ✅ **高性能** - MTEB中文排行榜Top 3
2. ✅ **大维度** - 1024/1536维，语义表达更丰富
3. ✅ **免费额度** - 每月100万tokens免费
4. ✅ **低延迟** - 国内服务，响应快
5. ✅ **批量支持** - 单次最多25个文本

---

## 二、集成方案设计

### 方案1：多模型支持（推荐）

支持本地模型 + 千问API，根据场景自动切换：
- **本地模型** (all-MiniLM-L6-v2): 开发/测试，快速启动
- **千问API** (text-embedding-v3): 生产环境，高精度检索

### 方案2：纯千问API

完全使用千问API，简化本地依赖，但需要网络连接。

---

## 三、代码实现

### 3.1 配置文件更新

**文件**: `config/system_config.py`

```python
# Embedding模型配置
EMBEDDING_CONFIG = {
    # 默认使用的embedding provider
    "default_provider": "qianwen",  # 可选: "local", "qianwen", "openai"
    
    # 本地模型配置
    "local": {
        "model_name": "all-MiniLM-L6-v2",
        "dimension": 384,
        "cache_dir": "data/model_cache"
    },
    
    # 千问API配置
    "qianwen": {
        "model_name": "text-embedding-v3",
        "dimension": 1024,
        "api_key_env": "QWEN_API_KEY",  # 从环境变量或api_keys.json读取
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "batch_size": 25,  # 单次最多25个文本
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
```

### 3.2 Embedding服务封装

**文件**: `src/embedding_service.py` (新建)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @self-expose: {"id": "embedding_service", "name": "Embedding服务", "type": "service", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["文本向量化", "多模型支持", "批量编码", "故障转移"], "methods": ["encode", "encode_batch"]}}
"""
Embedding服务 - 支持本地模型和千问API
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """统一的Embedding服务，支持多provider"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化Embedding服务
        
        Args:
            config: 配置字典，如果为None则从system_config加载
        """
        if config is None:
            from config.system_config import EMBEDDING_CONFIG
            config = EMBEDDING_CONFIG
        
        self.config = config
        self.default_provider = config.get("default_provider", "local")
        self.fallback_order = config.get("fallback_order", [self.default_provider])
        
        # 懒加载：延迟初始化各个provider
        self._providers = {}
        self._initialized_providers = set()
        
        logger.info(f"Embedding服务初始化，默认provider: {self.default_provider}")
    
    def _get_provider(self, provider_name: str):
        """获取或初始化指定的provider"""
        if provider_name in self._initialized_providers:
            return self._providers[provider_name]
        
        # 初始化provider
        if provider_name == "local":
            provider = self._init_local_provider()
        elif provider_name == "qianwen":
            provider = self._init_qianwen_provider()
        elif provider_name == "openai":
            provider = self._init_openai_provider()
        else:
            raise ValueError(f"未知的provider: {provider_name}")
        
        if provider:
            self._providers[provider_name] = provider
            self._initialized_providers.add(provider_name)
            logger.info(f"✅ {provider_name} provider 初始化成功")
        
        return provider
    
    def _init_local_provider(self):
        """初始化本地sentence-transformers模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            config = self.config["local"]
            model_name = config["model_name"]
            cache_dir = Path(config["cache_dir"])
            
            # 检查本地缓存
            local_model_dir = cache_dir / model_name
            if local_model_dir.exists():
                model = SentenceTransformer(str(local_model_dir))
                logger.info(f"✅ 加载本地模型: {local_model_dir}")
            else:
                # 首次下载（会比较慢）
                logger.warning(f"本地模型不存在，将从HuggingFace下载: {model_name}")
                model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
            
            return {
                "model": model,
                "dimension": config["dimension"],
                "type": "local"
            }
        except Exception as e:
            logger.error(f"本地模型初始化失败: {e}")
            return None
    
    def _init_qianwen_provider(self):
        """初始化千问API"""
        try:
            import requests
            
            config = self.config["qianwen"]
            
            # 获取API Key
            api_key = self._get_api_key(config["api_key_env"])
            if not api_key:
                logger.error("千问API密钥未配置")
                return None
            
            return {
                "api_key": api_key,
                "base_url": config["base_url"],
                "model_name": config["model_name"],
                "dimension": config["dimension"],
                "batch_size": config.get("batch_size", 25),
                "max_retries": config.get("max_retries", 3),
                "timeout": config.get("timeout", 30),
                "type": "qianwen"
            }
        except Exception as e:
            logger.error(f"千问API初始化失败: {e}")
            return None
    
    def _init_openai_provider(self):
        """初始化OpenAI API（可选）"""
        try:
            import openai
            
            config = self.config["openai"]
            api_key = self._get_api_key(config["api_key_env"])
            
            if not api_key:
                logger.error("OpenAI API密钥未配置")
                return None
            
            return {
                "api_key": api_key,
                "model_name": config["model_name"],
                "dimension": config["dimension"],
                "type": "openai"
            }
        except Exception as e:
            logger.error(f"OpenAI API初始化失败: {e}")
            return None
    
    def _get_api_key(self, env_var_name: str) -> Optional[str]:
        """从环境变量或api_keys.json获取API密钥"""
        # 1. 优先从环境变量读取
        api_key = os.getenv(env_var_name)
        if api_key:
            return api_key
        
        # 2. 从api_keys.json读取
        try:
            api_keys_file = Path("config/api_keys.json")
            if api_keys_file.exists():
                with open(api_keys_file, 'r', encoding='utf-8') as f:
                    api_keys = json.load(f)
                    
                # 千问API密钥可能存储在qwen或dashscope字段
                if env_var_name == "QWEN_API_KEY":
                    return api_keys.get("qwen", {}).get("api_key") or \
                           api_keys.get("dashscope", {}).get("api_key")
                elif env_var_name == "OPENAI_API_KEY":
                    return api_keys.get("openai", {}).get("api_key")
        except Exception as e:
            logger.error(f"读取API密钥失败: {e}")
        
        return None
    
    def encode(self, text: str, provider: Optional[str] = None) -> Optional[List[float]]:
        """
        将单个文本编码为向量
        
        Args:
            text: 待编码文本
            provider: 指定provider，None则使用默认provider
            
        Returns:
            向量列表，失败返回None
        """
        if not text or not text.strip():
            logger.warning("空文本，返回零向量")
            dimension = self.config[self.default_provider]["dimension"]
            return [0.0] * dimension
        
        # 确定使用的provider
        providers_to_try = [provider] if provider else self.fallback_order
        
        # 尝试各个provider
        for prov in providers_to_try:
            try:
                provider_obj = self._get_provider(prov)
                if not provider_obj:
                    continue
                
                # 根据provider类型调用不同的编码方法
                if provider_obj["type"] == "local":
                    vector = self._encode_local(text, provider_obj)
                elif provider_obj["type"] == "qianwen":
                    vector = self._encode_qianwen(text, provider_obj)
                elif provider_obj["type"] == "openai":
                    vector = self._encode_openai(text, provider_obj)
                else:
                    continue
                
                if vector:
                    logger.debug(f"✅ 使用 {prov} 编码成功，维度: {len(vector)}")
                    return vector
                    
            except Exception as e:
                logger.error(f"{prov} 编码失败: {e}")
                continue
        
        # 所有provider都失败，返回零向量
        logger.error("所有embedding provider失败，返回零向量")
        dimension = self.config[self.default_provider]["dimension"]
        return [0.0] * dimension
    
    def encode_batch(self, texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
        """
        批量编码文本
        
        Args:
            texts: 文本列表
            provider: 指定provider
            
        Returns:
            向量列表的列表
        """
        if not texts:
            return []
        
        # 确定使用的provider
        prov = provider or self.default_provider
        provider_obj = self._get_provider(prov)
        
        if not provider_obj:
            logger.error(f"Provider {prov} 不可用，逐个编码")
            return [self.encode(text, provider) for text in texts]
        
        # 批量编码
        try:
            if provider_obj["type"] == "local":
                return self._encode_batch_local(texts, provider_obj)
            elif provider_obj["type"] == "qianwen":
                return self._encode_batch_qianwen(texts, provider_obj)
            elif provider_obj["type"] == "openai":
                return self._encode_batch_openai(texts, provider_obj)
        except Exception as e:
            logger.error(f"批量编码失败: {e}，降级到逐个编码")
            return [self.encode(text, provider) for text in texts]
    
    # ========== 本地模型编码 ==========
    
    def _encode_local(self, text: str, provider: Dict) -> List[float]:
        """使用本地sentence-transformers模型编码"""
        model = provider["model"]
        vector = model.encode(text, convert_to_numpy=True)
        return vector.tolist()
    
    def _encode_batch_local(self, texts: List[str], provider: Dict) -> List[List[float]]:
        """本地模型批量编码"""
        model = provider["model"]
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [vec.tolist() for vec in vectors]
    
    # ========== 千问API编码 ==========
    
    def _encode_qianwen(self, text: str, provider: Dict) -> List[float]:
        """使用千问API编码单个文本"""
        import requests
        
        url = f"{provider['base_url']}/embeddings"
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider["model_name"],
            "input": text
        }
        
        for attempt in range(provider["max_retries"]):
            try:
                response = requests.post(
                    url, 
                    json=payload, 
                    headers=headers,
                    timeout=provider["timeout"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    vector = result["data"][0]["embedding"]
                    return vector
                else:
                    logger.error(f"千问API返回错误: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"千问API调用失败 (尝试 {attempt+1}/{provider['max_retries']}): {e}")
                time.sleep(1)  # 重试前等待1秒
        
        return None
    
    def _encode_batch_qianwen(self, texts: List[str], provider: Dict) -> List[List[float]]:
        """千问API批量编码（支持最多25个文本）"""
        import requests
        
        batch_size = provider["batch_size"]
        all_vectors = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            url = f"{provider['base_url']}/embeddings"
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider["model_name"],
                "input": batch
            }
            
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=provider["timeout"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    vectors = [item["embedding"] for item in result["data"]]
                    all_vectors.extend(vectors)
                else:
                    logger.error(f"千问批量API错误: {response.text}")
                    # 降级到逐个编码
                    for text in batch:
                        vec = self._encode_qianwen(text, provider)
                        all_vectors.append(vec or [0.0] * provider["dimension"])
            except Exception as e:
                logger.error(f"千问批量API失败: {e}")
                for text in batch:
                    vec = self._encode_qianwen(text, provider)
                    all_vectors.append(vec or [0.0] * provider["dimension"])
        
        return all_vectors
    
    # ========== OpenAI API编码（可选） ==========
    
    def _encode_openai(self, text: str, provider: Dict) -> List[float]:
        """使用OpenAI API编码"""
        import openai
        
        openai.api_key = provider["api_key"]
        
        try:
            response = openai.embeddings.create(
                model=provider["model_name"],
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI API失败: {e}")
            return None
    
    def _encode_batch_openai(self, texts: List[str], provider: Dict) -> List[List[float]]:
        """OpenAI批量编码"""
        import openai
        
        openai.api_key = provider["api_key"]
        
        try:
            response = openai.embeddings.create(
                model=provider["model_name"],
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI批量API失败: {e}")
            return [self._encode_openai(text, provider) for text in texts]
    
    # ========== 工具方法 ==========
    
    def get_dimension(self, provider: Optional[str] = None) -> int:
        """获取向量维度"""
        prov = provider or self.default_provider
        return self.config[prov]["dimension"]
    
    def get_available_providers(self) -> List[str]:
        """获取可用的provider列表"""
        available = []
        for prov_name in self.config.keys():
            if prov_name in ["default_provider", "fallback_order"]:
                continue
            try:
                provider = self._get_provider(prov_name)
                if provider:
                    available.append(prov_name)
            except:
                pass
        return available

# ========== 全局单例 ==========

_embedding_service_instance = None

def get_embedding_service() -> EmbeddingService:
    """获取全局Embedding服务单例"""
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance

# ========== 测试代码 ==========

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试
    service = get_embedding_service()
    
    # 1. 单文本编码
    text = "RAG系统是一种基于检索增强的生成模型"
    vector = service.encode(text)
    print(f"✅ 单文本编码: 维度={len(vector)}, 前5维={vector[:5]}")
    
    # 2. 批量编码
    texts = [
        "向量数据库用于存储和检索向量",
        "千问Embedding模型性能优秀",
        "sentence-transformers是本地embedding方案"
    ]
    vectors = service.encode_batch(texts)
    print(f"✅ 批量编码: 数量={len(vectors)}, 维度={len(vectors[0])}")
    
    # 3. 查看可用providers
    providers = service.get_available_providers()
    print(f"✅ 可用providers: {providers}")
```

### 3.3 向量数据库集成

**修改文件**: `src/vector_database.py`

```python
# 在文件开头导入Embedding服务
from src.embedding_service import get_embedding_service

class VectorDatabase:
    """基于SQLite的向量数据库"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_manager = get_database_manager()
        
        # 使用统一的Embedding服务（替换原来的本地模型）
        self.embedding_service = get_embedding_service()
        
        self._initialize_database()
    
    def _generate_query_vector(self, query: str) -> List[float]:
        """
        生成查询文本的向量表示
        使用统一的Embedding服务，支持多provider
        """
        if not query:
            dimension = self.embedding_service.get_dimension()
            return [0.0] * dimension
        
        try:
            # 使用Embedding服务编码（自动处理故障转移）
            vector = self.embedding_service.encode(query)
            return vector
        except Exception as e:
            logger.error(f"生成查询向量失败: {e}")
            dimension = self.embedding_service.get_dimension()
            return [0.0] * dimension
```

### 3.4 API配置文件示例

**文件**: `config/api_keys.json` (更新)

```json
{
  "deepseek": {
    "api_key": "sk-xxxxx",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "priority": 1
  },
  "qwen": {
    "api_key": "sk-xxxxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo",
    "priority": 2,
    "embedding_api_key": "sk-xxxxx",
    "embedding_model": "text-embedding-v3"
  }
}
```

---

## 五、环境切换与操作流程

### 5.1 开发/生产环境切换规则
- **开发环境**：`config/system_config.py` 中 `EMBEDDING_CONFIG["default_provider"] = "local"`
  - 使用本地 `all-MiniLM-L6-v2`，维度 384，适合快速迭代与离线调试。
- **生产环境**：`config/system_config.py` 中 `EMBEDDING_CONFIG["default_provider"] = "qianwen"`
  - 使用千问 `text-embedding-v3`，维度 1024，精度更高。
- 故障转移顺序：`EMBEDDING_CONFIG["fallback_order"] = ["qianwen", "local"]`，当千问不可用时自动降级到本地模型。

### 5.2 切换后的向量库重建
- 配置切换或维度变更后，为避免“旧维度向量”影响检索，应重建向量库：
  1. 确保 `config/api_keys.json` 中已配置 `qianwen.api_key` / `embedding_api_key`；
  2. 在项目根目录执行：
     ```bash
     python rebuild_embeddings.py
     ```
  3. 当前数据库数据量较小时，可安全全量重建。

> 说明：`rebuild_embeddings.py` 的存在仅作为示例与工具入口，后续可根据需要扩展为真正逐条重算并更新向量的迁移脚本。

## 六、成本与性能对比

### 示例1：默认使用千问Embedding

```python
from src.embedding_service import get_embedding_service

# 获取服务（默认使用千问）
service = get_embedding_service()

# 编码文本
text = "基于检索增强的生成模型"
vector = service.encode(text)
print(f"向量维度: {len(vector)}")  # 输出: 1024
```

### 示例2：手动切换provider

```python
# 使用本地模型
vector_local = service.encode("测试文本", provider="local")
print(f"本地模型维度: {len(vector_local)}")  # 输出: 384

# 使用千问API
vector_qw = service.encode("测试文本", provider="qianwen")
print(f"千问API维度: {len(vector_qw)}")  # 输出: 1024
```

### 示例3：批量编码

```python
texts = ["文本1", "文本2", "文本3"]
vectors = service.encode_batch(texts)
print(f"批量编码: {len(vectors)}个向量")
```

---

## 五、迁移步骤

### 步骤1：更新配置

1. 编辑 `config/system_config.py`，添加 `EMBEDDING_CONFIG`
2. 在 `config/api_keys.json` 中添加千问API密钥

### 步骤2：创建Embedding服务

1. 创建 `src/embedding_service.py`
2. 测试服务可用性: `python src/embedding_service.py`

### 步骤3：更新向量数据库

1. 修改 `src/vector_database.py`，集成Embedding服务
2. 注意：**向量维度变化**（384 → 1024），需要重建向量库或保持兼容

### 步骤4：数据迁移（可选）

如果要从384维迁移到1024维：

```python
# 迁移脚本
from src.vector_database import VectorDatabase
from src.embedding_service import get_embedding_service

db = VectorDatabase()
service = get_embedding_service()

# 获取所有记忆
memories = db.get_all_memories()

for memory in memories:
    content = memory['content']
    # 重新编码（使用千问API）
    new_vector = service.encode(content, provider="qianwen")
    # 更新数据库
    db.update_memory_vector(memory['id'], new_vector)
```

---

## 六、成本与性能对比

### 成本分析

| 方案 | 初始成本 | 运行成本 | 备注 |
|-----|---------|---------|------|
| 本地模型 | 90MB下载 | 0元 | 一次性下载 |
| 千问API | 0元 | 0.0007元/1K tokens | 免费额度100万tokens/月 |

**示例计算**:
- 1000条记忆，每条平均200字符 = 200K tokens
- 使用千问API编码成本 = 200 × 0.0007 = 0.14元
- 月编码10万条记忆 = 14元（远低于免费额度）

### 性能对比

| 指标 | 本地模型 | 千问API |
|-----|---------|---------|
| 编码速度 | ~100条/秒 | ~50条/秒（批量） |
| 检索精度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 启动时间 | 3-5秒（模型加载） | 即时 |
| 离线可用 | ✅ | ❌ |

---

## 七、推荐配置

### 开发环境
```python
EMBEDDING_CONFIG = {
    "default_provider": "local",  # 本地模型，快速启动
    "fallback_order": ["local"]
}
```

### 生产环境
```python
EMBEDDING_CONFIG = {
    "default_provider": "qianwen",  # 千问API，高精度
    "fallback_order": ["qianwen", "local"]  # 故障转移到本地
}
```

---

## 八、总结

### ✅ 优势
1. **灵活切换** - 支持本地/千问/OpenAI多种模型
2. **故障转移** - API不可用时自动降级到本地
3. **高精度** - 千问1024维向量，检索更准确
4. **低成本** - 免费额度足够中小规模使用
5. **易扩展** - 可轻松添加其他embedding provider

### 🔄 后续优化
1. **向量缓存** - 缓存常用文本的向量，减少API调用
2. **异步编码** - 大批量编码时使用异步IO提升性能
3. **质量监控** - 记录embedding质量指标，优化检索效果
4. **成本追踪** - 记录API调用次数和成本

### 📌 注意事项
- 切换provider后向量维度会变化，需要重建向量库或做兼容处理
- 千问API需要网络连接，离线场景请使用本地模型
- 建议生产环境配置故障转移，确保服务可用性
