#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控模块
"""
# @self-expose: {"id": "system_monitor", "name": "System Monitor", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["System Monitor功能"]}}

import os
import psutil
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'system_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """系统监控模块"""
    
    def __init__(self, check_interval=300):
        self.check_interval = check_interval
    
    def start_monitoring(self):
        """启动系统监控"""
        logger.info("🚀 启动系统监控")
        while True:
            self.check_system_status()
            time.sleep(self.check_interval)
    
    def check_system_status(self):
        """检查系统状态"""
        # 检查CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 检查内存使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 检查磁盘使用率
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # 检查网络连接
        network = psutil.net_io_counters()
        
        # 检查进程状态
        processes = psutil.pids()
        
        # 生成状态报告
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            },
            "process_count": len(processes)
        }
        
        # 保存状态报告
        self._save_status_report(status_report)
        
        # 检查是否需要告警
        self._check_alerts(status_report)
    
    def _save_status_report(self, status_report):
        """保存状态报告"""
        report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, 'system_status.log')
        with open(report_path, 'a', encoding='utf-8') as f:
            import json
            f.write(json.dumps(status_report, ensure_ascii=False) + '\n')
        
        logger.info(f"📊 系统状态报告已保存: CPU={status_report['cpu_usage']}%, 内存={status_report['memory_usage']}%, 磁盘={status_report['disk_usage']}%")
    
    def _check_alerts(self, status_report):
        """检查是否需要告警"""
        # 简单的告警规则
        if status_report['cpu_usage'] > 90:
            self._send_alert("高CPU使用率", f"CPU使用率: {status_report['cpu_usage']}%")
        if status_report['memory_usage'] > 90:
            self._send_alert("高内存使用率", f"内存使用率: {status_report['memory_usage']}%")
        if status_report['disk_usage'] > 90:
            self._send_alert("高磁盘使用率", f"磁盘使用率: {status_report['disk_usage']}%")
    
    def _send_alert(self, alert_type, message):
        """发送告警"""
        logger.warning(f"⚠️ 告警: {alert_type} - {message}")
        # 这里可以实现告警通知机制
        # 例如：发送消息到多智能体聊天室

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start_monitoring()
