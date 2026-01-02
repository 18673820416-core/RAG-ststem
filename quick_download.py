#!/usr/bin/env python
# @self-expose: {"id": "quick_download", "name": "Quick Download", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Quick Download功能"]}}
# -*- coding: utf-8 -*-
"""快速下载模型脚本 - 带进度显示"""

import os
import time
from pathlib import Path

# 设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

print("=" * 70)
print("SentenceTransformer 模型下载（国内镜像源）")
print("=" * 70)
print(f"镜像源: {os.environ['HF_ENDPOINT']}")
print(f"模型: sentence-transformers/all-MiniLM-L6-v2")
print(f"预计大小: ~120MB")
print("=" * 70)

# 目标目录
target = Path('data/model_cache/all-MiniLM-L6-v2')
target.parent.mkdir(parents=True, exist_ok=True)

print(f"\n目标目录: {target.absolute()}")

# 检查是否已存在
if target.exists() and (target / 'config.json').exists():
    print("\n⚠️ 检测到已存在的模型，跳过下载，直接验证...")
else:
    print("\n开始下载模型...")
    print("(这可能需要几分钟，请耐心等待)")
    print("-" * 70)
    
    start_time = time.time()
    
    from sentence_transformers import SentenceTransformer
    
    # 下载模型
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    download_time = time.time() - start_time
    print(f"\n✅ 下载完成！耗时: {download_time:.1f} 秒")
    
    print("\n保存模型到本地...")
    model.save(str(target))
    print("✅ 保存完成")

# 验证模型
print("\n" + "=" * 70)
print("验证模型...")
print("=" * 70)

from sentence_transformers import SentenceTransformer

try:
    test_model = SentenceTransformer(str(target))
    test_vec = test_model.encode("测试文本")
    
    print("\n" + "=" * 70)
    print("🎉 模型下载并验证成功！")
    print("=" * 70)
    print(f"✅ 模型路径: {target.absolute()}")
    print(f"✅ 向量维度: {len(test_vec)}")
    print(f"✅ 状态: 可用")
    print("=" * 70)
    print("\n现在可以运行 test_base_agent_tools.py 测试向量检索功能")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 模型验证失败: {e}")
    print("请检查下载是否完整")
    exit(1)
