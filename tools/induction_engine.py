#!/usr/bin/env python3
# @self-expose: {"id": "induction_engine", "name": "Induction Engine", "type": "tool", "version": "2.0.0", "needs": {"deps": ["memory_slicer_tool"], "resources": []}, "provides": {"capabilities": ["topic_induction", "event_extraction", "keypoint_extraction", "batch_process", "adaptive_compression", "semantic_scoring", "tfidf_keyword_extraction", "slicer_integration", "entropy_based_scoring", "perplexity_analysis"]}}

"""
Induction Engine
- 目的: 为主题维(结论摘要)的高频任务提供本地具象工具, 降低LLM认知负荷
- 特点: 纯本地、无外网、无第三方依赖; 语言无关的启发式实现, 对中文/英文均可用
- v2.0架构升级: 引入信息熄+困惑度评分机制，替代简陉的Lead权重

接口:
- summarize_topic(text: str, max_sentences: int = 3, max_chars: int = 280) -> dict
    返回: {
      'topic_summary': str,
      'key_points': list[str],
      'used_sentences': list[str],
      'tfidf_keywords': list[str],
      'stats': {'total_sentences': int, 'selected': int, 'compression_ratio': float}
    }

- extract_events(text: str, max_events: int = 8) -> list[dict]
    每条事件: {
      'snippet': str, 'position': int, 'time_hint': bool, 'numbers': int
    }

- batch_process(items: list[dict]) -> list[dict]
    items[i]: {'id': str, 'text': str}
    返回: [{'id': str, 'topic_summary': str, 'key_points': [...], 'events': [...]}]
"""

from typing import List, Dict, Set
import re
from collections import Counter
import math

# 句子分割: 支持中英文常见标点
_SENT_SPLIT = re.compile(r"[。！？!?；;]\s*|\n+|")
# 粗略时间指示词/模式(中文/英文常见)
_TIME_HINTS = [
    "年", "月", "日", "今天", "昨天", "明天", "此前", "之后", "期间",
    "today", "yesterday", "tomorrow", "week", "month", "year", "before", "after"
]

def _split_sentences(text: str) -> List[str]:
    text = text.strip()
    # 按常见分隔符切分, 同时保留较长片段
    parts = re.split(r"[。！？!?；;]\s*|\n+", text)
    # 清洗空白与过短片段
    sentences = [s.strip() for s in parts if s and len(s.strip()) > 0]
    return sentences

def _extract_tfidf_keywords(text: str, top_k: int = 10) -> List[str]:
    """【新增优化4】使用简化TF-IDF提取关键词"""
    # 分词（简化版：按空格和常见符号切分）
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    
    # 过滤停用词（简化版）
    stopwords = {'的', '了', '是', '在', '和', '与', '或', '等', '及', '为', '有', '个', '中', '这', '那',
                 'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    words = [w for w in words if w not in stopwords and len(w) > 1]
    
    if not words:
        return []
    
    # 计算词频（TF）
    word_count = Counter(words)
    total_words = len(words)
    tf_scores = {word: count / total_words for word, count in word_count.items()}
    
    # 简化IDF：按词频倒数加权（常见词权重低）
    idf_scores = {word: math.log(total_words / count) for word, count in word_count.items()}
    
    # TF-IDF得分
    tfidf_scores = {word: tf_scores[word] * idf_scores[word] for word in tf_scores}
    
    # 返回Top K关键词
    sorted_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
    return [word for word, score in sorted_keywords[:top_k]]

def _calculate_keyword_overlap(text1: str, text2: str, keywords: List[str] = None) -> float:
    """【新增优化5】计算两段文本的关键词重叠度"""
    if keywords:
        # 使用预提取的关键词
        words1 = set(re.findall(r'[\w\u4e00-\u9fff]+', text1.lower()))
        words2 = set(re.findall(r'[\w\u4e00-\u9fff]+', text2.lower()))
        keywords_set = set(keywords)
        
        # 计算关键词在两段文本中的出现情况
        overlap = len(keywords_set.intersection(words1).intersection(words2))
        total = len(keywords_set.intersection(words1.union(words2)))
        
        return overlap / total if total > 0 else 0.0
    else:
        # 简化版：直接比较词汇重叠
        words1 = set(re.findall(r'[\w\u4e00-\u9fff]+', text1.lower()))
        words2 = set(re.findall(r'[\w\u4e00-\u9fff]+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return overlap / union if union > 0 else 0.0

def _calculate_sentence_entropy(s: str) -> float:
    """【v2.0新增】计算句子的信息熄（香农熄）
    
    原理: H(X) = -∑ p(x) * log₂ p(x)
    高信息熄 = 信息量大 = 可能是核心句子
    """
    if not s or len(s) < 2:
        return 0.0
    
    # 统计字符频率（中英文混合）
    char_freq = Counter(s.lower())
    total_chars = len(s)
    
    # 计算信息熄
    entropy = 0.0
    for count in char_freq.values():
        probability = count / total_chars
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    # 正则化到[0, 1]范围（最大熄约为5-6）
    normalized_entropy = min(entropy / 6.0, 1.0)
    
    return normalized_entropy

def _calculate_sentence_perplexity(s: str, context: str = "") -> float:
    """【v2.0新增】计算句子的简化困惑度
    
    原理: 基于n-gram模型的简化困惑度估算
    低困惑度 = 语言流畅 = 表达清晰
    """
    if not s or len(s) < 2:
        return 1.0  # 默认低困惑度
    
    # 简化版：基于2-gram的频率估算
    words = re.findall(r'[\w\u4e00-\u9fff]+', s.lower())
    if len(words) < 2:
        return 0.5
    
    # 计算2-gram频率
    bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]
    bigram_freq = Counter(bigrams)
    
    # 简化困惑度：低频2-gram越多 = 困惑度越高
    rare_bigrams = sum(1 for count in bigram_freq.values() if count == 1)
    perplexity_score = rare_bigrams / len(bigrams) if bigrams else 0.5
    
    # 返回流畅度（困惑度的反向）
    fluency = 1.0 - perplexity_score
    
    return fluency

def _score_sentence(s: str, idx: int, total_sentences: int = 1, text_length: int = 0, 
                   tfidf_keywords: List[str] = None) -> float:
    """优化的启发式评分（v2.0：引入信息熄+困惑度机制）
    
    架构升级：
    - 信息熄：识别信息密度高的句子
    - 困惑度：识别表达清晰的句子
    - TF-IDF：识别核心术语
    - 位置：辅助权重（降低）
    """
    # 【v2.0核心】信息熄权重（最高3.0分）
    entropy = _calculate_sentence_entropy(s)
    entropy_weight = entropy * 3.0  # 高信息熄 = 高权重
    
    # 【v2.0核心】流畅度权重（最高2.0分）
    fluency = _calculate_sentence_perplexity(s)
    fluency_weight = fluency * 2.0  # 高流畅度 = 高权重
    
    # 【v2.0降级】Lead权重降为辅助（最高1.0分）
    lead_weight = 0.2 / (1 + idx * 0.3)  # 辅助权重
    
    # 数字/标点信号(可能包含事实/枚举)
    numbers = len(re.findall(r"\d", s))
    commas = s.count("，") + s.count(",") + s.count("；") + s.count(";")
    punct_weight = min((numbers + commas) * 0.15, 2.0)
    
    # 列表/要点指示符
    bullet_weight = 0.8 if re.match(r"^([\-•*·]|\d+\.|[（(]?\d+[）)])", s) else 0.0
    
    # 长度正则化(过长过短都降权)
    ln = len(s)
    length_weight = 1.0 if 30 <= ln <= 240 else 0.6
    
    # 语义关键词权重
    semantic_keywords = [
        '核心', '关键', '重要', '主要', '总结', '结论', '因此', '所以',
        '首先', '其次', '最后', '综上', '总之', '本质', '根本',
        'key', 'core', 'important', 'main', 'summary', 'conclusion',
        'therefore', 'thus', 'first', 'second', 'finally', 'essence'
    ]
    semantic_weight = sum(0.3 for kw in semantic_keywords if kw in s.lower())
    semantic_weight = min(semantic_weight, 1.5)
    
    # 逻辑连接词识别
    logic_connectors = [
        '因为', '所以', '但是', '然而', '如果', '那么', '导致', '基于',
        'because', 'therefore', 'but', 'however', 'if', 'then', 'due to', 'based on'
    ]
    logic_weight = 0.5 if any(conn in s.lower() for conn in logic_connectors) else 0.0
    
    # TF-IDF关键词权重（保持2.5分）
    keyword_weight = 0.0
    if tfidf_keywords:
        s_words = set(re.findall(r'[\w\u4e00-\u9fff]+', s.lower()))
        keyword_matches = len(s_words.intersection(set(tfidf_keywords)))
        keyword_weight = min(keyword_matches * 0.6, 2.5)
    
    # 【v2.0总分】信息熄(3.0) + 流畅度(2.0) + TF-IDF(2.5) + 其他辅助
    return entropy_weight + fluency_weight + lead_weight + punct_weight + bullet_weight + length_weight + semantic_weight + logic_weight + keyword_weight

def _collect_keypoints(sentences: List[str], top_k: int = 8) -> List[str]:
    """【优化2】增强关键点提取：不仅依赖符号，增加基于重要性的识别"""
    scored = []
    for i, s in enumerate(sentences):
        # 符号权重
        bullet = 1 if re.match(r"^([\-•*·]|\d+\.|[（(]?\d+[）)])", s) else 0
        numbers = len(re.findall(r"\d", s))
        
        # 【新增】语义重要性权重（即使没有符号也能识别关键点）
        semantic_keywords = ['核心', '关键', '重要', '主要', 'key', 'core', 'important', 'main']
        semantic_score = sum(0.5 for kw in semantic_keywords if kw in s.lower())
        
        # 【新增】句子长度合理性（20-150字符的句子更可能是关键点）
        length_score = 1.0 if 20 <= len(s) <= 150 else 0.3
        
        # 综合得分
        score = bullet * 2 + min(numbers, 3) + semantic_score + length_score
        scored.append((score, i, s))
    
    scored.sort(key=lambda x: (-x[0], x[1]))
    result = []
    used_idx = set()
    for score, i, s in scored:
        # 【优化】不再强制要求score > 0，允许低分但合理的关键点
        if i in used_idx:
            continue
        result.append(s)
        used_idx.add(i)
        if len(result) >= top_k:
            break
    return result

def summarize_topic(text: str, max_sentences: int = 3, max_chars: int = 280) -> Dict:
    """主题摘要生成（v2.0架构升级：信息熄+困惑度驱动）"""
    sentences = _split_sentences(text)
    if not sentences:
        return {
            'topic_summary': '',
            'key_points': [],
            'used_sentences': [],
            'stats': {'total_sentences': 0, 'selected': 0}
        }
    
    text_length = len(text)
    total_sentences = len(sentences)
    
    # 【优化4】提取TF-IDF关键词（用于增强句子评分）
    tfidf_keywords = _extract_tfidf_keywords(text, top_k=15)
    
    # 【架构修正】超长文本调用逻辑链分片器（>3000字符）
    if text_length > 3000:
        return _summarize_with_slicer(text, tfidf_keywords, max_chars)
    
    # 【优化3】根据原文长度动态调整压缩参数
    if text_length < 200:
        adaptive_max_sentences = 1
        target_compression_ratio = 0.4  # 短文本40%
    elif text_length < 500:
        adaptive_max_sentences = 2
        target_compression_ratio = 0.35  # 中等文本35%
    elif text_length < 2000:
        adaptive_max_sentences = max_sentences
        target_compression_ratio = 0.3  # 长文本30%
    else:
        # 【优化6】超长文本放宽压缩率，增加max_sentences
        adaptive_max_sentences = min(max_sentences + 2, 5)  # 最多5句
        target_compression_ratio = 0.4  # 超长文本40%（避免信息丢失）
    
    # 动态调整max_chars
    adaptive_max_chars = max(int(text_length * target_compression_ratio), 100)
    adaptive_max_chars = min(adaptive_max_chars, max_chars * 2)  # 超长文本允许超出默认上限
    
    # 评分并选取前N句（v1.5：移除强制位置多样性）
    scored = [(_score_sentence(s, i, total_sentences, text_length, tfidf_keywords), i, s) 
              for i, s in enumerate(sentences)]
    scored.sort(key=lambda x: (-x[0], x[1]))
    
    # 【v1.5修正】移除强制位置多样性，回归简单的按分数选句
    selected = []
    taken_idx = set()
    for score, i, s in scored:
        if i in taken_idx:
            continue
        selected.append(s)
        taken_idx.add(i)
        if len(selected) >= adaptive_max_sentences:
            break
    
    # 拼接并截断到目标长度
    summary = ' '.join(selected)
    if len(summary) > adaptive_max_chars:
        summary = summary[:adaptive_max_chars].rstrip() + '…'
    
    keypts = _collect_keypoints(sentences)
    
    # 【优化7】验证摘要质量：检查关键词覆盖率
    keyword_coverage = _calculate_keyword_overlap(text, summary, tfidf_keywords)
    
    return {
        'topic_summary': summary,
        'key_points': keypts,
        'used_sentences': selected,
        'tfidf_keywords': tfidf_keywords[:5],  # 返回前5个关键词供调试
        'stats': {
            'total_sentences': len(sentences), 
            'selected': len(selected),
            'original_length': text_length,
            'summary_length': len(summary),
            'compression_ratio': len(summary) / text_length if text_length > 0 else 0,
            'keyword_coverage': keyword_coverage  # 关键词覆盖率
        }
    }

def _summarize_with_slicer(text: str, tfidf_keywords: List[str], max_chars: int) -> Dict:
    """【架构修正】调用逻辑链分片器处理超长文本后再归纳"""
    try:
        # 动态导入逻辑链分片器
        from tools.memory_slicer_tool import MemorySlicerTool
        
        slicer = MemorySlicerTool()
        
        # 调用分片器（基于信息熄 + LLM困惑度）
        slices = slicer.slice_text(
            text=text,
            config={
                'size_thresholds': [2000, 1500, 1000],  # 超长文本用更大的阈值
                'max_recursion_depth': 8,
                'enable_entropy_analysis': True,  # 启用信息熄分析
                'enable_llm_refinement': False,  # 关闭LLM精炼（仅用算法分片）
                'enable_perplexity_analysis': True  # 启用困惑度分析
            }
        )
        
        if not slices:
            # 分片失败，降级到简化版分段摘要
            return _fallback_hierarchical_summarize(text, tfidf_keywords, max_chars)
        
        # 对每个分片生成摘要（每片选1句）
        slice_summaries = []
        for slice_data in slices[:5]:  # 最多取5个分片
            slice_text = slice_data.get('content', '')
            if not slice_text:
                continue
            
            # 对每个分片调用归纳引擎（递归调用）
            slice_summary = summarize_topic(slice_text, max_sentences=1, max_chars=200)
            if slice_summary['topic_summary']:
                slice_summaries.append(slice_summary['topic_summary'])
        
        # 合并分片摘要
        summary = ' '.join(slice_summaries)
        
        # 控制总长度（允许超长文本有更长的摘要）
        target_length = min(int(len(text) * 0.4), max_chars * 2)
        if len(summary) > target_length:
            summary = summary[:target_length].rstrip() + '…'
        
        # 提取关键点（使用原文）
        sentences = _split_sentences(text)
        keypts = _collect_keypoints(sentences)
        
        # 计算关键词覆盖率
        keyword_coverage = _calculate_keyword_overlap(text, summary, tfidf_keywords)
        
        return {
            'topic_summary': summary,
            'key_points': keypts,
            'used_sentences': slice_summaries,
            'tfidf_keywords': tfidf_keywords[:5],
            'stats': {
                'total_sentences': len(sentences),
                'selected': len(slice_summaries),
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text) if len(text) > 0 else 0,
                'keyword_coverage': keyword_coverage,
                'used_slicer': True,  # 标记使用了分片器
                'slices_count': len(slices)
            }
        }
        
    except Exception as e:
        # 分片器调用失败，降级到简化版
        import logging
        logging.warning(f"逻辑链分片器调用失败: {e}，降级到简化版")
        return _fallback_hierarchical_summarize(text, tfidf_keywords, max_chars)

def _fallback_hierarchical_summarize(text: str, tfidf_keywords: List[str], max_chars: int) -> Dict:
    """【降级方案】简化版分段摘要机制（当分片器失败时使用）"""
    sentences = _split_sentences(text)
    text_length = len(text)
    total_sentences = len(sentences)
    
    # 将文本分为3段（开头、中间、结尾）
    third = total_sentences // 3
    segments = [
        sentences[:third],           # 开头段
        sentences[third:third*2],    # 中间段
        sentences[third*2:]          # 结尾段
    ]
    
    # 为每段生成摘要（每段选1-2句）
    segment_summaries = []
    for seg_idx, segment in enumerate(segments):
        if not segment:
            continue
        
        # 对每段的句子评分
        scored = [(_score_sentence(s, i, len(segment), len(' '.join(segment)), tfidf_keywords), i, s) 
                  for i, s in enumerate(segment)]
        scored.sort(key=lambda x: (-x[0], x[1]))
        
        # 每段选1句（开头和结尾段可选2句）
        num_select = 2 if seg_idx in [0, 2] else 1
        for score, i, s in scored[:num_select]:
            segment_summaries.append(s)
    
    # 合并段落摘要
    summary = ' '.join(segment_summaries)
    
    # 控制总长度（允许超长文本有更长的摘要）
    target_length = min(int(text_length * 0.4), max_chars * 2)
    if len(summary) > target_length:
        summary = summary[:target_length].rstrip() + '…'
    
    # 提取关键点
    keypts = _collect_keypoints(sentences)
    
    # 计算关键词覆盖率
    keyword_coverage = _calculate_keyword_overlap(text, summary, tfidf_keywords)
    
    return {
        'topic_summary': summary,
        'key_points': keypts,
        'used_sentences': segment_summaries,
        'tfidf_keywords': tfidf_keywords[:5],
        'stats': {
            'total_sentences': total_sentences,
            'selected': len(segment_summaries),
            'original_length': text_length,
            'summary_length': len(summary),
            'compression_ratio': len(summary) / text_length if text_length > 0 else 0,
            'keyword_coverage': keyword_coverage,
            'hierarchical': True  # 标记使用了分段摘要
        }
    }

def extract_events(text: str, max_events: int = 8) -> List[Dict]:
    sentences = _split_sentences(text)
    events = []
    for i, s in enumerate(sentences):
        # 时间提示和数字计数
        time_hint = any(h in s for h in _TIME_HINTS)
        numbers = len(re.findall(r"\d", s))
        # 事件候选: 含动词/时间/数字的句子(启发式)
        verb_like = bool(re.search(r"(发生|进行|完成|开始|结束|推出|升级|发布|采用|实现)|\b(was|were|did|made|launched|adopted|updated|released)\b", s))
        score = (1.0 if verb_like else 0.0) + (0.8 if time_hint else 0.0) + min(numbers * 0.2, 1.0)
        if score >= 0.8:
            events.append({'snippet': s, 'position': i, 'time_hint': time_hint, 'numbers': numbers})
        if len(events) >= max_events:
            break
    return events

def batch_process(items: List[Dict]) -> List[Dict]:
    results = []
    for it in items:
        text = it.get('text', '') or ''
        rid = it.get('id') or ''
        summary = summarize_topic(text)
        events = extract_events(text)
        results.append({
            'id': rid,
            'topic_summary': summary['topic_summary'],
            'key_points': summary['key_points'],
            'events': events,
            'stats': summary['stats']
        })
    return results

if __name__ == '__main__':
    demo_text = (
        "我们在本季度完成了归纳引擎MVP的开发, 并在三个数据集上进行了初步验证。" 
        "昨天发布了v0.1版本, 采用启发式主题摘要与事件候选抽取, 后续将在夜间重构中评估其稳定性。"
        "接下来计划在两周内升级评分模型, 并引入人物维度的事件关联。"
    )
    print('== summarize_topic ==')
    print(summarize_topic(demo_text))
    print('== extract_events ==')
    print(extract_events(demo_text))
