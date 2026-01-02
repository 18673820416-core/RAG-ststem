# @self-expose: {"id": "context_deduplication_manager", "name": "Context Deduplication Manager", "type": "component", "version": "1.0.0", "needs": {"deps": ["vector_database", "agent_conversation_window"], "resources": []}, "provides": {"capabilities": ["上下文去重", "分层信息加载", "时间戳过滤"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上下文去重管理器
解决历史交互数据与向量库检索结果的重复信息问题

核心策略:
1. 【新鲜期】0-15分钟: 仅从历史上下文加载(原始完整对话)
2. 【过渡期】15-30分钟: 优先从向量库检索,历史上下文保留最近3-5轮
3. 【长期记忆】30分钟+: 完全依赖向量库检索

去重方法:
- 时间戳去重(首选)
- 内容哈希去重(降级)
- 向量库检索时间过滤(最优雅)
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

class ContextDeduplicationManager:
    """上下文去重管理器"""
    
    def __init__(
        self,
        history_window_minutes: int = 15,
        kg_cache_interval_minutes: int = 5
    ):
        """
        初始化去重管理器
        
        Args:
            history_window_minutes: 历史上下文时间窗口(分钟),默认15分钟
            kg_cache_interval_minutes: 知识图谱缓存间隔(分钟),默认5分钟
        """
        self.history_window_minutes = history_window_minutes
        self.kg_cache_interval_minutes = kg_cache_interval_minutes
        self.logger = logging.getLogger(__name__)
    
    def build_deduplicated_context(
        self,
        query: str,
        history_context: List[Dict[str, Any]],
        retrieval_results: Optional[List[Dict[str, Any]]] = None,
        enable_retrieval: bool = True
    ) -> str:
        """
        构建去重后的上下文(核心方法)
        
        策略:
        1. 历史上下文优先(0-15分钟内的原始对话)
        2. 向量库检索补充(15分钟外的长期记忆)
        3. 时间戳去重,避免信息重复
        
        Args:
            query: 用户查询
            history_context: 历史对话上下文(来自时间窗口)
            retrieval_results: 向量库检索结果(可选)
            enable_retrieval: 是否启用向量库检索
        
        Returns:
            去重后的上下文字符串
        """
        context_parts = []
        history_timestamps = set()
        
        # 1. 加载历史上下文(新鲜期信息)
        if history_context:
            context_parts.append("## 📝 近期对话历史\n")
            for entry in history_context:
                timestamp_str = entry.get('timestamp', '')
                if timestamp_str:
                    history_timestamps.add(timestamp_str)
                
                message = entry.get('message', '')
                response = entry.get('response', '')
                role = entry.get('agent_role', 'unknown')
                
                context_parts.append(
                    f"[{timestamp_str}] **{role}**: {message}\n"
                    f"→ {response}\n"
                )
            
            self.logger.info(
                f"✅ 历史上下文加载完成: {len(history_context)}条对话, "
                f"时间窗口: {self.history_window_minutes}分钟"
            )
        
        # 2. 加载向量库检索结果(长期记忆)
        if enable_retrieval and retrieval_results:
            # 时间戳去重
            deduplicated_memories = []
            for memory in retrieval_results:
                mem_timestamp = memory.get('timestamp', '')
                
                # 跳过历史上下文中已有的记忆
                if mem_timestamp and mem_timestamp in history_timestamps:
                    continue
                
                deduplicated_memories.append(memory)
            
            if deduplicated_memories:
                context_parts.append("\n## 🧠 相关长期记忆\n")
                for memory in deduplicated_memories:
                    timestamp = memory.get('timestamp', '')
                    content = memory.get('content', '')
                    source = memory.get('source_type', 'unknown')
                    importance = memory.get('importance', 0.5)
                    
                    context_parts.append(
                        f"[{timestamp}] **{source}** (重要性:{importance:.2f})\n"
                        f"{content}\n"
                    )
                
                self.logger.info(
                    f"✅ 向量库检索加载完成: {len(deduplicated_memories)}条记忆 "
                    f"(去重后,原始{len(retrieval_results)}条)"
                )
            else:
                self.logger.info(
                    "⚠️ 向量库检索结果全部与历史上下文重复,已过滤"
                )
        
        return "\n".join(context_parts)
    
    def deduplicate_by_timestamp(
        self,
        history_items: List[Dict[str, Any]],
        retrieval_items: List[Dict[str, Any]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        基于时间戳去重
        
        策略: 优先保留历史上下文(更新鲜),过滤向量库中的重复项
        
        Returns:
            (history_items, deduplicated_retrieval_items)
        """
        history_timestamps = {
            item.get('timestamp', '') 
            for item in history_items 
            if item.get('timestamp')
        }
        
        deduplicated = []
        duplicated_count = 0
        
        for item in retrieval_items:
            timestamp = item.get('timestamp', '')
            if timestamp and timestamp not in history_timestamps:
                deduplicated.append(item)
            else:
                duplicated_count += 1
        
        self.logger.debug(
            f"时间戳去重完成: 保留{len(deduplicated)}条, "
            f"过滤{duplicated_count}条重复记忆"
        )
        
        return history_items, deduplicated
    
    def deduplicate_by_content_hash(
        self,
        history_items: List[Dict[str, Any]],
        retrieval_items: List[Dict[str, Any]]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        基于内容哈希去重(降级方案)
        
        用于时间戳不可用或不精确的场景
        
        Returns:
            List[(source, item)] - source为'history'或'retrieval'
        """
        seen_hashes = set()
        deduplicated = []
        
        # 优先处理历史上下文(更新鲜)
        for item in history_items:
            content = item.get('message', '') + item.get('response', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduplicated.append(('history', item))
        
        # 再处理向量库检索结果
        for item in retrieval_items:
            content = item.get('content', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduplicated.append(('retrieval', item))
        
        self.logger.debug(
            f"内容哈希去重完成: 保留{len(deduplicated)}条, "
            f"原始{len(history_items) + len(retrieval_items)}条"
        )
        
        return deduplicated
    
    def get_retrieval_time_filter(self) -> Dict[str, str]:
        """
        生成向量库检索的时间过滤条件
        
        策略: 只检索历史窗口外的记忆(避免与历史上下文重复)
        
        Returns:
            时间过滤条件字典,格式: {"end_time": "ISO时间戳"}
        """
        cutoff_time = datetime.now() - timedelta(minutes=self.history_window_minutes)
        
        return {
            "end_time": cutoff_time.isoformat()
        }
    
    def analyze_context_statistics(
        self,
        history_context: List[Dict[str, Any]],
        retrieval_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析上下文统计信息(调试用)
        
        Returns:
            统计信息字典
        """
        history_count = len(history_context)
        retrieval_count = len(retrieval_results)
        
        # 统计重叠数量
        history_timestamps = {
            item.get('timestamp', '') 
            for item in history_context 
            if item.get('timestamp')
        }
        
        overlap_count = sum(
            1 for item in retrieval_results
            if item.get('timestamp') in history_timestamps
        )
        
        return {
            "history_count": history_count,
            "retrieval_count": retrieval_count,
            "overlap_count": overlap_count,
            "effective_retrieval_count": retrieval_count - overlap_count,
            "total_unique_count": history_count + retrieval_count - overlap_count,
            "overlap_rate": overlap_count / retrieval_count if retrieval_count > 0 else 0.0,
            "history_window_minutes": self.history_window_minutes,
        }


# 全局单例
_dedup_manager_instance = None

def get_dedup_manager(
    history_window_minutes: int = 15,
    kg_cache_interval_minutes: int = 5
) -> ContextDeduplicationManager:
    """获取去重管理器单例"""
    global _dedup_manager_instance
    
    if _dedup_manager_instance is None:
        _dedup_manager_instance = ContextDeduplicationManager(
            history_window_minutes=history_window_minutes,
            kg_cache_interval_minutes=kg_cache_interval_minutes
        )
    
    return _dedup_manager_instance


if __name__ == "__main__":
    # 测试去重功能
    logging.basicConfig(level=logging.INFO)
    
    manager = ContextDeduplicationManager(history_window_minutes=15)
    
    # 模拟历史上下文
    history = [
        {
            "timestamp": "2025-12-09T18:00:00",
            "message": "如何实现知识图谱持久化?",
            "response": "采用半静态策略...",
            "agent_role": "architect"
        },
        {
            "timestamp": "2025-12-09T18:05:00",
            "message": "时间窗口应该设置多长?",
            "response": "建议15分钟,知识图谱缓存5分钟×3倍安全系数",
            "agent_role": "architect"
        }
    ]
    
    # 模拟向量库检索结果(包含重复项)
    retrieval = [
        {
            "timestamp": "2025-12-09T18:00:00",  # 重复
            "content": "如何实现知识图谱持久化? 采用半静态策略...",
            "source_type": "chatroom_interaction",
            "importance": 0.8
        },
        {
            "timestamp": "2025-12-09T17:30:00",  # 不重复
            "content": "向量库应使用Chroma或FAISS",
            "source_type": "knowledge_base",
            "importance": 0.6
        }
    ]
    
    # 构建去重上下文
    context = manager.build_deduplicated_context(
        query="如何优化系统性能?",
        history_context=history,
        retrieval_results=retrieval
    )
    
    print("=" * 80)
    print("去重后的上下文:")
    print("=" * 80)
    print(context)
    print("=" * 80)
    
    # 统计分析
    stats = manager.analyze_context_statistics(history, retrieval)
    print("\n统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
