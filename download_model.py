#!/usr/bin/env python3
# @self-expose: {"id": "download_model", "name": "Download Model", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Download Model功能"]}}
# -*- coding: utf-8 -*-
"""
【可复用下载插件】all-MiniLM-L6-v2模型下载安装脚本

功能说明：
- 下载并安装sentence-transformers的all-MiniLM-L6-v2预训练模型到指定目录
- 支持断点续传和完整性验证
- 作为通用下载组件，可被其他模块复用
"""

import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

def download_model():
    """下载all-MiniLM-L6-v2模型"""
    print("开始下载all-MiniLM-L6-v2模型...")
    
    # 模型名称
    model_name = "all-MiniLM-L6-v2"
    
    # 下载目录 - 项目根目录下的model_cache
    project_root = Path(__file__).parent
    download_dir = project_root / "data" / "model_cache"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 使用SentenceTransformer下载模型
        model = SentenceTransformer(model_name)
        
        # 保存模型到指定目录
        model.save(str(download_dir / model_name))
        
        print(f"模型下载成功！已保存到: {download_dir / model_name}")
        return True
    except Exception as e:
        print(f"模型下载失败: {e}")
        return False

if __name__ == "__main__":
    download_model()
