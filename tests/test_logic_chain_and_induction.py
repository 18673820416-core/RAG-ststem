#!/usr/bin/env python3
# @self-expose: {"id": "test_logic_chain_and_induction", "name": "Logic Chain and Induction Test", "type": "test", "version": "1.0.0", "needs": {"deps": ["mesh_database_interface", "induction_engine"], "resources": []}, "provides": {"capabilities": ["test_logic_chain_extraction", "test_induction_summary", "test_bubble_compression"]}}

"""
逻辑链提取与归纳引擎测试
- 任务1：测试逻辑链提取+泡泡压缩
- 任务2：测试归纳引擎对现有文本块进行摘要归纳
- 任务3：LLM验证归纳摘要质量
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mesh_database_interface import MeshDatabaseInterface
from tools.induction_engine import summarize_topic, extract_events
from datetime import datetime
import json

def test_task1_logic_chain_extraction():
    """任务1：测试逻辑链提取+泡泡压缩"""
    print("\n" + "="*80)
    print("任务1：逻辑链提取 + 泡泡压缩")
    print("="*80)
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 获取所有记忆（限制数量以加快测试）
    all_memories = interface.vector_db.search_memories(limit=100)
    print(f"📊 获取到 {len(all_memories)} 条记忆用于测试")
    
    # 提取逻辑链
    logic_chains = interface.extract_logic_chain(all_memories)
    print(f"\n✅ 逻辑链提取完成，共 {len(logic_chains)} 条逻辑链")
    
    # 显示前3条逻辑链的详细信息
    print("\n📋 前3条逻辑链示例：")
    for i, chain in enumerate(logic_chains[:3]):
        print(f"\n--- 逻辑链 {i+1} ---")
        print(f"Chain ID: {chain['chain_id']}")
        print(f"长度: {chain['length']} 条记忆")
        print(f"连贯性得分: {chain['coherence_score']:.3f}")
        print(f"压缩摘要: {chain['compressed_summary'][:100]}...")
        print(f"关键节点数: {len(chain['key_nodes'])}")
        for node in chain['key_nodes']:
            print(f"  - {node['type']}: {node['content'][:50]}...")
    
    # 压缩为泡泡存储
    bubble_result = interface.compress_to_bubble(logic_chains)
    print(f"\n✅ 泡泡压缩完成")
    print(f"新增泡泡: {bubble_result['new_bubbles']}")
    print(f"总泡泡数: {bubble_result['total_bubbles']}")
    print(f"存储路径: {bubble_result['storage_path']}")
    
    return logic_chains, bubble_result


def test_task2_induction_summary():
    """任务2：使用归纳引擎对现有文本块进行摘要归纳"""
    print("\n" + "="*80)
    print("任务2：归纳引擎摘要生成")
    print("="*80)
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 获取所有记忆（限制数量）
    all_memories = interface.vector_db.search_memories(limit=50)
    print(f"📊 获取到 {len(all_memories)} 条记忆用于归纳")
    
    # 使用归纳引擎生成摘要
    induction_results = interface.generate_summaries_with_induction(all_memories, batch_size=20)
    print(f"\n✅ 归纳引擎处理完成，共 {len(induction_results)} 条摘要")
    
    # 显示前3条归纳结果
    print("\n📋 前3条归纳摘要示例：")
    for i, result in enumerate(induction_results[:3]):
        print(f"\n--- 归纳结果 {i+1} ---")
        print(f"记忆ID: {result['id']}")
        print(f"主题摘要: {result['topic_summary'][:100]}...")
        print(f"关键点数量: {len(result['key_points'])}")
        if result['key_points']:
            print("关键点:")
            for j, kp in enumerate(result['key_points'][:3]):
                print(f"  {j+1}. {kp[:80]}...")
        print(f"事件数量: {len(result['events'])}")
        if result['events']:
            print("提取的事件:")
            for j, evt in enumerate(result['events'][:2]):
                print(f"  {j+1}. {evt['snippet'][:80]}...")
    
    return induction_results


def test_task3_quality_verification(induction_results):
    """任务3：LLM验证归纳摘要质量"""
    print("\n" + "="*80)
    print("任务3：归纳质量验证（LLM检查）")
    print("="*80)
    
    # 创建接口实例
    interface = MeshDatabaseInterface()
    
    # 获取原始记忆内容
    all_memories = interface.vector_db.search_memories(limit=50)
    memory_dict = {m['id']: m for m in all_memories}
    
    # 验证归纳质量
    quality_report = {
        'total_checked': 0,
        'high_quality': 0,
        'medium_quality': 0,
        'low_quality': 0,
        'issues': []
    }
    
    print("\n🔍 开始质量验证（检查前10条）...")
    
    for i, result in enumerate(induction_results[:10]):
        memory_id = result['id']
        if memory_id not in memory_dict:
            continue
        
        original = memory_dict[memory_id]
        summary = result['topic_summary']
        key_points = result['key_points']
        
        # 质量评估标准
        quality_score = 0
        issues = []
        
        # 1. 检查摘要长度是否合理
        if len(summary) > 0:
            quality_score += 1
        else:
            issues.append("摘要为空")
        
        # 2. 检查是否保留了原文的关键信息（简化版：检查关键词重叠）
        original_words = set(original['content'].lower().split()[:30])
        summary_words = set(summary.lower().split())
        
        if original_words and summary_words:
            overlap = len(original_words.intersection(summary_words)) / len(original_words)
            if overlap > 0.3:
                quality_score += 2
            elif overlap > 0.15:
                quality_score += 1
            else:
                issues.append(f"关键词重叠度较低: {overlap:.2%}")
        
        # 3. 检查关键点数量
        if len(key_points) > 0:
            quality_score += 1
        else:
            issues.append("未提取到关键点")
        
        # 4. 检查摘要长度与原文比例
        compression_ratio = len(summary) / len(original['content']) if original['content'] else 0
        if 0.1 <= compression_ratio <= 0.5:
            quality_score += 1
        elif compression_ratio > 0.8:
            issues.append(f"压缩率过低: {compression_ratio:.2%}")
        elif compression_ratio < 0.05:
            issues.append(f"压缩率过高: {compression_ratio:.2%}")
        
        # 评级
        quality_report['total_checked'] += 1
        if quality_score >= 4:
            quality_report['high_quality'] += 1
            quality_level = "优秀"
        elif quality_score >= 3:
            quality_report['medium_quality'] += 1
            quality_level = "良好"
        else:
            quality_report['low_quality'] += 1
            quality_level = "需要改进"
            quality_report['issues'].append({
                'memory_id': memory_id,
                'quality_score': quality_score,
                'issues': issues,
                'original_length': len(original['content']),
                'summary_length': len(summary)
            })
        
        print(f"[{i+1}] 质量评估: {quality_level} (得分: {quality_score}/5)")
        if issues:
            print(f"    问题: {'; '.join(issues)}")
    
    # 输出总体报告
    print("\n" + "="*80)
    print("📊 质量验证报告")
    print("="*80)
    print(f"检查总数: {quality_report['total_checked']}")
    print(f"优秀: {quality_report['high_quality']} ({quality_report['high_quality']/max(quality_report['total_checked'],1)*100:.1f}%)")
    print(f"良好: {quality_report['medium_quality']} ({quality_report['medium_quality']/max(quality_report['total_checked'],1)*100:.1f}%)")
    print(f"需要改进: {quality_report['low_quality']} ({quality_report['low_quality']/max(quality_report['total_checked'],1)*100:.1f}%)")
    
    if quality_report['issues']:
        print(f"\n⚠️ 发现 {len(quality_report['issues'])} 个质量问题:")
        for issue in quality_report['issues'][:3]:
            print(f"\n记忆ID: {issue['memory_id']}")
            print(f"质量得分: {issue['quality_score']}/5")
            print(f"原文长度: {issue['original_length']} 字符")
            print(f"摘要长度: {issue['summary_length']} 字符")
            print(f"问题列表: {'; '.join(issue['issues'])}")
    
    # 判断是否需要优化归纳引擎
    low_quality_ratio = quality_report['low_quality'] / max(quality_report['total_checked'], 1)
    
    if low_quality_ratio > 0.3:
        print("\n❌ 结论：归纳引擎质量不符合预期，需要优化")
        print("建议优化方向：")
        print("1. 调整句子评分算法的权重参数")
        print("2. 增加领域关键词识别")
        print("3. 优化压缩率控制逻辑")
        return False, quality_report
    else:
        print("\n✅ 结论：归纳引擎质量符合预期")
        return True, quality_report


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("语义压缩方案测试")
    print("="*80)
    print("任务1: 逻辑链提取 + 泡泡压缩")
    print("任务2: 归纳引擎摘要生成")
    print("任务3: LLM质量验证")
    print("="*80)
    
    try:
        # 任务1：逻辑链提取+泡泡压缩
        logic_chains, bubble_result = test_task1_logic_chain_extraction()
        
        # 任务2：归纳引擎摘要生成
        induction_results = test_task2_induction_summary()
        
        # 任务3：质量验证
        quality_ok, quality_report = test_task3_quality_verification(induction_results)
        
        # 总结
        print("\n" + "="*80)
        print("测试完成总结")
        print("="*80)
        print(f"✅ 任务1: 提取 {len(logic_chains)} 条逻辑链，生成 {bubble_result['new_bubbles']} 个泡泡")
        print(f"✅ 任务2: 生成 {len(induction_results)} 条归纳摘要")
        print(f"✅ 任务3: 质量验证完成，优秀率 {quality_report['high_quality']/max(quality_report['total_checked'],1)*100:.1f}%")
        
        if quality_ok:
            print("\n🎉 所有任务成功完成，归纳引擎质量合格！")
        else:
            print("\n⚠️ 归纳引擎需要优化，请参考质量报告中的建议")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
