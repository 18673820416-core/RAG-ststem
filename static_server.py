#!/usr/bin/env python
# @self-expose: {"id": "static_server", "name": "Static Web Server", "type": "server", "version": "2.1.0", "needs": {"deps": ["system_maintenance_agent"], "resources": []}, "provides": {"capabilities": ["静态页面托管", "启动控制API", "状态检查", "前哨安全机制", "端口管理"], "endpoints": [{"path": "/", "method": "GET", "desc": "静态启动页面"}, {"path": "/api/start_backend", "method": "POST", "desc": "启动RAG主服务器"}, {"path": "/api/stop_backend", "method": "POST", "desc": "停止RAG主服务器"}, {"path": "/api/status", "method": "GET", "desc": "检查RAG主服务器状态"}, {"path": "/api/health", "method": "GET", "desc": "静态服务器健康检查"}, {"path": "/api/server/register", "method": "POST", "desc": "主服务器注册"}, {"path": "/api/server/unregister", "method": "POST", "desc": "主服务器注销"}, {"path": "/api/server/occupied-ports", "method": "POST", "desc": "查询占用端口"}, {"path": "/api/security/outpost-breach-test", "method": "POST", "desc": "前哨击穿模拟（测试）"}, {"path": "/api/text-blocks", "method": "GET", "desc": "代理RAG文本块接口"}, {"path": "/api/chatroom/*", "method": "PROXY", "desc": "代理多智能体聊天室API"}]} }
# -*- coding: utf-8 -*-
"""
RAG系统静态Web服务器
===================

服务器定位：
- 轻量级常驻服务器，端口10808
- 提供静态启动页面（start.html）
- 提供启动控制API，管理RAG主服务器的启动/停止
- 资源占用极小（~10MB），启动速度<1秒

功能职责：
1. 托管 start.html 静态启动页面
2. 提供 /api/start_backend 启动RAG主服务器
3. 提供 /api/stop_backend 停止RAG主服务器  
4. 提供 /api/status 检查RAG主服务器状态
5. 提供 /api/health 静态服务器健康检查

启动方式：
- 直接运行: python static_server.py
- 访问地址: http://localhost:10808

技术栈：
- Python http.server（轻量级HTTP服务器）
- subprocess（进程管理）
- 无任何RAG依赖，极度轻量

依赖特殊说明：
- 【random模块】使用Python标准库random，而非numpy.random
  原因：静态服务器必须零依赖、极度轻量，不能依赖NumPy等重型库
- 【虚拟环境管理】虚拟环境myenv_stable由静态服务器管理，属于基础设施层
  原因：虚拟环境是稳定的前置依赖，应由常驻进程管理，避免重复加载

注意：这是常驻服务器，不加载任何RAG资源
"""

import os
import sys
import json
import subprocess
import http.server
import socketserver
import logging
import time
import requests
import random  # 【设计意图】使用Python标准库random，而非numpy.random，因为静态服务器必须零依赖、极度轻量
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
from threading import Thread

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('static_server')

# 全局变量：RAG主服务器进程
rag_server_process = None
# 全局变量：动态随机端口
rag_server_port = None

# 服务器实例安全注册表（内存存储，进程级，无持久化）
class SecureServerRegistry:
    """安全的服务器注册表 - 仅内存存储，进程结束即销毁
    
    设计原则：
    - 无门即安全：端口信息不持久化到文件系统
    - 进程级隔离：进程结束即销毁
    - 击穿自毁：检测到入侵时立即销毁所有数据
    - 前哨-主堡联动：静态服务器=前哨，主服务器=主堡
    """
    
    def __init__(self):
        # 内存存储（不加密，简化实现，进程级隔离已足够）
        self._instances = {}  # {port: {pid, start_time, status}}
        
        # 安全状态
        self.is_compromised = False
        self.last_integrity_check = datetime.now()
        
        logger.info("🔒 安全服务器注册表已初始化（内存存储，无持久化）")
    
    def register(self, port: int, pid: int) -> bool:
        """注册实例（内存存储）"""
        self._instances[port] = {
            "pid": pid,
            "port": port,
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
        logger.info(f"✅ 已注册主服务器实例: Port={port}, PID={pid}")
        return True
    
    def unregister(self, port: int) -> bool:
        """注销实例（主服务器关闭时调用）"""
        if port in self._instances:
            self._instances[port]["status"] = "stopped"
            self._instances[port]["end_time"] = datetime.now().isoformat()
            logger.info(f"✅ 已注销主服务器实例: Port={port}")
            return True
        return False
    
    def get_occupied_ports(self) -> list:
        """获取所有正在运行的服务器端口"""
        return [port for port, info in self._instances.items() if info["status"] == "running"]
    
    def get_available_port(self, start_port: int = 5000, end_port: int = 5010) -> int:
        """智能分配空闲端口"""
        occupied = self.get_occupied_ports()
        for port in range(start_port, end_port + 1):
            if port not in occupied:
                return port
        # 如果所有端口都被占用，返回 None
        return None
    
    def get_all_instances(self) -> dict:
        """获取所有服务器实例信息（调试用）"""
        return self._instances.copy()
    
    def self_destruct(self) -> dict:
        """前哨击穿：自毁所有端口数据，返回销毁前的状态快照供维护师记录"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "destroyed_instances": list(self._instances.keys()),
            "total_instances": len(self._instances)
        }
        
        # 销毁所有数据
        self._instances.clear()
        self.is_compromised = True
        
        logger.critical("💥 前哨自毁：所有端口数据已销毁")
        return snapshot
    
    def alert_main_servers_breach(self) -> list:
        """向所有主服务器发送前哨击穿警报"""
        alerted_servers = []
        
        for port, info in list(self._instances.items()):
            if info["status"] == "running":
                try:
                    response = requests.post(
                        f"http://localhost:{port}/api/security/outpost-breached",
                        json={
                            "alert": "前哨被击穿，立即切断网络",
                            "timestamp": datetime.now().isoformat()
                        },
                        timeout=1
                    )
                    alerted_servers.append(port)
                    logger.warning(f"🚨 已通知主服务器 Port={port} 前哨被击穿")
                except Exception as e:
                    logger.error(f"❌ 通知主服务器 Port={port} 失败: {e}")
        
        return alerted_servers

# 全局安全注册表实例
server_registry = SecureServerRegistry()

class StaticServerHandler(http.server.SimpleHTTPRequestHandler):
    """静态服务器HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """重写日志方法，使用自定义logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")
    
    def end_headers(self):
        """添加CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API路由
        if path == '/api/health':
            self.handle_health_check()
        elif path == '/api/status':
            self.handle_status_check()
        elif path == '/api/text-blocks' or path.startswith('/api/chatroom'):
            # 通过静态服务器代理访问RAG主服务器，符合瓮城/安全前哨架构
            self.handle_rag_proxy(path, method='GET')
        else:
            # 静态文件服务
            self.serve_static_file(path)
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API路由
        if path == '/api/start_backend':
            self.handle_start_backend()
        elif path == '/api/stop_backend':
            self.handle_stop_backend()
        elif path == '/api/error-report':
            self.handle_error_report()
        elif path == '/api/server/register':
            self.handle_server_register()
        elif path == '/api/server/unregister':
            self.handle_server_unregister()
        elif path == '/api/server/occupied-ports':
            self.handle_occupied_ports()
        elif path == '/api/security/outpost-breach-test':
            self.handle_outpost_breach_test()
        elif path.startswith('/api/chatroom'):
            # 通过静态服务器代理多智能体聊天室API
            self.handle_rag_proxy(path, method='POST')
        else:
            self.send_error(404, "Not Found")
    
    def serve_static_file(self, path):
        """提供静态文件服务"""
        try:
            # 根路径重定向到 start.html
            if path == '/' or path == '':
                path = '/start.html'
            
            # 移除开头的斜杠
            file_path = path.lstrip('/')
            
            # 安全检查：防止路径遍历攻击
            file_path = os.path.normpath(file_path)
            if file_path.startswith('..'):
                self.send_error(403, "Forbidden")
                return
            
            # 尝试读取文件
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # 根据文件扩展名设置Content-Type
                content_type = self.guess_type(file_path)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, f"File not found: {file_path}")
                
        except Exception as e:
            logger.error(f"静态文件服务失败: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_health_check(self):
        """静态服务器健康检查"""
        try:
            response = {
                "status": "healthy",
                "service": "Static Web Server",
                "port": 10808,
                "timestamp": datetime.now().isoformat(),
                "message": "静态服务器运行正常"
            }
            
            self.send_json_response(200, response)
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            self.send_json_response(500, {
                "status": "error",
                "message": str(e)
            })
    
    def handle_status_check(self):
        """检查RAG主服务器状态"""
        global rag_server_process, rag_server_port
        
        try:
            # 检查进程是否存在
            if rag_server_process and rag_server_process.poll() is None:
                # 进程存在，检查端口是否可访问
                if rag_server_port:
                    try:
                        response = requests.get(f'http://localhost:{rag_server_port}/api/health', timeout=2)
                        if response.status_code == 200:
                            self.send_json_response(200, {
                                "status": "running",
                                "message": "RAG系统运行正常",
                                "port": rag_server_port  # 返回动态端口（仅用于调试和内部代理）
                            })
                        else:
                            self.send_json_response(200, {
                                "status": "starting",
                                "message": "RAG系统正在启动中..."
                            })
                    except requests.exceptions.RequestException:
                        self.send_json_response(200, {
                            "status": "starting",
                            "message": "RAG系统正在启动中..."
                        })
                else:
                    self.send_json_response(200, {
                        "status": "starting",
                        "message": "RAG系统正在启动中..."
                    })
            else:
                self.send_json_response(200, {
                    "status": "stopped",
                    "message": "RAG系统未启动"
                })
                
        except Exception as e:
            logger.error(f"状态检查失败: {e}")
            self.send_json_response(500, {
                "status": "error",
                "message": str(e)
            })
    
    def handle_rag_proxy(self, path, method='GET'):
        """通过静态服务器代理访问RAG主服务器API，遵守瓮城/安全前哨架构"""
        global rag_server_port
        
        # 检查是否通过命令行启动的RAG服务器
        if not rag_server_port:
            # 尝试从服务器注册表获取端口
            active_servers = server_registry.get_all_servers()
            if active_servers:
                rag_server_port = active_servers[0]['port']
            else:
                logger.error(f"RAG主服务器未启动，无法代理请求: {path}")
                self.send_json_response(500, {
                    "success": False,
                    "error": "RAG主服务器未启动，请先通过启动页面启动系统",
                    "path": path
                })
                return
        
        target_url = f"http://localhost:{rag_server_port}{path}"
        logger.info(f"🔁 代理请求到RAG主服务器: {target_url} ({method})")
        
        try:
            if method == 'GET':
                backend_resp = requests.get(target_url, timeout=30)
            else:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else None
                headers = {
                    'Content-Type': self.headers.get('Content-Type', 'application/json')
                }
                backend_resp = requests.post(target_url, data=body, headers=headers, timeout=60)
            
            # 优先按JSON处理，保持统一的返回格式和编码
            try:
                data = backend_resp.json()
                self.send_json_response(backend_resp.status_code, data)
            except ValueError:
                # 如果后端不是JSON，直接透传文本内容
                self.send_response(backend_resp.status_code)
                self.send_header('Content-Type', backend_resp.headers.get('Content-Type', 'application/json; charset=utf-8'))
                self.end_headers()
                self.wfile.write(backend_resp.content)
        except Exception as e:
            logger.error(f"RAG代理请求失败: {path} - {e}")
            self.send_json_response(500, {
                "success": False,
                "error": f"RAG代理请求失败: {str(e)}",
                "path": path
            })
    
    def handle_start_backend(self):
        """启动RAG主服务器（动态随机端口）"""
        global rag_server_process, rag_server_port
        
        try:
            # 检查是否已在运行
            if rag_server_process and rag_server_process.poll() is None:
                self.send_json_response(200, {
                    "status": "success",
                    "message": "RAG系统已在运行",
                    "port": rag_server_port
                })
                return
            
            # 随机分配端口（5000-9999，避免常用端口）
            # 【设计意图】使用Python标准库random.randint，不依赖numpy.random，保持静态服务器零依赖特性
            rag_server_port = random.randint(5000, 9999)
            logger.info(f"🎲 随机分配端口: {rag_server_port}")
            
            # 启动RAG主服务器（在虚拟环境中）
            logger.info("正在启动RAG主服务器...")
            
            # 构建启动命令
            project_dir = Path.cwd()
            # 【架构设计】虚拟环境myenv_stable由静态服务器管理，属于基础设施层
            # 静态服务器负责启动RAG主服务器时调用虚拟环境中的Python解释器
            # 这样设计的原因：虚拟环境是稳定的前置依赖，应由常驻进程管理，避免重复加载
            venv_python = project_dir / "myenv_stable" / "Scripts" / "python.exe"
            
            if not venv_python.exists():
                raise FileNotFoundError(f"虚拟环境Python不存在: {venv_python}")
            
            # 启动命令：传递动态端口作为命令行参数
            cmd = [str(venv_python), "rag_main_server.py", "--port", str(rag_server_port)]
            
            # 启动进程（后台运行，不捕获输出避免阻塞）
            # Windows下使用CREATE_NEW_CONSOLE创建新窗口，让输出直接显示在新控制台
            rag_server_process = subprocess.Popen(
                cmd,
                cwd=str(project_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            logger.info(f"RAG主服务器启动命令已发送，PID: {rag_server_process.pid}, 端口: {rag_server_port}")
            logger.info("RAG主服务器已在新控制台窗口中启动，查看该窗口获取启动日志")
            
            self.send_json_response(200, {
                "status": "success",
                "message": "RAG系统正在启动，请稍候...",
                "port": rag_server_port,  # 返回动态端口
                "estimated_time": "5-10秒"
            })
            
        except Exception as e:
            logger.error(f"启动RAG主服务器失败: {e}")
            rag_server_port = None  # 重置端口
            self.send_json_response(500, {
                "status": "error",
                "message": f"启动失败: {str(e)}"
            })
    
    def handle_stop_backend(self):
        """停止RAG主服务器"""
        global rag_server_process, rag_server_port
        
        try:
            if rag_server_process and rag_server_process.poll() is None:
                logger.info("正在停止RAG主服务器...")
                rag_server_process.terminate()
                rag_server_process.wait(timeout=5)
                rag_server_process = None
                rag_server_port = None  # 重置端口
                
                self.send_json_response(200, {
                    "status": "success",
                    "message": "RAG系统已停止"
                })
            else:
                self.send_json_response(200, {
                    "status": "info",
                    "message": "RAG系统未在运行"
                })
                
        except Exception as e:
            logger.error(f"停止RAG主服务器失败: {e}")
            self.send_json_response(500, {
                "status": "error",
                "message": f"停止失败: {str(e)}"
            })
    
    def handle_error_report(self):
        """处理前端错误报告"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            error_data = json.loads(post_data.decode('utf-8'))
            
            # 记录错误日志
            logger.error(f"前端错误报告: {error_data}")
            
            self.send_json_response(200, {
                "status": "success",
                "message": "错误报告已记录"
            })
            
        except Exception as e:
            logger.error(f"处理错误报告失败: {e}")
            self.send_json_response(500, {
                "status": "error",
                "message": str(e)
            })
    
    def handle_server_register(self):
        """主服务器启动时向静态服务器注册"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            port = data.get('port')
            pid = data.get('pid')
            
            if port and pid:
                success = server_registry.register(port, pid)
                self.send_json_response(200, {
                    "success": success,
                    "message": f"服务器实例已注册: PID={pid}, Port={port}",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.send_json_response(400, {
                    "success": False,
                    "error": "缺少port或pid参数",
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"注册服务器失败: {e}")
            self.send_json_response(500, {
                "success": False,
                "error": str(e)
            })
    
    def handle_server_unregister(self):
        """主服务器关闭时向静态服务器报告"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            port = data.get('port')
            reason = data.get('reason', 'unknown')
            
            if port:
                # 从注册表中注销实例
                success = server_registry.unregister(port)
                logger.info(f"收到主服务器注销请求: Port={port}, Reason={reason}, 注销结果={success}")
                self.send_json_response(200, {
                    "success": success,
                    "message": f"服务器实例已注销: Port={port}",
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.send_json_response(400, {
                    "success": False,
                    "error": "缺少port参数",
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"注销服务器失败: {e}")
            self.send_json_response(500, {
                "success": False,
                "error": str(e)
            })
    
    def handle_occupied_ports(self):
        """主服务器启动前查询哪些端口已被占用"""
        try:
            occupied = server_registry.get_occupied_ports()
            available = server_registry.get_available_port()
            
            self.send_json_response(200, {
                "success": True,
                "occupied_ports": occupied,
                "available_port": available,
                "all_instances": server_registry.get_all_instances(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"查询端口失败: {e}")
            self.send_json_response(500, {
                "success": False,
                "error": str(e)
            })
    
    def handle_outpost_breach_test(self):
        """模拟前哨被击穿，触发自毁和警报流程（仅用于测试）"""
        try:
            # 1. 自毁端口数据
            snapshot = server_registry.self_destruct()
            
            # 2. 向所有主服务器发送警报
            alerted_servers = server_registry.alert_main_servers_breach()
            
            # 3. 向系统维护师报告（如果维护师已启动）
            try:
                # 动态导入系统维护师
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
                from system_maintenance_agent import get_system_maintenance
                maintenance_agent = get_system_maintenance()
                
                alert_result = maintenance_agent.receive_security_alert({
                    "event": "outpost_compromised",
                    "timestamp": snapshot["timestamp"],
                    "destroyed_instances": snapshot["destroyed_instances"],
                    "total_instances": snapshot["total_instances"],
                    "action_taken": "self_destruct_and_alert_main_servers",
                    "alerted_servers": alerted_servers
                })
                
                maintenance_report = {
                    "reported_to_maintenance": True,
                    "maintenance_response": alert_result
                }
            except Exception as e:
                logger.warning(f"向系统维护师报告失败（可能未启动）: {e}")
                maintenance_report = {
                    "reported_to_maintenance": False,
                    "reason": str(e)
                }
            
            self.send_json_response(200, {
                "success": True,
                "message": "前哨击穿模拟完成",
                "self_destruct": snapshot,
                "alerted_servers": alerted_servers,
                "maintenance": maintenance_report,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"前哨击穿模拟失败: {e}", exc_info=True)
            self.send_json_response(500, {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    

    
    def send_json_response(self, status_code, data):
        """发送JSON响应"""
        try:
            response_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)
            
        except BrokenPipeError:
            # 客户端提前关闭连接（正常现象，无需记录错误）
            logger.debug("客户端已关闭连接，响应未完全发送")
        except ConnectionAbortedError:
            # Windows下的连接中止（客户端主动断开）
            logger.debug("连接被客户端中止")
        except OSError as e:
            # Windows特有的连接错误（如WinError 10053）
            if e.winerror == 10053:
                logger.debug("客户端软件中止连接（正常现象）")
            else:
                logger.error(f"发送JSON响应时发生网络错误: {e}")
        except Exception as e:
            logger.error(f"发送JSON响应失败: {e}")

def start_static_server(port=10808):
    """启动静态Web服务器"""
    try:
        # 创建服务器
        with socketserver.TCPServer(("", port), StaticServerHandler) as httpd:
            logger.info("=" * 60)
            logger.info("RAG系统静态Web服务器")
            logger.info("=" * 60)
            logger.info(f"📡 访问地址: http://localhost:{port}")
            logger.info(f"🎯 功能: 启动控制 + 静态页面托管")
            logger.info(f"💡 提示: 打开浏览器访问上述地址即可使用")
            logger.info("=" * 60)
            logger.info("")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        logger.info("\n静态服务器已停止")
    except Exception as e:
        logger.error(f"静态服务器启动失败: {e}")

if __name__ == '__main__':
    start_static_server()
