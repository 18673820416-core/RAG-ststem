#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件维度编码索引系统
基于逻辑链完整性的切片逻辑，实现宏观-中观-微观三层检索架构

核心思想：
1. 一次切片：逻辑链完整性 → 事件切片（原因+推导+结果）
2. 二次切片：序列号+因果关系 → 完整逻辑链
3. 事件维度：同类事件切片构成最下级知识图谱
4. 图谱合并：下级图谱合并成上级知识图谱
5. 森林结构：构成完整的知识森林检索系统

检索流程：
宏观：LLM查看最上级图谱 → 判断所需上下文在哪个二级图谱
中观：在二级图谱中查找事件
微观：找到事件后构成完整上下文
"""
# @self-expose: {"id": "event_dimension_encoder", "name": "Event Dimension Encoder", "type": "component", "version": "1.0.0", "needs": {"deps": ["database_manager"], "resources": []}, "provides": {"capabilities": ["Event Dimension Encoder功能"]}}

import sqlite3
import json
import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from config.system_config import DATABASE_PATH
from src.database_manager import get_database_manager

class EventType(Enum):
    """事件类型枚举"""
    CONVERSATION = "conversation"      # 对话事件
    LEARNING = "learning"              # 学习事件
    CREATION = "creation"              # 创作事件
    ANALYSIS = "analysis"               # 分析事件
    DECISION = "decision"              # 决策事件
    DISCOVERY = "discovery"            # 发现事件

@dataclass
class EventChain:
    """事件链数据结构"""
    chain_id: str
    title: str
    description: str
    event_type: EventType
    start_time: datetime
    end_time: datetime
    logical_completeness: float  # 逻辑链完整性评分 (0-1)
    theme_codes: List[str]      # 主题编码列表
    related_memories: List[str] # 相关记忆ID列表
    parent_chain: Optional[str] = None  # 父事件链ID
    sub_chains: List[str] = None       # 子事件链ID列表
    
    def __post_init__(self):
        if self.sub_chains is None:
            self.sub_chains = []

class EventDimensionEncoder:
    """事件维度编码索引器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_manager = get_database_manager()
        self._initialize_event_tables()
    
    def _initialize_event_tables(self):
        """初始化事件维度相关表结构"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 事件链表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_chains (
                chain_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                event_type TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                logical_completeness FLOAT DEFAULT 0.5,
                theme_codes TEXT,  -- JSON格式的主题编码列表
                related_memories TEXT,  -- JSON格式的相关记忆ID列表
                parent_chain TEXT,
                sub_chains TEXT,  -- JSON格式的子事件链ID列表
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 事件-记忆关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_memory_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_chain_id TEXT NOT NULL,
                memory_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,  -- cause, effect, context, etc.
                relation_strength FLOAT DEFAULT 0.5,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_chain_id) REFERENCES event_chains(chain_id),
                FOREIGN KEY (memory_id) REFERENCES memory_units(id)
            )
        """)
        
        # 事件时间线索引
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_timeline (
                event_chain_id TEXT PRIMARY KEY,
                timeline_position INTEGER,  -- 时间线位置（用于排序）
                timeline_depth INTEGER DEFAULT 1,  -- 时间线深度
                FOREIGN KEY (event_chain_id) REFERENCES event_chains(chain_id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON event_chains(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_time ON event_chains(start_time, end_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_completeness ON event_chains(logical_completeness)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_memory ON event_memory_relations(memory_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_position ON event_timeline(timeline_position)")
        
        conn.commit()
    
    def extract_event_codes_from_memory(self, memory_data: Dict[str, Any]) -> List[str]:
        """从记忆数据中提取事件编码"""
        event_codes = []
        
        # 从主题中提取编码
        topic = memory_data.get('topic', '')
        if topic:
            # 将主题转换为编码格式（例如：AI技术 -> ai_tech）
            event_code = self._normalize_event_code(topic)
            event_codes.append(event_code)
        
        # 从标签中提取编码
        tags = memory_data.get('tags', [])
        for tag in tags:
            event_code = self._normalize_event_code(tag)
            event_codes.append(event_code)
        
        # 从内容中提取关键词作为事件编码
        content = memory_data.get('content', '')
        if content:
            keywords = self._extract_keywords(content)
            for keyword in keywords:
                event_code = self._normalize_event_code(keyword)
                event_codes.append(event_code)
        
        # 去重并返回
        return list(set(event_codes))
    
    def _normalize_event_code(self, text: str) -> str:
        """标准化事件编码格式"""
        # 转换为小写，替换空格为下划线，移除特殊字符
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        return normalized
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """从文本中提取关键词（简化实现）"""
        # 这里可以集成更复杂的关键词提取算法
        # 目前使用简单的频率统计
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # 过滤停用词（简化版）
        stop_words = {'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'this', 'that', 'these', 'those'}
        filtered_words = [word for word in words if word not in stop_words]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的关键词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def calculate_logical_completeness(self, memories: List[Dict[str, Any]]) -> float:
        """计算逻辑链完整性评分"""
        if not memories:
            return 0.0
        
        # 基于以下因素计算逻辑链完整性：
        # 1. 时间连续性
        # 2. 主题一致性
        # 3. 因果关系强度
        # 4. 信息完整性
        
        completeness_score = 0.0
        
        # 时间连续性评分（20%）
        time_score = self._calculate_time_continuity(memories)
        completeness_score += time_score * 0.2
        
        # 事件一致性评分（30%）
        event_score = self._calculate_event_consistency(memories)
        completeness_score += event_score * 0.3
        
        # 因果关系评分（30%）
        causality_score = self._calculate_causality_strength(memories)
        completeness_score += causality_score * 0.3
        
        # 信息完整性评分（20%）
        info_score = self._calculate_information_completeness(memories)
        completeness_score += info_score * 0.2
        
        return min(completeness_score, 1.0)
    
    def _calculate_time_continuity(self, memories: List[Dict[str, Any]]) -> float:
        """计算时间连续性评分"""
        if len(memories) < 2:
            return 1.0  # 单个记忆时间连续性为满分
        
        # 提取时间戳并排序
        timestamps = []
        for memory in memories:
            timestamp_str = memory.get('timestamp', '')
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
            except:
                continue
        
        if len(timestamps) < 2:
            return 0.5  # 无法计算时间连续性
        
        timestamps.sort()
        
        # 计算时间间隔的连续性
        total_gap = 0
        max_gap = 0
        
        for i in range(1, len(timestamps)):
            gap = (timestamps[i] - timestamps[i-1]).total_seconds()
            total_gap += gap
            max_gap = max(max_gap, gap)
        
        # 平均间隔越小，连续性越好
        avg_gap = total_gap / (len(timestamps) - 1)
        
        # 归一化评分（假设最大可接受间隔为1天）
        max_acceptable_gap = 24 * 3600  # 1天
        continuity_score = max(0, 1 - (avg_gap / max_acceptable_gap))
        
        return continuity_score
    
    def _calculate_event_consistency(self, memories: List[Dict[str, Any]]) -> float:
        """计算事件一致性评分"""
        if not memories:
            return 0.0
        
        # 提取所有记忆的事件编码
        all_event_codes = []
        for memory in memories:
            event_codes = self.extract_event_codes_from_memory(memory)
            all_event_codes.extend(event_codes)
        
        if not all_event_codes:
            return 0.5  # 无事件信息
        
        # 计算事件分布的熵（熵越小，一致性越好）
        event_counts = {}
        for event in all_event_codes:
            event_counts[event] = event_counts.get(event, 0) + 1
        
        total_events = len(all_event_codes)
        entropy = 0.0
        
        for count in event_counts.values():
            probability = count / total_events
            entropy -= probability * (probability and math.log(probability) or 0)
        
        # 归一化熵值（最大熵为log(n)，n为事件数量）
        max_entropy = math.log(len(event_counts)) if len(event_counts) > 0 else 1
        if max_entropy == 0:
            consistency_score = 1.0  # 只有一个事件，一致性最高
        else:
            consistency_score = max(0, 1 - (entropy / max_entropy))
        
        return consistency_score
    
    def _calculate_causality_strength(self, memories: List[Dict[str, Any]]) -> float:
        """计算因果关系强度评分（简化实现）"""
        # 这里可以集成更复杂的因果关系分析
        # 目前基于关键词的因果关系模式匹配
        
        causality_patterns = [
            (r'(因为|由于|原因是)', 'cause'),
            (r'(所以|因此|结果是|导致)', 'effect'),
            (r'(首先|然后|接着|最后)', 'sequence'),
            (r'(如果|假如|假设)', 'condition'),
            (r'(但是|然而|不过)', 'contrast')
        ]
        
        causality_count = 0
        total_sentences = 0
        
        for memory in memories:
            content = memory.get('content', '')
            sentences = re.split(r'[.!?。！？]', content)
            
            for sentence in sentences:
                if len(sentence.strip()) > 10:  # 只分析有意义的句子
                    total_sentences += 1
                    for pattern, relation_type in causality_patterns:
                        if re.search(pattern, sentence):
                            causality_count += 1
                            break
        
        if total_sentences == 0:
            return 0.3  # 无句子可分析
        
        causality_score = causality_count / total_sentences
        return min(causality_score, 1.0)
    
    def _calculate_information_completeness(self, memories: List[Dict[str, Any]]) -> float:
        """计算信息完整性评分"""
        if not memories:
            return 0.0
        
        # 基于以下因素：
        # 1. 记忆内容的丰富程度
        # 2. 主题覆盖的广度
        # 3. 时间跨度的合理性
        
        total_score = 0.0
        
        # 内容丰富度（40%）
        content_score = 0.0
        for memory in memories:
            content = memory.get('content', '')
            content_length = len(content)
            # 内容长度在合理范围内得分更高
            if 50 <= content_length <= 1000:
                content_score += 0.8
            elif content_length > 1000:
                content_score += 0.6
            else:
                content_score += 0.3
        
        content_score = content_score / len(memories)
        total_score += content_score * 0.4
        
        # 事件覆盖广度（30%）
        all_events = set()
        for memory in memories:
            event_codes = self.extract_event_codes_from_memory(memory)
            all_events.update(event_codes)
        
        event_coverage = min(len(all_events) / 10, 1.0)  # 假设10个事件为完整覆盖
        total_score += event_coverage * 0.3
        
        # 时间跨度合理性（30%）
        timestamps = []
        for memory in memories:
            timestamp_str = memory.get('timestamp', '')
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
            except:
                continue
        
        if len(timestamps) >= 2:
            time_span = max(timestamps) - min(timestamps)
            # 时间跨度在1小时到30天之间为合理
            if timedelta(hours=1) <= time_span <= timedelta(days=30):
                time_score = 0.9
            elif time_span < timedelta(hours=1):
                time_score = 0.6  # 时间跨度太短
            else:
                time_score = 0.7  # 时间跨度太长
        else:
            time_score = 0.5  # 无法计算时间跨度
        
        total_score += time_score * 0.3
        
        return total_score
    
    def create_event_chain(self, 
                         title: str,
                         description: str,
                         event_type: EventType,
                         related_memories: List[Dict[str, Any]],
                         start_time: datetime = None,
                         end_time: datetime = None,
                         parent_chain: str = None) -> EventChain:
        """创建事件链"""
        
        # 自动确定时间范围
        if not start_time or not end_time:
            start_time, end_time = self._determine_time_range(related_memories)
        
        # 计算逻辑链完整性
        logical_completeness = self.calculate_logical_completeness(related_memories)
        
        # 提取事件编码
        event_codes = []
        for memory in related_memories:
            codes = self.extract_event_codes_from_memory(memory)
            event_codes.extend(codes)
        event_codes = list(set(event_codes))
        
        # 生成事件链ID
        chain_id = f"event_chain_{hash(str(event_codes) + str(start_time))}"
        
        # 提取相关记忆ID
        memory_ids = [memory.get('id', '') for memory in related_memories if memory.get('id')]
        
        # 创建事件链对象
        event_chain = EventChain(
            chain_id=chain_id,
            title=title,
            description=description,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            logical_completeness=logical_completeness,
            theme_codes=event_codes,
            related_memories=memory_ids,
            parent_chain=parent_chain
        )
        
        # 保存到数据库
        self._save_event_chain(event_chain)
        
        return event_chain
    
    def _determine_time_range(self, memories: List[Dict[str, Any]]) -> Tuple[datetime, datetime]:
        """根据记忆数据确定时间范围"""
        timestamps = []
        
        for memory in memories:
            timestamp_str = memory.get('timestamp', '')
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
            except:
                continue
        
        if timestamps:
            start_time = min(timestamps)
            end_time = max(timestamps)
        else:
            # 如果没有时间信息，使用当前时间
            current_time = datetime.now()
            start_time = current_time - timedelta(hours=1)
            end_time = current_time
        
        return start_time, end_time
    
    def _save_event_chain(self, event_chain: EventChain):
        """保存事件链到数据库"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO event_chains 
            (chain_id, title, description, event_type, start_time, end_time, 
             logical_completeness, theme_codes, related_memories, parent_chain, sub_chains)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_chain.chain_id,
            event_chain.title,
            event_chain.description,
            event_chain.event_type.value,
            event_chain.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            event_chain.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            event_chain.logical_completeness,
            json.dumps(event_chain.theme_codes, ensure_ascii=False),
            json.dumps(event_chain.related_memories, ensure_ascii=False),
            event_chain.parent_chain,
            json.dumps(event_chain.sub_chains, ensure_ascii=False)
        ))
        
        # 更新时间线索引
        cursor.execute("""
            INSERT OR REPLACE INTO event_timeline 
            (event_chain_id, timeline_position, timeline_depth)
            VALUES (?, ?, ?)
        """, (
            event_chain.chain_id,
            int(event_chain.start_time.timestamp()),
            1 if not event_chain.parent_chain else 2  # 子事件链深度为2
        ))
        
        conn.commit()
    
    def search_event_chains(self, 
                          query: str = None,
                          event_type: EventType = None,
                          start_time: datetime = None,
                          end_time: datetime = None,
                          min_completeness: float = 0.3,
                          theme_codes: List[str] = None,
                          limit: int = 10) -> List[EventChain]:
        """搜索事件链"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        conditions = ["logical_completeness >= ?"]
        params = [min_completeness]
        
        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type.value)
        
        if start_time:
            conditions.append("start_time >= ?")
            params.append(start_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        if end_time:
            conditions.append("end_time <= ?")
            params.append(end_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        if theme_codes:
            # 使用JSON函数搜索主题编码
            theme_conditions = []
            for theme in theme_codes:
                theme_conditions.append("json_extract(theme_codes, '$') LIKE ?")
                params.append(f'%"{theme}"%')
            conditions.append(f"({' OR '.join(theme_conditions)})")
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT chain_id, title, description, event_type, start_time, end_time,
                   logical_completeness, theme_codes, related_memories, parent_chain, sub_chains
            FROM event_chains
            WHERE {where_clause}
            ORDER BY logical_completeness DESC, start_time DESC
            LIMIT ?
        """
        
        params.append(limit)
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            event_chain = EventChain(
                chain_id=row[0],
                title=row[1],
                description=row[2],
                event_type=EventType(row[3]),
                start_time=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S'),
                end_time=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
                logical_completeness=row[6],
                theme_codes=json.loads(row[7]) if row[7] else [],
                related_memories=json.loads(row[8]) if row[8] else [],
                parent_chain=row[9],
                sub_chains=json.loads(row[10]) if row[10] else []
            )
            results.append(event_chain)
        
        return results
    
    def get_event_timeline(self, depth: int = 1) -> List[EventChain]:
        """获取事件时间线"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ec.chain_id, ec.title, ec.description, ec.event_type, 
                   ec.start_time, ec.end_time, ec.logical_completeness,
                   ec.theme_codes, ec.related_memories, ec.parent_chain, ec.sub_chains
            FROM event_chains ec
            JOIN event_timeline et ON ec.chain_id = et.event_chain_id
            WHERE et.timeline_depth <= ?
            ORDER BY et.timeline_position ASC
        """, (depth,))
        
        results = []
        for row in cursor.fetchall():
            event_chain = EventChain(
                chain_id=row[0],
                title=row[1],
                description=row[2],
                event_type=EventType(row[3]),
                start_time=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S'),
                end_time=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
                logical_completeness=row[6],
                theme_codes=json.loads(row[7]) if row[7] else [],
                related_memories=json.loads(row[8]) if row[8] else [],
                parent_chain=row[9],
                sub_chains=json.loads(row[10]) if row[10] else []
            )
            results.append(event_chain)
        
        return results
    
    def build_event_knowledge_graph(self, event_chains: List[EventChain]) -> Dict[str, Any]:
        """构建事件知识图谱"""
        graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'total_events': len(event_chains),
                'time_span': None,
                'theme_coverage': set(),
                'logical_completeness_avg': 0.0
            }
        }
        
        if not event_chains:
            return graph
        
        # 计算元数据
        total_completeness = 0.0
        all_themes = set()
        start_times = []
        end_times = []
        
        # 添加节点
        for event_chain in event_chains:
            node = {
                'id': event_chain.chain_id,
                'type': 'event',
                'label': event_chain.title,
                'event_type': event_chain.event_type.value,
                'start_time': event_chain.start_time.isoformat(),
                'end_time': event_chain.end_time.isoformat(),
                'logical_completeness': event_chain.logical_completeness,
                'theme_codes': event_chain.theme_codes,
                'related_memories_count': len(event_chain.related_memories)
            }
            graph['nodes'].append(node)
            
            # 更新元数据
            total_completeness += event_chain.logical_completeness
            all_themes.update(event_chain.theme_codes)
            start_times.append(event_chain.start_time)
            end_times.append(event_chain.end_time)
        
        # 添加边（事件间的关系）
        for i, event1 in enumerate(event_chains):
            for j, event2 in enumerate(event_chains):
                if i != j:
                    # 计算事件间的关系强度
                    relation_strength = self._calculate_event_relation(event1, event2)
                    if relation_strength > 0.3:  # 只添加较强的关系
                        edge = {
                            'source': event1.chain_id,
                            'target': event2.chain_id,
                            'relation_type': 'temporal_causal',
                            'strength': relation_strength
                        }
                        graph['edges'].append(edge)
        
        # 更新元数据
        graph['metadata']['logical_completeness_avg'] = total_completeness / len(event_chains)
        graph['metadata']['theme_coverage'] = list(all_themes)
        
        if start_times and end_times:
            graph['metadata']['time_span'] = {
                'start': min(start_times).isoformat(),
                'end': max(end_times).isoformat(),
                'duration_days': (max(end_times) - min(start_times)).days
            }
        
        return graph
    
    def _calculate_event_relation(self, event1: EventChain, event2: EventChain) -> float:
        """计算两个事件间的关系强度"""
        relation_score = 0.0
        
        # 时间关系（40%）
        time_overlap = self._calculate_time_overlap(event1, event2)
        relation_score += time_overlap * 0.4
        
        # 主题相似度（40%）
        theme_similarity = self._calculate_theme_similarity(event1, event2)
        relation_score += theme_similarity * 0.4
        
        # 因果关系（20%）
        causality = self._calculate_causality(event1, event2)
        relation_score += causality * 0.2
        
        return relation_score
    
    def _calculate_time_overlap(self, event1: EventChain, event2: EventChain) -> float:
        """计算时间重叠度"""
        # 计算两个事件时间范围的重叠程度
        latest_start = max(event1.start_time, event2.start_time)
        earliest_end = min(event1.end_time, event2.end_time)
        
        if latest_start < earliest_end:
            overlap = (earliest_end - latest_start).total_seconds()
            duration1 = (event1.end_time - event1.start_time).total_seconds()
            duration2 = (event2.end_time - event2.start_time).total_seconds()
            
            # 重叠度取两个事件重叠部分的最大比例
            overlap_ratio1 = overlap / duration1 if duration1 > 0 else 0
            overlap_ratio2 = overlap / duration2 if duration2 > 0 else 0
            
            return max(overlap_ratio1, overlap_ratio2)
        
        return 0.0
    
    def _calculate_theme_similarity(self, event1: EventChain, event2: EventChain) -> float:
        """计算主题相似度"""
        themes1 = set(event1.theme_codes)
        themes2 = set(event2.theme_codes)
        
        if not themes1 or not themes2:
            return 0.0
        
        intersection = themes1.intersection(themes2)
        union = themes1.union(themes2)
        
        return len(intersection) / len(union)
    
    def _calculate_causality(self, event1: EventChain, event2: EventChain) -> float:
        """计算因果关系（简化实现）"""
        # 基于时间顺序和主题连续性判断因果关系
        causality_score = 0.0
        
        # 如果event1在event2之前，且主题有连续性
        if event1.end_time < event2.start_time:
            # 检查主题连续性
            common_themes = set(event1.theme_codes).intersection(set(event2.theme_codes))
            if common_themes:
                causality_score += 0.5
            
            # 检查时间间隔（间隔越短，因果关系越强）
            time_gap = (event2.start_time - event1.end_time).total_seconds()
            max_gap = 7 * 24 * 3600  # 一周
            if time_gap <= max_gap:
                causality_score += 0.5 * (1 - time_gap / max_gap)
        
        return causality_score

def main():
    """测试事件维度编码索引功能"""
    encoder = EventDimensionEncoder()
    
    # 创建测试记忆数据
    test_memories = [
        {
            'id': 'mem_test_1',
            'topic': 'AI技术发展',
            'content': '深度学习技术在图像识别领域取得了重大突破，准确率超过人类水平。',
            'source_type': 'research',
            'timestamp': '2024-01-15 10:00:00',
            'importance': 0.8,
            'confidence': 0.9,
            'tags': ['AI', '深度学习', '图像识别']
        },
        {
            'id': 'mem_test_2',
            'topic': '自然语言处理进展',
            'content': '大语言模型在自然语言理解任务上表现出色，能够进行复杂的推理。',
            'source_type': 'research',
            'timestamp': '2024-01-20 14:30:00',
            'importance': 0.7,
            'confidence': 0.8,
            'tags': ['NLP', '大语言模型', '推理']
        },
        {
            'id': 'mem_test_3',
            'topic': 'AI应用场景',
            'content': 'AI技术正在医疗、金融、教育等多个领域得到广泛应用。',
            'source_type': 'analysis',
            'timestamp': '2024-01-25 09:15:00',
            'importance': 0.6,
            'confidence': 0.85,
            'tags': ['AI应用', '医疗', '金融']
        }
    ]
    
    # 创建事件链
    event_chain = encoder.create_event_chain(
        title="AI技术发展时间线",
        description="记录AI技术从深度学习到应用的发展过程",
        event_type=EventType.DISCOVERY,
        related_memories=test_memories
    )
    
    print(f"创建事件链成功: {event_chain.title}")
    print(f"逻辑链完整性: {event_chain.logical_completeness:.2f}")
    print(f"主题编码: {event_chain.theme_codes}")
    
    # 搜索事件链
    results = encoder.search_event_chains(
        query="AI技术",
        event_type=EventType.DISCOVERY,
        min_completeness=0.5
    )
    
    print(f"\n搜索到 {len(results)} 个相关事件链")
    
    # 构建事件知识图谱
    event_graph = encoder.build_event_knowledge_graph(results)
    print(f"\n事件知识图谱统计:")
    print(f"节点数: {len(event_graph['nodes'])}")
    print(f"边数: {len(event_graph['edges'])}")
    print(f"平均逻辑完整性: {event_graph['metadata']['logical_completeness_avg']:.2f}")
    
    # 获取事件时间线
    timeline = encoder.get_event_timeline(depth=1)
    print(f"\n事件时间线包含 {len(timeline)} 个事件")
    
    print("\n✅ 事件维度编码索引功能测试完成！")

if __name__ == "__main__":
    main()