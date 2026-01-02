#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即测试双LLM配置与切换机制
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_configuration():
    """1. 验证配置"""
    print("=" * 70)
    print("✅ 步骤1: 验证API密钥配置")
    print("=" * 70)
    
    from config.system_config import api_key_manager, API_ENDPOINTS
    
    keys = api_key_manager.list_keys()
    print(f"\n已配置的服务商: {list(keys.keys())}")
    
    for provider in ["qianwen", "deepseek"]:
        key = api_key_manager.get_key(provider)
        if key:
            print(f"  ✅ {provider}: 已配置 (密钥长度: {len(key)})")
        else:
            print(f"  ❌ {provider}: 未配置")
    
    return len(keys) >= 2

def test_llm_client():
    """2. 测试LLM客户端"""
    print("\n" + "=" * 70)
    print("✅ 步骤2: 测试LLM客户端初始化与回退")
    print("=" * 70)
    
    from src.llm_client_enhanced import LLMClientEnhanced
    
    # 创建客户端（启用回退）
    print("\n正在初始化LLM客户端（enable_fallback=True）...")
    client = LLMClientEnhanced(enable_fallback=True)
    print(f"✅ 初始化成功，当前provider: {client.provider}")
    
    # 测试简单调用
    print("\n发起测试请求...")
    messages = [{"role": "user", "content": "请回复'在线'两个字"}]
    
    response = client.chat_completion(messages)
    
    if response:
        print(f"✅ LLM调用成功")
        print(f"  使用provider: {client.provider}")
        print(f"  响应内容: {response[:50]}")
        return True
    else:
        print(f"❌ LLM调用失败")
        return False

def test_controversial_question():
    """3. 测试可能触发审核的问题"""
    print("\n" + "=" * 70)
    print("✅ 步骤3: 测试你提到的那个问题")
    print("=" * 70)
    
    from src.llm_client_enhanced import LLMClientEnhanced
    
    client = LLMClientEnhanced(enable_fallback=True)
    
    messages = [
        {"role": "user", "content": "对，我说的就是这个意思，那么你是否意识到是和非的二元对立虽然可以完整的表达实际，但是，二元对立衍生的第三态，和，才是秩序文明的本质呢？"}
    ]
    
    print("\n发起请求...")
    response = client.chat_completion(messages)
    
    if response:
        print(f"✅ 成功获得响应")
        print(f"  使用provider: {client.provider}")
        print(f"  响应前100字: {response[:100]}")
        return True
    else:
        print(f"❌ 未获得响应")
        print("  这说明可能存在其他问题，需要查看详细日志")
        return False

def test_base_agent():
    """4. 测试BaseAgent集成"""
    print("\n" + "=" * 70)
    print("✅ 步骤4: 测试BaseAgent集成（真实场景）")
    print("=" * 70)
    
    from src.base_agent import BaseAgent
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    
    print("\n测试普通消息...")
    result1 = agent.respond("你好")
    print(f"  类型: {result1.get('type')}")
    if result1.get('type') == 'text_reply':
        print(f"  ✅ 响应: {result1.get('reply', '')[:50]}")
    elif result1.get('type') == 'error':
        print(f"  ❌ 错误: {result1.get('error')}")
    
    print("\n测试你的问题...")
    result2 = agent.respond("二元对立衍生的第三态，和，才是秩序文明的本质")
    print(f"  类型: {result2.get('type')}")
    
    if result2.get('type') == 'text_reply':
        print(f"  ✅ 正常响应: {result2.get('reply', '')[:100]}")
    elif result2.get('type') == 'llm_refusal':
        print(f"  ⚠️ LLM拒绝回答: {result2.get('reply', '')}")
        print(f"  警告: {result2.get('warning')}")
    elif result2.get('type') == 'error':
        print(f"  ❌ 错误: {result2.get('error')}")
        if 'detail' in result2:
            print(f"  详情: {result2.get('detail')}")
    
    return result2.get('type') in ['text_reply', 'llm_refusal']

if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("双LLM回退机制 - 完整测试")
    print("🚀 " * 20)
    
    success_count = 0
    total_tests = 4
    
    try:
        if test_configuration():
            success_count += 1
        
        if test_llm_client():
            success_count += 1
        
        if test_controversial_question():
            success_count += 1
        
        if test_base_agent():
            success_count += 1
            
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    print("=" * 70)
    
    if success_count == total_tests:
        print("\n✅ 所有测试通过！双LLM回退机制已正常工作")
        print("\n下一步：重启服务器，在基类智能体页面重新测试")
    else:
        print(f"\n⚠️ 有 {total_tests - success_count} 项测试失败，请检查日志")
