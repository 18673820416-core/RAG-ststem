# @self-expose: {"id": "embedding_service", "name": "Embedding Service", "type": "component", "version": "1.0.0", "needs": {"deps": ["system_config", "api_keys"], "resources": []}, "provides": {"capabilities": ["文本向量化", "多模型支持", "批量编码", "故障转移"], "methods": {"encode": {"signature": "(text: str, provider: Optional[str]) -> Optional[List[float]]", "description": "编码单个文本为向量"}, "encode_batch": {"signature": "(texts: List[str], provider: Optional[str]) -> List[List[float]]", "description": "批量编码文本"}}}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Embedding服务 - 支持本地模型与千问API，并提供故障转移能力"""

from typing import List, Dict, Any, Optional
import os
import json
import logging
import time
from pathlib import Path

import numpy as np

from config.system_config import EMBEDDING_CONFIG

logger = logging.getLogger(__name__)


class EmbeddingService:
    """统一的Embedding服务，支持多provider"""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config is None:
            config = EMBEDDING_CONFIG
        self.config = config
        self.default_provider = config.get("default_provider", "local")
        self.fallback_order = config.get("fallback_order", [self.default_provider])

        self._providers: Dict[str, Dict[str, Any]] = {}
        self._initialized_providers = set()

        logger.info(f"Embedding服务初始化，默认provider: {self.default_provider}")

    # ---------------- Provider初始化 -----------------
    def _get_provider(self, provider_name: str) -> Optional[Dict[str, Any]]:
        if provider_name in self._initialized_providers:
            return self._providers.get(provider_name)

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

    def _init_local_provider(self) -> Optional[Dict[str, Any]]:
        try:
            from sentence_transformers import SentenceTransformer

            config = self.config["local"]
            model_name = config["model_name"]
            cache_dir = Path(config["cache_dir"])

            local_model_dir = cache_dir / model_name
            if local_model_dir.exists():
                model = SentenceTransformer(str(local_model_dir))
                logger.info(f"✅ 加载本地Embedding模型: {local_model_dir}")
            else:
                logger.warning(f"本地模型不存在，将从HuggingFace下载: {model_name}")
                model = SentenceTransformer(model_name, cache_folder=str(cache_dir))

            return {
                "model": model,
                "dimension": config["dimension"],
                "type": "local",
            }
        except Exception as e:
            logger.error(f"本地模型初始化失败: {e}")
            return None

    def _init_qianwen_provider(self) -> Optional[Dict[str, Any]]:
        try:
            config = self.config["qianwen"]
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
                "type": "qianwen",
            }
        except Exception as e:
            logger.error(f"千问API初始化失败: {e}")
            return None

    def _init_openai_provider(self) -> Optional[Dict[str, Any]]:
        try:
            config = self.config["openai"]
            api_key = self._get_api_key(config["api_key_env"])
            if not api_key:
                logger.error("OpenAI API密钥未配置")
                return None

            return {
                "api_key": api_key,
                "model_name": config["model_name"],
                "dimension": config["dimension"],
                "type": "openai",
            }
        except Exception as e:
            logger.error(f"OpenAI API初始化失败: {e}")
            return None

    def _get_api_key(self, env_var_name: str) -> Optional[str]:
        api_key = os.getenv(env_var_name)
        if api_key:
            return api_key

        try:
            api_keys_file = Path("config/api_keys.json")
            if api_keys_file.exists():
                with open(api_keys_file, "r", encoding="utf-8") as f:
                    api_keys = json.load(f)
                if env_var_name == "QWEN_API_KEY":
                    qwen_cfg = api_keys.get("qianwen", {})
                    return qwen_cfg.get("api_key") or qwen_cfg.get("embedding_api_key")
                if env_var_name == "OPENAI_API_KEY":
                    openai_cfg = api_keys.get("openai", {})
                    return openai_cfg.get("api_key")
        except Exception as e:
            logger.error(f"读取API密钥失败: {e}")

        return None

    # ---------------- 编码接口 -----------------
    def encode(self, text: str, provider: Optional[str] = None) -> Optional[List[float]]:
        if not text or not text.strip():
            # 返回零向量
            dimension = self.config[self.default_provider]["dimension"]
            return [0.0] * dimension

        providers_to_try = [provider] if provider else self.fallback_order

        for prov in providers_to_try:
            try:
                provider_obj = self._get_provider(prov)
                if not provider_obj:
                    continue

                if provider_obj["type"] == "local":
                    vector = self._encode_local(text, provider_obj)
                elif provider_obj["type"] == "qianwen":
                    vector = self._encode_qianwen(text, provider_obj)
                elif provider_obj["type"] == "openai":
                    vector = self._encode_openai(text, provider_obj)
                else:
                    continue

                if vector:
                    return vector
            except Exception as e:
                logger.error(f"provider={prov} 编码失败: {e}")
                continue

        # 所有provider失败时返回零向量
        dimension = self.config[self.default_provider]["dimension"]
        return [0.0] * dimension

    def encode_batch(self, texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
        if not texts:
            return []

        prov = provider or self.default_provider
        provider_obj = self._get_provider(prov)
        if not provider_obj:
            # 降级为逐个编码
            return [self.encode(t, provider) for t in texts]

        try:
            if provider_obj["type"] == "local":
                return self._encode_batch_local(texts, provider_obj)
            if provider_obj["type"] == "qianwen":
                return self._encode_batch_qianwen(texts, provider_obj)
            if provider_obj["type"] == "openai":
                return self._encode_batch_openai(texts, provider_obj)
        except Exception as e:
            logger.error(f"批量编码失败: {e}，降级为逐个编码")
            return [self.encode(t, provider) for t in texts]

        return [self.encode(t, provider) for t in texts]

    # ---------------- 本地模型编码 -----------------
    def _encode_local(self, text: str, provider: Dict[str, Any]) -> List[float]:
        from sentence_transformers import SentenceTransformer

        model = provider["model"]
        vector = model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    def _encode_batch_local(self, texts: List[str], provider: Dict[str, Any]) -> List[List[float]]:
        from sentence_transformers import SentenceTransformer

        model = provider["model"]
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    # ---------------- 千问API编码 -----------------
    def _encode_qianwen(self, text: str, provider: Dict[str, Any]) -> Optional[List[float]]:
        import requests

        url = f"{provider['base_url']}/embeddings"
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {"model": provider["model_name"], "input": text}

        for attempt in range(provider["max_retries"]):
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=provider["timeout"])
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
                logger.error(f"千问API错误: {resp.status_code} - {resp.text}")
            except Exception as e:
                logger.error(f"千问API调用失败({attempt+1}/{provider['max_retries']}): {e}")
                time.sleep(1)
        return None

    def _encode_batch_qianwen(self, texts: List[str], provider: Dict[str, Any]) -> List[List[float]]:
        import requests

        url = f"{provider['base_url']}/embeddings"
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json",
        }

        batch_size = provider["batch_size"]
        all_vectors: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {"model": provider["model_name"], "input": batch}
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=provider["timeout"])
                if resp.status_code == 200:
                    data = resp.json()
                    vectors = [item["embedding"] for item in data["data"]]
                    all_vectors.extend(vectors)
                else:
                    logger.error(f"千问批量API错误: {resp.text}")
                    for t in batch:
                        v = self._encode_qianwen(t, provider) or [0.0] * provider["dimension"]
                        all_vectors.append(v)
            except Exception as e:
                logger.error(f"千问批量API失败: {e}")
                for t in batch:
                    v = self._encode_qianwen(t, provider) or [0.0] * provider["dimension"]
                    all_vectors.append(v)
        return all_vectors

    # ---------------- OpenAI编码（可选） -----------------
    def _encode_openai(self, text: str, provider: Dict[str, Any]) -> Optional[List[float]]:
        import openai

        openai.api_key = provider["api_key"]
        try:
            resp = openai.embeddings.create(model=provider["model_name"], input=text)
            return resp.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI API失败: {e}")
            return None

    def _encode_batch_openai(self, texts: List[str], provider: Dict[str, Any]) -> List[List[float]]:
        import openai

        openai.api_key = provider["api_key"]
        try:
            resp = openai.embeddings.create(model=provider["model_name"], input=texts)
            return [item.embedding for item in resp.data]
        except Exception as e:
            logger.error(f"OpenAI批量API失败: {e}")
            return [self._encode_openai(t, provider) or [0.0] * provider["dimension"] for t in texts]

    # ---------------- 工具方法 -----------------
    def get_dimension(self, provider: Optional[str] = None) -> int:
        prov = provider or self.default_provider
        return self.config[prov]["dimension"]

    def get_available_providers(self) -> List[str]:
        available: List[str] = []
        for name in self.config.keys():
            if name in ["default_provider", "fallback_order"]:
                continue
            try:
                provider = self._get_provider(name)
                if provider:
                    available.append(name)
            except Exception:
                continue
        return available


_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
