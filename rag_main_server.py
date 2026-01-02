#!/usr/bin/env python
# @self-expose: {"id": "rag_main_server", "name": "RAG Main Server", "type": "api", "version": "1.2.0", "needs": {"deps": ["vector_database", "mesh_thought_engine", "multi_agent_chatroom", "memory_bubble_manager", "event_dimension_encoder", "induction_engine", "nightly_maintenance_scheduler"], "resources": []}, "provides": {"capabilities": ["RAG核心服务", "多智能体协作", "向量检索", "认知引擎", "前置主题归纳接入", "评估任务下发", "手动触发记忆重构"], "endpoints": [{"path": "/api/text-blocks", "method": "GET", "desc": "获取文本块列表和关联关系"}, {"path": "/api/health", "method": "GET", "desc": "API健康检查"}, {"path": "/api/status", "method": "GET", "desc": "系统状态"}, {"path": "/api/agents", "method": "GET", "desc": "智能体列表"}, {"path": "/api/chatroom/status", "method": "GET", "desc": "聊天室状态"}, {"path": "/api/chatroom/message", "method": "POST", "desc": "发送聊天室消息"}, {"path": "/maintenance/memory_reconstruction", "method": "POST", "desc": "手动触发记忆重构"}]}}
# -*- coding: utf-8 -*-
"""
RAG智能系统主服务器
==================

服务器定位：
- RAG系统核心服务器，包含所有业务逻辑和重资源
- 多智能体协作平台、向量数据库、认知引擎集成
- 运行在端口5000，按需启动（由static_server控制）
- 【架构设计】在虚拟环境中运行，虚拟环境由静态服务器管理

核心功能：
1. 多智能体聊天室 (templates/chatroom.html) - 智能体协作平台
2. 基类智能体交互 (templates/base_agent_chat.html) - 单智能体对话
3. 向量数据库、Embedding服务、认知引擎等RAG核心组件

启动方式：
- 【推荐】由static_server.py控制启动（通过/api/start_backend）
  静态服务器负责调用虚拟环境中的Python解释器启动本服务器
- 【调试】直接运行: python rag_main_server.py（需确保在虚拟环境中）
- 访问地址: http://localhost:5000

技术栈：
- Python 3.13.7 + NumPy 2.2.6 + OpenCV-Python 4.12.0.88
- 内置HTTP服务器 (http.server)
- 多智能体聊天室引擎
- 网状思维引擎、认知破障引擎等

虚拟环境说明：
- 【架构设计】虚拟环境myenv_stable由静态服务器管理，属于基础设施层
- 本服务器在虚拟环境中运行，但不负责虚拟环境的创建和管理
- 原因：虚拟环境是稳定的前置依赖，应由常驻进程（静态服务器）管理

注意：这是RAG系统主服务器，包含所有重资源（NumPy、OpenCV等），纯业务逻辑层。
"""

import os
import sys
import json
import threading
import time
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# 配方验证
import sys
import numpy
import cv2

# 严格按照稳定配方进行版本检查
assert sys.version_info[:2] == (3, 13), f"必须使用Python 3.13.x版本，当前版本: {sys.version}"
assert numpy.__version__ == "2.2.6", f"必须使用NumPy 2.2.6版本，当前版本: {numpy.__version__}"
assert cv2.__version__ == "4.12.0", f"必须使用OpenCV-Python 4.12.0版本，当前版本: {cv2.__version__}"

# 忽略numpy警告
import warnings
warnings.filterwarnings('ignore')

# 禁用numpy的实验性警告
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['PYTHONWARNINGS'] = 'ignore'

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 创建日志记录器
logger = logging.getLogger('rag_system')
logger.setLevel(logging.INFO)

# ✅ 清理已存在的handlers，避免重复输出（关键修复）
if logger.handlers:
    logger.handlers.clear()

# 🔥 阻止日志向根logger传播，避免memory_log_handler重复捕获
logger.propagate = False

# 创建文件处理器
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'system_errors.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(file_handler)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 🔥 添加内存日志捕获器（用于实时分析启动日志）
class MemoryLogHandler(logging.Handler):
    """内存日志处理器，捕获启动过程中的所有日志"""
    def __init__(self):
        super().__init__()
        self.logs = []  # 存储所有日志记录
        
    def emit(self, record):
        try:
            log_entry = {
                "timestamp": self.format(record).split(' - ')[0],
                "logger": record.name,
                "level": record.levelname,
                "message": record.getMessage()
            }
            self.logs.append(log_entry)
        except:
            pass
    
    def add_print_output(self, message: str):
        """手动添加print输出到日志列表"""
        try:
            log_entry = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
                "logger": "stdout",
                "level": "INFO",
                "message": message
            }
            self.logs.append(log_entry)
        except:
            pass
    
    def get_duplicates(self):
        """分析并返回重复日志"""
        from collections import defaultdict
        log_counter = defaultdict(list)
        
        for log in self.logs:
            log_key = f"{log['logger']}::{log['message']}"
            log_counter[log_key].append(log['timestamp'])
        
        duplicates = []
        for log_key, timestamps in log_counter.items():
            if len(timestamps) > 1:
                logger_name, message = log_key.split('::', 1)
                duplicates.append({
                    "message": message,
                    "logger": logger_name,
                    "count": len(timestamps),
                    "timestamps": timestamps
                })
        return duplicates


# 🔥 标准输出重定向类（捕获print输出）
class StdoutCapture:
    """捕获标准输出，同时显示到终端和记录到内存"""
    def __init__(self, memory_handler):
        self.memory_handler = memory_handler
        self.terminal = sys.stdout
        
    def write(self, message):
        # 输出到终端
        self.terminal.write(message)
        # 记录到内存（去除空行）
        message = message.rstrip()
        if message:
            self.memory_handler.add_print_output(message)
    
    def flush(self):
        self.terminal.flush()

# 创建并添加内存日志捕获器
memory_log_handler = MemoryLogHandler()
memory_log_handler.setLevel(logging.INFO)
memory_log_handler.setFormatter(formatter)
logger.addHandler(memory_log_handler)

# 🔥 将内存日志捕获器添加到根日志记录器，捕获所有模块的日志
root_logger = logging.getLogger()
root_logger.addHandler(memory_log_handler)

# 🔥 重定向标准输出，捕获print输出
sys.stdout = StdoutCapture(memory_log_handler)

# 本地交互日志记录（JSONL）
try:
    from config.system_config import INTERACTION_LOG_DIR, LOG_INTERACTIONS
    INTERACTION_LOG_DIR = str(INTERACTION_LOG_DIR)
except Exception:
    INTERACTION_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'interactions')
    LOG_INTERACTIONS = True
os.makedirs(INTERACTION_LOG_DIR, exist_ok=True)

def log_interaction(event: dict):
    if not LOG_INTERACTIONS:
        return
    try:
        event = dict(event)
        event['timestamp'] = datetime.now().isoformat()
        filename = datetime.now().strftime('%Y%m%d') + '.jsonl'
        with open(os.path.join(INTERACTION_LOG_DIR, filename), 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    except Exception as e:
        logger.error(f"交互日志写入失败: {e}")

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

# 启动自曝光状态文件（便于外部查看启动结果）
STARTUP_STATUS_FILE = os.path.join(log_dir, 'startup_status.json')

# 导入聊天室模块
chatroom_import_ok = False
try:
    from src.multi_agent_chatroom import MultiAgentChatroom, AgentRole
    print("导入多智能体聊天室模块成功")
    chatroom_import_ok = True
except Exception as e:
    print(f"导入多智能体聊天室模块失败: {e}")
    logger.error(f"导入多智能体聊天室模块失败: {e}")

# 导入时机选择策略引擎
timing_engine_import_ok = False
try:
    from src.timing_strategy_engine import TimingStrategyEngine, OptimizationTiming
    print("导入时机选择策略引擎成功")
    timing_engine_import_ok = True
except Exception as e:
    print(f"导入时机选择策略引擎失败: {e}")
    logger.error(f"导入时机选择策略引擎失败: {e}")

# 导入记忆重构引擎
memory_reconstruct_import_ok = False
try:
    from src.cognitive_engines.memory_reconstruction_engine import BatchMemoryReconstructor
    from src.vector_database import VectorDatabase
    print("导入记忆重构引擎成功")
    memory_reconstruct_import_ok = True
except Exception as e:
    print(f"导入记忆重构引擎失败: {e}")
    logger.error(f"导入记忆重构引擎失败: {e}")

# 导入夜间维护调度器
nightly_scheduler_import_ok = False
try:
    from src.nightly_maintenance_scheduler import NightlyMaintenanceScheduler
    from src.agent_manager import get_agent_manager
    print("导入夜间维护调度器成功")
    nightly_scheduler_import_ok = True
except Exception as e:
    print(f"导入夜间维护调度器失败: {e}")
    logger.error(f"导入夜间维护调度器失败: {e}")

# 记录启动模块加载状态，便于外部查看
try:
    startup_status = {
        "timestamp": datetime.now().isoformat(),
        "server_type": "rag_main",
        "python_version": sys.version,
        "numpy_version": numpy.__version__,
        "opencv_version": cv2.__version__,
        "chatroom_import_ok": chatroom_import_ok,
        "timing_engine_import_ok": timing_engine_import_ok,
        "memory_reconstruct_import_ok": memory_reconstruct_import_ok,
        "nightly_scheduler_import_ok": nightly_scheduler_import_ok
    }
    # 写入最新快照文件
    with open(STARTUP_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(startup_status, f, ensure_ascii=False, indent=2)
    # 追加写入历史记录文件，保留时间序列
    history_file = os.path.join(log_dir, 'startup_status_history.jsonl')
    with open(history_file, 'a', encoding='utf-8') as hf:
        hf.write(json.dumps(startup_status, ensure_ascii=False) + "\n")
except Exception as e:
    logger.error(f"写入启动状态文件失败: {e}")

# 全局时机策略引擎实例
timing_engine = None

# 全局记忆重构器实例
batch_reconstructor = None

# 全局夜间维护调度器实例
nightly_scheduler = None

class RAGStableStartHandler(http.server.SimpleHTTPRequestHandler):
    """RAG系统稳定版HTTP请求处理器"""
    
    # 聊天室实例（类变量，所有实例共享）
    chatroom_instance = None
    
    # 后端服务状态
    backend_status = "inactive"
    
    def _send_json_response(self, response_data: dict, status_code: int = 200):
        """统一的JSON响应发送方法，处理连接中止异常
        
        Args:
            response_data: 要返回的数据字典
            status_code: HTTP状态码
        """
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            # 客户端提前关闭连接，静默处理
            pass
        except Exception as e:
            # 其他异常才记录
            logger.error(f"发送JSON响应失败: {e}")
    
    @classmethod
    def initialize_chatroom(cls):
        """初始化聊天室实例"""
        if cls.chatroom_instance is None:
            try:
                cls.chatroom_instance = MultiAgentChatroom()
                logger.info("多智能体聊天室初始化成功")
            except Exception as e:
                logger.error(f"聊天室初始化失败: {e}")
                cls.chatroom_instance = None
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API健康检查
        if path == '/api/health':
            # 根据后端服务状态返回不同的状态信息
            status = "running"
            backend_status = self.backend_status
            
            if backend_status == "active":
                message = "RAG系统后端服务运行正常"
            elif backend_status == "starting":
                message = "RAG系统后端服务正在启动"
            elif backend_status == "error":
                message = "RAG系统后端服务启动失败"
                status = "error"
            else:
                message = "RAG系统前端服务运行正常，后端服务未启动"
            
            response = {
                "version": "1.0.0",
                "message": message,
                "status": status,
                "backend_status": backend_status,
                "python_version": "3.13.7",
                "numpy_version": "2.3.3",
                "timestamp": datetime.now().isoformat()
            }
            self._send_json_response(response)
            return
        
        # 系统状态
        elif path == '/api/status':
            response = {
                "status": "running",
                "server_type": "stable",
                "modules_loaded": ["网状思维引擎", "视觉处理引擎", "多模态融合引擎", "向量数据库"],
                "timestamp": datetime.now().isoformat()
            }
            self._send_json_response(response)
            return

        # 聊天室历史记录接口 - 直接从chatroom实例获取
        elif path == '/api/chatroom/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 初始化聊天室实例
                self.initialize_chatroom()
                
                if self.chatroom_instance:
                    # 直接从聊天室获取历史记录
                    history = self.chatroom_instance.get_conversation_history()
                    response = {
                        "success": True,
                        "history": history,
                        "count": len(history),
                        "source": "chatroom_direct",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response = {
                        "success": False,
                        "error": "聊天室未初始化",
                        "history": [],
                        "count": 0,
                        "source": "chatroom_not_initialized",
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                logger.error(f"获取聊天室历史失败: {e}")
                response = {
                    "success": False,
                    "error": str(e),
                    "history": [],
                    "count": 0,
                    "source": "error",
                    "timestamp": datetime.now().isoformat()
                }
            
            self._send_json_response(response)
            return
        
        # 文本块关联关系接口
        elif path == '/api/text-blocks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # ✅ 引用统一数据源服务（Single Source of Truth）
                from src.system_statistics_service import get_system_statistics_service
                
                # ✅ 修复：使用缓存（5分钟TTL），避免每次API调用都重建知识图谱
                # force_refresh=True会导致每次都调用build_knowledge_graph()，产生重复日志
                stats_service = get_system_statistics_service()
                system_stats = stats_service.get_system_statistics(force_refresh=False)
                
                # 提取统计数据
                vdb_stats = system_stats['vector_database']
                kg_stats = system_stats['knowledge_graph']
                te_stats = system_stats['thought_engine']
                
                # 🐞 DEBUG: 输出统计数据
                logger.info(f"📊 [API] 向量数据库统计: {vdb_stats}")
                logger.info(f"📊 [API] 知识图谱统计: {kg_stats}")
                logger.info(f"📊 [API] 思维引擎统计: {te_stats}")
                
                # 构建文本块列表（依然从向量数据库获取，但统计数据使用统一来源）
                from src.vector_database import VectorDatabase
                vector_db = VectorDatabase()
                all_memories = vector_db.get_all_memories()
                
                # 只保留主数据库(status='active')的记忆
                active_memories = [
                    memory for memory in all_memories 
                    if memory.get('status', 'active') == 'active'
                ]
                
                logger.info(f"📊 记忆库统计: 总记忆={len(all_memories)}, 主库(active)={len(active_memories)}, 备库/淘汰库={len(all_memories) - len(active_memories)}")
                
                # 构建文本块数据
                blocks = []
                for memory in active_memories:
                    content = memory.get('content', '')
                    timestamp_str = memory.get('timestamp', '')
                    
                    # 转换时间格式
                    try:
                        if isinstance(timestamp_str, str):
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        else:
                            timestamp = datetime.now()
                        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 创建文本块
                    block = {
                        'id': memory.get('id', f'memory_{len(blocks)}'),
                        'title': content[:30] + '...' if len(content) > 30 else content,
                        'content': content,
                        'timestamp': formatted_time,
                        'importance': memory.get('importance', 0.5),
                        'connections': [],
                        'source': memory.get('source_type', 'vector_database')
                    }
                    blocks.append(block)
                
                # 按重要性排序
                blocks.sort(key=lambda x: x['importance'], reverse=True)
                
                # ✅ 返回统一数据源的统计数据
                response = {
                    'success': True,
                    'blocks': blocks[:50],  # 限制返回前50个文本块
                    # ✅ 所有统计数据都来自 SystemStatisticsService
                    'count': vdb_stats['total_memories'],  # 总文本块数
                    'total_connections': kg_stats['total_edges'],  # 知识图谱关联数
                    'thought_nodes_count': te_stats['total_nodes'],  # 思维节点数
                    'knowledge_graph_nodes': kg_stats['total_nodes'],  # 知识图谱节点数
                    'metadata': {
                        'data_source': system_stats['metadata']['data_source'],
                        'timestamp': system_stats['metadata']['timestamp'],
                        'memory_classification': {
                            'active': vdb_stats['active_memories'],
                            'archived': vdb_stats['archived_memories'],
                            'retired': vdb_stats['retired_memories']
                        },
                        'deduplication_rate': te_stats['deduplication_rate'],
                        'coverage_rate': kg_stats['coverage_rate']
                    }
                }
                
                # 🐞 DEBUG: 输出最终响应
                logger.info(f"📊 [API] 最终响应: count={response['count']}, thought_nodes={response['thought_nodes_count']}, connections={response['total_connections']}")
            except Exception as e:
                response = {
                    'success': False,
                    'error': str(e),
                    'blocks': [],
                    'count': 0,
                    'total_connections': 0,
                    'thought_nodes_count': 0,
                    'knowledge_graph_nodes': 0
                }
                import traceback
                traceback.print_exc()
            
            self._send_json_response(response)
            return
            
        # 智能体列表接口 - 动态获取智能体列表
        elif path == '/api/agents' or path == '/api/chatroom/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 初始化聊天室实例
                self.initialize_chatroom()
                
                if self.chatroom_instance:
                    # 获取智能体窗口信息
                    agent_windows = self.chatroom_instance.get_agent_windows_info()
                    
                    # 智能体角色映射字典 - 中文角色名称映射为英文agent_id
                    role_mapping = {
                        "构架师": "architect",
                        "方案评估师": "evaluator",
                        "代码实现师": "implementer",
                        "数据收集师": "data_collector",
                        "系统维护师": "maintenance"
                    }
                    
                    # 智能体图标映射
                    agent_icons = {
                        "architect": "🏗️",
                        "evaluator": "📊",
                        "implementer": "💻",
                        "data_collector": "📡",
                        "maintenance": "🔧"
                    }
                    
                    # 转换为前端需要的格式 - 匹配前端期望的字段名
                    agents = []
                    for window in agent_windows:
                        chinese_role = window["role"]
                        # 获取英文agent_id，如果没有映射则使用默认值
                        agent_id = role_mapping.get(chinese_role, chinese_role.lower())
                        
                        # 前端期望的字段名：id, nickname, role, icon
                        agents.append({
                            "id": agent_id,  # 前端使用 agent.id
                            "nickname": chinese_role,  # 前端使用 agent.nickname
                            "role": chinese_role,  # 前端使用 agent.role
                            "icon": agent_icons.get(agent_id, "🤖"),  # 前端使用 agent.icon
                            "status": "active",
                            "window_id": window["window_id"]
                        })
                    
                    response = {
                        "success": True,
                        "agents": agents,
                        "total": len(agents),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response = {
                        "success": False,
                        "error": "聊天室未初始化",
                        "agents": [],
                        "total": 0,
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                response = {
                    "success": False,
                    "error": str(e),
                    "agents": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            self._send_json_response(response)
            return
        
        # 聊天室状态接口
        elif path == '/api/chatroom/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 初始化聊天室实例
                self.initialize_chatroom()
                
                if self.chatroom_instance:
                    response = {
                        "success": True,
                        "status": "active" if self.chatroom_instance.is_active else "inactive",
                        "agent_count": len(self.chatroom_instance.agent_windows),
                        "collaboration_level": getattr(self.chatroom_instance, 'window_collaboration_level', 'low'),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response = {
                        "success": False,
                        "status": "inactive",
                        "error": "聊天室未初始化",
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                response = {
                    "success": False,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            self._send_json_response(response)
            return
        
        # 系统问题诊断接口
        elif path == '/api/diagnostics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 导入路径处理工具
                from src.path_utils import get_path_utils
                
                # 导入错误处理模块
                from src.agent_error_handler import AgentErrorHandler
                from src.error_knowledge_base import ErrorKnowledgeBase
                from src.problem_diagnostics import get_problem_diagnostics
                
                # 初始化诊断模块
                diagnostics = get_problem_diagnostics()
                results = diagnostics.run_full_diagnostics()
                
                response = {
                    "success": True,
                    "diagnostics": results
                }
            except Exception as e:
                logger.error(f"问题诊断接口错误: {e}")
                response = {
                    "success": False,
                    "error": str(e)
                }
            
            self._send_json_response(response)
            return
        
        # 根路径重定向到start.html
        elif path == '/':
            self.send_response(302)
            self.send_header('Location', '/start.html')
            self.end_headers()
            return
        
        # 静态文件服务
        else:
            try:
                # 设置当前目录为静态文件根目录
                self.directory = os.path.dirname(os.path.abspath(__file__))
                super().do_GET()
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                # 客户端提前关闭连接，这是正常现象（如页面刷新、导航离开等）
                # 不需要记录错误日志，静默处理即可
                pass
            except Exception as e:
                # 其他异常才记录日志
                logger.error(f"静态文件服务异常: {e}")
    
    def start_real_backend_service(self, port):
        """启动真正的后端服务进程"""
        try:
            logger.info(f"正在启动真正的后端服务进程，端口: {port}")
            
            # 这里可以启动真正的后端服务，比如启动一个独立的进程
            # 目前先模拟启动过程
            import time
            time.sleep(2)  # 模拟启动时间
            
            logger.info(f"后端服务进程启动成功，端口: {port}")
            
            # 更新健康检查状态，表示后端服务已启动
            self.backend_status = "active"
            
        except Exception as e:
            logger.error(f"后端服务启动失败: {e}")
            self.backend_status = "error"
    
    def _handle_file_upload(self):
        """处理文件上传请求 - 手动解析multipart数据"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            logger.info(f"收到文件上传请求，请求体大小: {len(body)} 字节")
            
            # 获取Content-Type和boundary
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                raise ValueError("请求中缺少boundary参数")
            
            # 提取boundary
            boundary = content_type.split('boundary=')[1].strip()
            boundary_bytes = ('--' + boundary).encode('utf-8')
            
            logger.info(f"Boundary: {boundary}")
            
            # 手动解析multipart数据
            parts = body.split(boundary_bytes)
            
            filename = None
            content = None
            
            for part in parts:
                if not part or part == b'--\r\n' or part == b'--':
                    continue
                
                # 查找fieldname="file"
                if b'name="file"' in part:
                    # 提取文件名
                    if b'filename="' in part:
                        filename_start = part.find(b'filename="') + len(b'filename="')
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode('utf-8')
                    
                    # 提取文件内容（在\r\n\r\n之后）
                    content_start = part.find(b'\r\n\r\n')
                    if content_start != -1:
                        content_start += 4  # 跳过\r\n\r\n
                        # 内容结束于\r\n之前
                        content_end = len(part)
                        if part.endswith(b'\r\n'):
                            content_end -= 2
                        
                        content = part[content_start:content_end]
                    break
            
            if not filename or content is None:
                raise ValueError("未找到文件数据")
            
            logger.info(f"解析文件成功 - 文件名: {filename}, 内容大小: {len(content)} 字节")
            
            if filename:
                # 确保uploads目录存在
                current_dir = os.path.dirname(os.path.abspath(__file__))
                upload_dir = os.path.join(current_dir, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 获取文件扩展名
                file_ext = os.path.splitext(filename)[1].lower()
                logger.info(f"上传文件: {filename}, 扩展名: {file_ext}")
                
                # 保存文件到uploads目录
                file_path = os.path.join(upload_dir, os.path.basename(filename))
                
                # 根据文件类型决定保存方式
                if file_ext in ['.txt', '.md', '.json', '.xml', '.csv', '.log', '.py', '.java', '.cpp', '.c', '.h', '.js', '.ts', '.html', '.css']:
                    # 文本文件，尝试使用UTF-8编码
                    try:
                        # 尝试解码为UTF-8
                        text_content = content.decode('utf-8')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(text_content)
                        logger.info(f"文本文件以UTF-8编码保存: {file_path}")
                    except UnicodeDecodeError:
                        # 如果解码失败，尝试GBK编码
                        try:
                            text_content = content.decode('gbk')
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(text_content)
                            logger.info(f"文本文件以GBK转UTF-8保存: {file_path}")
                        except:
                            # 最后尝试，直接保存二进制
                            with open(file_path, 'wb') as f:
                                f.write(content)
                            logger.warning(f"文本文件编码无法识别，以二进制保存: {file_path}")
                else:
                    # 非文本文件（如DOCX、PDF等），直接保存二进制
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"二进制文件保存: {file_path}")
                
                logger.info(f"文件上传成功: {filename} -> {file_path}")
                
                # 【新增】文件上传后立即触发：分片 → 向量化 → 入库流程
                vectorization_result = self._process_uploaded_file_to_vector_db(
                    file_path, filename, file_ext
                )
                
                # 返回成功响应
                response = {
                    "success": True,
                    "file_path": file_path,
                    "file_name": os.path.basename(filename),
                    "file_ext": file_ext,
                    "message": "文件上传成功",
                    "vectorization": vectorization_result  # 附加向量化结果
                }
                # 记录交互日志
                log_interaction({
                    "path": "/api/upload",
                    "method": "POST",
                    "content_type": self.headers.get('Content-Type', ''),
                    "request": {"file_name": filename},
                    "response": response
                })
            else:
                response = {
                    "success": False,
                    "error": "没有选择文件"
                }
                # 记录交互日志
                log_interaction({
                    "path": "/api/upload",
                    "method": "POST",
                    "content_type": self.headers.get('Content-Type', ''),
                    "request": {"file_name": None},
                    "response": response
                })
        except Exception as e:
            logger.error(f"文件上传失败: {e}", exc_info=True)
            response = {
                "success": False,
                "error": str(e)
            }
            # 记录交互日志
            log_interaction({
                "path": "/api/upload",
                "method": "POST",
                "content_type": self.headers.get('Content-Type', ''),
                "request": {"file_name": None},
                "response": response,
                "error": str(e)
            })
        
        # 发送响应
        self._send_json_response(response)
    
    def _process_uploaded_file_to_vector_db(self, file_path: str, filename: str, file_ext: str) -> dict:
        """处理上传文件：分片 → 向量化 → 存入向量库
        
        流程：
        1. 读取文件内容
        2. 调用 MemorySlicerTool 进行多层次自适应分片
        3. 使用 EventDimensionEncoder 提取事件编码
        4. 使用 MeshThoughtEngine 分析文本关系
        5. 为每个切片生成向量
        6. 将切片保存到向量数据库
        
        Args:
            file_path: 文件保存路径
            filename: 原始文件名
            file_ext: 文件扩展名
            
        Returns:
            dict: 向量化处理结果
        """
        try:
            # 导入必要的模块
            from tools.memory_slicer_tool import MemorySlicerTool
            from src.vector_database import VectorDatabase
            from src.event_dimension_encoder import EventDimensionEncoder
            from src.mesh_thought_engine import MeshThoughtEngine
            from tools.induction_engine import summarize_topic, extract_events
            from src.memory_bubble_manager import MemoryBubbleManager
            
            logger.info(f"开始处理上传文件的向量化流程: {filename}")
            
            # 1. 读取文件内容
            try:
                if file_ext in ['.txt', '.md', '.json', '.xml', '.csv', '.log', '.py', '.java', '.cpp', '.c', '.h', '.js', '.ts', '.html', '.css']:
                    # 文本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif file_ext in ['.docx']:
                    # Word文档（需要python-docx）
                    try:
                        from docx import Document
                        doc = Document(file_path)
                        content = '\n'.join([para.text for para in doc.paragraphs])
                    except ImportError:
                        logger.warning("未安装python-docx，跳过DOCX文件处理")
                        return {"status": "skipped", "reason": "DOCX处理需要python-docx库"}
                else:
                    # 其他文件类型暂不支持文本提取
                    logger.info(f"文件类型 {file_ext} 暂不支持文本提取，跳过向量化")
                    return {"status": "skipped", "reason": f"不支持的文件类型: {file_ext}"}
                
                if not content or len(content.strip()) < 10:
                    logger.warning(f"文件内容为空或过短，跳过向量化: {filename}")
                    return {"status": "skipped", "reason": "文件内容为空或过短"}
                    
            except Exception as e:
                logger.error(f"读取文件内容失败: {e}")
                return {"status": "error", "reason": f"读取文件失败: {str(e)}"}
            
            # 2. 创建工具实例
            slicer = MemorySlicerTool()
            vector_db = VectorDatabase()
            event_encoder = EventDimensionEncoder()
            mesh_engine = MeshThoughtEngine()
            
            # 3. 调用多层次自适应分片工具
            metadata = {
                "source": "file_upload",
                "filename": filename,
                "file_ext": file_ext,
                "upload_time": datetime.now().isoformat()
            }
            
            slices = slicer.slice_text(
                text=content,
                metadata=metadata,
                source_file=filename
            )
            
            logger.info(f"分片完成，生成 {len(slices)} 个切片")
            
            if not slices:
                return {"status": "error", "reason": "分片失败，未生成任何切片"}
            
            # 4. 对每个切片进行向量化并保存
            saved_count = 0
            evaluation_context = []
            for slice_data in slices:
                slice_content = slice_data.get('content', '')
                if not slice_content:
                    continue
                
                try:
                    # 4.1 使用事件维编码器提取事件编码
                    event_codes = event_encoder.extract_event_codes_from_memory(slice_data)
                    
                    # 4.2 使用网状思维引擎分析文本关系
                    mesh_engine.add_thought(slice_content, slice_data)
                    
                    # 4.3 生成内容向量（简化实现）
                    content_vector = self._generate_simple_vector(slice_content)
                    
                    # 4.4 构建记忆数据（集成归纳引擎前置）
                    summary = summarize_topic(slice_content)
                    events = extract_events(slice_content)
                    topic_text = summary.get('topic_summary') or f"上传文件 - {filename}"
                    key_points = summary.get('key_points', [])[:5]
                    event_tags = [("evt:" + (e.get('snippet','')[:30])).strip() for e in events][:8]
                    memory_data = {
                        "topic": topic_text,
                        "content": slice_content,
                        "source_type": "file_upload",
                        "filename": filename,
                        "file_ext": file_ext,
                        "slice_id": slice_data.get('slice_id', ''),
                        "slice_depth": slice_data.get('slice_depth', 0),
                        "parent_id": slice_data.get('parent_id', ''),
                        "event_codes": event_codes,
                        "timestamp": metadata['upload_time'],
                        "importance": slice_data.get('importance', 0.7),
                        "confidence": slice_data.get('confidence', 0.9),
                        "tags": ["file_upload", filename, file_ext.replace('.', '')] + event_codes + [("kp:" + kp) for kp in key_points] + event_tags
                    }
                    
                    # 4.5 保存到向量数据库
                    mem_id = vector_db.add_memory(memory_data, vector=content_vector)
                    saved_count += 1
                    # 4.6 生成评估上下文条目（供评估师智能体检索）
                    evaluation_context.append({
                        "memory_id": mem_id,
                        "topic_summary": topic_text,
                        "key_points": key_points,
                        "event_count": len(events)
                    })
                    
                except Exception as e:
                    logger.error(f"保存切片到向量库失败: {e}")
                    continue
            
            logger.info(f"向量化完成，成功保存 {saved_count}/{len(slices)} 个切片到向量库")
            
            # 5. 下发评估任务泡泡（方案评估师/evaluator）
            try:
                bubble_mgr = MemoryBubbleManager(agent_id="evaluator")
                bubble_mgr.quick_note(
                    category=MemoryBubbleManager.CATEGORY_TODO,
                    content=f"评估主题归纳是否符合文本块特性：文件 {filename}，共 {saved_count} 个切片",
                    context={
                        "file_name": filename,
                        "slice_count": saved_count,
                        "mem_summaries": evaluation_context
                    },
                    priority="normal"
                )
            except Exception as be:
                logger.warning(f"评估任务泡泡下发失败: {be}")
            return {
                "status": "success",
                "total_slices": len(slices),
                "saved_slices": saved_count,
                "message": f"文件已分片并向量化存储，共 {saved_count} 个切片"
            }
            
        except Exception as e:
            logger.error(f"文件向量化处理失败: {e}", exc_info=True)
            return {
                "status": "error",
                "reason": str(e)
            }
    
    def _generate_simple_vector(self, text: str) -> list:
        """生成文本内容的简单向量表示（12维）
        
        Args:
            text: 文本内容
            
        Returns:
            list: 12维向量
        """
        if not text:
            return [0.0] * 12
        
        vector = []
        
        # 1. 文本长度特征
        length_feature = min(len(text) / 1000, 1.0)
        vector.append(length_feature)
        
        # 2. 架构相关关键词
        arch_keywords = ["架构", "设计", "系统", "模块"]
        arch_score = sum(1 for word in arch_keywords if word in text) / len(arch_keywords)
        vector.append(arch_score)
        
        # 3. 评估相关关键词
        eval_keywords = ["评估", "风险", "可行性", "成本"]
        eval_score = sum(1 for word in eval_keywords if word in text) / len(eval_keywords)
        vector.append(eval_score)
        
        # 4. 代码相关关键词
        code_keywords = ["代码", "实现", "函数", "类"]
        code_score = sum(1 for word in code_keywords if word in text) / len(code_keywords)
        vector.append(code_score)
        
        # 5. 测试相关关键词
        test_keywords = ["测试", "验证", "检查", "断言"]
        test_score = sum(1 for word in test_keywords if word in text) / len(test_keywords)
        vector.append(test_score)
        
        # 6. 问题相关关键词
        problem_keywords = ["问题", "错误", "异常", "Bug"]
        problem_score = sum(1 for word in problem_keywords if word in text) / len(problem_keywords)
        vector.append(problem_score)
        
        # 7. 优化相关关键词
        optimize_keywords = ["优化", "改进", "提升", "性能"]
        optimize_score = sum(1 for word in optimize_keywords if word in text) / len(optimize_keywords)
        vector.append(optimize_score)
        
        # 8. 文档相关关键词
        doc_keywords = ["文档", "说明", "注释", "备注"]
        doc_score = sum(1 for word in doc_keywords if word in text) / len(doc_keywords)
        vector.append(doc_score)
        
        # 9. 配置相关关键词
        config_keywords = ["配置", "参数", "设置", "选项"]
        config_score = sum(1 for word in config_keywords if word in text) / len(config_keywords)
        vector.append(config_score)
        
        # 10. 数据相关关键词
        data_keywords = ["数据", "信息", "内容", "记录"]
        data_score = sum(1 for word in data_keywords if word in text) / len(data_keywords)
        vector.append(data_score)
        
        # 11. 句子密度（句号数量 / 文本长度）
        sentence_density = text.count('。') / max(len(text), 1)
        vector.append(min(sentence_density * 100, 1.0))
        
        # 12. 数字密度（数字字符数量 / 文本长度）
        digit_count = sum(c.isdigit() for c in text)
        digit_density = digit_count / max(len(text), 1)
        vector.append(min(digit_density * 10, 1.0))
        
        return vector
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 【调试】记录POST请求路径
        logger.info(f"收到POST请求: {path}")
        logger.info(f"Content-Type: {self.headers.get('Content-Type', 'N/A')}")
        
        # 文件上传API需要特殊处理，不能提前读取 rfile
        if path == '/api/upload':
            logger.info("进入文件上传处理流程")
            self._handle_file_upload()
            return
        
        # 读取请求体（仅对非文件上传请求）
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"POST请求解析失败: {e}")
            response = {
                "success": False,
                "error": "无效的JSON格式或编码错误"
            }
            self._send_json_response(response, status_code=400)
            return
        
        # 简单的消息处理API（用于测试）
        if path == '/api/message':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "success": True,
                "message": "消息已收到",
                "received_data": data,
                "timestamp": datetime.now().isoformat()
            }
            # 记录交互日志
            log_interaction({
                "path": "/api/message",
                "method": "POST",
                "content_type": self.headers.get('Content-Type', ''),
                "request": data,
                "response": response
            })
            self._send_json_response(response)
            return
        
        # 智能体模板消息处理API
        elif path == '/api/agent-template/message':
            # 智能体模板消息接口 - 基于BaseAgent处理
            # 获取用户消息和上传文件路径
            user_message = data.get('message', '')
            uploaded_file = data.get('uploaded_file', '')
            
            try:
                # 导入BaseAgent
                from src.base_agent import BaseAgent
                
                # 初始化BaseAgent实例
                agent = BaseAgent(
                    agent_id="base_agent_template",
                    agent_type="base_agent",
                    prompt_file="src/agent_prompts/base_agent_prompt.md"
                )
                
                # 思维透明化：收集所有推理步骤
                thinking_steps = []
                def collect_step(content: str):
                    thinking_steps.append({
                        'content': content,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                
                # 调用BaseAgent的respond方法处理用户消息
                # 传入step_callback启用思维透明化
                response_result = agent.respond(
                    user_message, 
                    uploaded_file=uploaded_file,
                    step_callback=collect_step  # 思维透明化回调
                )
                
                # 解析respond的返回结果
                if response_result and isinstance(response_result, dict):
                    # 错误类型：LLM未就绪或调用异常
                    if response_result.get('type') == 'error':
                        response = {
                            "success": False,
                            "error": response_result.get('error', '未知错误'),
                            "user_message": {
                                "content": user_message, 
                                "sender": "用户",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            },
                            "agent_responses": [],
                            "thinking_steps": thinking_steps,  # 思维透明化数据
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    else:
                        # 提取响应内容
                        if response_result.get('type') == 'text_reply':
                            response_text = response_result.get('reply', '')
                        elif response_result.get('type') == 'tool_call_result':
                            # 工具调用结果
                            tool_result = response_result.get('result', {})
                            response_text = f"工具调用结果:\n{json.dumps(tool_result, ensure_ascii=False, indent=2)}"
                        else:
                            response_text = str(response_result)
                        
                        response = {
                            "success": True,
                        "user_message": {
                            "content": user_message, 
                            "sender": "用户",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        "agent_responses": [
                            {
                                'agent_id': agent.agent_id,
                                'agent_name': '基于基类智能体的RAG助手',
                                'content': response_text,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        ],
                        "thinking_steps": thinking_steps,  # 思维透明化数据
                        "methodology_insights": [
                            {
                                'type': 'response_strategy',
                                'content': '基于BaseAgent的智能响应，支持三层响应机制'
                            },
                            {
                                'type': 'thinking_transparency',
                                'content': f'思维透明化已启用，记录了 {len(thinking_steps)} 个推理步骤'
                            }
                        ],
                        "response_strategy": 'base_agent',
                        "tools_used": ['统一记忆系统', '工具集成器', '三层响应机制', '思维透明化'],
                        "memory_usage": len(user_message) * 10,
                        "knowledge_sources": ['本地知识库', '预训练模型', '统一记忆系统'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "full_timestamp": datetime.now().isoformat(),
                        "chatroom_status": 'active',
                        "design_principle": '基于BaseAgent的智能响应 - 支持工具调用与思维透明化'
                    }
                    # 记录交互日志
                    log_interaction({
                        "path": "/api/agent-template/message",
                        "method": "POST",
                        "content_type": self.headers.get('Content-Type', ''),
                        "request": {"message": user_message, "uploaded_file": uploaded_file},
                        "response": response
                    })
                else:
                    raise Exception("BaseAgent返回无效响应")
                
            except Exception as e:
                # 如果导入失败，返回错误信息
                logger.error(f"智能体模板API调用失败: {e}", exc_info=True)
                response = {
                    "success": False,
                    "error": "智能体模板API调用失败",
                    "message": str(e),
                    "user_message": {
                        "content": user_message,
                        "sender": "用户",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "agent_responses": [],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                # 记录交互日志
                log_interaction({
                    "path": "/api/agent-template/message",
                    "method": "POST",
                    "content_type": self.headers.get('Content-Type', ''),
                    "request": {"message": user_message, "uploaded_file": uploaded_file},
                    "response": response,
                    "error": str(e)
                })
            
            self._send_json_response(response)
            return
        
        # 手动触发记忆重构 API
        elif path == '/maintenance/memory_reconstruction':
            logger.info("收到手动触发记忆重构请求")
            try:
                # ✅ 修复：直接调用夜间维护调度器的记忆重构方法
                if nightly_scheduler_import_ok:
                    scheduler = NightlyMaintenanceScheduler()
                    result = scheduler.perform_memory_reconstruction()
                    
                    response = {
                        "success": result.get("status") == "success",
                        "data": result,
                        "message": "记忆重构任务执行完成",
                        "timestamp": datetime.now().isoformat()
                    }
                    self._send_json_response(response)
                    logger.info(f"记忆重构完成: {result.get('status')}")
                else:
                    response = {
                        "success": False,
                        "error": "记忆重构服务未启用（夜间维护调度器导入失败）",
                        "timestamp": datetime.now().isoformat()
                    }
                    self._send_json_response(response, status_code=503)
                    logger.warning("记忆重构服务未启用")
                return
            except Exception as e:
                response = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self._send_json_response(response, status_code=500)
                return
        
        # 启动后端服务
        elif path == '/api/start-backend':
            action = data.get('action', '')
            port = data.get('port', 10808)
            
            # 如果是真正的后端启动请求
            if action == 'start_real_backend':
                try:
                    # 启动真正的后端服务进程
                    backend_process = threading.Thread(target=self.start_real_backend_service, args=(port,))
                    backend_process.daemon = True
                    backend_process.start()
                    
                    response = {
                        "success": True,
                        "message": "后端服务进程已启动",
                        "port": port,
                        "backend_status": "starting",
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    response = {
                        "success": False,
                        "error": f"后端服务启动失败: {str(e)}",
                        "port": port,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # 默认响应（兼容旧版本）
                response = {
                    "success": True,
                    "message": "后端服务启动请求已接收",
                    "port": port,
                    "timestamp": datetime.now().isoformat()
                }
            
            self._send_json_response(response)
            return
        
        # 聊天室消息发送接口
        elif path == '/api/chatroom/message':
            # 聊天室消息发送接口 - 调用真正的聊天API
            # 获取用户消息
            user_message = data.get('message', '')
            
            # 初始化聊天室实例
            self.initialize_chatroom()
            
            try:
                if self.chatroom_instance:
                    # 启动聊天室（如果未启动）
                    if not self.chatroom_instance.is_active:
                        self.chatroom_instance.start_chatroom()
                    
                    # 发送用户消息
                    result = self.chatroom_instance.send_user_message(user_message)

                    # 适配前端期望的格式
                    agent_responses = []
                    methodology_insights = []
                    thinking_steps = []
                    if isinstance(result, dict):
                        # 如果result是字典，直接使用其中的agent_responses、methodology_insights和thinking_steps字段
                        agent_responses = result.get('agent_responses', [])
                        methodology_insights = result.get('methodology_insights', [])
                        thinking_steps = result.get('thinking_steps', [])
                    elif isinstance(result, list):
                        agent_responses = result
                    
                    response = {
                        "success": True,
                        "agent_responses": agent_responses,
                        "thinking_steps": thinking_steps,
                        "methodology_insights": methodology_insights,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                    # 记录交互日志
                    log_interaction({
                        "path": "/api/chatroom/message",
                        "method": "POST",
                        "content_type": self.headers.get('Content-Type', ''),
                        "request": {"message": user_message},
                        "response": response
                    })
                else:
                    response = {
                        "success": False,
                        "error": "聊天室未初始化",
                        "agent_responses": [],
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                response = {
                    "success": False,
                    "error": str(e),
                    "agent_responses": [],
                    "timestamp": datetime.now().isoformat()
                }
                # 记录交互日志
                log_interaction({
                    "path": "/api/chatroom/message",
                    "method": "POST",
                    "content_type": self.headers.get('Content-Type', ''),
                    "request": {"message": user_message},
                    "response": response,
                    "error": str(e)
                })
            
            self._send_json_response(response)
            return
        
        # 错误报告
        elif path == '/api/error-report':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 确保日志目录存在
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # 写入完整的错误日志
            log_file = os.path.join(log_dir, 'frontend_errors.log')
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    # 使用完整的错误数据，而不仅仅是几个字段
                    # 如果是组件级错误，使用完整的错误数据
                    if data.get('level') == 'component':
                        # 组件级错误，使用完整的错误数据
                        log_entry = data
                        # 确保包含时间戳
                        if 'timestamp' not in log_entry:
                            log_entry['timestamp'] = datetime.now().isoformat()
                    else:
                        # 其他类型的错误，兼容旧格式
                        log_entry = {
                            "type": data.get('type', 'unknown'),
                            "message": data.get('message', '无错误信息'),
                            "stack": data.get('stack', data.get('stack_trace', '无堆栈信息')),
                            "url": data.get('url', data.get('file_path', 'unknown')),
                            "timestamp": data.get('timestamp', datetime.now().isoformat())
                        }
                    
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                    print(f"记录前端错误: {log_entry.get('type', 'unknown')}")
            except Exception as e:
                print(f"错误日志写入失败: {e}")
            response = {
                "success": True,
                "message": "错误报告已接收",
                "timestamp": datetime.now().isoformat()
            }
            self._send_json_response(response)
            return
        
        else:
            response = {
                "success": False,
                "error": "API端点不存在"
            }
            self._send_json_response(response, status_code=404)
            return
    
    def determine_response_strategy(self, user_message):
        """根据用户消息判断响应策略"""
        # 简单的问题类型判断逻辑
        user_message_lower = user_message.lower()
        
        # 自我介绍类问题
        if any(keyword in user_message_lower for keyword in ['介绍', '自我介绍', '你是谁', '你是什么']):
            return "local_enhanced"
        
        # 实时信息类问题（需要网络工具）
        elif any(keyword in user_message_lower for keyword in ['今天', '现在', '实时', '最新', '天气', '新闻']):
            return "tool_only"
        
        # 复杂推理类问题
        elif any(keyword in user_message_lower for keyword in ['为什么', '如何', '怎样', '解释', '分析']):
            return "hybrid"
        
        # 默认使用本地知识增强
        else:
            return "local_enhanced"
    
    def generate_response(self, user_message, strategy):
        """根据策略生成智能回复"""
        user_message_lower = user_message.lower()
        
        # 自我介绍类问题
        if any(keyword in user_message_lower for keyword in ['介绍', '自我介绍', '你是谁', '你是什么']):
            return self.generate_introduction_response(user_message)
        
        # 根据策略生成不同回复
        if strategy == "local_only":
            return self.generate_local_response(user_message)
        elif strategy == "local_enhanced":
            return self.generate_enhanced_response(user_message)
        elif strategy == "tool_only":
            return self.generate_tool_response(user_message)
        else:  # hybrid
            return self.generate_hybrid_response(user_message)
    
    def generate_introduction_response(self, user_message):
        """生成自我介绍回复"""
        return """您好！我是RAG智能系统的智能体模板。我是一个基于本地知识库和预训练模型的AI助手，具备以下特点：

🔍 **智能检索能力**：能够查询本地知识库，获取相关记忆切片
🧠 **长期记忆**：支持连贯性对话，记得前面聊的内容
🛠️ **多工具集成**：可以根据问题类型调用不同的工具
📚 **三层响应机制**：
   - 本地知识层：查询知识图谱
   - 预训练知识层：综合预训练数据
   - 实时工具层：获取最新信息

我的目标是成为您有长期记忆的AI朋友，提供个性化的智能服务！"""
    
    def generate_local_response(self, user_message):
        """基于本地知识库生成回复"""
        # 模拟本地知识库查询
        return f"基于本地知识库查询，我为您找到以下信息：这是一个关于'{user_message}'的本地知识回复。"
    
    def generate_enhanced_response(self, user_message):
        """基于本地知识增强生成回复"""
        # 模拟本地知识库查询 + 预训练知识
        return f"结合本地知识和预训练模型，我为您提供以下回答：{user_message}是一个很好的问题，让我为您详细解答..."
    
    def generate_tool_response(self, user_message):
        """基于工具调用生成回复"""
        # 模拟工具调用
        return f"通过实时工具查询，我为您获取到以下最新信息：关于'{user_message}'的实时数据正在处理中..."
    
    def generate_hybrid_response(self, user_message):
        """混合策略生成回复"""
        # 模拟混合策略
        return f"综合本地知识、预训练模型和实时工具，我为您提供以下综合分析：{user_message}涉及多个方面，让我为您详细解析..."
    
    def get_tools_used(self, strategy):
        """根据策略返回使用的工具列表"""
        tools_map = {
            "local_only": ["知识图谱查询"],
            "local_enhanced": ["知识图谱查询", "记忆重构"],
            "tool_only": ["网络搜索", "实时工具"],
            "hybrid": ["知识图谱查询", "记忆重构", "网络搜索", "智能体协作"]
        }
        return tools_map.get(strategy, ["智能体模板"])
    
    def get_memory_usage(self, user_message):
        """计算内存使用量（模拟）"""
        # 根据消息长度模拟内存使用
        return len(user_message) * 10
    
    def get_knowledge_sources(self, strategy):
        """根据策略返回知识来源"""
        sources_map = {
            "local_only": ["本地知识库"],
            "local_enhanced": ["本地知识库", "预训练模型"],
            "tool_only": ["网络资源", "实时数据"],
            "hybrid": ["本地知识库", "预训练模型", "网络资源"]
        }
        return sources_map.get(strategy, ["系统默认配置"])

    def do_OPTIONS(self):
        """处理OPTIONS请求，支持CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

# 全局变量
PORT = 5000
HTTPD = None


def perform_memory_reconstruction():
    """执行记忆重构任务 - 统一调用 NightlyMaintenanceScheduler 管线
    
    开发提示词来源：用户要求实现每天晚上的记忆重构
    代码代谢说明：旧逻辑已迁移至 NightlyMaintenanceScheduler，此处统一调度新管线
    """
    logger.info("[代谢] 调用 NightlyMaintenanceScheduler 执行记忆重构")
    
    try:
        # ✅ 修复：直接使用全局夜间维护调度器，避免重复创建AgentManager
        global nightly_scheduler
        
        if nightly_scheduler is None:
            logger.warning("夜间维护调度器未初始化，无法执行记忆重构")
            return {"status": "failed", "error": "nightly_scheduler_not_initialized"}
        
        result = nightly_scheduler.perform_memory_reconstruction()
        
        logger.info(f"记忆重构完成: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"记忆重构任务失败: {e}")
        return {"status": "failed", "error": str(e)}

def start_server(host='0.0.0.0', port=10808):
    """启动RAG系统稳定版服务器"""
    global HTTPD, timing_engine, PORT
    
    # ✅ 更新全局PORT为实际运行端口
    PORT = port
    logger.info(f"全局PORT已设置为: {PORT}")
    
    try:
        logger.info("进入start_server函数")
        print("初始化聊天室...")

        # 初始化多智能体聊天室
        try:
            RAGStableStartHandler.initialize_chatroom()
            if RAGStableStartHandler.chatroom_instance is not None:
                # ✅ 只保留logger，移除重复print
                logger.info("多智能体聊天室初始化成功（main server）")
            else:
                logger.error("多智能体聊天室初始化失败：chatroom_instance 为 None")
        except Exception as e:
            logger.error(f"多智能体聊天室初始化异常: {e}")

        # 初始化时机选择策略引擎
        print("初始化时机选择策略引擎...")
        try:
            timing_engine = TimingStrategyEngine()
            # 启动监控
            timing_engine.start_monitoring()
            # ✅ 只保留logger，移除重复print
            logger.info("时机选择策略引擎初始化成功并启动监控")
            
            # 调度记忆重构任务
            print("调度记忆重构任务...")
            timing_engine.schedule_optimization(
                task_type="memory_reconstruction",
                task_description="每天晚上执行记忆重构",
                priority="medium",
                estimated_duration=60,  # 预计60分钟完成
                optimization_function=perform_memory_reconstruction
            )
            # ✅ 只保留logger，移除重复print
            logger.info("记忆重构任务已调度")
            
        except Exception as e:
            logger.error(f"初始化时机选择策略引擎失败: {e}")
            print(f"初始化时机选择策略引擎失败: {e}")
        
        print("设置服务器...")
        # 设置服务器
        handler = RAGStableStartHandler
        # ✅ 只保留logger，移除重复print
        logger.info(f"创建TCPServer实例，监听 {host}:{port}")
        
        # 创建TCP服务器实例
        try:
            httpd = socketserver.ThreadingTCPServer((host, port), handler)
            HTTPD = httpd
            # ✅ 只保留logger，移除重复print
            logger.info("TCPServer实例创建成功")
            
            # ✅ 服务器启动成功，标记backend状态为active
            handler.backend_status = "active"
            logger.info("后端服务状态已设置为active")
        except Exception as e:
            logger.error(f"创建TCPServer实例失败: {e}")
            raise
        
        # ⚠️ 安全考虑：端口号是系统"密码"，只在日志文件中记录一次
        logger.info(f"RAG系统稳定版启动服务器，端口: {port}")
        logger.debug(f"安全入口: http://localhost:{port}")  # 降级为DEBUG
        
        # ✅ 控制台输出：不暴露端口号
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  RAG系统稳定版已启动")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n⚠️  重要提示:")
        print(f"1. 端口号是您的系统安全密钥，请妥善保管")
        print(f"2. 如需查看端口号，请查看日志文件: logs/startup_status.json")
        print(f"3. 打开浏览器访问启动页面即可使用系统\n")
        
        # 启动夜间维护调度器
        global nightly_scheduler
        try:
            print("\n🌙 正在启动夜间维护调度器...")
            logger.info("正在启动夜间维护调度器")
            
            # ✅ 修复：复用MultiAgentChatroom中已创建的智能体，避免重复发现
            # 从聊天室获取已创建的智能体字典，而不是重新创建AgentManager
            if RAGStableStartHandler.chatroom_instance:
                # 创建一个轻量级的智能体管理器包装器，不触发重复发现
                class ChatroomAgentManagerAdapter:
                    """聊天室智能体管理器适配器 - 复用已创建的智能体"""
                    def __init__(self, chatroom_agents):
                        self.chatroom_agents = chatroom_agents
                    
                    def get_all_agent_instances(self):
                        """返回所有智能体实例（列表形式）"""
                        return list(self.chatroom_agents.values())
                
                # 使用适配器包装聊天室中的智能体
                agent_manager_adapter = ChatroomAgentManagerAdapter(
                    RAGStableStartHandler.chatroom_instance.agents
                )
                
                # 创建夜间维护调度器实例（传入适配器，不触发重复发现）
                nightly_scheduler = NightlyMaintenanceScheduler(agent_manager=agent_manager_adapter)
            else:
                # 如果聊天室未初始化，则创建独立的AgentManager
                from src.agent_manager import get_agent_manager
                agent_manager = get_agent_manager()
                nightly_scheduler = NightlyMaintenanceScheduler(agent_manager=agent_manager)
            
            # 启动定时维护
            nightly_scheduler.start_scheduled_maintenance()
            
            print("✅ 夜间维护调度器已启动")
            print("   - 智能体将在系统空闲时（晚上22:00-6:00）自动写日记")
            print("   - 自动执行记忆重构和向量库更新")
            print("   - 明天可查看维护报告\n")
            logger.info("夜间维护调度器启动成功")
            
        except Exception as e:
            print(f"⚠️  夜间维护调度器启动失败: {e}")
            logger.error(f"夜间维护调度器启动失败: {e}")
            print("系统将继续运行，但夜间维护功能不可用\n")
        
        # ✅ 服务器完全启动后，更新startup_status.json为全量信息
        # 【重要】此逻辑必须在httpd.serve_forever()之前执行，且不能被夜间维护调度器的异常影响
        print("\n🔍 开始更新全量启动状态JSON...")
        logger.info("🔍 开始更新全量启动状态JSON...")
        try:
            # 🔥 使用内存日志捕获器的实时数据（而非读取文件）
            startup_logs = memory_log_handler.logs  # 当前启动的所有日志
            log_duplicates = memory_log_handler.get_duplicates()  # 实时分析重复
            
            # 获取智能体信息
            agent_info = []
            if RAGStableStartHandler.chatroom_instance:
                for agent_role_enum, agent_inst in RAGStableStartHandler.chatroom_instance.agents.items():
                    # 🔥 修复：键就是AgentRole枚举，直接转换为字符串
                    # agent_role_enum是AgentRole枚举对象，需要转换为字符串
                    agent_name_str = agent_role_enum.value if hasattr(agent_role_enum, 'value') else str(agent_role_enum)
                    
                    # 获取agent_inst的role属性（可能不存在）
                    agent_role_attr = getattr(agent_inst, 'role', None)
                    if agent_role_attr:
                        if hasattr(agent_role_attr, 'value'):
                            role_str = agent_role_attr.value
                        elif hasattr(agent_role_attr, 'name'):
                            role_str = agent_role_attr.name
                        else:
                            role_str = str(agent_role_attr)
                    else:
                        # role属性不存在，使用键名作为角色
                        role_str = agent_name_str
                    
                    # 获取agent_id（处理所有可能的类型）
                    agent_id = getattr(agent_inst, 'agent_id', 'unknown')
                    agent_id_str = str(agent_id) if agent_id else 'unknown'
                    
                    agent_info.append({
                        "name": agent_name_str,
                        "role": role_str,
                        "agent_id": agent_id_str
                    })
            
            # 🔥 轻量级统计：直接读取向量库数量，避免知识图谱构建阻塞
            from src.vector_database import VectorDatabase
            vector_db = VectorDatabase()
            all_memories = vector_db.get_all_memories()
            total_memories = len(all_memories)
            
            # 主动初始化思维引擎单例，获取真实节点数
            try:
                from src.mesh_thought_engine import MeshThoughtEngine
                mesh_engine = MeshThoughtEngine()  # 触发单例初始化，加载持久化数据
                thought_nodes_count = len(mesh_engine.nodes)
                thought_dedup_rate = (total_memories - thought_nodes_count) / total_memories * 100 if total_memories > 0 else 0
                thought_status = "active" if thought_nodes_count > 0 else "pending_initialization"
            except Exception as e:
                logger.warning(f"初始化思维引擎失败: {e}")
                thought_nodes_count = 0
                thought_dedup_rate = 0
                thought_status = "initialization_failed"
            
            # 构建全量启动状态（优先写入基础信息）
            full_startup_status = {
                "timestamp": datetime.now().isoformat(),
                "server_type": "rag_main",
                "port": port,
                "pid": os.getpid(),
                "python_version": sys.version,
                "numpy_version": numpy.__version__,
                "opencv_version": cv2.__version__,
                
                # 🔥 启动日志完整记录（镜像控制台输出）
                "startup_logs": {
                    "total_logs": len(startup_logs),
                    "logs": startup_logs,  # 完整日志，不做截断
                    "duplicates_detected": log_duplicates,
                    "duplicate_count": len(log_duplicates)
                },
                
                # 模块导入状态
                "modules": {
                    "chatroom_import_ok": chatroom_import_ok,
                    "timing_engine_import_ok": timing_engine_import_ok,
                    "memory_reconstruct_import_ok": memory_reconstruct_import_ok,
                    "nightly_scheduler_import_ok": nightly_scheduler_import_ok
                },
                
                # 智能体发现信息
                "agents": {
                    "count": len(agent_info),
                    "list": agent_info
                },
                
                # 向量数据库统计（轻量级直接查询）
                "vector_database": {
                    "total_memories": total_memories,
                    "active_memories": total_memories,  # 简化：启动阶段无需精确分类
                    "archived_memories": 0,
                    "retired_memories": 0
                },
                
                # 知识图谱统计（延迟加载，避免阻塞）
                "knowledge_graph": {
                    "total_nodes": 0,
                    "total_edges": 0,
                    "coverage_rate": 0,
                    "status": "pending_initialization"  # 标记为待初始化
                },
                
                # 思维引擎统计（使用预先初始化的真实数据）
                "thought_engine": {
                    "total_nodes": thought_nodes_count,
                    "deduplication_rate": thought_dedup_rate,
                    "status": thought_status
                },
                
                # 服务器状态
                "status": "active",
                "startup_complete": True
            }
            
            # 写入最新快照文件
            with open(STARTUP_STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(full_startup_status, f, ensure_ascii=False, indent=2)
            
            # 追加写入历史记录文件
            history_file = os.path.join(log_dir, 'startup_status_history.jsonl')
            with open(history_file, 'a', encoding='utf-8') as hf:
                hf.write(json.dumps(full_startup_status, ensure_ascii=False) + "\n")
            
            logger.info(f"✅ 全量启动状态已更新: 端口={port}, PID={os.getpid()}, 智能体={len(agent_info)}, 向量库={total_memories}条, 日志={len(startup_logs)}条, 重复日志={len(log_duplicates)}处")
            # ✅ 控制台输出统计信息（包含日志诊断）
            print(f"✅ 系统初始化完成: 智能体={len(agent_info)}, 向量库={total_memories}条")
            if log_duplicates:
                print(f"⚠️  检测到 {len(log_duplicates)} 处日志重复问题（详见startup_status.json）")
            
            # 🔥 启动后异步初始化知识图谱（首次启动时构建持久化文件）
            import threading
            def async_init_knowledge_graph():
                try:
                    from src.system_statistics_service import get_system_statistics_service
                    import os
                    
                    stats_service = get_system_statistics_service()
                    kg_cache_file = os.path.join(os.path.dirname(__file__), 'data', 'knowledge_graph_cache', 'global_knowledge_graph.json')
                    
                    # 检查持久化文件是否存在
                    if not os.path.exists(kg_cache_file):
                        print(f"\n⏳ 检测到首次启动，开始构建知识图谱持久化文件...")
                        logger.info("检测到首次启动，开始构建知识图谱持久化文件")
                        
                        # 触发首次构建（force_rebuild_kg=True）
                        kg_stats = stats_service.get_system_statistics(force_refresh=True, force_rebuild_kg=True)
                        
                        kg_nodes = kg_stats['knowledge_graph']['total_nodes']
                        kg_edges = kg_stats['knowledge_graph']['total_edges']
                        coverage = kg_stats['knowledge_graph']['coverage_rate']
                        
                        print(f"✅ 知识图谱初始化完成: 节点={kg_nodes}, 边={kg_edges}, 覆盖率={coverage:.1f}%")
                        logger.info(f"知识图谱初始化完成: 节点={kg_nodes}, 边={kg_edges}, 覆盖率={coverage:.1f}%")
                    else:
                        print(f"✅ 知识图谱持久化文件已存在，跳过重复构建")
                        logger.info("知识图谱持久化文件已存在，跳过重复构建")
                        
                except Exception as kg_error:
                    logger.error(f"异步初始化知识图谱失败: {kg_error}")
                    print(f"⚠️ 异步初始化知识图谱失败: {kg_error}")
            
            # 在后台线程中执行，不阻塞服务器启动
            kg_init_thread = threading.Thread(target=async_init_knowledge_graph, daemon=True, name="KGInitThread")
            kg_init_thread.start()
            print(f"🚀 知识图谱异步初始化已启动（后台线程）")
            
        except Exception as e:
            logger.error(f"❌ 更新全量启动状态失败: {e}")
            print(f"❌ 更新全量启动状态失败: {e}")
            import traceback
            traceback.print_exc()
              
        try:
            httpd.serve_forever()
            logger.info("serve_forever()循环结束")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"serve_forever()循环异常退出: {e}")
            print(f"serve_forever()循环异常退出: {e}")
            raise
        
    except KeyboardInterrupt:
        logger.info("服务器正在关闭...")
        print("\n服务器正在关闭...")
        
        # 停止时机选择策略引擎监控
        if timing_engine:
            timing_engine.stop_monitoring()
            logger.info("时机选择策略引擎监控已停止")
            print("时机选择策略引擎监控已停止")
        
        # 停止夜间维护调度器
        if nightly_scheduler:
            try:
                nightly_scheduler.timing_engine.stop_monitoring()
                logger.info("夜间维护调度器已停止")
                print("夜间维护调度器已停止")
            except Exception as e:
                logger.error(f"停止夜间维护调度器失败: {e}")
        
        if HTTPD:
            HTTPD.server_close()
        logger.info("服务器已成功关闭")
        print("服务器已成功关闭")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 停止时机选择策略引擎监控
        if timing_engine:
            timing_engine.stop_monitoring()
        
        # 停止夜间维护调度器
        if nightly_scheduler:
            try:
                nightly_scheduler.timing_engine.stop_monitoring()
            except:
                pass
        
        if HTTPD:
            try:
                HTTPD.server_close()
            except:
                pass


if __name__ == "__main__":
    # 支持命令行参数传入动态端口
    import argparse
    import requests
    
    parser = argparse.ArgumentParser(description='RAG系统主服务器')
    parser.add_argument('--port', type=int, default=PORT, help=f'服务器端口（默认: {PORT}）')
    args = parser.parse_args()
    
    # 使用动态端口或默认端口
    server_port = args.port
    server_pid = os.getpid()
    
    # 记录启动信息到日志
    shutdown_status = None
    
    try:
        print(f"开始启动RAG系统服务器... 端口: {server_port}, PID: {server_pid}")
        logger.info(f"程序开始执行，端口: {server_port}, PID: {server_pid}")
        
        # 向静态服务器注册（启动前）
        try:
            register_response = requests.post(
                "http://localhost:10808/api/server/register",
                json={"port": server_port, "pid": server_pid},
                timeout=3
            )
            logger.info(f"已向静态服务器注册实例, 端口={server_port}, PID={server_pid}")
        except Exception as e:
            logger.warning(f"向静态服务器注册失败（静态服务器可能未运行）: {e}")
        
        # 启动服务器
        start_server(port=server_port)
        print("服务器已退出")
        logger.info("程序执行结束")
        shutdown_status = "normal_exit"
        
    except KeyboardInterrupt:
        print("\n接收到Ctrl+C，准备优雅关闭RAG主服务器...")
        logger.info("接收到Ctrl+C，准备优雅关闭RAG主服务器...")
        shutdown_status = "keyboard_interrupt"
        
    except Exception as e:
        logger.error(f"服务器运行异常: {e}", exc_info=True)
        shutdown_status = "error"
        
    finally:
        # 记录关闭状态到持久化日志
        try:
            shutdown_info = {
                "timestamp": datetime.now().isoformat(),
                "server_type": "rag_main",
                "port": server_port,
                "pid": server_pid,
                "shutdown_reason": shutdown_status or "unknown",
                "python_version": sys.version,
                "numpy_version": numpy.__version__,
                "opencv_version": cv2.__version__
            }
            
            # 更新启动状态文件（记录关闭信息）
            with open(STARTUP_STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(shutdown_info, f, ensure_ascii=False, indent=2)
            
            # 追加到历史记录
            history_file = os.path.join(log_dir, 'startup_status_history.jsonl')
            with open(history_file, 'a', encoding='utf-8') as hf:
                hf.write(json.dumps(shutdown_info, ensure_ascii=False) + "\n")
                
            logger.info(f"已记录关闭状态: {shutdown_status}, 端口={server_port}")
            
        except Exception as e:
            logger.error(f"记录关闭状态失败: {e}")
        
        # 向静态服务器上报注销状态
        try:
            unregister_response = requests.post(
                "http://localhost:10808/api/server/unregister",
                json={"port": server_port, "reason": shutdown_status or "unknown"},
                timeout=3
            )
            result = unregister_response.json()
            logger.info(f"已向静态服务器上报主服务器注销状态, 端口={server_port}, 结果={result.get('success')}")
        except Exception as e:
            logger.warning(f"上报静态服务器注销状态失败: {e}")
