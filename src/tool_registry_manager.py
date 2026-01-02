#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具注册表管理器 - 管理审核通过的工具注册信息
开发提示词来源：用户要求工具发现机制与注册机制联动，发现的工具需用户审核后才能关联到注册表
"""

# @self-expose: {"id": "tool_registry_manager", "name": "Tool Registry Manager", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Tool Registry Manager功能"]}}

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ToolRegistryManager:
    """工具注册表管理器"""
    
    def __init__(self, registry_file: str = "data/tool_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.registered_tools: Dict[str, Dict] = {}
        self._load_registry()
    
    def _load_registry(self):
        """加载工具注册表"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registered_tools = json.load(f)
            else:
                self.registered_tools = {}
                self._save_registry()
            logger.info(f"工具注册表已加载，包含 {len(self.registered_tools)} 个已注册工具")
        except Exception as e:
            logger.error(f"加载工具注册表失败: {e}")
            self.registered_tools = {}
    
    def _save_registry(self):
        """保存工具注册表"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registered_tools, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存工具注册表失败: {e}")
    
    def register_tool(self, tool_info: Dict[str, Any]) -> bool:
        """注册工具到注册表"""
        try:
            tool_id = tool_info.get('tool_id')
            if not tool_id:
                logger.error("工具ID不能为空")
                return False
            
            # 检查工具是否已存在
            if tool_id in self.registered_tools:
                logger.warning(f"工具 {tool_id} 已存在，将更新注册信息")
            
            # 添加注册信息
            tool_info['registration_status'] = 'approved'
            tool_info['registration_timestamp'] = datetime.now().isoformat()
            tool_info['last_used'] = datetime.now().isoformat()
            tool_info['usage_count'] = 0
            
            self.registered_tools[tool_id] = tool_info
            self._save_registry()
            
            logger.info(f"工具 {tool_id} 已成功注册")
            return True
            
        except Exception as e:
            logger.error(f"注册工具失败: {e}")
            return False
    
    def unregister_tool(self, tool_id: str) -> bool:
        """从注册表注销工具"""
        try:
            if tool_id in self.registered_tools:
                del self.registered_tools[tool_id]
                self._save_registry()
                logger.info(f"工具 {tool_id} 已注销")
                return True
            else:
                logger.warning(f"工具 {tool_id} 不存在于注册表中")
                return False
        except Exception as e:
            logger.error(f"注销工具失败: {e}")
            return False
    
    def get_registered_tools(self) -> Dict[str, Dict]:
        """获取所有已注册工具"""
        return self.registered_tools.copy()
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """获取指定工具的详细信息"""
        return self.registered_tools.get(tool_id)
    
    def search_tools(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词搜索工具"""
        results = []
        for tool_id, tool_info in self.registered_tools.items():
            # 在工具名称、描述、类别中搜索
            search_fields = [
                tool_info.get('tool_name', ''),
                tool_info.get('description', ''),
                tool_info.get('tool_category', ''),
                tool_info.get('capabilities', '')
            ]
            
            if any(keyword.lower() in field.lower() for field in search_fields):
                results.append(tool_info)
        
        return results
    
    def update_tool_usage(self, tool_id: str) -> bool:
        """更新工具使用统计"""
        try:
            if tool_id in self.registered_tools:
                tool_info = self.registered_tools[tool_id]
                tool_info['usage_count'] = tool_info.get('usage_count', 0) + 1
                tool_info['last_used'] = datetime.now().isoformat()
                self._save_registry()
                return True
            return False
        except Exception as e:
            logger.error(f"更新工具使用统计失败: {e}")
            return False
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        total_tools = len(self.registered_tools)
        
        # 按类别统计
        categories = {}
        for tool_info in self.registered_tools.values():
            category = tool_info.get('tool_category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # 使用频率统计
        usage_stats = {
            'total_usage': sum(tool_info.get('usage_count', 0) for tool_info in self.registered_tools.values()),
            'most_used': max([(tool_info.get('usage_count', 0), tool_id) 
                            for tool_id, tool_info in self.registered_tools.items()], 
                            default=(0, None))[1]
        }
        
        return {
            'total_registered_tools': total_tools,
            'categories': categories,
            'usage_statistics': usage_stats
        }

# 全局工具注册表管理器实例
tool_registry_manager = ToolRegistryManager()

def get_tool_registry_manager() -> ToolRegistryManager:
    """获取工具注册表管理器实例"""
    return tool_registry_manager