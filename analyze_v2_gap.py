#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2.0质量差距诊断：找出为什么信息熵+困惑度也没到90%"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.mesh_database_interface import MeshDatabaseInterface
from tools.induction_engine import summarize_topic

def analyze_failed_case():
    """分析失败案例：关键词重叠度低的根本原因"""
    
    print("=" * 80)
    print("v2.0质量差距诊断：为什么信息熵+困惑度也没到90%？")
    print("=" * 80)
    
    # 加载数据
    db = MeshDatabaseInterface()
    all_memories = db.vector_db.get_all_memories()
    memories = sorted(all_memories, key=lambda m: m.get('timestamp', ''), reverse=True)[:50]
    
    print(f"\n📊 获取到 {len(memories)} 条记忆用于分析\n")
    
    # 找到问题记忆
    target_id = 'mem_-3257990327454786600'
    target_memory = None
    for mem in memories:
        if mem['id'] == target_id:
            target_memory = mem
            break
    
    if not target_memory:
        print(f"⚠️ 未找到目标记忆 {target_id}")
        return
    
    print(f"🎯 找到问题记忆: {target_id}")
    print(f"原文长度: {len(target_memory['content'])} 字符")
    print(f"\n原文内容（前800字符）:")
    print("-" * 80)
    print(target_memory['content'][:800])
    print("-" * 80)
    
    # 调用归纳引擎
    result = summarize_topic(target_memory['content'], max_sentences=3, max_chars=280)
    
    print(f"\n📝 归纳引擎v2.0输出:")
    print(f"摘要: {result['topic_summary']}")
    print(f"摘要长度: {len(result['topic_summary'])} 字符")
    print(f"压缩率: {result['stats']['compression_ratio']:.2%}")
    print(f"关键词覆盖率: {result['stats']['keyword_coverage']:.2%}")
    print(f"TF-IDF关键词: {result['tfidf_keywords']}")
    
    # 诊断问题
    print(f"\n🔍 诊断分析:")
    
    # 1. 检查原文特征
    content = target_memory['content']
    lines = content.split('\n')
    print(f"\n【原文特征】")
    print(f"  - 总行数: {len(lines)}")
    print(f"  - 平均行长: {len(content) / len(lines):.1f} 字符")
    print(f"  - 是否包含代码: {'是' if any(line.strip().startswith(('#', 'def', 'class', 'import')) for line in lines) else '否'}")
    print(f"  - 是否包含列表: {'是' if any(line.strip().startswith(('-', '*', '1.', '2.')) for line in lines) else '否'}")
    
    # 2. 检查摘要句子的评分
    from tools.induction_engine import _split_sentences, _score_sentence, _extract_tfidf_keywords
    
    sentences = _split_sentences(content)
    tfidf_keywords = _extract_tfidf_keywords(content, top_k=15)
    
    print(f"\n【句子评分分析】（前10句）")
    scored = []
    for i, s in enumerate(sentences[:10]):
        score = _score_sentence(s, i, len(sentences), len(content), tfidf_keywords)
        scored.append((score, i, s[:60]))
        print(f"  [{i}] 得分: {score:.2f} | {s[:60]}...")
    
    scored_all = [(_score_sentence(s, i, len(sentences), len(content), tfidf_keywords), i, s) 
                  for i, s in enumerate(sentences)]
    scored_all.sort(key=lambda x: -x[0])
    
    print(f"\n【最高得分句子TOP 5】")
    for rank, (score, idx, s) in enumerate(scored_all[:5], 1):
        print(f"  {rank}. [位置{idx}] 得分: {score:.2f}")
        print(f"     {s[:100]}...")
    
    # 3. 关键词覆盖分析
    print(f"\n【关键词覆盖分析】")
    print(f"  - TF-IDF关键词: {', '.join(tfidf_keywords[:10])}")
    
    summary_words = set(result['topic_summary'].lower().split())
    matched_keywords = [kw for kw in tfidf_keywords if kw.lower() in result['topic_summary'].lower()]
    print(f"  - 摘要中包含的关键词: {', '.join(matched_keywords)}")
    print(f"  - 覆盖率: {len(matched_keywords)}/{len(tfidf_keywords)} = {len(matched_keywords)/len(tfidf_keywords)*100:.1f}%")
    
    # 4. 诊断结论
    print(f"\n🎯 诊断结论:")
    
    if result['stats']['keyword_coverage'] < 0.15:
        print(f"  ❌ 问题1: 关键词覆盖率过低 ({result['stats']['keyword_coverage']:.2%} < 15%)")
        print(f"     → 可能原因: TF-IDF关键词与高分句子不匹配")
    
    if result['stats']['compression_ratio'] > 0.5:
        print(f"  ⚠️ 问题2: 压缩率过高 ({result['stats']['compression_ratio']:.2%} > 50%)")
        print(f"     → 可能原因: 摘要过长，未抓住核心")
    
    # 5. 优化建议
    print(f"\n💡 优化建议:")
    
    # 检查是否是代码/日志类记忆
    if any(line.strip().startswith(('Traceback', 'Error', 'File "')) for line in lines):
        print(f"  1. 这是错误日志类记忆，建议：")
        print(f"     - 提高错误关键词权重（Error, Traceback, Exception）")
        print(f"     - 优先提取错误位置和错误信息")
    
    # 检查是否需要调整信息熵/困惑度权重
    entropy_scores = []
    fluency_scores = []
    from tools.induction_engine import _calculate_sentence_entropy, _calculate_sentence_perplexity
    
    for s in sentences[:20]:
        entropy_scores.append(_calculate_sentence_entropy(s))
        fluency_scores.append(_calculate_sentence_perplexity(s))
    
    avg_entropy = sum(entropy_scores) / len(entropy_scores) if entropy_scores else 0
    avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
    
    print(f"  2. 信息熵/困惑度统计（前20句）:")
    print(f"     - 平均信息熵: {avg_entropy:.3f}")
    print(f"     - 平均流畅度: {avg_fluency:.3f}")
    
    if avg_entropy < 0.5:
        print(f"     → 信息熵普遍偏低，可能是重复性文本")
    if avg_fluency < 0.5:
        print(f"     → 流畅度偏低，可能是代码或日志文本")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_failed_case()
