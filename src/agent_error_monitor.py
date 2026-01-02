# @self-expose: {"id": "agent_error_monitor", "name": "Agent Error Monitor", "type": "component", "version": "1.0.0", "needs": {"deps": ["error_decorator", "agent_error_handler"], "resources": []}, "provides": {"capabilities": ["Agent Error Monitor功能"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体错误监听服务
定期检查错误日志，通知智能体处理错误
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# 导入错误捕获装饰器
try:
    from error_decorator import error_catcher, async_error_catcher
except ImportError:
    from src.error_decorator import error_catcher, async_error_catcher

# 配置日志
log_file_path = os.path.join(Path(__file__).parent.parent, 'logs', 'agent_error_monitor.log')

# 创建文件处理器，使用UTF-8编码
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 创建控制台处理器，处理中文和emoji
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 获取根日志记录器并配置
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger = logging.getLogger(__name__)

class AgentErrorMonitor:
    """智能体错误监听服务"""
    
    @error_catcher("AgentErrorMonitor")
    def __init__(self, log_dir=None, check_interval=60):
        # 使用相对路径，避免硬编码绝对路径导致的问题
        if log_dir is None:
            self.log_dir = Path(__file__).parent.parent / "logs"
        else:
            self.log_dir = Path(log_dir)
        self.check_interval = check_interval
        self.last_check_time = datetime.now()
        self.processed_errors = set()
        
    @error_catcher("AgentErrorMonitor")
    def start_monitoring(self):
        """启动错误监听服务"""
        logger.info("🚀 启动智能体错误监听服务")
        while True:
            self.check_errors()
            time.sleep(self.check_interval)
    
    @error_catcher("AgentErrorMonitor")
    def check_errors(self):
        """检查错误日志"""
        # 检查前端错误日志
        frontend_log = self.log_dir / "frontend_errors.log"
        if frontend_log.exists():
            self._process_log_file(frontend_log)
        
        # 检查系统错误日志
        system_log = self.log_dir / "system_errors.log"
        if system_log.exists():
            self._process_log_file(system_log)
    
    @error_catcher("AgentErrorMonitor")
    def _process_log_file(self, log_file):
        """处理日志文件"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError as e:
            # 只使用utf-8编码，因为日志文件是用utf-8写入的
            logger.error(f"使用utf-8编码读取日志文件失败: {e}")
            # 尝试跳过错误行，继续读取
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                logger.info(f"使用ignore模式成功读取日志文件")
            except Exception as e2:
                logger.error(f"读取日志文件失败: {e2}")
                return
        except Exception as e:
            logger.error(f"读取日志文件失败: {e}")
            return
        
        # 组件级错误聚合字典
        component_errors = {}
        
        for line in lines:
            try:
                error_data = json.loads(line.strip())
                error_id = self._generate_error_id(error_data)
                
                # 只处理新错误
                if error_id not in self.processed_errors:
                    self.processed_errors.add(error_id)
                    
                    # 如果是组件级错误，进行聚合
                    if error_data.get('level') == 'component':
                        component_name = error_data.get('component', 'unknown')
                        error_type = error_data.get('type', 'unknown')
                        
                        # 聚合键：组件名 + 错误类型
                        aggregate_key = f"{component_name}:{error_type}"
                        
                        if aggregate_key not in component_errors:
                            component_errors[aggregate_key] = {
                                'component': component_name,
                                'error_type': error_type,
                                'count': 0,
                                'errors': [],
                                'first_occurrence': error_data.get('timestamp'),
                                'last_occurrence': error_data.get('timestamp')
                            }
                        
                        # 更新聚合信息
                        component_errors[aggregate_key]['count'] += 1
                        component_errors[aggregate_key]['errors'].append(error_data)
                        component_errors[aggregate_key]['last_occurrence'] = error_data.get('timestamp')
                        
                        # 通知智能体处理单个组件错误
                        self._notify_agents(error_data)
                    else:
                        # 系统级错误直接处理
                        self._notify_agents(error_data)
            except json.JSONDecodeError:
                # 系统日志可能不是JSON格式，需要特殊处理
                self._process_system_log_line(line.strip())
            except Exception as e:
                logger.error(f"处理日志行失败: {e}")
        
        # 处理聚合后的组件级错误，生成系统级错误
        self._process_aggregated_errors(component_errors)
    
    def _generate_error_id(self, error_data):
        """生成错误唯一标识符"""
        return f"{error_data.get('timestamp', '')}-{error_data.get('type', '')}-{hash(str(error_data.get('message', '')))}"
    
    def _process_aggregated_errors(self, component_errors):
        """处理聚合后的组件级错误，生成系统级错误"""
        for aggregate_key, agg_data in component_errors.items():
            # 如果同一组件的同一类型错误超过阈值（这里设为3），生成系统级错误
            if agg_data['count'] >= 3:
                # 生成系统级错误数据
                system_error = {
                    "level": "system",
                    "type": "system_aggregated_error",
                    "message": f"组件 {agg_data['component']} 频繁出现 {agg_data['error_type']} 错误，已累计 {agg_data['count']} 次",
                    "timestamp": agg_data['last_occurrence'],
                    "component": agg_data['component'],
                    "error_type": agg_data['error_type'],
                    "error_count": agg_data['count'],
                    "first_occurrence": agg_data['first_occurrence'],
                    "last_occurrence": agg_data['last_occurrence'],
                    "affected_components": [agg_data['component']],
                    "severity": "critical",
                    "related_errors": [err['error_id'] for err in agg_data['errors'][:5]],  # 只保留前5个相关错误ID
                    "context": {
                        "aggregate_key": aggregate_key,
                        "sample_error": agg_data['errors'][0] if agg_data['errors'] else {}
                    }
                }
                
                # 生成系统级错误ID
                system_error_id = self._generate_error_id(system_error)
                
                # 通知智能体处理系统级错误
                if system_error_id not in self.processed_errors:
                    self.processed_errors.add(system_error_id)
                    self._notify_agents(system_error)
                    logger.warning(f"⚠️  生成系统级错误: {system_error['message']}")
    
    def _process_system_log_line(self, log_line):
        """处理系统日志行"""
        # 系统日志格式：2025-11-28 09:45:30,123 - rag_system - ERROR - 错误信息
        try:
            # 提取时间戳和错误信息
            if "ERROR" in log_line:
                parts = log_line.split(" - ERROR - ")
                if len(parts) == 2:
                    timestamp_str = parts[0].split(" - ")[0]
                    error_message = parts[1]
                    
                    # 生成错误数据
                    error_data = {
                        "level": "system",
                        "timestamp": timestamp_str,
                        "type": "system_error",
                        "message": error_message,
                        "log_file": "system_errors.log",
                        "severity": "error"
                    }
                    
                    error_id = self._generate_error_id(error_data)
                    if error_id not in self.processed_errors:
                        self.processed_errors.add(error_id)
                        self._notify_agents(error_data)
        except Exception as e:
            logger.error(f"处理系统日志行失败: {e}")
    
    def _notify_agents(self, error_data):
        """通知智能体处理错误"""
        # 这里可以实现智能体通知机制
        # 例如：发送消息到多智能体聊天室
        logger.info(f"发现新错误: {error_data.get('type')} - {error_data.get('message')}")
        
        # 调用智能体处理错误
        self._call_agent_to_handle_error(error_data)
    
    def _call_agent_to_handle_error(self, error_data):
        """调用智能体处理错误"""
        # 这里可以实现智能体调用逻辑
        # 例如：使用多智能体聊天室API发送错误信息
        try:
            # 导入智能体错误处理器
            try:
                from agent_error_handler import AgentErrorHandler
            except ImportError:
                from src.agent_error_handler import AgentErrorHandler
            
            error_handler = AgentErrorHandler()
            success = error_handler.handle_error(error_data)
            
            if success:
                logger.info(f"错误处理成功: {error_data.get('type')}")
            else:
                logger.error(f"错误处理失败: {error_data.get('type')}")
        except Exception as e:
            logger.error(f"调用智能体处理错误失败: {e}")

    def get_error_stats(self):
        """获取错误统计信息"""
        # 简化实现：返回已处理错误的数量和最后检查时间
        return {
            "total_errors": len(self.processed_errors),
            "last_check": self.last_check_time.isoformat(),
            "recent_errors": list(self.processed_errors)[-10:] if self.processed_errors else []  # 最近10个错误ID
        }
