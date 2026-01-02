#!/usr/bin/env python3
# @self-expose: {"id": "system_statistics_service", "name": "System Statistics Service", "type": "service", "version": "1.0.1", "needs": {"deps": ["mesh_database_interface", "vector_database", "mesh_thought_engine"], "resources": []}, "provides": {"capabilities": ["统一数据源管理", "系统统计数据计算", "单一数据源真相"]}}
"""
系统统计服务 - 唯一数据源（Single Source of Truth）

功能：
1. 提供系统级统计数据的唯一计算来源
2. 避免多处重复计算导致的数据不一致
3. 确保所有组件引用相同的统计数据

设计原则：
- 所有统计数据都从这个服务获取
- 禁止在其他地方重复计算相同的数据
- 数据源：MeshDatabaseInterface.build_knowledge_graph()
"""

from typing import Dict, Any, Optional
from datetime import datetime


class SystemStatisticsService:
    """系统统计服务 - 单一数据源（半静态知识图谱策略）"""
    
    def __init__(self):
        self._cached_stats = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 缓存5分钟（避免频繁IO）
        
        # 知识图谱持久化路径
        import os
        self._kg_cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_graph_cache')
        self._kg_cache_file = os.path.join(self._kg_cache_dir, 'global_knowledge_graph.json')
        os.makedirs(self._kg_cache_dir, exist_ok=True)
    
    def get_system_statistics(self, force_refresh: bool = False, force_rebuild_kg: bool = False) -> Dict[str, Any]:
        """
        获取系统统计数据（唯一数据源）
        
        Args:
            force_refresh: 是否强制刷新缓存
            force_rebuild_kg: 是否强制重建知识图谱（记忆重构时调用）
        
        Returns:
            统一的系统统计数据字典
        """
        # 检查缓存
        if not force_refresh and not force_rebuild_kg and self._is_cache_valid():
            return self._cached_stats
        
        # 重新计算统计数据
        stats = self._calculate_statistics(force_rebuild_kg=force_rebuild_kg)
        
        # 更新缓存
        self._cached_stats = stats
        self._cache_timestamp = datetime.now()
        
        return stats
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._cached_stats is None or self._cache_timestamp is None:
            return False
        
        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed < self._cache_ttl
    
    def _calculate_statistics(self, force_rebuild_kg: bool = False) -> Dict[str, Any]:
        """
        计算系统统计数据（半静态知识图谱策略）
        
        Args:
            force_rebuild_kg: 是否强制重建知识图谱（记忆重构时使用）
        
        ✅ 策略：
        1. 优先从持久化文件加载知识图谱
        2. 文件不存在或force_rebuild_kg=True时重新构建
        3. 构建后保存到持久化文件
        """
        from .mesh_database_interface import MeshDatabaseInterface
        from .vector_database import VectorDatabase
        from .mesh_thought_engine import MeshThoughtEngine
        import time
        import json
        import os
        
        # 初始化组件
        mesh_db_interface = MeshDatabaseInterface()
        vector_db = VectorDatabase()
        mesh_engine = MeshThoughtEngine()
        
        # ✅ 半静态策略：优先加载持久化知识图谱
        knowledge_graph = None
        kg_loaded_from_cache = False
        
        if not force_rebuild_kg and os.path.exists(self._kg_cache_file):
            try:
                with open(self._kg_cache_file, 'r', encoding='utf-8') as f:
                    knowledge_graph = json.load(f)
                
                # ✅ 验证缓存格式是否包含memory_classification字段
                kg_metadata = knowledge_graph.get('metadata', {})
                if 'memory_classification' not in kg_metadata:
                    print(f"⚠️ 缓存格式过旧（缺少memory_classification），强制重建")
                    knowledge_graph = None
                else:
                    kg_loaded_from_cache = True
                    print(f"📂 从持久化文件加载知识图谱: {len(knowledge_graph.get('nodes', []))}节点, {len(knowledge_graph.get('edges', []))}边")
            except Exception as e:
                print(f"⚠️ 加载知识图谱失败: {e}，将重新构建")
                knowledge_graph = None
        
        # 如果缓存加载失败或强制重建，则重新构建
        if knowledge_graph is None:
            start_time = time.time()
            knowledge_graph = mesh_db_interface.build_knowledge_graph(
                topic=None,  # 全局知识图谱
                max_nodes=100,  # 💾 首次启动轻量化构建(避免超时)
                full_index=True,  # 💾 全覆盖索引
                use_multiple_dimensions=False  # 🚀 关闭多维关联(避免O(n²)性能瓶颈)
            )
            build_time = time.time() - start_time
            
            # 💾 保存到持久化文件
            try:
                with open(self._kg_cache_file, 'w', encoding='utf-8') as f:
                    json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
                print(f"💾 知识图谱已保存: {self._kg_cache_file}")
                print(f"⚡ 知识图谱构建耗时: {build_time:.2f}秒（max_nodes=100，轻量化模式）")
            except Exception as e:
                print(f"❌ 知识图谱保存失败: {e}")
        
        # 提取基础数据
        all_memories = vector_db.get_all_memories()
        kg_metadata = knowledge_graph.get('metadata', {})
        memory_classification = kg_metadata.get('memory_classification', {})

        # 统一使用向量库中的status字段统计三层记忆分布，避免与知识图谱缓存不一致
        active_memories = [m for m in all_memories if m.get('status', 'active') == 'active']
        archived_memories = [m for m in all_memories if m.get('status') == 'archived']
        retired_memories = [m for m in all_memories if m.get('status') == 'retired']

        # 如有需要，仅将memory_classification作为参考元数据，不再直接作为统计结果来源
        if memory_classification:
            classified_total = sum(memory_classification.values())
            if classified_total != len(all_memories):
                print(f"⚠️ 知识图谱memory_classification与向量库数量不一致: kg={classified_total}, vdb={len(all_memories)}")
        
        # 构建统一的统计数据
        stats = {
            # ========== 向量数据库统计 ==========
            'vector_database': {
                'total_memories': len(all_memories),  # 总文本块数
                'active_memories': len(active_memories),  # 主库
                'archived_memories': len(archived_memories),  # 备库
                'retired_memories': len(retired_memories),  # 淘汰库
            },
            
            # ========== 知识图谱统计 ==========
            'knowledge_graph': {
                'total_nodes': len(knowledge_graph.get('nodes', [])),  # 知识图谱节点数
                'total_edges': len(knowledge_graph.get('edges', [])),  # 知识图谱关联数
                'coverage_rate': kg_metadata.get('coverage_rate', 0),  # 覆盖率
                'build_time': kg_metadata.get('build_time'),  # 构建时间
            },
            
            # ========== 思维引擎统计 ==========
            'thought_engine': {
                'total_nodes': len(mesh_engine.nodes),  # 思维节点数（去重后）
                'deduplication_rate': (len(all_memories) - len(mesh_engine.nodes)) / len(all_memories) * 100 if all_memories else 0,  # 去重率
            },
            
            # ========== 元数据 ==========
            'metadata': {
                'timestamp': datetime.now().isoformat(),  # 统计时间
                'data_source': 'MeshDatabaseInterface.build_knowledge_graph()',  # 数据源标识
                'cache_ttl': self._cache_ttl,  # 缓存时长
            }
        }
        
        return stats
    
    def rebuild_knowledge_graph(self) -> Dict[str, Any]:
        """
        强制重建知识图谱（记忆重构时调用）
        
        Returns:
            重建后的统计数据
        """
        print("🔄 开始重建全局知识图谱...")
        return self.get_system_statistics(force_refresh=True, force_rebuild_kg=True)
    
    def get_summary_text(self) -> str:
        """
        生成统计摘要文本（用于系统管家报告）
        
        Returns:
            格式化的统计文本
        """
        stats = self.get_system_statistics()
        
        vdb = stats['vector_database']
        kg = stats['knowledge_graph']
        te = stats['thought_engine']
        
        summary = f"""## 当前记忆库状态分析结果

### 📊 记忆库基础指标
- **总记忆泡泡数量**：{vdb['total_memories']:,}个（向量库文本块）
- **知识图谱节点数**：{kg['total_nodes']:,}个概念节点
- **知识图谱边数**：{kg['total_edges']:,}条关联关系
- **思维引擎节点数**：{te['total_nodes']:,}个思维节点（去重后）

### 📂 三层记忆库分布
- **主库(active)**：{vdb['active_memories']:,}个（高活性核心记忆）
- **备库(archived)**：{vdb['archived_memories']:,}个（低活性长期记忆）
- **淘汰库(retired)**：{vdb['retired_memories']:,}个（认知偏差样本）

### 🔄 去重与复用效率
- **去重率**：{te['deduplication_rate']:.1f}%（{vdb['total_memories']:,}个文本块 → {te['total_nodes']:,}个思维节点）
- **知识图谱覆盖率**：{kg['coverage_rate']:.1f}%

---
*数据源：MeshDatabaseInterface.build_knowledge_graph()  
*统计时间：{stats['metadata']['timestamp']}*
"""
        
        return summary


# 全局单例
_statistics_service_instance = None


def get_system_statistics_service() -> SystemStatisticsService:
    """获取系统统计服务单例"""
    global _statistics_service_instance
    if _statistics_service_instance is None:
        _statistics_service_instance = SystemStatisticsService()
    return _statistics_service_instance
