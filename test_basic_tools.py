# -*- coding: utf-8 -*-
"""
12个基础工具调用测试脚本
验证基础工具是否能被智能体正常调用

基础工具清单（让LLM进化为智能体的必备能力）：
1. memory_retrieval (记忆检索) - 向量库查询，RAG核心能力
2. file_reading (文件读取) - 读取本地文件，加载提示词/配置
3. file_writing (文件写入) - 写入本地文件，保存日志/泡泡
4. command_line (命令行) - 执行系统命令，调用外部工具
5. web_search (网页搜索) - 联网搜索，获取实时信息
6. memory_iteration (记忆迭代) - 记忆管理，长期记忆维护
7. equality_assessment (平等律评估) - 基础评估能力
8. memory_slicer (记忆切片) - 文本分片，长文档处理
9. networked_thinking (网状思维) - 思维追踪，构建思维网络
10. reasoning_engine (理性认知) - 逻辑推理，基于四大逻辑规则
11. cognitive_barrier_break (认知破障) - 破除AI幻觉，质量保障
12. terminal_display (终端显示) - 终端输出，调试反馈
"""

import sys
from pathlib import Path

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

from src.base_agent import BaseAgent
import json
from datetime import datetime

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}\n")

def test_tool_call(agent, tool_name, parameters, description):
    """测试单个工具调用"""
    print(f"\n🔧 测试工具: {tool_name}")
    print(f"📝 描述: {description}")
    print(f"📋 参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
    
    try:
        result = agent.call_tool(tool_name, parameters)
        success = result.get('success', False)
        
        if success:
            print(f"✅ 调用成功!")
            # 打印结果摘要（避免输出过长）
            if 'data' in result:
                data = result['data']
                if isinstance(data, dict):
                    print(f"📊 返回数据字段: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"📊 返回列表长度: {len(data)}")
                else:
                    print(f"📊 返回数据类型: {type(data).__name__}")
        else:
            error = result.get('error', '未知错误')
            print(f"❌ 调用失败: {error}")
        
        return success
    except Exception as e:
        print(f"💥 异常: {str(e)}")
        return False

def main():
    """主测试流程"""
    print_separator("12个基础工具调用测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 测试目标: 验证基础工具是否能被智能体正常调用")
    print(f"📌 测试原理: 基于'智能体 = LLM + 工具集合'的本质定义")
    
    # 1. 创建基类智能体
    print_separator("步骤1: 创建基类智能体")
    try:
        agent = BaseAgent(
            agent_id="test_agent_001",
            agent_type="base",
            prompt_file="src/agent_prompts/base_agent_prompt.md"
        )
        print("✅ 基类智能体创建成功")
        print(f"   - Agent ID: {agent.agent_id}")
        print(f"   - Agent Type: {agent.agent_type}")
        print(f"   - Tool Integrator: {'已加载' if agent.tool_integrator else '未加载'}")
    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return
    
    # 2. 测试12个基础工具
    print_separator("步骤2: 测试12个基础工具")
    
    test_results = {}
    
    # 测试1: memory_retrieval (记忆检索)
    test_results['memory_retrieval'] = test_tool_call(
        agent,
        'memory_retrieval',
        {
            'query': '智能体基础工具',
            'top_k': 3
        },
        '向量库查询，RAG核心能力'
    )
    
    # 测试2: file_reading (文件读取)
    test_results['file_reading'] = test_tool_call(
        agent,
        'file_reading',
        {
            'file_path': 'docs/DEVELOPMENT_RULES.md',
            'start_line': 1,
            'num_lines': 10
        },
        '读取本地文件，加载提示词/配置'
    )
    
    # 测试3: file_writing (文件写入)
    # 注意:需要模拟实现师权限才能写入
    print(f"\n🔧 测试工具: file_writing")
    print(f"📝 描述: 写入本地文件,保存日志/泡泡")
    print(f"⚠️  权限限制: 写操作仅限实现师/实现者 (agent_type: implementer)")
    print(f"📋 当前测试智能体类型: {agent.agent_type}")
    test_results['file_writing'] = False  # 预期失败,因为权限不足
    print(f"❌ 跳过测试 (基础智能体无写权限)")
    
    # 测试4: command_line (命令行)
    test_results['command_line'] = test_tool_call(
        agent,
        'command_line',
        {
            'command': 'echo "基础工具测试"'
        },
        '执行系统命令,调用外部工具'
    )
    
    # 测试5: web_search (网页搜索)
    test_results['web_search'] = test_tool_call(
        agent,
        'web_search',
        {
            'query': 'RAG系统',
            'max_results': 3
        },
        '联网搜索，获取实时信息'
    )
    
    # 测试6: memory_iteration (记忆迭代)
    test_results['memory_iteration'] = test_tool_call(
        agent,
        'memory_iteration',
        {
            'topic': '智能体基础工具'
        },
        '记忆管理,长期记忆维护'
    )
    
    # 测试7: equality_assessment (平等律评估)
    test_results['equality_assessment'] = test_tool_call(
        agent,
        'equality_assessment',
        {
            'file_path': 'test_file.txt',
            'content': '测试内容'
        },
        '基础评估能力,写入前评估'
    )
    
    # 测试8: memory_slicer (记忆切片)
    test_results['memory_slicer'] = test_tool_call(
        agent,
        'memory_slicer',
        {
            'content': '基础工具是让LLM进化为智能体的必备能力。包括文件读写、记忆检索、命令行调用等核心功能。',
            'config': {
                'max_chunk_size': 100
            }
        },
        '文本分片，长文档处理'
    )
    
    # 测试9: networked_thinking (网状思维)
    test_results['networked_thinking'] = test_tool_call(
        agent,
        'networked_thinking',
        {
            'query': '基础工具',
            'max_depth': 2
        },
        '思维追踪,构建思维网络'
    )
    
    # 测试10: reasoning_engine (理性认知)
    test_results['reasoning_engine'] = test_tool_call(
        agent,
        'reasoning_engine',
        {
            'text': '基础工具是让LLM进化为智能体的必备能力',
            'check_type': 'reasoning'
        },
        '逻辑推理,基于四大逻辑规则'
    )
    
    # 测试11: cognitive_barrier_break (认知破障)
    test_results['cognitive_barrier_break'] = test_tool_call(
        agent,
        'cognitive_barrier_break',
        {
            'text': '基础工具是系统启动时加载的工具',
            'context': '智能体工具定义'
        },
        '破除AI幻觉,质量保障'
    )
    
    # 测试12: terminal_display (终端显示)
    test_results['terminal_display'] = test_tool_call(
        agent,
        'terminal_display',
        {
            'action': 'get_startup_status'
        },
        '终端输出，调试反馈'
    )
    
    # 3. 汇总测试结果
    print_separator("步骤3: 测试结果汇总")
    
    success_count = sum(1 for v in test_results.values() if v)
    total_count = len(test_results)
    
    print(f"\n📊 测试统计:")
    print(f"   ✅ 成功: {success_count}/{total_count}")
    print(f"   ❌ 失败: {total_count - success_count}/{total_count}")
    print(f"   📈 成功率: {success_count/total_count*100:.1f}%")
    
    print(f"\n📋 详细结果:")
    for i, (tool_name, success) in enumerate(test_results.items(), 1):
        status = "✅" if success else "❌"
        print(f"   {i:2d}. {status} {tool_name}")
    
    # 4. 关键性验证
    print_separator("步骤4: 系统关键性验证")
    
    if success_count == total_count:
        print("✅ 所有基础工具调用成功!")
        print("✅ 智能体具备完整的基础能力,可以正常运行!")
    elif success_count >= 9:
        print("⚠️  大部分基础工具可用,部分工具需要特殊权限或参数调整")
        print("⚠️  核心功能正常,系统可以运行")
    elif success_count >= 6:
        print("⚠️  半数基础工具可用")
        print("⚠️  部分功能受限,需要检查工具参数和权限")
    else:
        print("❌ 大部分基础工具调用失败!")
        print("❌ 需要检查工具集成和参数配置!")
    
    print(f"\n💡 关键洞察:")
    print(f"   基础工具 = 让LLM进化为智能体的必备能力")
    print(f"   如果这12个基础工具没有被统一初始化和加载，RAG系统完全无法运行")
    print(f"   这就像人需要'呼吸、进食、饮水'才能存活")
    print(f"   基础工具是智能体的'生命支持系统'")
    
    print_separator("测试完成")
    
    return test_results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"\n💥 测试脚本执行异常: {e}")
        import traceback
        traceback.print_exc()
