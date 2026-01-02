#!/usr/bin/env python
# @self-expose: {"id": "check_download_progress", "name": "Check Download Progress", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Download Progress功能"]}}
# -*- coding: utf-8 -*-
"""检查模型下载进度"""

import os
import time
from pathlib import Path

def get_folder_size(folder):
    """获取文件夹大小（MB）"""
    total = 0
    try:
        for entry in Path(folder).rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except:
        pass
    return total / (1024 * 1024)

# 检查位置
cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2"
target_dir = Path("data") / "model_cache" / "all-MiniLM-L6-v2"

print("=" * 70)
print("模型下载进度监控")
print("=" * 70)

while True:
    cache_size = get_folder_size(cache_dir) if cache_dir.exists() else 0
    target_size = get_folder_size(target_dir) if target_dir.exists() else 0
    
    print(f"\r缓存目录: {cache_size:.2f}MB | 目标目录: {target_size:.2f}MB | 预计: ~120MB", end="", flush=True)
    
    # 检查是否完成
    if target_dir.exists() and (target_dir / "config.json").exists():
        print("\n\n✅ 模型下载完成！")
        print(f"最终大小: {target_size:.2f}MB")
        break
    
    time.sleep(5)  # 每5秒刷新一次
