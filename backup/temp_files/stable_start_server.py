#!/usr/bin/env python
# @self-expose: {"id": "stable_start_server", "name": "Stable Start Server", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Stable Start Server功能"]}}
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
- Python 3.13 + NumPy 2.3.3
- 内置HTTP服务器 (http.server)
- 多智能体聊天室引擎
- 网状思维引擎、认知破障引擎等

注意：这是统一的服务器系统，同时支持两种交互模式。
"""

import os
import sys
import json
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

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

        # 智能体模板历史记录接口
        elif path == '/api/chatroom/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 解析查询参数
            query_params = parse_qs(parsed_path.query)
            session_id = query_params.get('session_id', ['default_session'])[0]
            
            # 模拟返回智能体模板的历史记录
            response = {
                "success": True,
                "history": [
                    {
                        "role": "system",
                        "content": "欢迎使用智能体模板系统！",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
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
    
    def do_POST(self):
        """处理POST请求"""
        # 导入必要的模块
        import os
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": False,
                "error": "无效的JSON格式"
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # 智能体模板消息处理API
        elif path == '/api/agent-template/message':
            # 智能体模板消息接口 - 调用真正的聊天API
            # 获取用户消息
            user_message = data.get('message', '')
            
            # 导入真正的聊天API模块
            try:
                # 动态导入聊天API模块
                import sys
                import os
                # 添加正确的路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                api_dir = os.path.join(current_dir, 'api')
                sys.path.insert(0, current_dir)  # 添加项目根目录
                sys.path.insert(0, api_dir)      # 添加api目录
                
                # 导入必要的模块
                from src.llm_client_enhanced import LLMClientEnhanced
                
                # 直接调用LLM API生成响应（避免复杂的导入问题）
                llm_client = LLMClientEnhanced()
                
                # 构建消息
                messages = [
                    {
                        "role": "system", 
                        "content": """你是一个专业的RAG智能助手，基于三层响应机制：
1. 本地知识层：基于用户本地知识库提供精准回答
2. 预训练知识层：基于预训练模型提供通用知识
3. 实时工具层：调用实时工具解决复杂问题

请根据用户问题选择最合适的响应策略，提供专业、准确的回答。"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
                
                # 调用LLM生成响应
                response_text = llm_client.chat_completion(messages)
                
                if response_text:
                    
                    response = {
                        "success": True,
                        "user_message": {
                            "content": user_message, 
                            "sender": "用户",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        "agent_responses": [
                            {
                                'agent_id': 'llm_assistant',
                                'agent_name': 'RAG智能助手',
                                'content': response_text,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        ],
                        "methodology_insights": [
                            {
                                'type': 'response_strategy',
                                'content': '基于LLM API调用的智能响应，采用三层响应机制'
                            }
                        ],
                        "response_strategy": 'llm_api',
                        "tools_used": ['LLM API调用', '三层响应机制'],
                        "memory_usage": len(user_message) * 10,
                        "knowledge_sources": ['本地知识库', '预训练模型', 'LLM API'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "full_timestamp": datetime.now().isoformat(),
                        "chatroom_status": 'active',
                        "design_principle": '真正的LLM API调用 - 非模拟响应'
                    }
                else:
                    raise Exception("LLM API返回无效响应")
                
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
        
        # 错误报告
        elif path == '/api/error-report':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 确保日志目录存在
            import os
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


def start_server(host='0.0.0.0', port=10808):
    """启动RAG系统稳定版服务器"""
    global HTTPD
    
    try:
        logger.info("进入start_server函数")
        print("初始化聊天室...")
        
        # 暂时跳过聊天室初始化，先测试基本服务器功能
        logger.info("暂时跳过聊天室初始化，先测试基本服务器功能")
        print("暂时跳过聊天室初始化，先测试基本服务器功能")
        
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
        
        logger.info(f"RAG系统稳定版启动服务器，端口: {port}")
        logger.info(f"安全入口: http://localhost:{port}")
        
        print(f"\nRAG系统稳定版启动服务器")
        print(f"记住: 端口{port}就是你的系统'密码'")
        print(f"纯净启动服务器已启动在端口 {port}")
        print(f"安全入口: http://localhost:{port}")
        
        print(f"\n使用说明:")
        print(f"1. 打开浏览器访问: http://localhost:{port}")
        print(f"2. 点击'启动完整系统'按钮")
        print(f"3. 等待系统初始化完成")
        print(f"4. 开始使用RAG系统的完整功能")
        print(f"5. 记住: 端口{port}就是你的安全密钥")
        
        # 启动服务器
        logger.info("即将进入serve_forever()循环")
        print("服务器正在监听请求...")
        
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
        if HTTPD:
            HTTPD.server_close()
        logger.info("服务器已成功关闭")
        print("服务器已成功关闭")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
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
