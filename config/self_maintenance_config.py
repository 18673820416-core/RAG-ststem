#!/usr/bin/env python3
# @self-expose: {"id": "self_maintenance_config", "name": "Self Maintenance Config", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Self Maintenance Config功能"]}}
# -*- coding: utf-8 -*-
"""
自我维护功能配置文件
"""

SELF_MAINTENANCE_CONFIG = {
    # 错误监听配置
    "error_monitor": {
        "check_interval": 60,  # 检查间隔（秒）
        "log_dir": "E:\RAG系统\logs",
        "max_processed_errors": 1000  # 最大处理的错误数量
    },
    
    # 错误处理配置
    "error_handler": {
        "max_retries": 3,  # 最大重试次数
        "timeout": 30,  # 命令执行超时时间（秒）
        "auto_fix": True  # 是否自动修复错误
    },
    
    # 系统监控配置
    "system_monitor": {
        "check_interval": 300,  # 检查间隔（秒）
        "alert_thresholds": {
            "cpu_usage": 90,  # CPU使用率告警阈值
            "memory_usage": 90,  # 内存使用率告警阈值
            "disk_usage": 90  # 磁盘使用率告警阈值
        }
    },
    
    # 知识库配置
    "knowledge_base": {
        "auto_learn": True,  # 是否自动学习新的错误模式
        "save_interval": 3600  # 知识库保存间隔（秒）
    },
    
    # 二级报错机制配置
    "secondary_error_reporting": {
        # 组件级错误配置
        "component_level": {
            "enabled": True,  # 是否启用组件级错误上报
            "report_all": True,  # 是否上报所有组件级错误
            "max_errors_per_minute": 100,  # 每分钟最大上报错误数
            "include_context": True,  # 是否包含上下文信息
            "include_stack_trace": True  # 是否包含堆栈信息
        },
        
        # 系统级错误配置
        "system_level": {
            "enabled": True,  # 是否启用系统级错误上报
            "alert_on_critical": True,  # 关键错误是否立即告警
            "notify_agents": True,  # 是否通知智能体处理
            "notify_ide": True,  # 是否通知IDE
            "severity_levels": ["critical", "error", "warning"]  # 关注的严重级别
        },
        
        # 错误聚合配置
        "error_aggregation": {
            "enabled": True,  # 是否启用错误聚合
            "aggregate_window": 300,  # 聚合时间窗口（秒）
            "error_threshold": 3,  # 生成系统级错误的阈值
            "aggregate_keys": ["component", "type", "message"]  # 聚合关键字段
        },
        
        # 错误上报配置
        "reporting": {
            "enabled": True,  # 是否启用错误上报
            "backend_url": "/api/error-report",  # 错误上报后端URL
            "timeout": 10,  # 上报超时时间（秒）
            "retry_count": 3,  # 上报失败重试次数
            "local_storage_backup": True  # 后端离线时是否保存到本地存储
        }
    }
}
