#!/usr/bin/env python
# @self-expose: {"id": "memory_bubble_manager", "name": "Memory Bubble Manager", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Memory Bubble Manager功能"]}}
# -*- coding: utf-8 -*-
"""
记忆泡泡管理器 - 智能体的随手记工具
集成到 BaseAgent，所有智能体自动具备该功能
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryBubbleManager:
    """记忆泡泡管理器 - 智能体的即时笔记本"""
    
    # 泡泡类别定义
    CATEGORY_PROBLEM = "问题"           # 遇到的问题
    CATEGORY_IDEA = "构思"              # 计划和想法
    CATEGORY_OPTIMIZATION = "优化建议"   # 优化建议
    CATEGORY_CONFUSION = "理解困难"      # 理解不了的内容
    CATEGORY_TODO = "待办"              # 待执行的任务
    CATEGORY_TOOL_ISSUE = "工具问题"     # 工具相关问题
    CATEGORY_MEMORY_ISSUE = "记忆问题"   # 记忆质量问题
    
    def __init__(self, agent_id: str, base_path: str = "data/memory_bubbles"):
        """初始化记忆泡泡管理器
        
        Args:
            agent_id: 智能体ID
            base_path: 泡泡存储根目录
        """
        self.agent_id = agent_id
        self.base_path = Path(base_path)
        self.bubble_dir = self.base_path / agent_id
        
        # 确保目录存在
        self.bubble_dir.mkdir(parents=True, exist_ok=True)
    
    def quick_note(self, 
                   category: str, 
                   content: str, 
                   context: Optional[Dict[str, Any]] = None,
                   priority: str = "normal") -> str:
        """快速记录泡泡（智能体的随手记）
        
        Args:
            category: 泡泡类型（问题/构思/优化建议/理解困难等）
            content: 记录内容
            context: 上下文信息（工具名、文本块ID、相关文件等）
            priority: 优先级（low/normal/high/urgent）
            
        Returns:
            bubble_id: 泡泡ID（时间戳）
            
        Examples:
            # 工具问题
            bubble_manager.quick_note(
                category="工具问题",
                content="file_reading工具处理大文件时很慢",
                context={"tool": "file_reading", "file_size": "10MB"}
            )
            
            # 构思记录
            bubble_manager.quick_note(
                category="构思",
                content="计划实现自动化测试框架，需要集成pytest",
                context={"related_files": ["test_*.py"]}
            )
            
            # 理解困难
            bubble_manager.quick_note(
                category="理解困难",
                content="检索到的文本块'mem_12345'语义不清晰",
                context={"memory_id": "mem_12345"}
            )
        """
        # 使用时间戳作为文件名（自然时空属性）
        timestamp = datetime.now()
        bubble_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        bubble_data = {
            "bubble_id": bubble_id,
            "agent_id": self.agent_id,
            "timestamp": timestamp.isoformat(),
            "category": category,
            "content": content,
            "context": context or {},
            "priority": priority,
            "status": "未解决",
            "created_at": timestamp.isoformat(),
            "resolved_at": None,
            "resolution_note": None
        }
        
        # 保存泡泡到文件
        bubble_file = self.bubble_dir / f"{bubble_id}.json"
        with open(bubble_file, 'w', encoding='utf-8') as f:
            json.dump(bubble_data, f, ensure_ascii=False, indent=2)
        
        return bubble_id
    
    def mark_resolved(self, bubble_id: str, resolution_note: str = "") -> bool:
        """标记泡泡已解决
        
        Args:
            bubble_id: 泡泡ID
            resolution_note: 解决说明
            
        Returns:
            是否成功标记
        """
        bubble_file = self.bubble_dir / f"{bubble_id}.json"
        
        if not bubble_file.exists():
            return False
        
        # 读取泡泡数据
        with open(bubble_file, 'r', encoding='utf-8') as f:
            bubble_data = json.load(f)
        
        # 更新状态
        bubble_data['status'] = "已解决"
        bubble_data['resolved_at'] = datetime.now().isoformat()
        bubble_data['resolution_note'] = resolution_note
        
        # 保存更新
        with open(bubble_file, 'w', encoding='utf-8') as f:
            json.dump(bubble_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_today_bubbles(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """获取今天的泡泡（用于写日记）
        
        Args:
            include_resolved: 是否包含已解决的泡泡
            
        Returns:
            今天的泡泡列表
        """
        today = datetime.now().date()
        bubbles = []
        
        for bubble_file in self.bubble_dir.glob("*.json"):
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            # 检查日期
            bubble_date = datetime.fromisoformat(bubble_data['timestamp']).date()
            if bubble_date != today:
                continue
            
            # 检查是否包含已解决
            if not include_resolved and bubble_data['status'] == "已解决":
                continue
            
            bubbles.append(bubble_data)
        
        # 按时间排序
        bubbles.sort(key=lambda x: x['timestamp'])
        return bubbles
    
    def get_unresolved_bubbles(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取未解决的泡泡（用于问题汇报）
        
        Args:
            days: 获取最近N天的未解决泡泡
            
        Returns:
            未解决的泡泡列表
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        unresolved_bubbles = []
        
        for bubble_file in self.bubble_dir.glob("*.json"):
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            # 只获取未解决的
            if bubble_data['status'] != "未解决":
                continue
            
            # 检查日期范围
            bubble_time = datetime.fromisoformat(bubble_data['timestamp'])
            if bubble_time < cutoff_date:
                continue
            
            unresolved_bubbles.append(bubble_data)
        
        # 按优先级和时间排序
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        unresolved_bubbles.sort(
            key=lambda x: (priority_order.get(x['priority'], 2), x['timestamp'])
        )
        
        return unresolved_bubbles
    
    def export_for_diary(self, date: Optional[datetime] = None) -> str:
        """导出泡泡为日记素材
        
        Args:
            date: 指定日期，默认为今天
            
        Returns:
            格式化的日记素材文本
        """
        if date is None:
            date = datetime.now()
        
        target_date = date.date()
        bubbles = []
        
        for bubble_file in self.bubble_dir.glob("*.json"):
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            bubble_date = datetime.fromisoformat(bubble_data['timestamp']).date()
            if bubble_date == target_date:
                bubbles.append(bubble_data)
        
        if not bubbles:
            return "今天没有记录泡泡。"
        
        # 按类别分组
        bubbles_by_category = {}
        for bubble in bubbles:
            category = bubble['category']
            if category not in bubbles_by_category:
                bubbles_by_category[category] = []
            bubbles_by_category[category].append(bubble)
        
        # 生成日记素材
        diary_parts = [f"# {date.strftime('%Y年%m月%d日')} 工作记录\n"]
        
        for category, category_bubbles in bubbles_by_category.items():
            diary_parts.append(f"\n## {category} ({len(category_bubbles)}项)\n")
            
            for bubble in category_bubbles:
                status_icon = "✅" if bubble['status'] == "已解决" else "⏳"
                time_str = datetime.fromisoformat(bubble['timestamp']).strftime("%H:%M")
                
                diary_parts.append(f"\n### {status_icon} [{time_str}] {bubble['content']}")
                
                # 添加上下文信息
                if bubble['context']:
                    diary_parts.append(f"\n**上下文**: {json.dumps(bubble['context'], ensure_ascii=False)}")
                
                # 添加解决说明
                if bubble['status'] == "已解决" and bubble.get('resolution_note'):
                    diary_parts.append(f"\n**解决方案**: {bubble['resolution_note']}")
                
                diary_parts.append("\n")
        
        return "".join(diary_parts)
    
    def cleanup_resolved_bubbles(self) -> int:
        """清理已解决的泡泡（写日记后执行）
        
        Returns:
            清理的泡泡数量
        """
        cleaned_count = 0
        
        for bubble_file in self.bubble_dir.glob("*.json"):
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            if bubble_data['status'] == "已解决":
                bubble_file.unlink()
                cleaned_count += 1
        
        return cleaned_count
    
    def get_bubbles_by_category(self, category: str, status: str = "未解决") -> List[Dict[str, Any]]:
        """按类别获取泡泡
        
        Args:
            category: 泡泡类别
            status: 状态筛选（未解决/已解决/全部）
            
        Returns:
            符合条件的泡泡列表
        """
        bubbles = []
        
        for bubble_file in self.bubble_dir.glob("*.json"):
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            # 类别筛选
            if bubble_data['category'] != category:
                continue
            
            # 状态筛选
            if status != "全部" and bubble_data['status'] != status:
                continue
            
            bubbles.append(bubble_data)
        
        bubbles.sort(key=lambda x: x['timestamp'], reverse=True)
        return bubbles
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取泡泡统计信息
        
        Returns:
            统计数据字典
        """
        all_bubbles = list(self.bubble_dir.glob("*.json"))
        
        stats = {
            "total": len(all_bubbles),
            "resolved": 0,
            "unresolved": 0,
            "by_category": {},
            "by_priority": {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        }
        
        for bubble_file in all_bubbles:
            with open(bubble_file, 'r', encoding='utf-8') as f:
                bubble_data = json.load(f)
            
            # 状态统计
            if bubble_data['status'] == "已解决":
                stats['resolved'] += 1
            else:
                stats['unresolved'] += 1
            
            # 类别统计
            category = bubble_data['category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # 优先级统计
            priority = bubble_data.get('priority', 'normal')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return stats
