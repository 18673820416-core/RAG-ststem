#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具审核管理器 - 管理工具发现后的审核流程
开发提示词来源：用户要求发现的工具需上报用户审核后才能关联到注册表
"""

# @self-expose: {"id": "tool_review_manager", "name": "Tool Review Manager", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Tool Review Manager功能"]}}

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ToolReviewManager:
    """工具审核管理器"""
    
    def __init__(self, pending_file: str = "data/pending_tools.json", 
                 review_file: str = "data/tool_reviews.json"):
        self.pending_file = Path(pending_file)
        self.review_file = Path(review_file)
        
        # 创建目录
        self.pending_file.parent.mkdir(parents=True, exist_ok=True)
        self.review_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.pending_tools: Dict[str, Dict] = {}
        self.review_history: List[Dict] = []
        
        self._load_pending_tools()
        self._load_review_history()
    
    def _load_pending_tools(self):
        """加载待审核工具列表"""
        try:
            if self.pending_file.exists():
                with open(self.pending_file, 'r', encoding='utf-8') as f:
                    self.pending_tools = json.load(f)
            else:
                self.pending_tools = {}
            logger.info(f"待审核工具列表已加载，包含 {len(self.pending_tools)} 个待审核工具")
        except Exception as e:
            logger.error(f"加载待审核工具列表失败: {e}")
            self.pending_tools = {}
    
    def _save_pending_tools(self):
        """保存待审核工具列表"""
        try:
            with open(self.pending_file, 'w', encoding='utf-8') as f:
                json.dump(self.pending_tools, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存待审核工具列表失败: {e}")
    
    def _load_review_history(self):
        """加载审核历史记录"""
        try:
            if self.review_file.exists():
                with open(self.review_file, 'r', encoding='utf-8') as f:
                    self.review_history = json.load(f)
            else:
                self.review_history = []
            logger.info(f"审核历史记录已加载，包含 {len(self.review_history)} 条记录")
        except Exception as e:
            logger.error(f"加载审核历史记录失败: {e}")
            self.review_history = []
    
    def _save_review_history(self):
        """保存审核历史记录"""
        try:
            with open(self.review_file, 'w', encoding='utf-8') as f:
                json.dump(self.review_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存审核历史记录失败: {e}")
    
    def submit_tool_for_review(self, tool_info: Dict[str, Any]) -> str:
        """提交工具进行审核"""
        try:
            tool_id = tool_info.get('tool_id')
            if not tool_id:
                # 生成工具ID
                tool_id = f"pending_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                tool_info['tool_id'] = tool_id
            
            # 添加审核信息
            tool_info['review_status'] = 'pending'
            tool_info['submission_timestamp'] = datetime.now().isoformat()
            tool_info['reviewer'] = None
            tool_info['review_timestamp'] = None
            tool_info['review_notes'] = None
            
            # 添加到待审核列表
            self.pending_tools[tool_id] = tool_info
            self._save_pending_tools()
            
            logger.info(f"工具 {tool_id} 已提交审核")
            
            # 通知用户有新工具需要审核
            self._notify_user_new_tool(tool_info)
            
            return tool_id
            
        except Exception as e:
            logger.error(f"提交工具审核失败: {e}")
            return ""
    
    def get_pending_tools(self) -> Dict[str, Dict]:
        """获取所有待审核工具"""
        return self.pending_tools.copy()
    
    def get_tool_for_review(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """获取指定工具的审核信息"""
        return self.pending_tools.get(tool_id)
    
    def approve_tool(self, tool_id: str, reviewer: str = "user", 
                    review_notes: str = "审核通过") -> bool:
        """审核通过工具"""
        try:
            if tool_id not in self.pending_tools:
                logger.error(f"工具 {tool_id} 不存在于待审核列表中")
                return False
            
            tool_info = self.pending_tools[tool_id]
            
            # 更新审核信息
            tool_info['review_status'] = 'approved'
            tool_info['reviewer'] = reviewer
            tool_info['review_timestamp'] = datetime.now().isoformat()
            tool_info['review_notes'] = review_notes
            
            # 添加到审核历史
            review_record = {
                'tool_id': tool_id,
                'tool_name': tool_info.get('tool_name', 'Unknown'),
                'review_status': 'approved',
                'reviewer': reviewer,
                'review_timestamp': tool_info['review_timestamp'],
                'review_notes': review_notes
            }
            self.review_history.append(review_record)
            
            # 从待审核列表中移除
            del self.pending_tools[tool_id]
            
            self._save_pending_tools()
            self._save_review_history()
            
            logger.info(f"工具 {tool_id} 已审核通过")
            
            # 通知工具注册管理器进行注册
            self._register_approved_tool(tool_info)
            
            return True
            
        except Exception as e:
            logger.error(f"审核通过工具失败: {e}")
            return False
    
    def reject_tool(self, tool_id: str, reviewer: str = "user", 
                   review_notes: str = "审核未通过") -> bool:
        """审核拒绝工具"""
        try:
            if tool_id not in self.pending_tools:
                logger.error(f"工具 {tool_id} 不存在于待审核列表中")
                return False
            
            tool_info = self.pending_tools[tool_id]
            
            # 更新审核信息
            tool_info['review_status'] = 'rejected'
            tool_info['reviewer'] = reviewer
            tool_info['review_timestamp'] = datetime.now().isoformat()
            tool_info['review_notes'] = review_notes
            
            # 添加到审核历史
            review_record = {
                'tool_id': tool_id,
                'tool_name': tool_info.get('tool_name', 'Unknown'),
                'review_status': 'rejected',
                'reviewer': reviewer,
                'review_timestamp': tool_info['review_timestamp'],
                'review_notes': review_notes
            }
            self.review_history.append(review_record)
            
            # 从待审核列表中移除
            del self.pending_tools[tool_id]
            
            self._save_pending_tools()
            self._save_review_history()
            
            logger.info(f"工具 {tool_id} 已审核拒绝")
            
            return True
            
        except Exception as e:
            logger.error(f"审核拒绝工具失败: {e}")
            return False
    
    def _register_approved_tool(self, tool_info: Dict[str, Any]):
        """注册审核通过的工具"""
        try:
            # 修复导入路径
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from tool_registry_manager import get_tool_registry_manager
            
            registry_manager = get_tool_registry_manager()
            
            # 准备注册信息
            registration_info = tool_info.copy()
            # 移除审核相关的字段
            for field in ['review_status', 'reviewer', 'review_timestamp', 'review_notes', 'submission_timestamp']:
                registration_info.pop(field, None)
            
            # 注册工具
            success = registry_manager.register_tool(registration_info)
            
            if success:
                logger.info(f"工具 {tool_info.get('tool_id')} 已成功注册到工具注册表")
            else:
                logger.error(f"工具 {tool_info.get('tool_id')} 注册到工具注册表失败")
                
        except Exception as e:
            logger.error(f"注册审核通过的工具失败: {e}")
    
    def _notify_user_new_tool(self, tool_info: Dict[str, Any]):
        """通知用户有新工具需要审核"""
        try:
            tool_name = tool_info.get('tool_name', '未知工具')
            tool_description = tool_info.get('description', '无描述')
            
            # 在实际系统中，这里可以发送邮件、消息通知等
            # 这里我们简单打印日志
            logger.info(f"新工具等待审核: {tool_name}")
            logger.info(f"工具描述: {tool_description}")
            logger.info("请使用审核API进行审核")
            
        except Exception as e:
            logger.error(f"通知用户失败: {e}")
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """获取审核统计信息"""
        total_pending = len(self.pending_tools)
        total_reviews = len(self.review_history)
        
        # 审核结果统计
        approved_count = sum(1 for record in self.review_history if record.get('review_status') == 'approved')
        rejected_count = sum(1 for record in self.review_history if record.get('review_status') == 'rejected')
        
        # 最近审核活动
        recent_reviews = self.review_history[-10:] if self.review_history else []
        
        return {
            'pending_tools_count': total_pending,
            'total_reviews': total_reviews,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'approval_rate': approved_count / total_reviews if total_reviews > 0 else 0,
            'recent_reviews': recent_reviews
        }

# 全局工具审核管理器实例
tool_review_manager = ToolReviewManager()

def get_tool_review_manager() -> ToolReviewManager:
    """获取工具审核管理器实例"""
    return tool_review_manager