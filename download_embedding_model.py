#!/usr/bin/env python
# @self-expose: {"id": "download_embedding_model", "name": "Download Embedding Model", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Download Embedding Model功能"]}}
# -*- coding: utf-8 -*-
"""
从国内镜像源下载 SentenceTransformer 模型到本地
避免联网阻塞，支持离线使用
"""

import os
import sys
from pathlib import Path

def download_model_from_mirror():
    """从国内镜像源下载模型"""
    
    # 设置国内镜像源
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    
    # 目标模型名称
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # 本地缓存目录
    cache_dir = Path(__file__).parent / "data" / "model_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("SentenceTransformer 模型下载工具")
    print("=" * 60)
    print(f"模型名称: {model_name}")
    print(f"镜像源: {os.environ['HF_ENDPOINT']}")
    print(f"缓存目录: {cache_dir}")
    print("=" * 60)
    
    try:
        print("\n开始下载模型...")
        from sentence_transformers import SentenceTransformer
        
        # 下载模型到指定目录
        model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
        
        print("\n✅ 模型下载成功!")
        
        # 保存模型到本地目录
        local_model_dir = cache_dir / "all-MiniLM-L6-v2"
        local_model_dir.mkdir(parents=True, exist_ok=True)
        
        model.save(str(local_model_dir))
        print(f"✅ 模型已保存到: {local_model_dir}")
        
        # 测试模型加载
        print("\n测试本地模型加载...")
        test_model = SentenceTransformer(str(local_model_dir))
        test_embedding = test_model.encode("测试文本")
        print(f"✅ 本地模型加载成功，向量维度: {len(test_embedding)}")
        
        print("\n" + "=" * 60)
        print("模型下载完成！")
        print("=" * 60)
        print(f"\n本地模型路径: {local_model_dir}")
        print("\n可通过以下方式使用:")
        print("1. 默认路径已配置，系统将自动使用本地模型")
        print("2. 或设置环境变量: SENTENCE_MODEL_DIR=" + str(local_model_dir))
        print("=" * 60)
        
        return True
        
    except ImportError:
        print("\n❌ 错误: 未安装 sentence-transformers 库")
        print("请先安装: pip install sentence-transformers")
        return False
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 尝试手动设置镜像源: export HF_ENDPOINT=https://hf-mirror.com")
        print("3. 或使用其他国内镜像:")
        print("   - https://hf-mirror.com")
        print("   - https://mirrors.tuna.tsinghua.edu.cn/hugging-face-models")
        return False

def check_existing_model():
    """检查现有模型"""
    print("\n检查现有模型...")
    
    # 检查项目缓存目录
    cache_dir = Path(__file__).parent / "data" / "model_cache" / "all-MiniLM-L6-v2"
    if cache_dir.exists() and (cache_dir / "config.json").exists():
        print(f"✅ 找到本地模型: {cache_dir}")
        return str(cache_dir)
    
    # 检查环境变量
    env_model = os.getenv('SENTENCE_MODEL_DIR')
    if env_model and Path(env_model).exists():
        print(f"✅ 找到环境变量指定的模型: {env_model}")
        return env_model
    
    # 检查HuggingFace缓存目录（需要找到snapshots子目录）
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2"
    if hf_cache.exists():
        snapshots_dir = hf_cache / "snapshots"
        if snapshots_dir.exists():
            # 获取最新的快照
            snapshots = [d for d in snapshots_dir.iterdir() if d.is_dir()]
            if snapshots:
                latest_snapshot = max(snapshots, key=lambda p: p.stat().st_mtime)
                if (latest_snapshot / "config.json").exists():
                    print(f"✅ 找到系统缓存的模型: {latest_snapshot}")
                    return str(latest_snapshot)
    
    # 检查其他常见缓存目录
    common_paths = [
        Path.home() / ".cache" / "sentence_transformers" / "sentence-transformers_all-MiniLM-L6-v2",
        Path(os.getenv('LOCALAPPDATA', '')) / "sentence_transformers" if os.name == 'nt' else None,
    ]
    
    for path in common_paths:
        if path and path.exists() and (path / "config.json").exists():
            print(f"✅ 找到系统缓存的模型: {path}")
            return str(path)
    
    print("❌ 未找到本地模型")
    return None

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SentenceTransformer 本地模型管理")
    print("=" * 60)
    
    # 先检查现有模型
    existing_model = check_existing_model()
    
    if existing_model:
        print("\n已有本地模型，是否重新下载？")
        print("1. 使用现有模型（推荐）")
        print("2. 重新下载")
        
        choice = input("\n请选择 (1/2，默认1): ").strip() or "1"
        
        if choice == "1":
            print(f"\n将使用现有模型: {existing_model}")
            
            # 如果不在项目缓存目录，复制过来
            project_cache = Path(__file__).parent / "data" / "model_cache" / "all-MiniLM-L6-v2"
            if str(project_cache) != existing_model:
                print(f"\n是否复制到项目缓存目录？ {project_cache}")
                copy_choice = input("复制到项目目录 (y/n，默认y): ").strip().lower() or "y"
                
                if copy_choice == 'y':
                    try:
                        from sentence_transformers import SentenceTransformer
                        print("正在加载并正确保存模型...")
                        
                        # 从现有位置加载模型
                        model = SentenceTransformer(existing_model)
                        
                        # 保存到项目缓存目录（这样会创建正确的模型格式）
                        project_cache.parent.mkdir(parents=True, exist_ok=True)
                        model.save(str(project_cache))
                        print(f"✅ 模型已正确保存到: {project_cache}")
                        
                        # 验证加载
                        test_model = SentenceTransformer(str(project_cache))
                        test_vec = test_model.encode("测试")
                        print(f"✅ 验证成功，向量维度: {len(test_vec)}")
                        
                    except Exception as e:
                        print(f"❌ 保存失败: {e}")
                        print(f"建议设置环境变量: SENTENCE_MODEL_DIR={existing_model}")
            
            sys.exit(0)
    
    # 下载新模型
    print("\n开始从国内镜像源下载模型...")
    success = download_model_from_mirror()
    
    sys.exit(0 if success else 1)
