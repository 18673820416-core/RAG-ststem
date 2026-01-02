"""
时机选择策略引擎
实现空闲时段自优化功能

开发提示词来源：用户要求建立架构自优化记忆锚点，实现时机选择策略
"""

# @self-expose: {"id": "timing_strategy_engine", "name": "Timing Strategy Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Timing Strategy Engine功能"]}}

import json
import logging
import time
import threading
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizationTiming(Enum):
    """优化时机类型"""
    USER_REST = "user_rest"  # 用户休息时段（晚上/深夜）
    SYSTEM_IDLE = "system_idle"  # 系统空闲时段
    AGENT_COLLABORATION = "agent_collaboration"  # 智能体协作窗口
    REAL_TIME_MICRO = "real_time_micro"  # 实时微优化

class TimingStrategyEngine:
    """时机选择策略引擎"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化配置文件
        self.config_file = self.data_dir / "timing_strategy_config.json"
        self.schedule_file = self.data_dir / "optimization_schedule.json"
        
        # 默认配置
        self.default_config = {
            "user_rest_hours": {
                "start_hour": 22,  # 晚上10点
                "end_hour": 6,     # 早上6点
                "enabled": True
            },
            "system_idle_threshold": {
                "cpu_threshold": 30.0,  # CPU使用率低于30%
                "memory_threshold": 70.0,  # 内存使用率低于70%
                "network_threshold": 10.0,  # 网络使用率低于10%
                "enabled": True
            },
            "collaboration_windows": {
                "enabled": True,
                "weekend_enabled": True,
                "holiday_enabled": True,
                "daily_windows": [
                    {"start": "02:00", "end": "04:00", "enabled": True},
                    {"start": "14:00", "end": "16:00", "enabled": True}
                ]
            },
            "real_time_micro_optimization": {
                "max_duration_minutes": 5,
                "enabled": True
            },
            "optimization_priorities": {
                "high_priority_tasks": ["security", "performance", "critical_bugs"],
                "medium_priority_tasks": ["functionality", "usability", "maintenance"],
                "low_priority_tasks": ["refactoring", "documentation", "optimization"]
            },
            # 新增：启动时不立即执行任务
            "skip_execution_on_startup": True,
            "startup_delay_minutes": 120  # 启动后略2小时才开始检查任务，确保晚上启动也不会立即执行
        }
        
        # 加载配置
        self.config = self._load_config()
        
        # 优化任务队列
        self.optimization_queue = []
        self.running_tasks = {}
        
        # 监控线程
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # 系统负载历史
        self.system_load_history = []
        
        # 记录启动时间，用于延迟执行检查
        self.startup_time = datetime.now()
        
        logger.info("时机选择策略引擎初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并默认配置和用户配置
                    return self._deep_merge(self.default_config, user_config)
        except Exception as e:
            logger.warning(f"加载配置失败，使用默认配置: {e}")
        
        return self.default_config
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def schedule_optimization(self, task_type: str, task_description: str, 
                            priority: str, estimated_duration: int,
                            optimization_function: Callable,
                            daily_once: bool = False) -> str:
        """调度优化任务
        
        Args:
            task_type: 任务类型
            task_description: 任务描述
            priority: 优先级 (high/medium/low)
            estimated_duration: 预计耗时(分钟)
            optimization_function: 优化函数
            daily_once: 是否每天只执行一次
        """
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_type}"
        
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "description": task_description,
            "priority": priority,
            "estimated_duration": estimated_duration,  # 分钟
            "optimization_function": optimization_function,
            "scheduled_time": datetime.now().isoformat(),
            "status": "pending",
            "attempts": 0,
            "max_attempts": 3,
            "daily_once": daily_once,
            "last_execution_date": None  # 记录最后执行日期
        }
        
        # 添加到队列
        self.optimization_queue.append(task)
        
        # 根据优先级排序
        self._sort_optimization_queue()
        
        logger.info(f"优化任务已调度: {task_id} - {task_description}")
        
        return task_id
    
    def _sort_optimization_queue(self):
        """根据优先级排序优化队列"""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        self.optimization_queue.sort(key=lambda x: (
            priority_order.get(x["priority"], 2),
            x["scheduled_time"]
        ))
    
    def is_optimal_timing(self, timing_type: OptimizationTiming) -> bool:
        """检查是否为最佳时机"""
        
        if timing_type == OptimizationTiming.USER_REST:
            return self._is_user_rest_time()
        
        elif timing_type == OptimizationTiming.SYSTEM_IDLE:
            return self._is_system_idle()
        
        elif timing_type == OptimizationTiming.AGENT_COLLABORATION:
            return self._is_collaboration_window()
        
        elif timing_type == OptimizationTiming.REAL_TIME_MICRO:
            return self._is_real_time_micro_optimization_safe()
        
        return False
    
    def _is_user_rest_time(self) -> bool:
        """检查是否为用户休息时段"""
        if not self.config["user_rest_hours"]["enabled"]:
            return False
        
        current_hour = datetime.now().hour
        start_hour = self.config["user_rest_hours"]["start_hour"]
        end_hour = self.config["user_rest_hours"]["end_hour"]
        
        # 处理跨夜时段
        if start_hour > end_hour:
            return current_hour >= start_hour or current_hour < end_hour
        else:
            return start_hour <= current_hour < end_hour
    
    def _is_system_idle(self) -> bool:
        """检查系统是否空闲"""
        if not self.config["system_idle_threshold"]["enabled"]:
            return False
        
        try:
            # 简化版系统空闲检测 - 基于时间而非实际资源使用
            # 在实际系统中，可以集成真实的系统监控
            current_hour = datetime.now().hour
            
            # 假设凌晨2-6点为系统空闲时段
            is_night_time = 2 <= current_hour <= 6
            
            # 模拟系统负载检测
            # 在实际系统中，这里应该使用真实的系统监控数据
            cpu_threshold = self.config["system_idle_threshold"]["cpu_threshold"]
            memory_threshold = self.config["system_idle_threshold"]["memory_threshold"]
            
            # 返回夜间时段作为系统空闲的简化判断
            return is_night_time
            
        except ImportError:
            logger.warning("psutil未安装，无法检测系统负载")
            return False
        except Exception as e:
            logger.error(f"系统负载检测失败: {e}")
            return False
    
    def _is_collaboration_window(self) -> bool:
        """检查是否为协作窗口"""
        if not self.config["collaboration_windows"]["enabled"]:
            return False
        
        current_time = datetime.now()
        
        # 检查周末
        if self.config["collaboration_windows"]["weekend_enabled"]:
            if current_time.weekday() >= 5:  # 周六或周日
                return True
        
        # 检查节假日（简化版）
        if self.config["collaboration_windows"]["holiday_enabled"]:
            # 这里可以扩展为检查节假日列表
            pass
        
        # 检查每日窗口
        for window in self.config["collaboration_windows"]["daily_windows"]:
            if not window["enabled"]:
                continue
            
            start_time = datetime.strptime(window["start"], "%H:%M").time()
            end_time = datetime.strptime(window["end"], "%H:%M").time()
            current_time_only = current_time.time()
            
            if start_time <= current_time_only <= end_time:
                return True
        
        return False
    
    def _is_real_time_micro_optimization_safe(self) -> bool:
        """检查实时微优化是否安全"""
        if not self.config["real_time_micro_optimization"]["enabled"]:
            return False
        
        # 检查是否有正在运行的高优先级任务
        high_priority_running = any(
            task["priority"] == "high" and task["status"] == "running"
            for task in self.running_tasks.values()
        )
        
        if high_priority_running:
            return False
        
        # 检查系统负载是否足够低
        return self._is_system_idle()
    
    def _record_system_load(self, cpu_percent: float, memory_percent: float, 
                           network_usage: float):
        """记录系统负载历史"""
        load_record = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "network_usage": network_usage
        }
        
        self.system_load_history.append(load_record)
        
        # 保持最近100条记录
        if len(self.system_load_history) > 100:
            self.system_load_history = self.system_load_history[-100:]
    
    def start_monitoring(self):
        """开始监控和调度优化任务"""
        if self.is_monitoring:
            logger.warning("监控已经在运行中")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("时机选择监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("时机选择监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 检查并执行优化任务
                self._execute_optimization_tasks()
                
                # 休眠一段时间
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(10)  # 出错后短暂休眠
    
    def _execute_optimization_tasks(self):
        """执行优化任务"""
        if not self.optimization_queue:
            return
        
        # 检查是否在启动延迟期内
        if self.config.get("skip_execution_on_startup", True):
            delay_minutes = self.config.get("startup_delay_minutes", 5)
            elapsed_time = (datetime.now() - self.startup_time).total_seconds() / 60
            
            if elapsed_time < delay_minutes:
                # 还在启动延迟期内，不执行任务
                logger.debug(f"系统启动后 {elapsed_time:.1f} 分钟，跳过任务执行（延迟期：{delay_minutes}分钟）")
                return
        
        # 获取当前最佳时机类型
        optimal_timing = self._get_current_optimal_timing()
        
        if not optimal_timing:
            return
        
        # 根据时机类型选择任务
        suitable_tasks = self._get_suitable_tasks_for_timing(optimal_timing)
        
        for task in suitable_tasks:
            if task["status"] == "pending" and task["attempts"] < task["max_attempts"]:
                self._execute_single_task(task)
    
    def _get_current_optimal_timing(self) -> Optional[OptimizationTiming]:
        """获取当前最佳时机类型"""
        timing_priority = [
            OptimizationTiming.USER_REST,
            OptimizationTiming.SYSTEM_IDLE,
            OptimizationTiming.AGENT_COLLABORATION,
            OptimizationTiming.REAL_TIME_MICRO
        ]
        
        for timing in timing_priority:
            if self.is_optimal_timing(timing):
                return timing
        
        return None
    
    def _get_suitable_tasks_for_timing(self, timing: OptimizationTiming) -> List[Dict]:
        """根据时机类型获取合适的任务"""
        if timing == OptimizationTiming.USER_REST:
            # 用户休息时段：执行所有类型的任务
            return [task for task in self.optimization_queue 
                    if task["status"] == "pending"]
        
        elif timing == OptimizationTiming.SYSTEM_IDLE:
            # 系统空闲时段：执行中低优先级任务
            return [task for task in self.optimization_queue 
                    if task["status"] == "pending" and 
                    task["priority"] in ["medium", "low"]]
        
        elif timing == OptimizationTiming.AGENT_COLLABORATION:
            # 协作窗口：执行需要协作的任务
            return [task for task in self.optimization_queue 
                    if task["status"] == "pending" and 
                    "collaboration" in task.get("tags", [])]
        
        elif timing == OptimizationTiming.REAL_TIME_MICRO:
            # 实时微优化：执行短时间任务
            max_duration = self.config["real_time_micro_optimization"]["max_duration_minutes"]
            return [task for task in self.optimization_queue 
                    if task["status"] == "pending" and 
                    task["estimated_duration"] <= max_duration]
        
        return []
    
    def _execute_single_task(self, task: Dict):
        """执行单个任务"""
        task_id = task["task_id"]
        
        try:
            # 检查是否为每天只执行一次的任务
            if task.get("daily_once", False):
                today = datetime.now().strftime("%Y%m%d")
                last_execution = task.get("last_execution_date")
                
                # 如果今天已经执行过，跳过
                if last_execution == today:
                    logger.debug(f"任务 {task_id} 今天已执行，跳过")
                    return
                
                # 如果是刚调度的任务（启动时调度），不立即执行
                # 等待至少到2小时后才执行
                scheduled_time = datetime.fromisoformat(task["scheduled_time"])
                time_since_schedule = (datetime.now() - scheduled_time).total_seconds() / 3600  # 小时
                
                if time_since_schedule < 2:
                    logger.debug(f"任务 {task_id} 调度后仅 {time_since_schedule:.1f} 小时，等待至少 2 小时后执行")
                    return
            
            # 更新任务状态
            task["status"] = "running"
            task["start_time"] = datetime.now().isoformat()
            self.running_tasks[task_id] = task
            
            logger.info(f"开始执行优化任务: {task_id}")
            
            # 执行优化函数
            optimization_function = task["optimization_function"]
            result = optimization_function()
            
            # 更新任务状态
            task["status"] = "completed"
            task["end_time"] = datetime.now().isoformat()
            task["result"] = result
            
            # 记录执行日期(如果是每天只执行一次的任务)
            if task.get("daily_once", False):
                task["last_execution_date"] = datetime.now().strftime("%Y%m%d")
            
            logger.info(f"优化任务完成: {task_id}")
            
        except Exception as e:
            # 任务执行失败
            task["status"] = "failed"
            task["error"] = str(e)
            task["attempts"] += 1
            
            logger.error(f"优化任务失败: {task_id} - {e}")
        
        finally:
            # 从运行任务中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def get_scheduling_status(self) -> Dict[str, Any]:
        """获取调度状态"""
        return {
            "is_monitoring": self.is_monitoring,
            "queue_length": len(self.optimization_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len([t for t in self.optimization_queue if t["status"] == "completed"]),
            "failed_tasks": len([t for t in self.optimization_queue if t["status"] == "failed"]),
            "current_timing": self._get_current_optimal_timing(),
            "system_load_history_count": len(self.system_load_history)
        }

# 全局时机策略引擎实例
timing_engine = TimingStrategyEngine()

def get_timing_engine() -> TimingStrategyEngine:
    """获取时机策略引擎实例"""
    return timing_engine