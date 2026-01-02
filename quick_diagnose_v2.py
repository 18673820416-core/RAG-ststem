#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速诊断v2.0：分析所有记忆找出低质量案例"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.mesh_database_interface import MeshDatabaseInterface
from tools.induction_engine import (
    summarize_topic, _split_sentences, _score_sentence, 
    _extract_tfidf_keywords, _calculate_sentence_entropy,
    _calculate_sentence_perplexity
)

def main():
    print("=" * 100)
    print("v2.0质量诊断：找出低质量案例并分析原因")
    print("=" * 100)
    
    # 加载数据
    db = MeshDatabaseInterface()
    all_memories = db.vector_db.get_all_memories()
    memories = sorted(all_memories, key=lambda m: m.get('timestamp', ''), reverse=True)[:30]
    
    print(f"\n📊 获取到 {len(memories)} 条最新记忆\n")
    
    # 测试所有记忆
    results = []
    for i, mem in enumerate(memories, 1):
        content = mem.get('content', '')
        if not content or len(content) < 50:
            continue
        
        result = summarize_topic(content, max_sentences=3, max_chars=280)
        
        # 质量评分
        score = 0
        issues = []
        
        if result['topic_summary']:
            score += 1
        
        keyword_coverage = result['stats'].get('keyword_coverage', 0)
        if keyword_coverage > 0.15:
            score += 2
        else:
            issues.append(f"关键词覆盖率低: {keyword_coverage:.2%}")
        
        if result['key_points']:
            score += 1
        
        compression_ratio = result['stats'].get('compression_ratio', 1.0)
        if 0.1 <= compression_ratio <= 0.5:
            score += 1
        else:
            issues.append(f"压缩率异常: {compression_ratio:.2%}")
        
        quality = "优秀" if score >= 4 else ("良好" if score >= 3 else "需要改进")
        
        results.append({
            'id': mem['id'],
            'content_len': len(content),
            'summary': result['topic_summary'],
            'quality': quality,
            'score': score,
            'keyword_coverage': keyword_coverage,
            'compression_ratio': compression_ratio,
            'issues': issues,
            'content': content
        })
        
        if quality != "优秀":
            print(f"[{i}] {quality} ({score}/5) | {mem['id'][:30]}... | 覆盖率{keyword_coverage:.1%}")
    
    # 统计
    excellent = [r for r in results if r['quality'] == "优秀"]
    good = [r for r in results if r['quality'] == "良好"]
    poor = [r for r in results if r['quality'] == "需要改进"]
    
    print(f"\n" + "=" * 100)
    print(f"📊 质量统计")
    print(f"=" * 100)
    print(f"优秀: {len(excellent)} ({len(excellent)/len(results)*100:.1f}%)")
    print(f"良好: {len(good)} ({len(good)/len(results)*100:.1f}%)")
    print(f"需要改进: {len(poor)} ({len(poor)/len(results)*100:.1f}%)")
    
    # 分析低质量案例
    if poor:
        print(f"\n" + "=" * 100)
        print(f"🔍 分析需要改进的案例（共{len(poor)}个）")
        print(f"=" * 100)
        
        for idx, case in enumerate(poor[:3], 1):  # 只分析前3个
            print(f"\n【案例{idx}】")
            print(f"ID: {case['id']}")
            print(f"质量: {case['quality']} ({case['score']}/5)")
            print(f"关键词覆盖率: {case['keyword_coverage']:.2%}")
            print(f"压缩率: {case['compression_ratio']:.2%}")
            print(f"问题: {', '.join(case['issues'])}")
            print(f"\n原文长度: {case['content_len']} 字符")
            print(f"原文前300字符:")
            print(f"  {case['content'][:300]}...")
            print(f"\n摘要: {case['summary']}")
            
            # 深度分析
            content = case['content']
            sentences = _split_sentences(content)
            tfidf_keywords = _extract_tfidf_keywords(content, top_k=15)
            
            print(f"\nTF-IDF关键词: {', '.join(tfidf_keywords[:10])}")
            
            # 分析信息熵和困惑度
            entropy_scores = []
            fluency_scores = []
            for s in sentences[:10]:
                entropy_scores.append(_calculate_sentence_entropy(s))
                fluency_scores.append(_calculate_sentence_perplexity(s))
            
            avg_entropy = sum(entropy_scores) / len(entropy_scores) if entropy_scores else 0
            avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
            
            print(f"平均信息熵（前10句）: {avg_entropy:.3f}")
            print(f"平均流畅度（前10句）: {avg_fluency:.3f}")
            
            # 诊断
            print(f"\n🎯 问题诊断:")
            if avg_entropy < 0.4:
                print(f"  ⚠️ 信息熵过低 ({avg_entropy:.3f}) → 可能是重复性/模板化文本")
            if avg_fluency < 0.4:
                print(f"  ⚠️ 流畅度过低 ({avg_fluency:.3f}) → 可能是代码/日志/结构化数据")
            if case['keyword_coverage'] < 0.1:
                print(f"  ❌ 关键词覆盖率极低 → TF-IDF关键词与摘要不匹配")
            
            # 检查文本类型
            is_code = any(line.strip().startswith(('def ', 'class ', 'import ', '#', '//')) 
                         for line in content.split('\n')[:20])
            is_log = any(keyword in content[:500] for keyword in ['Traceback', 'Error:', 'File "', 'line '])
            
            if is_code:
                print(f"  📝 文本类型: 代码类记忆 → 需针对代码优化评分策略")
            if is_log:
                print(f"  📋 文本类型: 日志类记忆 → 需提高错误关键词权重")
    
    print(f"\n" + "=" * 100)
    print(f"✅ 诊断完成")
    print(f"=" * 100)

if __name__ == "__main__":
    main()
