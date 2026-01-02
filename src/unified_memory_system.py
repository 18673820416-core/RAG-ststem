#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆系统 - 基于八爪鱼架构的记忆统一管理

开发提示词来源：用户提出的八爪鱼架构理念 - 每个智能体是能力边界的精修进化体
核心功能：为所有智能体提供统一的记忆存储、检索、共享和进化管理
"""

# @self-expose: {"id": "unified_memory_system", "name": "Unified Memory System", "type": "component", "version": "2.0.0", "needs": {"deps": ["mesh_database_interface", "memory_slicer_tool", "event_dimension_encoder"], "resources": []}, "provides": {"capabilities": ["Unified Memory System功能", "向量化存储统一管理", "去重机制集成", "分片处理统一接口"]}}

import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """记忆类型枚举"""
    WORK_LOG = "work_log"           # 工作日志
    CONVERSATION = "conversation"   # 对话记录
    TOOL_USAGE = "tool_usage"       # 工具使用记录
    ERROR_LOG = "error_log"         # 错误日志
    KNOWLEDGE = "knowledge"         # 知识记忆
    EXPERIENCE = "experience"       # 经验记忆
    EVOLUTION = "evolution"         # 进化记录

class MemoryPriority(Enum):
    """记忆优先级枚举"""
    LOW = "low"         # 低优先级
    MEDIUM = "medium"   # 中优先级
    HIGH = "high"       # 高优先级
    CRITICAL = "critical"  # 关键优先级

class UnifiedMemorySystem:
    """统一记忆系统 - 八爪鱼架构的核心记忆管理
    
    职责边界：
    - 管理层：为上层业务提供统一的记忆存储接口
    - 存储层：调用mesh_database_interface处理向量化与去重
    - 处理层：调用memory_slicer_tool处理文本分片
    """
    
    def __init__(self, base_path: str):
        """
        初始化统一记忆系统
        
        Args:
            base_path: 系统基础路径
        """
        self.base_path = Path(base_path)
        self.memory_db_path = self.base_path / "data" / "unified_memory_db"
        self.memory_db_path.mkdir(parents=True, exist_ok=True)
        
        # 记忆索引
        self.memory_index = {}
        self.agent_memory_map = {}  # 智能体-记忆映射
        
        # 记忆统计
        self.memory_stats = {
            'total_memories': 0,
            'by_type': {},
            'by_agent': {},
            'by_priority': {}
        }
        
        # ✅ 集成mesh数据库接口（职责归位）
        try:
            from src.mesh_database_interface import MeshDatabaseInterface
            self.mesh_interface = MeshDatabaseInterface()
            logger.info("✅ MeshDatabaseInterface集成成功")
        except Exception as e:
            logger.warning(f"⚠️ MeshDatabaseInterface集成失败: {e}，将使用JSON备份")
            self.mesh_interface = None
        
        # 加载现有记忆索引
        self._load_memory_index()
        
        logger.info(f"统一记忆系统初始化完成 - 基础路径: {self.base_path}")
    
    def _load_memory_index(self):
        """加载记忆索引"""
        index_file = self.memory_db_path / "memory_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.memory_index = json.load(f)
            
            # 重建统计信息
            self._rebuild_stats()
    
    def _save_memory_index(self):
        """保存记忆索引"""
        index_file = self.memory_db_path / "memory_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_index, f, ensure_ascii=False, indent=2)
    
    def _rebuild_stats(self):
        """重建统计信息"""
        self.memory_stats = {
            'total_memories': len(self.memory_index),
            'by_type': {},
            'by_agent': {},
            'by_priority': {}
        }
        
        for memory_id, memory_info in self.memory_index.items():
            # 按类型统计
            memory_type = memory_info.get('type', 'unknown')
            self.memory_stats['by_type'][memory_type] = self.memory_stats['by_type'].get(memory_type, 0) + 1
            
            # 按智能体统计
            agent_id = memory_info.get('agent_id', 'unknown')
            self.memory_stats['by_agent'][agent_id] = self.memory_stats['by_agent'].get(agent_id, 0) + 1
            
            # 按优先级统计
            priority = memory_info.get('priority', 'medium')
            self.memory_stats['by_priority'][priority] = self.memory_stats['by_priority'].get(priority, 0) + 1
    
    def create_memory(self, agent_id: str, memory_type: MemoryType, content: Dict[str, Any], 
                     priority: MemoryPriority = MemoryPriority.MEDIUM, 
                     tags: List[str] = None, 
                     related_memories: List[str] = None) -> str:
        """
        创建统一格式的记忆
        
        Args:
            agent_id: 智能体ID
            memory_type: 记忆类型
            content: 记忆内容
            priority: 记忆优先级
            tags: 标签列表
            related_memories: 相关记忆ID列表
            
        Returns:
            str: 记忆ID
        """
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 构建标准记忆格式
        memory_data = {
            'id': memory_id,
            'agent_id': agent_id,
            'type': memory_type.value,
            'priority': priority.value,
            'timestamp': timestamp,
            'content': content,
            'tags': tags or [],
            'related_memories': related_memories or [],
            'version': 1,
            'access_count': 0,
            'last_accessed': timestamp
        }
        
        # 保存记忆文件
        memory_file = self.memory_db_path / f"{memory_id}.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        self.memory_index[memory_id] = {
            'agent_id': agent_id,
            'type': memory_type.value,
            'priority': priority.value,
            'timestamp': timestamp,
            'tags': tags or [],
            'file_path': str(memory_file)
        }
        
        # 更新智能体记忆映射
        if agent_id not in self.agent_memory_map:
            self.agent_memory_map[agent_id] = []
        self.agent_memory_map[agent_id].append(memory_id)
        
        # 更新统计
        self._update_stats(memory_data)
        
        # 保存索引
        self._save_memory_index()
        
        logger.info(f"创建记忆成功 - ID: {memory_id}, 类型: {memory_type.value}, 智能体: {agent_id}")
        return memory_id
    
    def _update_stats(self, memory_data: Dict[str, Any]):
        """更新统计信息"""
        self.memory_stats['total_memories'] += 1
        
        memory_type = memory_data['type']
        agent_id = memory_data['agent_id']
        priority = memory_data['priority']
        
        self.memory_stats['by_type'][memory_type] = self.memory_stats['by_type'].get(memory_type, 0) + 1
        self.memory_stats['by_agent'][agent_id] = self.memory_stats['by_agent'].get(agent_id, 0) + 1
        self.memory_stats['by_priority'][priority] = self.memory_stats['by_priority'].get(priority, 0) + 1
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        获取记忆内容
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            Optional[Dict]: 记忆数据，如果不存在返回None
        """
        if memory_id not in self.memory_index:
            return None
        
        memory_info = self.memory_index[memory_id]
        memory_file = Path(memory_info['file_path'])
        
        if not memory_file.exists():
            logger.warning(f"记忆文件不存在: {memory_file}")
            return None
        
        # 读取记忆文件
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
        
        # 更新访问统计
        memory_data['access_count'] += 1
        memory_data['last_accessed'] = datetime.now().isoformat()
        
        # 保存更新后的记忆
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        return memory_data
    
    def search_memories(self, agent_id: str = None, memory_type: MemoryType = None, 
                       tags: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            agent_id: 智能体ID筛选
            memory_type: 记忆类型筛选
            tags: 标签筛选
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 匹配的记忆列表
        """
        results = []
        
        for memory_id, memory_info in self.memory_index.items():
            # 智能体筛选
            if agent_id and memory_info['agent_id'] != agent_id:
                continue
            
            # 类型筛选
            if memory_type and memory_info['type'] != memory_type.value:
                continue
            
            # 标签筛选
            if tags:
                memory_tags = set(memory_info.get('tags', []))
                search_tags = set(tags)
                if not memory_tags.intersection(search_tags):
                    continue
            
            # 获取完整记忆数据
            memory_data = self.get_memory(memory_id)
            if memory_data:
                results.append(memory_data)
            
            # 数量限制
            if len(results) >= limit:
                break
        
        # 按时间倒序排序
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return results
    
    def get_agent_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """
        获取智能体记忆摘要
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            Dict: 记忆摘要信息
        """
        agent_memories = self.search_memories(agent_id=agent_id)
        
        if not agent_memories:
            return {
                'agent_id': agent_id,
                'total_memories': 0,
                'memory_types': {},
                'recent_activity': None,
                'evolution_trend': 'stable'
            }
        
        # 统计记忆类型
        memory_types = {}
        for memory in agent_memories:
            mem_type = memory['type']
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
        
        # 计算近期活动
        recent_memories = [m for m in agent_memories 
                          if datetime.fromisoformat(m['timestamp']).timestamp() > time.time() - 7*24*3600]
        
        # 进化趋势分析
        evolution_trend = self._analyze_evolution_trend(agent_memories)
        
        return {
            'agent_id': agent_id,
            'total_memories': len(agent_memories),
            'memory_types': memory_types,
            'recent_activity': {
                'last_7_days': len(recent_memories),
                'most_active_type': max(memory_types.items(), key=lambda x: x[1])[0] if memory_types else 'none'
            },
            'evolution_trend': evolution_trend
        }
    
    def _analyze_evolution_trend(self, memories: List[Dict[str, Any]]) -> str:
        """分析进化趋势"""
        if len(memories) < 10:
            return 'stable'
        
        # 按时间分组（最近3个月）
        three_months_ago = time.time() - 90*24*3600
        recent_memories = [m for m in memories 
                          if datetime.fromisoformat(m['timestamp']).timestamp() > three_months_ago]
        
        older_memories = [m for m in memories 
                          if datetime.fromisoformat(m['timestamp']).timestamp() <= three_months_ago]
        
        if len(recent_memories) > len(older_memories) * 1.5:
            return 'growing'
        elif len(recent_memories) < len(older_memories) * 0.7:
            return 'declining'
        else:
            return 'stable'
    
    def share_memory_across_agents(self, source_agent_id: str, target_agent_id: str, 
                                  memory_id: str, sharing_reason: str) -> bool:
        """
        在智能体间共享记忆
        
        Args:
            source_agent_id: 源智能体ID
            target_agent_id: 目标智能体ID
            memory_id: 记忆ID
            sharing_reason: 共享原因
            
        Returns:
            bool: 共享是否成功
        """
        # 获取源记忆
        source_memory = self.get_memory(memory_id)
        if not source_memory or source_memory['agent_id'] != source_agent_id:
            logger.error(f"记忆共享失败 - 源记忆不存在或权限不足")
            return False
        
        # 创建共享记忆（引用形式）
        shared_memory_id = self.create_memory(
            agent_id=target_agent_id,
            memory_type=MemoryType.KNOWLEDGE,
            content={
                'shared_memory_id': memory_id,
                'source_agent_id': source_agent_id,
                'sharing_reason': sharing_reason,
                'original_content': source_memory['content']
            },
            priority=MemoryPriority(source_memory['priority']),
            tags=source_memory['tags'] + ['shared'],
            related_memories=[memory_id]
        )
        
        logger.info(f"记忆共享成功 - 源智能体: {source_agent_id}, 目标智能体: {target_agent_id}, 记忆ID: {shared_memory_id}")
        return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 删除是否成功
        """
        if memory_id not in self.memory_index:
            logger.warning(f"删除记忆失败 - 记忆ID不存在: {memory_id}")
            return False
        
        try:
            # 获取记忆信息
            memory_info = self.memory_index[memory_id]
            memory_file = Path(memory_info['file_path'])
            agent_id = memory_info['agent_id']
            
            # 删除记忆文件
            if memory_file.exists():
                memory_file.unlink()
            
            # 从索引中删除
            del self.memory_index[memory_id]
            
            # 从智能体记忆映射中删除
            if agent_id in self.agent_memory_map:
                if memory_id in self.agent_memory_map[agent_id]:
                    self.agent_memory_map[agent_id].remove(memory_id)
                # 如果智能体没有记忆了，从映射中删除
                if not self.agent_memory_map[agent_id]:
                    del self.agent_memory_map[agent_id]
            
            # 更新统计信息
            self._rebuild_stats()
            
            # 保存索引
            self._save_memory_index()
            
            logger.info(f"删除记忆成功 - ID: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"删除记忆失败 - ID: {memory_id}, 错误: {e}")
            return False
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新记忆
        
        Args:
            memory_id: 记忆ID
            updates: 更新内容
            
        Returns:
            bool: 更新是否成功
        """
        if memory_id not in self.memory_index:
            logger.warning(f"更新记忆失败 - 记忆ID不存在: {memory_id}")
            return False
        
        try:
            # 获取记忆信息
            memory_info = self.memory_index[memory_id]
            memory_file = Path(memory_info['file_path'])
            
            if not memory_file.exists():
                logger.warning(f"更新记忆失败 - 记忆文件不存在: {memory_file}")
                return False
            
            # 读取现有记忆
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # 应用更新
            memory_data.update(updates)
            memory_data['version'] += 1
            memory_data['last_accessed'] = datetime.now().isoformat()
            
            # 保存更新后的记忆
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            if 'type' in updates:
                self.memory_index[memory_id]['type'] = updates['type']
            if 'priority' in updates:
                self.memory_index[memory_id]['priority'] = updates['priority']
            if 'tags' in updates:
                self.memory_index[memory_id]['tags'] = updates['tags']
            
            # 保存索引
            self._save_memory_index()
            
            # 更新统计信息
            self._rebuild_stats()
            
            logger.info(f"更新记忆成功 - ID: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"更新记忆失败 - ID: {memory_id}, 错误: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Returns:
            Dict: 系统统计信息
        """
        return {
            'memory_stats': self.memory_stats,
            'total_agents': len(self.agent_memory_map),
            'index_size': len(self.memory_index),
            'last_updated': datetime.now().isoformat()
        }
    
    def store_interaction_to_vector_db(self, interaction_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """✅ 统一向量化存储接口（职责归位）
        
        职责：
        1. 调用memory_slicer_tool进行分片
        2. 调用mesh_database_interface处理向量化与去重
        3. 统计并返回处理结果
        
        Args:
            interaction_content: 交互内容
            metadata: 元数据（包含source, sender, timestamp等）
            
        Returns:
            Dict: 处理结果（saved_count, duplicate_count）
        """
        if not self.mesh_interface:
            logger.warning("⚠️ MeshInterface未集成，跳过向量化存储")
            return {'saved_count': 0, 'duplicate_count': 0, 'error': 'MeshInterface未集成'}
        
        try:
            # 1. 导入分片工具和事件维编码器
            from tools.memory_slicer_tool import MemorySlicerTool
            from src.event_dimension_encoder import EventDimensionEncoder
            
            slicer = MemorySlicerTool()
            event_encoder = EventDimensionEncoder()
            
            # 2. 进行智能分片
            slices = slicer.slice_text(interaction_content, metadata)
            
            # 3. 统计去重情况
            duplicate_count = 0
            saved_count = 0
            
            # 4. 对每个分片进行向量化存储（✅ 通过mesh接口自动去重）
            for slice_data in slices:
                content = slice_data.get('content', '')
                if content:
                    # 4.1 提取事件编码
                    event_codes = event_encoder.extract_event_codes_from_memory(slice_data)
                    
                    # 4.2 构建记忆数据
                    memory_data = {
                        "topic": metadata.get('topic', f"{metadata.get('source', 'unknown')}交互"),
                        "content": slice_data.get('content', ''),
                        "source_type": metadata.get('source_type', metadata.get('source', 'unknown')),
                        "slice_id": slice_data.get('slice_id', ''),
                        "slice_depth": slice_data.get('slice_depth', 0),
                        "parent_id": slice_data.get('parent_id', ''),
                        "event_codes": event_codes,
                        "timestamp": metadata.get('timestamp', datetime.now().isoformat()),
                        "importance": slice_data.get('importance', 0.7),
                        "confidence": 0.9,
                        "tags": metadata.get('tags', []) + ["slice"] + event_codes
                    }
                    
                    # 4.3 ✅ 通过mesh接口保存（自动去重）
                    result = self.mesh_interface.store_memory_with_mesh(memory_data)
                    
                    if result.get('is_duplicate', False):
                        duplicate_count += 1
                        logger.debug(f"检测到重复切片: {slice_data.get('slice_id', 'unknown')}")
                    else:
                        saved_count += 1
            
            logger.info(f"✅ 向量化存储完成: 保存{saved_count}条，跳过{duplicate_count}条重复")
            
            return {
                'saved_count': saved_count,
                'duplicate_count': duplicate_count,
                'total_slices': len(slices)
            }
            
        except Exception as e:
            logger.error(f"向量化存储失败: {e}")
            return {'saved_count': 0, 'duplicate_count': 0, 'error': str(e)}

# 全局记忆系统实例
_unified_memory_system = None

def get_unified_memory_system(base_path: str = None) -> UnifiedMemorySystem:
    """
    获取统一记忆系统实例（单例模式）
    
    Args:
        base_path: 系统基础路径
        
    Returns:
        UnifiedMemorySystem: 统一记忆系统实例
    """
    global _unified_memory_system
    
    if _unified_memory_system is None:
        if base_path is None:
            # 默认使用当前工作目录
            base_path = Path.cwd()
        _unified_memory_system = UnifiedMemorySystem(str(base_path))
    
    return _unified_memory_system