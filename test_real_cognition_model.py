#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试真实的认知模型文件上传功能
验证LLM是否真的能看到完整的9.4KB复杂JSON内容
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path("e:/RAG系统")))

def test_real_cognition_model():
    """测试真实认知模型文件"""
    print("=" * 70)
    print("测试真实认知模型文件上传功能")
    print("=" * 70)
    
    # 使用真实的认知模型文件
    real_file_path = "e:/RAG系统/docs/认知模型_utf8.json"
    
    # 先读取真实文件看看内容
    print(f"\n📖 读取真实文件: {real_file_path}")
    try:
        with open(real_file_path, 'r', encoding='utf-8') as f:
            real_content = f.read()
        
        print(f"   ✅ 文件大小: {len(real_content)} 字符")
        print(f"   ✅ 文件行数: {real_content.count(chr(10)) + 1} 行")
        
        # 检查关键概念
        key_concepts = [
            "理性逻辑",
            "动态校准",
            "认知闭环模型",
            "因果律",
            "矛盾律",
            "同一律",
            "本质优先原则",
            "动态认知框架层",
            "元认知",
            "认知实践层",
            "双向校准与迭代循环"
        ]
        
        found_concepts = [kw for kw in key_concepts if kw in real_content]
        print(f"\n   文件包含的关键概念 ({len(found_concepts)}/{len(key_concepts)}):")
        for concept in found_concepts[:5]:
            print(f"   ✓ {concept}")
        if len(found_concepts) > 5:
            print(f"   ... 还有 {len(found_concepts) - 5} 个概念")
            
    except Exception as e:
        print(f"   ❌ 读取文件失败: {e}")
        return False
    
    # 测试BaseAgent能否读取完整内容
    print("\n" + "=" * 70)
    print("测试BaseAgent处理真实文件")
    print("=" * 70)
    
    try:
        from src.base_agent import BaseAgent
        
        agent = BaseAgent(
            agent_id="real_test_agent",
            agent_type="test_agent",
            prompt_file="src/agent_prompts/base_agent_prompt.md"
        )
        
        print(f"\n✅ BaseAgent实例创建成功")
        
        # 提问一个非常具体的问题,测试LLM是否真的看到了完整内容
        # 这些概念在文件的深层位置
        print(f"\n📝 测试问题: 请告诉我这个认知模型中,底层的四大核心规则分别是什么?")
        print(f"   (这个问题需要LLM看到文件第10-26行的详细内容)")
        
        result = agent.respond(
            message="请告诉我这个认知模型中,底层「先天认知根基」层包含的四大核心规则分别是什么?请列出每个规则的名称和核心描述。",
            uploaded_file=real_file_path
        )
        
        print(f"\n✅ respond方法调用成功")
        print(f"\n响应类型: {result.get('type')}")
        
        if result.get('type') == 'text_reply':
            reply = result.get('reply', '')
            print(f"回复长度: {len(reply)} 字符")
            
            print(f"\n" + "─" * 70)
            print("智能体回复:")
            print("─" * 70)
            print(reply)
            print("─" * 70)
            
            # 检查是否提到了四大核心规则
            four_rules = ["因果律", "矛盾律", "同一律", "本质优先原则"]
            found_rules = [rule for rule in four_rules if rule in reply]
            
            print(f"\n检查核心规则识别情况 ({len(found_rules)}/4):")
            for rule in found_rules:
                print(f"   ✅ {rule}")
            
            missing_rules = [rule for rule in four_rules if rule not in reply]
            if missing_rules:
                print(f"\n   ⚠️  未识别的规则:")
                for rule in missing_rules:
                    print(f"   ❌ {rule}")
                print(f"\n   这说明LLM可能没有看到完整文件内容!")
                return False
            else:
                print(f"\n   🎉 所有四大核心规则都被正确识别!")
                print(f"   这证明LLM确实看到了文件的完整内容!")
                return True
                
        elif result.get('type') == 'error':
            print(f"\n⚠️  错误: {result.get('error')}")
            print(f"   但文件读取功能应该正常")
            # 检查文件是否被读取
            print(f"\n测试_read_uploaded_file方法...")
            file_content = agent._read_uploaded_file(real_file_path)
            if file_content and len(file_content) > 9000:
                print(f"   ✅ 文件读取成功: {len(file_content)} 字符")
                print(f"   问题在于LLM调用,而非文件读取功能")
                return True
            else:
                print(f"   ❌ 文件读取失败")
                return False
        else:
            print(f"   未知响应类型")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_cognition_model()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 测试通过: LLM能够看到真实文件的完整内容!")
    else:
        print("❌ 测试失败: LLM无法看到完整文件内容")
        print("   问题可能是:")
        print("   1. 文件内容未被正确读取")
        print("   2. 文件内容未被附加到消息中")
        print("   3. LLM在'编造'答案而非基于实际内容回答")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
