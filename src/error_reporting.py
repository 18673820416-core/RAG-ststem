#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误上报链路管理
实现组件级到系统级的错误上报

开发提示词来源：二级报错机制优化方案.md
"""
# @self-expose: {"id": "error_reporting", "name": "Error Reporting", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Error Reporting功能"]}}

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorReportingService:
    """错误上报服务"""
    
    def __init__(self, rag_system_path=r"E:\RAG系统"):
        self.rag_system_path = Path(rag_system_path)
        self.error_log_dir = self.rag_system_path / "logs"
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 组件级错误日志
        self.component_error_log = self.error_log_dir / "component_errors.log"
        # 系统级错误日志
        self.system_error_log = self.error_log_dir / "system_errors.log"
    
    def report_component_error(self, error_data):
        """上报组件级错误"""
        # 验证错误数据结构
        self._validate_component_error(error_data)
        
        # 写入组件级错误日志
        with open(self.component_error_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        
        logger.info(f"组件级错误已上报: {error_data['component']}.{error_data['function']} - {error_data['type']} - {error_data['message']}")
        
        # 自动触发系统级错误分析
        self._analyze_system_impact(error_data)
    
    def report_system_error(self, error_data):
        """上报系统级错误"""
        # 验证错误数据结构
        self._validate_system_error(error_data)
        
        # 写入系统级错误日志
        with open(self.system_error_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        
        logger.info(f"系统级错误已上报: {error_data['type']} - {error_data['message']} - 影响组件: {', '.join(error_data['affected_components'])}")
        
        # 通知智能体和IDE
        self._notify_agents(error_data)
        self._notify_ide(error_data)
    
    def _validate_component_error(self, error_data):
        """验证组件级错误数据结构"""
        required_fields = ['error_id', 'level', 'type', 'message', 'timestamp', 'component', 'function']
        for field in required_fields:
            if field not in error_data:
                raise ValueError(f"组件级错误缺少必填字段: {field}")
    
    def _validate_system_error(self, error_data):
        """验证系统级错误数据结构"""
        required_fields = ['error_id', 'level', 'type', 'message', 'timestamp', 'affected_components', 'severity']
        for field in required_fields:
            if field not in error_data:
                raise ValueError(f"系统级错误缺少必填字段: {field}")
    
    def _analyze_system_impact(self, component_error):
        """分析组件级错误对系统的影响"""
        # 这里可以实现更复杂的影响分析逻辑
        # 例如：检查相关组件的状态，分析错误传播路径等
        
        # 简单示例：如果是关键组件错误，直接生成系统级错误
        critical_components = ['MultiAgentChatroom', 'AgentErrorHandler', 'SystemMonitor', 'AgentErrorMonitor']
        if component_error['component'] in critical_components:
            system_error = {
                "error_id": f"system-{datetime.now().isoformat()}-{hash(str(component_error))}",
                "level": "system",
                "type": f"{component_error['component']}_failure",
                "message": f"关键组件 {component_error['component']} 发生错误",
                "timestamp": component_error['timestamp'],
                "affected_components": [component_error['component']],
                "severity": "critical",
                "component_errors": [component_error['error_id']],
                "system_state": self._get_current_system_state(),
                "impact": f"{component_error['component']} 功能完全不可用"
            }
            self.report_system_error(system_error)
    
    def _get_current_system_state(self):
        """获取当前系统状态"""
        # 这里可以集成系统监控模块，获取更详细的系统状态
        return {
            "cpu_usage": "unknown",
            "memory_usage": "unknown",
            "disk_usage": "unknown"
        }
    
    def _notify_agents(self, system_error):
        """通知智能体处理系统级错误"""
        # 这里可以调用agent_error_monitor.py的相关方法
        # 目前直接写入日志，后续可以扩展为调用智能体
        logger.info(f"通知智能体处理系统级错误: {system_error['error_id']}")
    
    def _notify_ide(self, system_error):
        """通知IDE显示系统级错误"""
        # 这里可以实现与IDE的通信机制
        # 目前直接写入日志，后续可以扩展为与IDE通信
        logger.info(f"通知IDE显示系统级错误: {system_error['error_id']}")
    
    def generate_error_id(self, component, error_type):
        """生成唯一错误ID"""
        return f"{component}-{error_type}-{datetime.now().isoformat()}-{hash(str(traceback.format_stack()))}"

# 全局错误上报服务实例
_error_reporting_service = None

def get_error_reporting_service():
    """获取全局错误上报服务实例"""
    global _error_reporting_service
    if _error_reporting_service is None:
        _error_reporting_service = ErrorReportingService()
    return _error_reporting_service

def report_component_error(error_data):
    """上报组件级错误的便捷函数"""
    service = get_error_reporting_service()
    service.report_component_error(error_data)

def report_system_error(error_data):
    """上报系统级错误的便捷函数"""
    service = get_error_reporting_service()
    service.report_system_error(error_data)
