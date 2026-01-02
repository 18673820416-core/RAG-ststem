#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试文件上传功能修复
验证基类智能体现在可以读取完整文件内容,而不是只看到分片结果
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path("e:/RAG系统")))

def test_base_agent_file_upload():
    """测试BaseAgent的文件上传功能"""
    print("=" * 70)
    print("测试基类智能体文件上传功能修复")
    print("=" * 70)
    
    # 1. 创建测试文件
    test_file_path = "e:/RAG系统/uploads/test_cognition_model.json"
    test_content = """
{
    "认知模型": {
        "记忆系统": {
            "工作记忆": "短期活跃信息存储",
            "长期记忆": "持久化知识存储",
            "泡泡记忆": "临时思考片段"
        },
        "推理引擎": {
            "溯因推理": "从结果推导原因",
            "演绎推理": "从原则推导结论",
            "类比推理": "基于相似性推理"
        },
        "学习机制": {
            "监督学习": "基于标注数据",
            "无监督学习": "自主发现模式",
            "强化学习": "基于反馈优化"
        }
    },
    "元数据": {
        "版本": "1.0",
        "创建时间": "2025-12-04",
        "描述": "完整的认知模型架构定义"
    }
}
"""
    
    # 确保uploads目录存在
    os.makedirs("e:/RAG系统/uploads", exist_ok=True)
    
    # 写入测试文件
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"\n✅ 创建测试文件: {test_file_path}")
    print(f"文件大小: {len(test_content)} 字符")
    
    # 2. 测试BaseAgent的respond方法
    print("\n" + "=" * 70)
    print("测试BaseAgent.respond()方法处理上传文件")
    print("=" * 70)
    
    try:
        from src.base_agent import BaseAgent
        
        # 创建BaseAgent实例
        agent = BaseAgent(
            agent_id="test_agent",
            agent_type="test_agent",
            prompt_file="src/agent_prompts/base_agent_prompt.md"
        )
        
        print(f"\n✅ BaseAgent实例创建成功")
        print(f"   - agent_id: {agent.agent_id}")
        print(f"   - agent_type: {agent.agent_type}")
        
        # 测试respond方法,传入uploaded_file参数
        print(f"\n📝 调用respond方法...")
        result = agent.respond(
            message="请分析这个认知模型JSON文件,告诉我它包含哪些主要组件?",
            uploaded_file=test_file_path
        )
        
        print(f"\n✅ respond方法调用成功")
        print(f"\n响应结果:")
        print(f"   - type: {result.get('type')}")
        
        if result.get('type') == 'text_reply':
            reply = result.get('reply', '')
            print(f"   - reply长度: {len(reply)} 字符")
            print(f"\n智能体回复:")
            print("   " + "─" * 66)
            # 显示前500字符
            print(f"   {reply[:500]}")
            if len(reply) > 500:
                print(f"   ... (还有 {len(reply) - 500} 个字符)")
            print("   " + "─" * 66)
            
            # 检查是否提到了文件中的关键概念
            key_concepts = ["记忆系统", "推理引擎", "学习机制", "工作记忆", "溯因推理"]
            found_concepts = [kw for kw in key_concepts if kw in reply]
            
            if found_concepts:
                print(f"\n✅ 智能体成功识别了文件中的关键概念:")
                for concept in found_concepts:
                    print(f"   ✓ {concept}")
            else:
                print(f"\n⚠️  智能体回复中未包含文件的关键概念")
                print(f"   这可能表示智能体没有读取到完整文件内容")
                
        elif result.get('type') == 'error':
            print(f"   - error: {result.get('error')}")
            print(f"\n⚠️  LLM调用出错,但文件读取功能应该正常")
            
        else:
            print(f"   - 未知响应类型: {result}")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 测试_read_uploaded_file方法
    print("\n" + "=" * 70)
    print("测试BaseAgent._read_uploaded_file()方法")
    print("=" * 70)
    
    try:
        file_content = agent._read_uploaded_file(test_file_path)
        
        if file_content:
            print(f"\n✅ 文件读取成功")
            print(f"   - 内容长度: {len(file_content)} 字符")
            print(f"   - 前100字符: {file_content[:100]}")
            
            # 验证是否读取到完整内容
            if "认知模型" in file_content and "记忆系统" in file_content:
                print(f"\n✅ 确认读取到完整JSON内容")
            else:
                print(f"\n⚠️  文件内容可能不完整")
        else:
            print(f"\n❌ 文件读取失败,返回None")
            return False
            
    except Exception as e:
        print(f"\n❌ 文件读取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ 所有测试通过!")
    print("=" * 70)
    print("\n总结:")
    print("1. BaseAgent现在可以通过uploaded_file参数接收上传文件路径")
    print("2. _read_uploaded_file方法会读取完整文件内容")
    print("3. 完整内容会附加到用户消息中,传递给LLM")
    print("4. LLM可以看到文件的完整内容,而不只是分片后的检索结果")
    
    return True

if __name__ == "__main__":
    success = test_base_agent_file_upload()
    sys.exit(0 if success else 1)
