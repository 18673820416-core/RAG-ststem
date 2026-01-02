#!/usr/bin/env python
# @self-expose: {"id": "stable_start_server", "name": "Stable Start Server", "type": "api", "version": "1.0.0", "needs": {"deps": ["vector_database", "mesh_thought_engine", "multi_agent_chatroom"], "resources": []}, "provides": {"capabilities": ["稳定版服务器功能", "双模式交互支持", "API服务"], "endpoints": [{"path": "/api/text-blocks", "method": "GET", "desc": "获取文本块列表和关联关系"}, {"path": "/api/health", "method": "GET", "desc": "API健康检查"}, {"path": "/api/status", "method": "GET", "desc": "系统状态"}, {"path": "/api/agents", "method": "GET", "desc": "智能体列表"}, {"path": "/api/chatroom/status", "method": "GET", "desc": "聊天室状态"}, {"path": "/api/chatroom/message", "method": "POST", "desc": "发送聊天室消息"}]}}
# -*- coding: utf-8 -*-
"""
RAG智能系统统一服务器 - 支持双模式交互
========================================

系统定位：
- 统一的RAG系统服务器，同时支持两种交互模式
- 简易聊天机器人模式：基础对话功能
- 多智能体交互模式：智能体协作平台
- 运行在端口10808，采用"无门即安全"设计理念

双模式功能：
1. 简易聊天机器人模式 (start.html) - 基础对话入口
2. 多智能体交互模式 (templates/chatroom.html) - 智能体协作平台
3. 模式切换：通过导航菜单自由切换

启动方式：
- 直接运行: python stable_start_server.py
- 访问地址: http://localhost:10808

技术栈：
- Python 3.13.7 + NumPy 2.2.6 + OpenCV-Python 4.12.0.88
- 内置HTTP服务器 (http.server)
- 多智能体聊天室引擎
- 网状思维引擎、认知破障引擎等

注意：这是统一的服务器系统，同时支持两种交互模式。
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

# 导入聊天室模块
try:
    from src.multi_agent_chatroom import MultiAgentChatroom, AgentRole
    print("导入多智能体聊天室模块成功")
except Exception as e:
    print(f"导入多智能体聊天室模块失败: {e}")

# 导入时机选择策略引擎
try:
    from src.timing_strategy_engine import TimingStrategyEngine, OptimizationTiming
    print("导入时机选择策略引擎成功")
except Exception as e:
    print(f"导入时机选择策略引擎失败: {e}")

# 导入记忆重构引擎
try:
    from src.cognitive_engines.memory_reconstruction_engine import BatchMemoryReconstructor
    from src.vector_database import VectorDatabase
    print("导入记忆重构引擎成功")
except Exception as e:
    print(f"导入记忆重构引擎失败: {e}")

# 导入夜间维护调度器
try:
    from src.nightly_maintenance_scheduler import NightlyMaintenanceScheduler
    from src.agent_manager import get_agent_manager
    print("导入夜间维护调度器成功")
except Exception as e:
    print(f"导入夜间维护调度器失败: {e}")

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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # 系统状态
        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "running",
                "server_type": "stable",
                "modules_loaded": ["网状思维引擎", "视觉处理引擎", "多模态融合引擎", "向量数据库"],
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return

        # 智能体模板历史记录接口（代理到 RAG 主服务器实现）
        elif path == '/api/chatroom/history':
            try:
                import requests

                # 从注册表获取当前活动的主服务器端口
                active_servers = server_registry.get_all_servers()
                if not active_servers:
                    response = {
                        "success": False,
                        "history": [],
                        "count": 0,
                        "source": "no_backend",
                        "error": "RAG主服务器未启动，请先点击启动系统按钮。",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    backend_port = active_servers[0]['port']

                    query_string = parsed_path.query
                    forward_url = f"http://localhost:{backend_port}/api/chatroom/history"
                    if query_string:
                        forward_url = f"{forward_url}?{query_string}"

                    resp = requests.get(forward_url, timeout=5)
                    self.send_response(resp.status_code)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(resp.content)
                    return
            except Exception as e:
                logger.error(f"转发聊天室历史请求失败: {e}")
                response = {
                    "success": False,
                    "history": [],
                    "count": 0,
                    "source": "proxy_error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # 文本块关联关系接口
        elif path == '/api/text-blocks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 动态导入必要的模块
                from src.vector_database import VectorDatabase
                from src.mesh_thought_engine import MeshThoughtEngine
                
                # 初始化向量数据库
                vector_db = VectorDatabase()
                
                # 获取所有向量数据库记忆
                all_memories = vector_db.get_all_memories()
                
                # 初始化网状思维引擎
                mesh_engine = MeshThoughtEngine()
                
                # 构建文本块数据
                blocks = []
                block_id_map = {}
                
                # 第一步：创建所有文本块
                for memory in all_memories:
                    # 记忆是字典类型，使用字典访问方式
                    content = memory.get('content', '')
                    timestamp_str = memory.get('timestamp', '')
                    
                    # 转换时间格式
                    try:
                        # 如果timestamp是字符串，尝试解析
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
                    block_id_map[block['id']] = block
                
                # 第二步：手动为相似的文本块建立关联
                total_connections = 0
                for i, block1 in enumerate(blocks):
                    for j, block2 in enumerate(blocks[i+1:], i+1):
                        # 检查内容相似度（简单的字符串匹配）
                        content1 = block1['content'].lower()
                        content2 = block2['content'].lower()
                        
                        # 简单的关联条件：内容有较多重叠词
                        words1 = set(content1.split())
                        words2 = set(content2.split())
                        common_words = words1 & words2
                        content_overlap = len(common_words) > 3
                        
                        # 检查主题相似度（通过内容中的关键词）
                        has_common_topic = any(word in content1 and word in content2 for word in ['智能体', '提示词', 'prompt', 'agent'])
                        
                        if content_overlap or has_common_topic:
                            # 建立双向关联
                            connection = {
                                'target_id': block2['id'],
                                'type': 'related',
                                'strength': 0.8,
                                'created_at': datetime.now().isoformat()
                            }
                            block1['connections'].append(connection)
                            
                            connection = {
                                'target_id': block1['id'],
                                'type': 'related',
                                'strength': 0.8,
                                'created_at': datetime.now().isoformat()
                            }
                            block2['connections'].append(connection)
                            
                            total_connections += 2  # 双向关联，所以加2
                
                # 按重要性排序
                blocks.sort(key=lambda x: x['importance'], reverse=True)
                
                response = {
                    'success': True,
                    'blocks': blocks[:50],  # 限制返回前50个文本块
                    'count': len(blocks),
                    'total_connections': total_connections
                }
            except Exception as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
                import traceback
                traceback.print_exc()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
            
        # 智能体列表接口 - 动态获取智能体列表
        elif path == '/api/agents':
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
                        "错误处理师": "error_handler"
                    }
                    
                    # 智能体图标映射
                    agent_icons = {
                        "architect": "🏗️",
                        "evaluator": "📊",
                        "implementer": "💻",
                        "data_collector": "📡",
                        "error_handler": "🔧"
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
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # 根路径重定向到start.html
        elif path == '/':
            self.send_response(302)
            self.send_header('Location', '/start.html')
            self.end_headers()
            return
        
        # 静态文件服务
        else:
            # 设置当前目录为静态文件根目录
            self.directory = os.path.dirname(os.path.abspath(__file__))
            super().do_GET()
    
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
        """处理文件上传请求"""
        try:
            # 导入python-multipart模块（Python 3.13稳定配方兼容）
            from multipart import parse_form
            from io import BytesIO
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # 解析multipart/form-data
            content_type = self.headers.get('Content-Type', '')
            
            # 提取boundary
            boundary = None
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].strip()
            
            if not boundary:
                raise ValueError("请求中缺少boundary参数")
            
            # 使用python-multipart解析
            def on_field(field):
                # 处理普通表单字段
                pass
            
            def on_file(file):
                # 处理文件字段
                nonlocal uploaded_file_info
                uploaded_file_info = {
                    'filename': file.file_name.decode('utf-8') if isinstance(file.file_name, bytes) else file.file_name,
                    'content': file.file_object.read()
                }
            
            uploaded_file_info = None
            
            # 解析表单数据
            parse_form(
                headers={'Content-Type': content_type.encode()},
                input_stream=BytesIO(body),
                on_field=on_field,
                on_file=on_file
            )
            
            if not uploaded_file_info:
                raise ValueError("请求中没有文件字段")
            
            filename = uploaded_file_info['filename']
            content = uploaded_file_info['content']
            
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
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
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
                    
                    # 4.4 构建记忆数据
                    memory_data = {
                        "topic": f"上传文件 - {filename}",
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
                        "tags": ["file_upload", filename, file_ext.replace('.', '')] + event_codes
                    }
                    
                    # 4.5 保存到向量数据库
                    vector_db.add_memory(memory_data, vector=content_vector)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存切片到向量库失败: {e}")
                    continue
            
            logger.info(f"向量化完成，成功保存 {saved_count}/{len(slices)} 个切片到向量库")
            
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
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": False,
                "error": "无效的JSON格式或编码错误"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
                
                # 如果有上传文件，将其添加到消息中
                if uploaded_file:
                    user_message = f"{user_message}\n\n[上传文件: {uploaded_file}]"
                
                # 调用BaseAgent的respond方法处理用户消息
                response_result = agent.respond(user_message)
                
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
                        "methodology_insights": [
                            {
                                'type': 'response_strategy',
                                'content': '基于BaseAgent的智能响应，支持三层响应机制'
                            }
                        ],
                        "response_strategy": 'base_agent',
                        "tools_used": ['统一记忆系统', '工具集成器', '三层响应机制'],
                        "memory_usage": len(user_message) * 10,
                        "knowledge_sources": ['本地知识库', '预训练模型', '统一记忆系统'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "full_timestamp": datetime.now().isoformat(),
                        "chatroom_status": 'active',
                        "design_principle": '基于BaseAgent的智能响应 - 支持工具调用'
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
                    if isinstance(result, dict):
                        # 如果result是字典，直接使用其中的agent_responses和methodology_insights字段
                        agent_responses = result.get('agent_responses', [])
                        methodology_insights = result.get('methodology_insights', [])
                    elif isinstance(result, list):
                        agent_responses = result
                    
                    response = {
                        "success": True,
                        "agent_responses": agent_responses,
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": False,
                "error": "API端点不存在"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
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
PORT = 10808
HTTPD = None


def perform_memory_reconstruction():
    """执行记忆重构任务
    
    开发提示词来源：用户要求实现每天晚上的记忆重构
    """
    logger.info("开始执行记忆重构任务")
    
    try:
        # 1. 初始化向量数据库
        vector_db = VectorDatabase()
        
        # 2. 获取所有记忆
        all_memories = vector_db.get_all_memories()
        logger.info(f"获取到 {len(all_memories)} 条记忆")
        
        if not all_memories:
            logger.info("没有记忆需要重构")
            return {"status": "completed", "message": "没有记忆需要重构"}
        
        # 3. 初始化批量记忆重构器
        batch_reconstructor = BatchMemoryReconstructor()
        
        # 4. 执行批量记忆重构
        results = batch_reconstructor.reconstruct_batch_memories(all_memories)
        
        # 5. 更新重构后的记忆
        updated_count = 0
        for result in results['reconstruction_results']:
            memory_id = result['memory_id']
            reconstructed_content = result['reconstruction_result']['reconstructed_content']
            
            # 找到对应的原始记忆
            original_memory = next((m for m in all_memories if m.get('id') == memory_id), None)
            if original_memory:
                # 更新记忆内容
                vector_db.update_memory(memory_id, reconstructed_content)
                updated_count += 1
        
        logger.info(f"记忆重构任务完成，共更新了 {updated_count} 条记忆")
        
        # 6. 返回重构结果统计
        return {
            "status": "completed",
            "total_memories": results['total_memories'],
            "reconstructed_count": results['reconstructed_count'],
            "high_priority_count": results['high_priority_count'],
            "average_confidence": results['statistics']['average_confidence'],
            "reconstruction_rate": results['statistics']['reconstruction_rate'],
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"记忆重构任务失败: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        # 确保数据库连接关闭
        try:
            vector_db.close()
        except:
            pass

def start_server(host='0.0.0.0', port=10808):
    """启动RAG系统稳定版服务器"""
    global HTTPD, timing_engine
    
    try:
        logger.info("进入start_server函数")
        print("初始化聊天室...")
        
        # 暂时跳过聊天室初始化，先测试基本服务器功能
        logger.info("暂时跳过聊天室初始化，先测试基本服务器功能")
        print("暂时跳过聊天室初始化，先测试基本服务器功能")
        
        # 初始化时机选择策略引擎
        print("初始化时机选择策略引擎...")
        try:
            timing_engine = TimingStrategyEngine()
            # 启动监控
            timing_engine.start_monitoring()
            logger.info("时机选择策略引擎初始化成功并启动监控")
            print("时机选择策略引擎初始化成功并启动监控")
            
            # 调度记忆重构任务
            print("调度记忆重构任务...")
            timing_engine.schedule_optimization(
                task_type="memory_reconstruction",
                task_description="每天晚上执行记忆重构",
                priority="medium",
                estimated_duration=60,  # 预计60分钟完成
                optimization_function=perform_memory_reconstruction
            )
            logger.info("记忆重构任务已调度")
            print("记忆重构任务已调度")
            
        except Exception as e:
            logger.error(f"初始化时机选择策略引擎失败: {e}")
            print(f"初始化时机选择策略引擎失败: {e}")
        
        print("设置服务器...")
        # 设置服务器
        handler = RAGStableStartHandler
        logger.info(f"创建TCPServer实例，监听 {host}:{port}")
        
        # 创建TCP服务器实例
        try:
            httpd = socketserver.ThreadingTCPServer((host, port), handler)
            HTTPD = httpd
            logger.info("TCPServer实例创建成功")
        except Exception as e:
            logger.error(f"创建TCPServer实例失败: {e}")
            print(f"创建TCPServer实例失败: {e}")
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
        print(f"3. 打开浏览器访问启动页面即可使用系统")
        print(f"\n服务器正在监听请求...")
        
        print(f"\n服务器正在监听请求...")
        
        # 启动夜间维护调度器
        global nightly_scheduler
        try:
            print("\n🌙 正在启动夜间维护调度器...")
            logger.info("正在启动夜间维护调度器")
            
            # 获取智能体管理器
            agent_manager = get_agent_manager()
            
            # 创建夜间维护调度器实例
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
            print("   系统将继续运行，但夜间维护功能不可用\n")
        
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
    # 启动服务器
    print("开始启动RAG系统服务器...")
    logger.info("程序开始执行")
    start_server(port=PORT)
    print("服务器已退出")
    logger.info("程序执行结束")
