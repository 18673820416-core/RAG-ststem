#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM回退机制与多服务商配置
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_api_keys_config():
    """测试API密钥配置"""
    print("=" * 60)
    print("1. 测试API密钥配置")
    print("=" * 60)
    
    try:
        from config.system_config import api_key_manager, API_ENDPOINTS
        
        # 列出配置的密钥
        keys_dict = api_key_manager.list_keys()
        print(f"\n已配置的API密钥: {list(keys_dict.keys())}")
        
        # 列出所有支持的端点
        print(f"\n支持的LLM端点: {list(API_ENDPOINTS.keys())}")
        
        # 检查每个端点是否有密钥
        print("\n密钥状态检查:")
        for provider in API_ENDPOINTS.keys():
            key = api_key_manager.get_key(provider)
            status = "✅ 已配置" if key else "❌ 未配置"
            print(f"  {provider}: {status}")
            
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        import traceback
        traceback.print_exc()

def test_single_llm_call():
    """测试单个LLM调用"""
    print("\n" + "=" * 60)
    print("2. 测试单个LLM调用")
    print("=" * 60)
    
    try:
        from src.llm_client_enhanced import LLMClientEnhanced
        from config.system_config import LLM_CONFIG
        
        default_provider = LLM_CONFIG.get("default_provider", "qianwen")
        print(f"\n默认服务商: {default_provider}")
        
        # 创建客户端
        print(f"\n正在创建 {default_provider} 客户端...")
        client = LLMClientEnhanced(provider=default_provider)
        print(f"✅ 客户端创建成功")
        
        # 发起测试请求
        print(f"\n发起测试请求...")
        messages = [
            {"role": "user", "content": "你好，请回复'在线'两个字即可"}
        ]
        
        response = client.chat_completion(messages)
        
        if response:
            print(f"✅ LLM调用成功")
            print(f"响应内容: {response[:100]}")
        else:
            print(f"❌ LLM返回空结果（None）")
            
    except ValueError as e:
        print(f"❌ 初始化失败（密钥未配置）: {e}")
    except Exception as e:
        print(f"❌ 调用失败: {e}")
        import traceback
        traceback.print_exc()

def test_available_providers():
    """测试可用服务商检测"""
    print("\n" + "=" * 60)
    print("3. 测试可用服务商检测")
    print("=" * 60)
    
    try:
        from src.llm_client_enhanced import LLMClientEnhanced
        
        # 尝试获取可用服务商列表
        try:
            # 用qianwen初始化（因为它已配置）
            client = LLMClientEnhanced(provider="qianwen")
            available = client.get_available_providers()
            print(f"\n可用的LLM服务商: {available}")
            
            if len(available) < 2:
                print(f"\n⚠️ 警告：只有 {len(available)} 个服务商可用，无法实现回退机制！")
                print(f"建议：至少配置两个LLM服务商的API密钥")
        except Exception as e:
            print(f"❌ 无法检测可用服务商: {e}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_fallback_scenario():
    """测试回退场景（模拟第一个LLM失败）"""
    print("\n" + "=" * 60)
    print("4. 测试回退场景（模拟）")
    print("=" * 60)
    
    print("\n当前代码分析:")
    print("  - LLMClientEnhanced只能初始化一个provider")
    print("  - _make_request失败时返回None，无切换逻辑")
    print("  - chat_api的_generate_llm_response未处理fallback")
    print("\n结论: ❌ 当前没有实现双LLM回退机制！")

if __name__ == "__main__":
    print("\n🔍 LLM回退机制诊断工具\n")
    
    test_api_keys_config()
    test_single_llm_call()
    test_available_providers()
    test_fallback_scenario()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
