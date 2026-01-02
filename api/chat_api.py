# @self-expose: {"id": "chat_api", "name": "多智能体聊天室API", "type": "api", "version": "1.0.2", "needs": {"endpoints": [{"path": "/api/chatroom/history", "method": "GET", "desc": "获取聊天历史"}, {"path": "/api/chatroom/message", "method": "POST", "desc": "发送聊天消息"}, {"path": "/api/chatroom/status", "method": "GET", "desc": "获取聊天室状态"}], "deps": ["src.multi_agent_chatroom", "src.agent_manager", "src.llm_client_enhanced"]}, "provides": {"capabilities": ["多智能体交互", "聊天历史管理", "实时消息发送", "世界观访问观测"]}}

"""
多智能体聊天室API接口
将聊天机器人改造成支持用户和三个智能体交互的聊天室

开发提示词来源：用户对话中关于智能体交互产生方法论的深刻洞察
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from dataclasses import dataclass
from typing import Literal

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import sys
import os

# 添加正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入多智能体聊天室模块
from src.multi_agent_chatroom import MultiAgentChatroom, AgentRole, MessageType
from src.agent_manager import AgentManager
# 导入LLM客户端
from src.llm_client_enhanced import LLMClientEnhanced

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Verdict = Literal["ALLOW", "WARN", "BLOCK"]


@dataclass
class WorldviewCheckResult:
    verdict: Verdict
    reason: str
    actor: str
    purpose: str
    data_type: str
    extra: dict


def evaluate_data_access(actor: str, purpose: str, data_type: str, extra: dict) -> WorldviewCheckResult:
    """世界观引擎MVP：对一次数据访问做轻量评估（当前只用于观测与日志记录）"""
    if purpose in ["answer_question", "context_retrieval", "system_diagnostics"]:
        verdict: Verdict = "ALLOW"
        reason = "功能性被需要的数据访问，用于完成当前职责。"
    elif purpose in ["model_tuning", "stats_analysis"]:
        verdict = "ALLOW"
        reason = "用于提升系统整体认知与秩序度的访问。"
    else:
        verdict = "WARN"
        reason = f"用途未在白名单中，需后续结合上下文复盘：purpose={purpose}"

    return WorldviewCheckResult(
        verdict=verdict,
        reason=reason,
        actor=actor,
        purpose=purpose,
        data_type=data_type,
        extra=extra,
    )


def log_worldview_event(event_type: str, result: WorldviewCheckResult) -> None:
    """将世界观相关事件写入日志（MVP阶段只做INFO记录，不影响业务逻辑）"""
    try:
        logger.info(
            "[worldview_event] type=%s verdict=%s reason=%s actor=%s purpose=%s data_type=%s extra=%s",
            event_type,
            result.verdict,
            result.reason,
            result.actor,
            result.purpose,
            result.data_type,
            result.extra,
        )
    except Exception as e:
        logger.error("记录世界观事件失败: %s", e)

app = Flask(__name__, static_folder='../templates', static_url_path='')
CORS(app)

# 全局聊天室实例
chatroom = None

# 在应用启动时初始化聊天室
def initialize_app():
    """初始化应用"""
    global chatroom
    if not chatroom:
        initialize_chatroom()

# 在第一个请求时初始化
@app.before_request
def before_request():
    """在每个请求前检查初始化"""
    global chatroom
    if not chatroom:
        initialize_chatroom()

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('../templates', 'agent_chatbot.html')

def _handle_cognitive_unloading_error(user_message: str, error: Exception) -> Dict:
    """处理认知卸载架构错误 - 问题直接暴露"""
    logger.error(f"多智能体认知卸载架构错误: {error}")
    
    return {
        'success': False,
        'error': '多智能体认知卸载架构错误',
        'message': str(error),
        'user_message': {'content': user_message, 'sender': '用户', 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        'agent_responses': [],
        'methodology_insights': [],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'full_timestamp': datetime.now().isoformat(),
        'chatroom_status': 'error',
        'design_principle': '问题直接暴露 - 开发阶段不隐藏错误'
    }

def initialize_chatroom():
    """初始化聊天室"""
    global chatroom
    try:
        chatroom = MultiAgentChatroom()
        # 将聊天室实例同时挂载到app，避免仅使用全局变量导致首次请求无法读取历史
        setattr(app, 'chatroom', chatroom)
        # 启动聊天室
        if chatroom.start_chatroom():
            logger.info("多智能体聊天室初始化并启动成功")
            return True
        else:
            logger.error("多智能体聊天室启动失败")
            return False
    except Exception as e:
        logger.error(f"多智能体聊天室初始化失败: {e}")
        return False

def chatroom_message_endpoint(request_data=None):
    """聊天室消息接口 - 核心API"""
    try:
        # 解析请求数据获取用户消息
        if request_data is None:
            data = request.get_json()
        else:
            data = request_data
            
        if not data or 'message' not in data:
            return {
                'error': '缺少message参数',
                'success': False
            }
            
        user_message = data.get('message', '')
        
        # 检查全局chatroom变量是否存在且已初始化
        if 'chatroom' not in globals() or not globals()['chatroom']:
            # 如果聊天室未初始化，直接调用LLM生成响应
            return _generate_llm_response(user_message)
        
        chatroom = globals()['chatroom']
        
        try:
            # 发送用户消息到聊天室
            response = chatroom.send_user_message(user_message)
            
            # 构建响应
            return {
                'success': True,
                'user_message': response['user_message'],
                'agent_responses': response['agent_responses'],
                'methodology_insights': response['methodology_insights'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'full_timestamp': datetime.now().isoformat(),
                'chatroom_status': 'active'
            }
        except Exception as inner_e:
            # 如果chatroom操作失败，调用LLM生成响应
            print(f"聊天室消息处理错误: {str(inner_e)}")
            return _generate_llm_response(user_message)
        
    except Exception as e:
        logger.error(f"聊天室消息接口错误: {e}")
        return _generate_llm_response(user_message if 'user_message' in locals() else '')

# Flask路由版本，用于HTTP请求
@app.route('/api/chatroom/message', methods=['POST'])
def chatroom_message_endpoint():
    """处理聊天室消息接口 - 基于认知卸载架构"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': '消息内容不能为空',
                'design_principle': '问题直接暴露 - 输入验证'
            }), 400
        
        # 检查聊天室是否已初始化
        if not hasattr(app, 'chatroom') or app.chatroom is None:
            # 如果聊天室未初始化，直接暴露问题
            error_msg = "多智能体聊天室未初始化 - 请先调用初始化接口"
            logger.error(error_msg)
            return jsonify(_handle_cognitive_unloading_error(user_message, Exception(error_msg)))
        
        # 使用聊天室处理消息
        result = app.chatroom.process_user_message(user_message)
        
        if result.get('success'):
            return jsonify(result)
        else:
            # 如果聊天室处理失败，直接暴露问题
            error_msg = f"多智能体聊天室处理失败: {result.get('message', '未知错误')}"
            logger.error(error_msg)
            return jsonify(_handle_cognitive_unloading_error(user_message, Exception(error_msg)))
            
    except Exception as e:
        # 发生异常时直接暴露问题
        logger.error(f"多智能体认知卸载架构异常: {e}")
        return jsonify(_handle_cognitive_unloading_error(
            user_message if 'user_message' in locals() else '', e
        ))

@app.route('/api/chatroom/history', methods=['GET'])
def chatroom_history_endpoint():
    """获取聊天室最近历史记录

    返回最近 N 条对话消息，默认 50 条。
    优先从内存中的 chatroom.conversation_history 读取，
    如聊天室未初始化则从日志文件中尝试恢复。
    """
    try:
        limit = 50
        try:
            raw_limit = request.args.get('limit')
            if raw_limit:
                limit = max(1, min(200, int(raw_limit)))
        except Exception:
            limit = 50

        # 优先使用应用上的聊天室实例
        if hasattr(app, 'chatroom') and app.chatroom is not None:
            try:
                if hasattr(app.chatroom, 'get_conversation_history'):
                    history = app.chatroom.get_conversation_history(limit=limit)
                else:
                    # 兼容旧实现：直接返回内存中的 conversation_history
                    full_history = getattr(app.chatroom, 'conversation_history', [])
                    history = full_history[-limit:] if isinstance(full_history, list) else []

                return jsonify({
                    'success': True,
                    'history': history,
                    'count': len(history),
                    'source': 'memory',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'full_timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"从内存聊天室获取历史失败: {e}")

        # 回退：尝试从日志文件读取
        try:
            from pathlib import Path
            from src.multi_agent_chatroom import CHATROOM_LOG_PATH

            log_path = CHATROOM_LOG_PATH
            if not isinstance(log_path, Path):
                log_path = Path(log_path)

            if log_path.exists():
                with log_path.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                conv = data.get('conversation_history', [])
                history = conv[-limit:] if isinstance(conv, list) else []
            else:
                history = []
        except Exception as e:
            logger.error(f"从日志文件读取聊天室历史失败: {e}")
            history = []

        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'source': 'log' if history else 'none',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'full_timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"聊天室历史接口异常: {e}")
        return jsonify({
            'success': False,
            'history': [],
            'count': 0,
            'source': 'error',
            'error': str(e),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'full_timestamp': datetime.now().isoformat()
        })

@app.route('/api/chatroom/status', methods=['GET'])
def chatroom_status_endpoint():
    """获取聊天室状态接口 - 增强容错避免前端卡死"""
    try:
        # 检查聊天室是否已初始化
        if hasattr(app, 'chatroom') and app.chatroom is not None:
            try:
                # 尝试访问chatroom的详细状态（二级容错）
                agents_count = len(getattr(app.chatroom, 'agents', {}))
                return jsonify({
                    'success': True,
                    'status': '运行中',
                    'chatroom_status': 'active',
                    'message': f'聊天室正常运行（{agents_count}个智能体）',
                    'agents_count': agents_count,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'full_timestamp': datetime.now().isoformat()
                })
            except Exception as inner_e:
                # 如果访问chatroom属性失败，返回基础状态（避免前端卡死）
                logger.warning(f"获取聊天室详细状态失败，返回基础状态: {inner_e}")
                return jsonify({
                    'success': True,
                    'status': '运行中',
                    'chatroom_status': 'active',
                    'message': '聊天室正常运行',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'full_timestamp': datetime.now().isoformat()
                })
        else:
            return jsonify({
                'success': True,
                'status': '初始化中',
                'chatroom_status': 'initializing',
                'message': '聊天室正在初始化',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'full_timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        # 外层异常捕获：即使出错也返回success:True，避免前端错误卡死
        logger.error(f"聊天室状态检查错误: {e}")
        return jsonify({
            'success': True,  # 关键：返回成功状态，避免前端错误
            'status': '初始化中',
            'chatroom_status': 'initializing',
            'message': '系统正在准备',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'full_timestamp': datetime.now().isoformat()
        })

@app.route('/api/agents', methods=['GET'])
def agents_endpoint():
    """获取智能体列表接口"""
    try:
        # 检查聊天室是否已初始化
        if not hasattr(app, 'chatroom') or app.chatroom is None:
            # 如果聊天室未初始化，返回默认智能体列表
            return jsonify({
                'success': True,
                'agents': [
                    {
                        'id': 'system_architect',
                        'name': '系统架构师',
                        'description': '负责系统架构设计和规划',
                        'status': 'active',
                        'color': '#FF6B6B'
                    },
                    {
                        'id': 'scheme_evaluator', 
                        'name': '方案评估师',
                        'description': '负责方案评估和优化建议',
                        'status': 'active',
                        'color': '#4ECDC4'
                    },
                    {
                        'id': 'code_implementer',
                        'name': '代码实现师',
                        'description': '负责代码实现和技术实现',
                        'status': 'active',
                        'color': '#45B7D1'
                    },
                    {
                        'id': 'data_collector',
                        'name': '数据收集师',
                        'description': '负责数据收集和分析',
                        'status': 'active',
                        'color': '#96CEB4'
                    }
                ],
                'count': 4,
                'message': '使用默认智能体列表（聊天室未初始化）',
                'status': 'initializing'
            })
        
        # 获取聊天室中的智能体列表
        chatroom = app.chatroom
        
        # 构建智能体列表响应
        agents_list = []
        for role, agent in chatroom.agents.items():
            agent_info = {
                'id': role.value if hasattr(role, 'value') else str(role),
                'name': agent.name if hasattr(agent, 'name') else str(role),
                'description': agent.description if hasattr(agent, 'description') else f'{str(role)}智能体',
                'status': 'active',
                'color': get_agent_color(role)
            }
            agents_list.append(agent_info)
        
        return jsonify({
            'success': True,
            'agents': agents_list,
            'count': len(agents_list),
            'message': '成功获取智能体列表',
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"智能体列表接口错误: {e}")
        # 即使出错也返回默认智能体列表
        return jsonify({
            'success': True,
            'agents': [
                {
                    'id': 'system_architect',
                    'name': '系统架构师',
                    'description': '负责系统架构设计和规划',
                    'status': 'active',
                    'color': '#FF6B6B'
                },
                {
                    'id': 'scheme_evaluator', 
                    'name': '方案评估师',
                    'description': '负责方案评估和优化建议',
                    'status': 'active',
                    'color': '#4ECDC4'
                },
                {
                    'id': 'code_implementer',
                    'name': '代码实现师',
                    'description': '负责代码实现和技术实现',
                    'status': 'active',
                    'color': '#45B7D1'
                },
                {
                    'id': 'data_collector',
                    'name': '数据收集师',
                    'description': '负责数据收集和分析',
                    'status': 'active',
                    'color': '#96CEB4'
                }
            ],
            'count': 4,
            'message': '使用默认智能体列表（接口错误）',
            'status': 'error'
        })

def get_agent_color(role):
    """根据智能体角色获取颜色"""
    color_map = {
        'ARCHITECT': '#FF6B6B',      # 红色
        'EVALUATOR': '#4ECDC4',      # 青色
        'IMPLEMENTER': '#45B7D1',    # 蓝色
        'DATA_COLLECTOR': '#96CEB4'  # 绿色
    }
    
    role_str = role.value if hasattr(role, 'value') else str(role)
    return color_map.get(role_str, '#6C757D')  # 默认灰色

@app.route('/api/tools', methods=['GET'])
def tools_endpoint():
    """工具列表接口"""
    try:
        # 不需要检查chatroom，直接返回工具列表信息
        # 聊天室模式下暂时返回空工具列表
        return jsonify({
            'success': True,
            'tools': [],
            'count': 0,
            'message': '聊天室模式下工具功能暂不可用',
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"工具列表接口错误: {e}")
        # 即使出错也返回成功状态，避免前端错误
        return jsonify({
            'success': True,
            'tools': [],
            'count': 0,
            'message': '工具服务正在初始化',
            'status': 'initializing'
        })

@app.route('/api/memory/iterate', methods=['POST'])
def memory_iteration_endpoint():
    """记忆迭代接口"""
    try:
        # 不需要检查chatroom，直接返回功能信息
        data = request.get_json() or {}
        topic = data.get('topic', '')
        
        # 聊天室模式下记忆迭代功能暂不可用
        return jsonify({
            'success': True,
            'iteration_result': {
                'topic': topic,
                'insights': ['聊天室模式下记忆迭代功能暂不可用']
            },
            'message': '聊天室模式下记忆迭代功能暂不可用',
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"记忆迭代接口错误: {e}")
        # 即使出错也返回成功状态，避免前端错误
        return jsonify({
            'success': True,
            'iteration_result': {
                'topic': '',
                'insights': ['服务正在初始化']
            },
            'message': '记忆服务正在初始化',
            'status': 'initializing'
        })

@app.route('/api/chatroom/history', methods=['GET'])
def chatroom_history_endpoint():
    """聊天室历史记录接口 + 世界观引擎MVP观测"""
    try:
        # 优先使用app属性中的chatroom实例（与消息接口一致），否则回退到全局
        active_chatroom = getattr(app, 'chatroom', None)
        if not active_chatroom and 'chatroom' in globals() and globals()['chatroom']:
            active_chatroom = globals()['chatroom']

        # 无聊天室实例时，记录一次访问观测并返回默认欢迎消息
        if not active_chatroom:
            result = evaluate_data_access(
                actor="chat_history_endpoint",
                purpose="answer_question",
                data_type="chat_log",
                extra={
                    "has_chatroom": False,
                    "limit": 0,
                },
            )
            log_worldview_event("data_access", result)

            resp = jsonify({
                'success': True,
                'history': [
                    {
                        'sender': '系统',
                        'content': '您好！我是RAG智能助手，很高兴为您服务。',
                        'message_type': 'system_notification',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                ],
                'count': 1,
                'status': 'initializing'
            })
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # 解析limit参数
        try:
            limit = int(request.args.get('limit', 20))
        except Exception:
            limit = 20

        # 有聊天室实例时，记录一次访问观测
        result = evaluate_data_access(
            actor="chat_history_endpoint",
            purpose="answer_question",
            data_type="chat_log",
            extra={
                "has_chatroom": True,
                "limit": limit,
            },
        )
        log_worldview_event("data_access", result)

        # 获取历史
        history = active_chatroom.get_conversation_history(limit=limit)
        resp = jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'status': 'active'
        })
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except Exception as e:
        logger.error(f"聊天室历史接口错误: {e}")
        resp = jsonify({
            'error': str(e),
            'success': False
        })
        resp.headers['Cache-Control'] = 'no-store'
        return resp, 500
@app.route('/api/knowledge-graph', methods=['GET'])
def knowledge_graph_endpoint():
    """知识图谱数据接口 - 为LLM提供结构化上下文数据"""
    try:
        # 检查全局chat_engine变量是否存在且已初始化
        if 'chat_engine' not in globals() or not globals()['chat_engine']:
            # 返回可用的默认数据，避免API调用失败
            return jsonify({
                'success': True,
                'message': '知识图谱服务正在初始化中',
                'type': 'default',
                'knowledge_overview': {
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'node_count': 0,
                        'edge_count': 0,
                        'initialized': False
                    }
                }
            }), 200
        
        chat_engine = globals()['chat_engine']
        # 获取查询参数
        query = request.args.get('query', '')
        center_node_id = request.args.get('center_node', type=int)
        
        # 获取网状思维引擎实例
        if not hasattr(chat_engine, 'mesh_thought_engine') or not chat_engine.mesh_thought_engine:
            # 如果网状思维引擎未初始化，返回默认数据
            return jsonify({
                'success': True,
                'message': '网状思维引擎正在初始化中',
                'type': 'default',
                'knowledge_overview': {
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'node_count': 0,
                        'edge_count': 0,
                        'initialized': False
                    }
                }
            }), 200
        
        mesh_engine = chat_engine.mesh_thought_engine
        
        # 根据查询类型获取不同的知识图谱数据
        if query:
            # 查询模式：为LLM提供与用户问题相关的知识图谱上下文
            try:
                knowledge_context = _get_knowledge_context_for_llm(query, mesh_engine)
                return jsonify({
                    'success': True,
                    'knowledge_context': knowledge_context,
                    'query': query,
                    'type': 'query_context'
                })
            except Exception as e:
                # 处理可能的异常，返回默认数据
                print(f"知识图谱查询处理错误: {str(e)}")
                return jsonify({
                    'success': True,
                    'message': '知识图谱查询处理中',
                    'type': 'default',
                    'knowledge_context': {'related_topics': [], 'key_concepts': []}
                }), 200
        elif center_node_id:
            # 中心节点模式：获取以指定节点为中心的思维网络
            try:
                thought_network = mesh_engine.get_thought_network(center_node_id)
                knowledge_graph = _build_visualization_data(thought_network, mesh_engine)
                return jsonify({
                    'success': True,
                    'knowledge_graph': knowledge_graph,
                    'type': 'visualization'
                })
            except Exception as e:
                # 处理可能的异常，返回默认数据
                print(f"知识图谱可视化处理错误: {str(e)}")
                return jsonify({
                    'success': True,
                    'message': '知识图谱可视化处理中',
                    'type': 'default',
                    'knowledge_graph': {'nodes': [], 'edges': []}
                }), 200
        else:
            # 默认模式：获取完整的知识图谱概览
            try:
                knowledge_overview = _get_knowledge_overview(mesh_engine)
                return jsonify({
                    'success': True,
                    'knowledge_overview': knowledge_overview,
                    'type': 'overview'
                })
            except Exception as e:
                # 处理可能的异常，返回默认数据
                print(f"知识图谱概览处理错误: {str(e)}")
                return jsonify({
                    'success': True,
                    'message': '知识图谱概览处理中',
                    'type': 'default',
                    'knowledge_overview': {
                        'nodes': [],
                        'edges': [],
                        'stats': {
                            'node_count': 0,
                            'edge_count': 0,
                            'initialized': False
                        }
                    }
                }), 200
    
    except Exception as e:
        logger.error(f"知识图谱接口错误: {e}")
        # 返回错误信息，而不是演示数据
        return jsonify({
            'success': False,
            'error': f'知识图谱服务异常: {str(e)}',
            'type': 'error'
        }), 500

def _get_knowledge_context_for_llm(query: str, mesh_engine) -> Dict[str, Any]:
    """为LLM提供与查询相关的知识图谱上下文"""
    
    # 向量化查询
    query_vector = mesh_engine.vector_store.embed(query)
    
    # 查找相似的思维节点
    similar_nodes = mesh_engine.find_similar_thoughts(query_vector, threshold=0.6)
    
    # 构建LLM友好的上下文格式
    context_parts = []
    
    if similar_nodes:
        context_parts.append("相关记忆知识图谱：")
        
        for i, node in enumerate(similar_nodes[:5]):  # 限制为前5个最相关的节点
            # 获取节点的关联网络
            node_network = mesh_engine.get_thought_network(node.id, max_depth=2)
            
            # 构建节点描述
            node_desc = f"\n{i+1}. 核心概念: {node.content}"
            
            # 添加关联概念
            if node_network.get('connections'):
                related_concepts = []
                for conn in node_network['connections']:
                    if conn['target'] in mesh_engine.nodes:
                        target_node = mesh_engine.nodes[conn['target']]
                        related_concepts.append(f"{target_node.content}（{conn['type']}，强度:{conn['strength']:.2f}）")
                
                if related_concepts:
                    node_desc += f"\n   关联概念: {', '.join(related_concepts[:3])}"
            
            context_parts.append(node_desc)
    else:
        # 如果没有找到相关节点，提供知识图谱概览
        overview = _get_knowledge_overview(mesh_engine)
        context_parts.append("知识图谱概览：")
        context_parts.append(f"总概念数: {overview['total_nodes']}")
        context_parts.append(f"核心概念: {', '.join(overview['top_concepts'][:3])}")
    
    return {
        'context_text': '\n'.join(context_parts),
        'relevant_nodes_count': len(similar_nodes),
        'query_similarity': '高' if len(similar_nodes) >= 3 else '中' if len(similar_nodes) >= 1 else '低'
    }

def _build_visualization_data(thought_network: Dict, mesh_engine) -> Dict[str, Any]:
    """构建可视化数据格式"""
    
    # 获取查重统计信息
    duplicate_stats = mesh_engine.get_duplicate_statistics()
    
    # 构建知识图谱数据结构
    knowledge_graph = {
        'nodes': [],
        'connections': [],
        'statistics': duplicate_stats
    }
    
    # 转换节点数据
    if 'nodes' in thought_network:
        for node_data in thought_network['nodes']:
            knowledge_graph['nodes'].append({
                'id': node_data['id'],
                'content': node_data['content'][:50] + '...' if len(node_data['content']) > 50 else node_data['content'],
                'type': 'thought',
                'importance': node_data.get('importance', 0.5),
                'connections_count': node_data.get('connections_count', 0)
            })
    
    # 转换连接数据
    if 'connections' in thought_network:
        for conn in thought_network['connections']:
            knowledge_graph['connections'].append({
                'source': conn['source'],
                'target': conn['target'],
                'strength': conn.get('strength', 0.5),
                'type': conn.get('type', 'related_to')
            })
    
    return knowledge_graph

def _get_knowledge_overview(mesh_engine) -> Dict[str, Any]:
    """获取知识图谱概览"""
    
    # 获取最重要的节点
    important_nodes = mesh_engine.get_most_important_nodes(limit=10)
    
    # 获取统计信息
    stats = mesh_engine.get_duplicate_statistics()
    
    return {
        'total_nodes': len(mesh_engine.nodes),
        'top_concepts': [node.content for node in important_nodes],
        'average_importance': sum(node.importance for node in mesh_engine.nodes.values()) / len(mesh_engine.nodes) if mesh_engine.nodes else 0,
        'duplicate_statistics': stats
    }

def _generate_llm_response(user_message: str) -> Dict[str, Any]:
    """生成真正的LLM响应 - 基于三层响应机制（支持自动回退）"""
    try:
        # 初始化LLM客户端（启用自动回退）
        logger.info(f"🛠️ 正在初始化LLM客户端...")
        llm_client = LLMClientEnhanced(enable_fallback=True)
        logger.info(f"✅ LLM客户端初始化成功，使用provider: {llm_client.provider}")
        
        # 构建消息列表
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
        logger.info(f"🤖 开始调用LLM生成响应...")
        response_text = llm_client.chat_completion(messages)
        
        if response_text:
            logger.info(f"✅ LLM响应成功，使用provider: {llm_client.provider}，响应长度: {len(response_text)}")
            return {
                'success': True,
                'user_message': {
                    'content': user_message, 
                    'sender': '用户',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                'agent_responses': [
                    {
                        'agent_id': 'llm_assistant',
                        'agent_name': f'RAG智能助手 ({llm_client.provider})',
                        'content': response_text,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                ],
                'methodology_insights': [
                    {
                        'type': 'response_strategy',
                        'content': f'基于{llm_client.provider} API调用的智能响应，采用三层响应机制'
                    }
                ],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'full_timestamp': datetime.now().isoformat(),
                'chatroom_status': 'active',
                'design_principle': f'真正的LLM API调用 ({llm_client.provider}) - 非模拟响应'
            }
        else:
            # 如果LLM调用失败，返回错误信息
            logger.error(f"❌ LLM API调用失败：所有provider均返回空结果")
            return {
                'success': False,
                'error': 'LLM API调用失败',
                'message': '所有配置的LLM服务商均无法生成回复，请检查：1. API密钥是否有效 2. 网络连接是否正常 3. 服务商是否限流',
                'user_message': {'content': user_message, 'sender': '用户', 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                'agent_responses': [],
                'methodology_insights': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'full_timestamp': datetime.now().isoformat(),
                'chatroom_status': 'error'
            }
    
    except ValueError as e:
        # 密钥未配置
        logger.error(f"❌ LLM初始化失败（密钥未配置）: {e}")
        return {
            'success': False,
            'error': '配置错误',
            'message': f'LLM服务商未配置：{str(e)}，请使用 tools/api_key_tool.py 添加API密钥',
            'user_message': {'content': user_message, 'sender': '用户', 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            'agent_responses': [],
            'methodology_insights': [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'full_timestamp': datetime.now().isoformat(),
            'chatroom_status': 'config_error'
        }
            
    except Exception as e:
        logger.error(f"❌ LLM响应生成异常: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'LLM响应生成异常',
            'message': f'系统内部错误：{str(e)}，请稍后重试或联系管理员',
            'user_message': {'content': user_message, 'sender': '用户', 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            'agent_responses': [],
            'methodology_insights': [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'full_timestamp': datetime.now().isoformat(),
            'chatroom_status': 'error'
        }


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version': '1.0.0'
    })

@app.route('/api/text-blocks', methods=['GET'])
def text_blocks_endpoint():
    """获取文本块关联关系接口"""
    try:
        from src.mesh_thought_engine import MeshThoughtEngine
        
        # 初始化网状思维引擎
        mesh_engine = MeshThoughtEngine()
        
        # 获取所有思维节点
        nodes = mesh_engine.nodes.values()
        
        # 构建文本块数据
        blocks = []
        for node in nodes:
            # 获取节点的关联
            connections = []
            for conn in node.connections:
                target_id = conn.get('target_id') or conn.get('target')
                if target_id and target_id in mesh_engine.nodes:
                    target_node = mesh_engine.nodes[target_id]
                    connections.append({
                        'id': target_id,
                        'title': target_node.content[:30] + '...' if len(target_node.content) > 30 else target_node.content,
                        'relation_type': conn.get('type', 'related_to'),
                        'strength': conn.get('strength', 0.5)
                    })
            
            # 生成时间戳
            ts = None
            try:
                ts_val = (node.metadata or {}).get('timestamp')
                if isinstance(ts_val, (int, float)):
                    ts = datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(ts_val, str):
                    ts = ts_val
            except Exception:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加文本块
            blocks.append({
                'id': node.id,
                'title': node.content[:30] + '...' if len(node.content) > 30 else node.content,
                'content': node.content,
                'timestamp': ts,
                'importance': node.importance,
                'connections': connections,
                'duplicate_id': getattr(node, 'duplicate_of', None)
            })
        
        # 按重要性排序
        blocks.sort(key=lambda x: x['importance'], reverse=True)
        
        # 构建响应并添加防缓存响应头
        resp = jsonify({
            'success': True,
            'blocks': blocks[:50],  # 限制返回数量
            'count': len(blocks),
            'total_connections': sum(len(block['connections']) for block in blocks)
        })
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except Exception as e:
        logger.error(f"文本块关联关系接口错误: {e}")
        resp = jsonify({
            'success': False,
            'error': str(e)
        })
        resp.headers['Cache-Control'] = 'no-store'
        return resp, 500

@app.route('/api/diagnostics', methods=['GET'])
def diagnostics_endpoint():
    """系统问题诊断接口"""
    try:
        import os
        import sys
        from datetime import datetime
        
        # 导入路径处理工具
        from src.path_utils import get_path_utils
        
        # 导入错误处理模块
        from src.agent_error_handler import AgentErrorHandler
        from src.error_knowledge_base import ErrorKnowledgeBase
        
        # 初始化诊断结果
        diagnostics_result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'problems': [],
            'system_info': {},
            'component_status': {},
            'recommendations': []
        }
        
        # 1. 系统基本信息
        diagnostics_result['system_info'] = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'env_path': sys.executable
        }
        
        # 2. 检查路径处理工具
        path_utils = get_path_utils()
        problems_dir = path_utils.get_problems_directory()
        diagnostics_result['component_status']['path_utils'] = {
            'status': 'healthy',
            'problems_directory': str(problems_dir),
            'directory_exists': os.path.exists(problems_dir)
        }
        
        # 3. 检查错误处理模块
        error_handler = AgentErrorHandler()
        diagnostics_result['component_status']['error_handler'] = {
            'status': 'healthy'
        }
        
        # 4. 检查错误知识库
        kb = ErrorKnowledgeBase()
        kb_stats = kb.get_statistics()
        diagnostics_result['component_status']['error_knowledge_base'] = {
            'status': 'healthy',
            'statistics': kb_stats
        }
        
        # 5. 检查路径解析问题
        problematic_path = r"e:\AI\qiusuo-framework\#problems_and_diagnostics"
        safe_path = path_utils.fix_path(problematic_path)
        diagnostics_result['problems'].append({
            'type': 'path_issue',
            'original_path': problematic_path,
            'fixed_path': safe_path,
            'status': 'fixed'
        })
        
        # 6. 检查是否存在其他常见问题
        # 检查端口占用情况
        try:
            import socket
            # 检查系统是否能创建socket（简单的网络可用性检查）
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.close()
            diagnostics_result['component_status']['network'] = {
                'status': 'healthy',
                'socket_check': 'passed'
            }
        except Exception as e:
            diagnostics_result['problems'].append({
                'type': 'network_issue',
                'message': str(e),
                'status': 'detected'
            })
            diagnostics_result['component_status']['network'] = {
                'status': 'unhealthy',
                'socket_check': 'failed'
            }
        
        # 7. 生成建议
        if diagnostics_result['problems']:
            diagnostics_result['status'] = 'unhealthy'
            diagnostics_result['recommendations'].append(
                f"检测到 {len(diagnostics_result['problems'])} 个问题，建议查看详细报告并修复"
            )
        else:
            diagnostics_result['status'] = 'healthy'
            diagnostics_result['recommendations'].append("系统运行正常，定期检查建议继续保持")
        
        return jsonify({
            'success': True,
            'diagnostics': diagnostics_result
        })
    except Exception as e:
        logger.error(f"问题诊断接口错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': '接口不存在',
        'success': False
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '内部服务器错误',
        'success': False
    }), 500

def run_server(host='127.0.0.1', port=8888, debug=False):
    """启动API服务器"""
    if initialize_chatroom():
        logger.info(f"多智能体聊天室API服务器启动在 http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
    else:
        logger.error("聊天室初始化失败，服务器无法启动")

if __name__ == '__main__':
    run_server(debug=True)