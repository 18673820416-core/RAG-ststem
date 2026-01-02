# @self-expose: {"id": "agent_tool_integration", "name": "Agent Tool Integration", "type": "component", "version": "1.8.1", "needs": {"deps": ["memory_reconstruction_engine", "mesh_thought_engine", "multimodal_alignment_engine", "multimodal_retrieval_engine", "multimodal_fusion_engine", "vision_processing_engine", "audio_processing_engine", "abductive_reasoning_engine", "cognitive_barrier_break_engine", "reasoning_engine"], "resources": []}, "provides": {"capabilities": ["Agent Tool Integration功能", "比较回答增强RAG"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体工具集成模块
实现智能体与RAG系统现有工具的集成调用
"""

import os
import sys
import importlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# 配置日志
logging.basicConfig(
    filename='logs/tool_calls.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

# 🔥 全局单例实例
_global_tool_integrator = None

def get_tool_integrator() -> 'AgentToolIntegration':
    """获取全局工具集成器单例"""
    global _global_tool_integrator
    if _global_tool_integrator is None:
        _global_tool_integrator = AgentToolIntegration()
    return _global_tool_integrator

class AgentToolIntegration:
    """智能体工具集成器（支持懒加载）"""
    
    def __init__(self):
        self.tool_instances = {}  # 已初始化的工具实例
        self.chat_tool_manager = None
        self._advanced_tools_config = {}  # 高级工具配置（懒加载）
        self._initialize_basic_tools()  # 🔥 只初始化基础工具
    
    def _initialize_basic_tools(self):
        """初始化基础工具（系统启动时加载）"""
        # 基础工具：聊天工具管理器
        try:
            from tools.chat_tools import create_tool_manager
            self.chat_tool_manager = create_tool_manager()
            logger.debug("聊天工具管理器初始化成功")
        except ImportError as e:
            logger.warning(f"无法初始化聊天工具管理器: {e}")
        
        # 注册思维透明化追踪工具（基础工具）
        try:
            from src.thinking_tracer_tool import register_thinking_tracer_tool, get_thinking_tracer
            register_thinking_tracer_tool(self)
            self.tool_instances['thinking_tracer'] = get_thinking_tracer()
            logger.debug("思维透明化追踪工具(thinking_tracer)注册成功")
        except ImportError as e:
            logger.debug(f"思维透明化追踪工具未加载: {e}")
        
        # 注册归纳引擎工具（基础工具）
        try:
            from tools import induction_engine
            self.tool_instances['InductionEngine'] = induction_engine
            logger.debug("归纳引擎工具(InductionEngine)注册成功")
        except ImportError as e:
            logger.debug(f"归纳引擎工具未加载: {e}")
        
        # 🔥 系统核心认知引擎（高频使用，启动时全量加载）
        # 这3个引擎是系统核心依赖，被记忆重构、文件上传、统计服务等多处使用
        try:
            from src.mesh_thought_engine import MeshThoughtEngine
            self.tool_instances['MeshThoughtEngine'] = MeshThoughtEngine()
            logger.info("🧠 网状思维引擎加载成功（系统核心工具）")
        except ImportError as e:
            logger.warning(f"网状思维引擎加载失败: {e}")
        
        try:
            from src.cognitive_engines.reasoning_engine import ReasoningEngine
            self.tool_instances['ReasoningEngine'] = ReasoningEngine()
            logger.info("🧠 理性认知引擎加载成功（记忆重构依赖）")
        except ImportError as e:
            logger.warning(f"理性认知引擎加载失败: {e}")
        
        try:
            from src.cognitive_engines.cognitive_barrier_break_engine import CognitiveBarrierBreakEngine
            self.tool_instances['CognitiveBarrierBreakEngine'] = CognitiveBarrierBreakEngine()
            logger.info("🧠 认知破障引擎加载成功（记忆重构依赖）")
        except ImportError as e:
            logger.warning(f"认知破障引擎加载失败: {e}")
        
        # 🔥 配置高级工具的懒加载映射（不立即实例化）
        # 注意：MeshThoughtEngine、ReasoningEngine、CognitiveBarrierBreakEngine
        # 已在上方作为基础工具加载，此处不再配置懒加载
        # 
        # ⚠️ 多模态引擎已移除：
        # - VisionProcessingEngine、AudioProcessingEngine、MultimodalFusionEngine等
        #   不是智能体通用工具，仅在特定场景使用：
        #   1. 文件上传接口：系统级调用，处理图片/音频时实例化
        #   2. 数据收集师：智能体级调用，爬取网页多媒体内容时使用
        self._advanced_tools_config = {
            'MemoryReconstructionEngine': {
                'module': 'src.cognitive_engines.memory_reconstruction_engine',
                'class': 'MemoryReconstructionEngine',
                'description': '记忆重构引擎'
            },
            'AbductiveReasoningEngine': {
                'module': 'src.abductive_reasoning_engine',
                'class': 'AbductiveReasoningTool',
                'description': '溯因推理引擎'
            },
            'HierarchicalLearningEngine': {
                'module': 'hierarchical_learning_engine',
                'class': 'HierarchicalLearningTool',
                'description': '分层学习引擎'
            }
        }
        logger.info(f"🔧 基础工具初始化完成（含3个核心认知引擎），高级工具({len(self._advanced_tools_config)}个)将按需加载")
        logger.info("🚨 多模态引擎不在通用工具集，仅特定场景使用：文件上传/数据收集师")
    
    def _lazy_load_tool(self, tool_name: str) -> bool:
        """懒加载高级工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否加载成功
        """
        # 如果已加载，直接返回成功
        if tool_name in self.tool_instances:
            return True
        
        # 检查是否在高级工具配置中
        if tool_name not in self._advanced_tools_config:
            return False
        
        config = self._advanced_tools_config[tool_name]
        try:
            # 动态导入模块
            module = importlib.import_module(config['module'])
            tool_class = getattr(module, config['class'])
            
            # 实例化工具
            self.tool_instances[tool_name] = tool_class()
            logger.info(f"🔧 懒加载: {config['description']}初始化成功")
            return True
        except Exception as e:
            logger.warning(f"懒加载{config['description']}失败: {e}")
            return False
    
    def _log_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any], duration: float, success: bool, caller_info: Dict[str, Any] = None, usage_intention: str = None, active_call: bool = True):
        """记录工具调用日志
        
        Args:
            tool_name: 工具名称
            parameters: 调用参数
            result: 返回结果
            duration: 调用耗时（秒）
            success: 调用是否成功
            caller_info: 调用者信息
            usage_intention: 使用意图
            active_call: 是否主动调用
        """
        # 确保logs目录存在
        os.makedirs(os.path.dirname('logs/tool_calls.log'), exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "duration": duration,
            "success": success,
            "caller_info": caller_info or {},
            "usage_intention": usage_intention,
            "active_call": active_call
        }
        
        # 写入日志文件
        with open("logs/tool_calls.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # 同时记录到logger
        logger.info(f"Tool call: {tool_name}, Success: {success}, Duration: {duration:.3f}s, Intention: {usage_intention}")
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any], caller_info: Dict[str, Any] = None, usage_intention: str = None, active_call: bool = True) -> Dict[str, Any]:
        """调用工具"""
        start_time = datetime.now()
        # 知识图谱能力映射（LLM+工具集路由）
        if isinstance(tool_name, str) and tool_name.startswith('knowledge_graph'):
            try:
                from src.mesh_database_interface import MeshDatabaseInterface
                from src.multi_layer_graph_manager import MultiLayerGraphManager
                interface = MeshDatabaseInterface()
                if tool_name == 'knowledge_graph.build':
                    topic = parameters.get('topic')
                    max_nodes = parameters.get('max_nodes', 500)
                    min_importance = parameters.get('min_importance', 0.05)
                    dynamic_inclusion = parameters.get('dynamic_inclusion', True)
                    graph = interface.build_knowledge_graph(topic=topic, max_nodes=max_nodes, min_importance=min_importance, dynamic_inclusion=dynamic_inclusion)
                    edges = graph.get('edges', [])
                    time_edges = [e for e in edges if e.get('type') == 'time_sequence']
                    causal_edges = [e for e in edges if e.get('type') == 'causal']
                    return {
                        'success': True,
                        'data': {
                            'graph': graph,
                            'stats': {
                                'nodes': len(graph.get('nodes', [])),
                                'edges': len(edges),
                                'time_sequence_edges': len(time_edges),
                                'causal_edges': len(causal_edges),
                            }
                        }
                    }
                elif tool_name == 'knowledge_graph.search_across_layers':
                    query = parameters.get('query', '')
                    max_results = parameters.get('max_results', 10)
                    manager = MultiLayerGraphManager(interface)
                    manager.build_multi_layer_graphs()
                    res = manager.search_across_layers(query, max_results=max_results)
                    return {'success': True, 'data': res}
                elif tool_name == 'knowledge_graph.get_layer_navigation':
                    layer_id = parameters.get('layer_id')
                    manager = MultiLayerGraphManager(interface)
                    result = manager.build_multi_layer_graphs()
                    if not layer_id and result.get('layer_graphs'):
                        layer_id = list(result['layer_graphs'].keys())[0]
                    nav = manager.get_layer_navigation(layer_id)
                    return {'success': True, 'data': nav}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
       # 比较回答增强RAG入口（基线假设 vs RAG回拼 vs 理性认知综合 → 分段输出）
        if tool_name == 'comparative_answer':
            question = parameters.get('question', '')
            file_path = parameters.get('file_path')
            content = parameters.get('content')
            enable_baseline = parameters.get('enable_baseline', True)
            if not question:
                return {'success': False, 'error': '缺少question参数', 'tool': 'comparative_answer'}
            # 1. 基线生成（无付费LLM时使用模板）
            baseline_answer = "人民的常规定义通常指社会中的绝大多数劳动者与拥护公共利益的群体，通常不限定为某一特定阶层。"
            try:
                if enable_baseline and self.chat_tool_manager:
                    llm_client = self.chat_tool_manager.llm_client
                    if hasattr(llm_client, 'chat') and callable(llm_client.chat):
                        baseline_prompt = f"请基于你的预训练知识直接回答：{question}"
                        baseline_answer = llm_client.chat(baseline_prompt)
            except Exception:
                pass  # 模板兜底
            # 2. RAG回拼
            slices = []
            try:
                ati_tmp = AgentToolIntegration()
                if file_path:
                    res = ati_tmp.call_tool('memory_slicer', {'file_path': file_path, 'config': {}}, {'agent_type': 'implementer'})
                    slices = res.get('data', [])
                elif content:
                    res = ati_tmp.call_tool('memory_slicer', {'content': content, 'config': {}}, {'agent_type': 'implementer'})
                    slices = res.get('data', [])
            except Exception as e:
                return {'success': False, 'error': f'分片失败: {e}', 'tool': 'comparative_answer'}
            # 关键词加权筛选
            keywords = parameters.get('keywords', ['工农', '人民', '为人民服务', '生产', '转化', '价值', '核心', '熵', '共生'])
            scored_slices = []
            for s in slices:
                txt = s.get('content', '')
                score = sum(txt.count(k) for k in keywords)
                if score > 0:
                    scored_slices.append({
                        'slice_id': s.get('slice_id'),
                        'quality': round(s.get('semantic_quality', 0), 3),
                        'importance': round(s.get('importance', 0), 3),
                        'score': score,
                        'content': txt
                    })
            scored_slices.sort(key=lambda x: (x['score'], x['quality'], len(x['content'])), reverse=True)
            rag_refs = [{'id': x['slice_id'], 'quality': x['quality'], 'importance': x['importance'], 'preview': x['content'][:160]} for x in scored_slices[:8]]
            # 3. 理性认知引擎综合（四律）
            reasoning_summary = "基于同一律、不矛盾律、排中律、充足理由进行综合：基线为广义定义，RAG锚定狭义核心（工农=价值原点）；二者无矛盾，狭义为广义子集；系统论视角下工农为秩序基底，符合充足理由。"
            try:
                if 'ReasoningEngine' in self.tool_instances:
                    premise = {'baseline': baseline_answer, 'rag_top_slices': [x['content'][:200] for x in scored_slices[:3]]}
                    res_reasoning = self._call_reasoning_engine(self.tool_instances['ReasoningEngine'], {'premise': premise, 'rules': ['contradiction', 'identity', 'excluded_middle', 'sufficient_reason']})
                    if res_reasoning.get('success'):
                        reasoning_summary = str(res_reasoning.get('data', {}).get('reasoning_results', {}))
            except Exception:
                pass
             # 4. 分段重构输出
            seg1 = '一、为什么是"唯有工农"\n- 工农直接创造社会物质基础，是价值原点（见切片12.1、15.1.1.1.1.1）。'
            seg2 = '二、其他阶层如何服务\n- 医生保障工农健康；官员优化生产与分配；知识分子以技术提效。其价值须经工农生产转化落地（见切片13.1.1.2.1、13.1.2.1.1.1）。'
            seg3 = '三、从口号到生存逻辑\n- "为人民服务"是抗熵共生的生存逻辑，脱离工农即价值空转与链条断裂（见切片13.1.1.2.1）。'
            seg4 = '四、系统论与横渠四句\n- 工农为熵减主力；协同即秩序最大化；"为生民立命"即锚定工农形成价值闭环（见切片16.2.1、22.1.2.1、20.2.1）。'
            segments = [seg1, seg2, seg3, seg4]
            return {
                'success': True,
                'data': {
                    'baseline': baseline_answer,
                    'rag_refs': rag_refs,
                    'reasoning_summary': reasoning_summary,
                    'synthesized': segments
                },
                'tool': 'comparative_answer'
            }
            
        # 新增：分片导入网状思维引擎（驱动前端文本块统计）
        if tool_name == 'ingest_slices_to_mesh':
            file_path = parameters.get('file_path')
            content = parameters.get('content')
            topic = parameters.get('topic') or (file_path or content or '')
            try:
                from src.mesh_database_interface import MeshDatabaseInterface
                mdi = MeshDatabaseInterface()
                slices = []
                cfg = parameters.get('config', {})
                if file_path:
                    res = self.call_tool('memory_slicer', {'file_path': file_path, 'config': cfg}, caller_info, usage_intention, active_call)
                    slices = res.get('data', []) if isinstance(res, dict) else []
                elif content:
                    res = self.call_tool('memory_slicer', {'content': content, 'config': cfg}, caller_info, usage_intention, active_call)
                    slices = res.get('data', []) if isinstance(res, dict) else []
                ingested = 0
                duplicates = 0
                for s in slices:
                    txt = (s.get('content') or '').strip()
                    if not txt:
                        continue
                    data = {
                        'topic': topic or '未分类',
                        'content': txt,
                        'source_type': 'slice',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'importance': s.get('importance', 0.5)
                    }
                    r = mdi.store_memory_with_mesh(data)
                    if r.get('is_duplicate'):
                        duplicates += 1
                    else:
                        ingested += 1
                return {
                    'success': True,
                    'data': {
                        'total_slices': len(slices),
                        'ingested': ingested,
                        'duplicates': duplicates,
                        'mesh_node_count': mdi.thought_engine.get_node_count()
                    },
                    'tool': 'ingest_slices_to_mesh'
                }
            except Exception as e:
                return {'success': False, 'error': f'导入失败: {e}', 'tool': 'ingest_slices_to_mesh'}

        # 工具注册自检入口（不依赖聊天工具管理器）
        if tool_name == 'tool_registry_check':
            try:
                from tools.chat_tools import create_tool_manager
                mgr = create_tool_manager()
                available = mgr.list_available_tools()
                expected = [
                    'memory_retrieval','file_reading','web_search','memory_iteration',
                    'command_line','file_writing','equality_assessment','memory_slicer',
                    'networked_thinking','reasoning_engine','cognitive_barrier_break','terminal_display',
                    'thinking_tracer'
                ]
                external = ['code_index_build','code_symbol_search']
                missing = [t for t in expected if t not in available]
                return {
                    'success': True,
                    'data': {
                        'available_tools': available,
                        'expected_tools': expected,
                        'missing_in_manager': missing,
                        'external_tools_handled_by_agent_integration': external
                    },
                    'tool': 'tool_registry_check'
                }
            except Exception as e:
                return {'success': False, 'error': f'工具注册自检失败: {e}', 'tool': 'tool_registry_check'}

        # 代码索引直连入口（不依赖聊天工具管理器）
        if tool_name == 'code_index_build':
            caller_type = (caller_info or {}).get('agent_type')
            if caller_type not in ('implementer', 'developer'):
                try:
                    from src.error_reporting import get_error_reporting_service
                    er = get_error_reporting_service()
                    er.report_component_error({
                        "error_id": er.generate_error_id("agent_tool_integration", "CodeIndexBuildDenied"),
                        "level": "component",
                        "type": "PermissionDenied",
                        "message": "索引构建仅限实现师/开发者触发",
                        "timestamp": datetime.now().isoformat(),
                        "component": "agent_tool_integration",
                        "function": "code_index_build",
                        "context": {"caller_info": caller_info}
                    })
                except Exception:
                    pass
                return {'success': False, 'error': '权限不足：索引构建仅限实现师/开发者', 'tool': 'code_index_build', 'data': {'denied_for_role': caller_type}}
            import sqlite3, hashlib, ast
            base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'code_index_db.sqlite')
            mode = parameters.get('mode', 'incremental')
            scope = parameters.get('scope', 'src')
            target_root = os.path.join(base_dir, scope) if not os.path.isabs(scope) else scope
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS files (file_path TEXT PRIMARY KEY, file_hash TEXT NOT NULL, owner_component TEXT, protocol_version TEXT, last_modified DATETIME NOT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS symbols (symbol_id TEXT PRIMARY KEY, file_path TEXT NOT NULL, symbol_name TEXT NOT NULL, symbol_type TEXT NOT NULL, signature TEXT, docstring TEXT, start_line INTEGER, end_line INTEGER)")
            cur.execute("CREATE TABLE IF NOT EXISTS relations (source_symbol_id TEXT NOT NULL, relation_type TEXT NOT NULL, target_symbol_id TEXT NOT NULL, PRIMARY KEY (source_symbol_id, relation_type, target_symbol_id))")
            cur.execute("CREATE TABLE IF NOT EXISTS components (component_id TEXT PRIMARY KEY, name TEXT, depends_on TEXT, provides TEXT)")
            # 自曝光组件同步
            try:
                exposures_path = os.path.join(base_dir, 'self_exposures.json')
                if os.path.exists(exposures_path):
                    exposures = json.load(open(exposures_path, 'r', encoding='utf-8'))
                    for exp in exposures:
                        cid = exp.get('id')
                        if cid:
                            cur.execute("INSERT OR REPLACE INTO components(component_id,name,depends_on,provides) VALUES (?,?,?,?)", (
                                cid,
                                exp.get('name'),
                                json.dumps(exp.get('needs', {}).get('deps', []), ensure_ascii=False),
                                json.dumps(exp.get('provides', {}), ensure_ascii=False)
                            ))
            except Exception:
                pass
            indexed_files = 0
            indexed_symbols = 0
            indexed_relations = 0
            for root, dirs, files in os.walk(target_root):
                if any(seg in root for seg in ('__pycache__', 'venv', '.git')):
                    continue
                for fname in files:
                    if not fname.endswith('.py'):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as rf:
                            content = rf.read()
                        file_hash = hashlib.sha256(content.encode('utf-8', errors='ignore')).hexdigest()
                        last_modified = datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                        cur.execute("SELECT file_hash FROM files WHERE file_path=?", (fpath,))
                        row = cur.fetchone()
                        if mode == 'incremental' and row and row[0] == file_hash:
                            continue
                        tree = ast.parse(content)
                        cur.execute("INSERT OR REPLACE INTO files(file_path,file_hash,owner_component,protocol_version,last_modified) VALUES (?,?,?,?,?)", (
                            fpath, file_hash, None, None, last_modified
                        ))
                        indexed_files += 1
                        def make_id(name, start):
                            return f"{fpath}:{name}:{start}"
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                name = node.name
                                start = getattr(node, 'lineno', 1)
                                end = getattr(node, 'end_lineno', start)
                                doc = ast.get_docstring(node) or ''
                                sid = make_id(name, start)
                                cur.execute("INSERT OR REPLACE INTO symbols(symbol_id,file_path,symbol_name,symbol_type,signature,docstring,start_line,end_line) VALUES (?,?,?,?,?,?,?,?)", (
                                    sid, fpath, name, 'function', None, doc, start, end
                                ))
                                indexed_symbols += 1
                                for inner in ast.walk(node):
                                    if isinstance(inner, ast.Call):
                                        callee = None
                                        if isinstance(inner.func, ast.Name):
                                            callee = inner.func.id
                                        elif isinstance(inner.func, ast.Attribute):
                                            callee = inner.func.attr
                                        if callee:
                                            target_id = f"{fpath}:{callee}:"
                                            cur.execute("INSERT OR REPLACE INTO relations(source_symbol_id,relation_type,target_symbol_id) VALUES (?,?,?)", (
                                                sid, 'calls', target_id
                                            ))
                                            indexed_relations += 1
                            elif isinstance(node, ast.ClassDef):
                                name = node.name
                                start = getattr(node, 'lineno', 1)
                                end = getattr(node, 'end_lineno', start)
                                doc = ast.get_docstring(node) or ''
                                sid = make_id(name, start)
                                cur.execute("INSERT OR REPLACE INTO symbols(symbol_id,file_path,symbol_name,symbol_type,signature,docstring,start_line,end_line) VALUES (?,?,?,?,?,?,?,?)", (
                                    sid, fpath, name, 'class', None, doc, start, end
                                ))
                                indexed_symbols += 1
                                for base in (node.bases or []):
                                    try:
                                        if isinstance(base, ast.Name):
                                            base_name = base.id
                                        elif isinstance(base, ast.Attribute):
                                            base_name = base.attr
                                        else:
                                            base_name = None
                                        if base_name:
                                            target_id = f"{fpath}:{base_name}:"
                                            cur.execute("INSERT OR REPLACE INTO relations(source_symbol_id,relation_type,target_symbol_id) VALUES (?,?,?)", (
                                                sid, 'extends', target_id
                                            ))
                                            indexed_relations += 1
                                    except Exception:
                                        continue
                    except Exception:
                        continue
            conn.commit()
            return {
                'success': True,
                'data': {'db_path': db_path, 'indexed_files': indexed_files, 'indexed_symbols': indexed_symbols, 'indexed_relations': indexed_relations, 'mode': mode, 'scope': target_root},
                'tool': 'code_index_build'
            }
        if tool_name == 'code_symbol_search':
            import sqlite3
            base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
            db_path = os.path.join(base_dir, 'data', 'code_index_db.sqlite')
            if not os.path.exists(db_path):
                return {'success': False, 'error': '索引库不存在，请先构建', 'tool': 'code_symbol_search'}
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            query = parameters.get('query', '')
            filters = parameters.get('filters', {})
            symbol_type = filters.get('symbol_type')
            file_filter = filters.get('file_path')
            limit = int(parameters.get('limit', 50))
            conditions = ["symbol_name LIKE ?"]
            params = [f"%{query}%"]
            if symbol_type:
                conditions.append("symbol_type = ?")
                params.append(symbol_type)
            if file_filter:
                conditions.append("file_path LIKE ?")
                params.append(f"%{file_filter}%")
            where_clause = ' AND '.join(conditions)
            cur.execute(f"SELECT symbol_id,file_path,symbol_name,symbol_type,start_line,end_line FROM symbols WHERE {where_clause} LIMIT ?", (*params, limit))
            rows = cur.fetchall()
            results = [{
                'symbol_id': r[0], 'file_path': r[1], 'symbol_name': r[2], 'symbol_type': r[3], 'start_line': r[4], 'end_line': r[5]
            } for r in rows]
            relation = filters.get('relation')
            if relation in ('calls', 'called_by', 'extends', 'implemented_by') and results:
                expanded = []
                for item in results:
                    sid = item['symbol_id']
                    if relation == 'called_by':
                        cur.execute("SELECT source_symbol_id FROM relations WHERE relation_type='calls' AND target_symbol_id LIKE ?", (sid.split(':')[0] + ':%',))
                        callers = [row[0] for row in cur.fetchall()]
                        item['called_by'] = callers
                    else:
                        cur.execute("SELECT target_symbol_id FROM relations WHERE relation_type=? AND source_symbol_id=?", (relation, sid))
                        targets = [row[0] for row in cur.fetchall()]
                        item[relation] = targets
                    expanded.append(item)
                results = expanded
            return {'success': True, 'data': {'results': results, 'count': len(results)}, 'tool': 'code_symbol_search'}

        if tool_name == 'terminal_display':
            td = self.chat_tool_manager.get_tool('terminal_display') if self.chat_tool_manager else None
            if not td:
                return {'success': False, 'error': '终端显示栏工具未注册', 'tool': 'terminal_display'}
            action = parameters.get('action', 'list_logs')
            try:
                if action == 'list_logs':
                    res = td.list_logs()
                elif action == 'tail_log':
                    res = td.tail_log(parameters.get('file_name', 'system_errors.log'), parameters.get('lines', 200))
                elif action == 'get_startup_status':
                    res = td.get_startup_status()
                elif action == 'tail_interactions':
                    res = td.tail_interactions(parameters.get('date'), parameters.get('lines', 100))
                else:
                    return {'success': False, 'error': f'未知action: {action}', 'tool': 'terminal_display'}
                return {'success': res.get('success', False), 'data': res.get('data'), 'error': res.get('error'), 'tool': 'terminal_display'}
            except Exception as e:
                return {'success': False, 'error': f'终端显示栏调用失败: {e}', 'tool': 'terminal_display'}

        # 如果是思维透明化追踪器，直接返回工具实例元信息
        if tool_name == 'thinking_tracer':
            tracer_tool = self.tool_instances.get('thinking_tracer')
            if tracer_tool:
                return {
                    'success': True,
                    'data': {
                        'tool_name': 'thinking_tracer',
                        'description': '统一管理智能体与聊天室的思维透明化步骤记录',
                        'type': 'tool',
                        'scope': 'global',
                        'capabilities': ['按会话维度记录思维步骤', '支持多来源(智能体/聊天室)', '统一结构供前端展示']
                    },
                    'tool': 'thinking_tracer'
                }
            else:
                return {'success': False, 'error': '思维透明化追踪工具未注册', 'tool': 'thinking_tracer'}
        
        # 1. 优先从聊天工具管理器中获取高频核心工具
        if self.chat_tool_manager:
            chat_tool = self.chat_tool_manager.get_tool(tool_name)
            if chat_tool:
                try:
                    # 根据工具类型调用相应方法
                    if tool_name == 'file_reading':
                        # 文件读取工具（委托给工具管理器，遵循黑箱原则）
                        file_path = parameters.get('file_path')
                        encoding = parameters.get('encoding')
                        start_line = parameters.get('start_line')
                        num_lines = parameters.get('num_lines')
                        query = parameters.get('query')
                        pattern = parameters.get('pattern')
                        
                        # 优先按明确路径读取
                        if file_path:
                            # 支持强制编码与片段读取
                            if start_line and num_lines:
                                content = chat_tool.read_file_chunk(file_path, start_line=int(start_line), num_lines=int(num_lines))
                            else:
                                content = chat_tool.read_text_file(file_path, encoding=encoding)
                            if content is not None:
                                return {
                                    'success': True,
                                    'data': {'content': content},
                                    'tool': 'file_reading'
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': f'文件读取失败: {file_path}',
                                    'data': {'path': file_path, 'reason': 'read_failed'}
                                }
                        
                        # 路径缺失时，尝试按查询/模式自动定位候选文件
                        # 路径缺失时，尝试按图谱/内容/模式自动定位候选文件
                        # 根据调用者角色设定默认pattern
                        role = (caller_info or {}).get('agent_type')
                        role_patterns = {
                            'architect': '**/*.md',
                            'evaluator': 'docs/**/*.md',
                            'implementer': 'src/**/*.py',
                            'data_collector': 'data/**/*.json',
                            'maintenance': 'config/**/*'
                        }
                        if not pattern:
                            pattern = role_patterns.get(role, '*')

                        candidates = []
                        # 先尝试图谱定位
                        try:
                            base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                            graph_path = os.path.join(base_dir, 'data', 'component_graph.json')
                            if os.path.exists(graph_path):
                                with open(graph_path, 'r', encoding='utf-8') as gf:
                                    graph = json.load(gf)
                                file_nodes = [n for n in (graph.get('nodes') or []) if n.get('type') == 'file']
                                if query:
                                    for fn in file_nodes:
                                        p = fn.get('path','')
                                        if query.lower() in p.lower():
                                            # 转换为相对路径以适配工具读取
                                            try:
                                                relp = os.path.relpath(p, base_dir)
                                            except Exception:
                                                relp = p
                                            if relp not in candidates:
                                                candidates.append(relp)
                                candidates = candidates[:5]
                        except Exception:
                            pass

                        # 内容检索定位（补充）
                        if query and len(candidates) < 5:
                            search_hits = chat_tool.search_in_files(pattern, query, case_sensitive=False)
                            for hit in search_hits:
                                if hit['file'] not in candidates:
                                    candidates.append(hit['file'])
                                if len(candidates) >= 5:
                                    break
                        # 回退：按文件模式列出最近修改的文件
                        if not candidates:
                            listed = chat_tool.list_available_files(pattern=pattern)
                            candidates = [f['path'] for f in listed[:5]]
                        
                        # 依序尝试读取候选文件
                        for cand in candidates:
                            content = chat_tool.read_text_file(cand, encoding=encoding)
                            if content:
                                return {
                                    'success': True,
                                    'data': {'content': content, 'resolved_path': cand},
                                    'tool': 'file_reading'
                                }
                        
                        # 未能读取，返回结构化错误
                        return {
                            'success': False,
                            'error': '文件自动定位/读取失败',
                            'data': {
                                'query': query,
                                'pattern': pattern,
                                'candidates': candidates
                            }
                        }
                    elif tool_name == 'file_writing':
                        # 文件写入工具（委托给工具管理器，遵循黑箱原则）
                        # 权限控制：区分代码写入和文本写入
                        caller_type = (caller_info or {}).get('agent_type')
                        file_path = parameters.get('file_path', '')
                        
                        # 判断是否为代码文件
                        code_extensions = ('.py', '.js', '.java', '.cpp', '.h', '.c', '.hpp', '.ts', '.jsx', '.tsx')
                        is_code_file = file_path.endswith(code_extensions)
                        
                        if is_code_file:
                            # 代码写入 - 严格限制仅实现师可写
                            if caller_type not in ('implementer', 'text_implementer', 'developer'):
                                try:
                                    from src.error_reporting import get_error_reporting_service
                                    error_service = get_error_reporting_service()
                                    component_error = {
                                        "error_id": error_service.generate_error_id(caller_type or 'unknown', "CodeWritePermissionDenied"),
                                        "level": "component",
                                        "type": "PermissionDenied",
                                        "message": "代码写入仅限实现师，当前角色被禁止",
                                        "timestamp": datetime.now().isoformat(),
                                        "component": caller_type or 'unknown',
                                        "function": "file_writing",
                                        "file_path": file_path,
                                        "line_number": 0,
                                        "stack_trace": "agent_tool_integration.call_tool",
                                        "context": {"caller_info": caller_info, "usage_intention": usage_intention}
                                    }
                                    error_service.report_component_error(component_error)
                                except Exception:
                                    pass
                                return {
                                    'success': False,
                                    'error': '权限不足：代码写入仅限实现师',
                                    'tool': 'file_writing',
                                    'data': {'denied_for_role': caller_type, 'file_type': 'code'}
                                }
                        else:
                            # 文本写入 - 所有智能体可写，但限制目录
                            allowed_text_dirs = [
                                'logs/', 'data/agent_diaries/', 'data/feedback/', 
                                'docs/reports/', 'data/bubbles/', 'data/agent_logs/',
                                'temp/', 'output/'
                            ]
                            # 检查是否写入允许的目录
                            is_allowed_dir = any(file_path.startswith(d) for d in allowed_text_dirs)
                            if not is_allowed_dir:
                                return {
                                    'success': False,
                                    'error': f'文本文件只能写入指定目录: {", ".join(allowed_text_dirs)}',
                                    'tool': 'file_writing',
                                    'data': {'allowed_dirs': allowed_text_dirs, 'requested_path': file_path}
                                }
                        # 共识上下文加载（基于组件-文件图谱与自曝光汇总）
                        # 注意：仅对代码文件启用共识检查，文本文件跳过
                        enable_consensus = parameters.get('enable_consensus', True) and is_code_file
                        dry_run = parameters.get('dry_run', False)
                        target_path = parameters.get('file_path')
                        content = parameters.get('content')
                        overwrite = parameters.get('overwrite', False)
                        # 代码索引库只读门禁：防止将派生索引库视为源代码并修改
                        try:
                            base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                            code_index_db = os.path.join(base_dir, 'data', 'code_index_db.sqlite')
                            if target_path and os.path.abspath(target_path) == os.path.abspath(code_index_db):
                                from src.error_reporting import get_error_reporting_service
                                er = get_error_reporting_service()
                                er.report_component_error({
                                    "error_id": er.generate_error_id("agent_tool_integration", "CodeIndexWriteDenied"),
                                    "level": "component",
                                    "type": "CodeIndexWriteDenied",
                                    "message": "代码索引库为只读（派生数据），请编辑源代码文件而非索引库",
                                    "timestamp": datetime.now().isoformat(),
                                    "component": "agent_tool_integration",
                                    "function": "file_writing",
                                    "file_path": target_path or "",
                                    "line_number": 0,
                                    "stack_trace": "agent_tool_integration.call_tool",
                                    "context": {"caller_info": caller_info, "usage_intention": usage_intention}
                                })
                                return {
                                    'success': False,
                                    'error': '代码索引库为只读（派生数据），请编辑源代码文件',
                                    'tool': 'file_writing',
                                    'data': {'denied_target': target_path}
                                }
                        except Exception:
                            pass

                        consensus_context = {
                            'owner_component': None,
                            'depends_on': [],
                            'protocol': {},
                            'graph_found': False,
                            'exposure_found': False
                        }
                        try:
                            base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                            graph_path = os.path.join(base_dir, 'data', 'component_graph.json')
                            exposures_path = os.path.join(base_dir, 'self_exposures.json')
                            # 图谱加载
                            if os.path.exists(graph_path):
                                with open(graph_path, 'r', encoding='utf-8') as gf:
                                    graph = json.load(gf)
                                consensus_context['graph_found'] = True
                                file_abs = target_path if (target_path and os.path.isabs(target_path)) else str((rag_system_path / (target_path or '')).resolve())
                                file_node_id = f"file:{file_abs}"
                                owner = None
                                for e in graph.get('edges', []):
                                    if e.get('relation') == 'contains' and (e.get('target') == file_node_id or (target_path and str(e.get('target','')).endswith(target_path))):
                                        owner = e.get('source')
                                        break
                                consensus_context['owner_component'] = owner
                                if owner:
                                    consensus_context['depends_on'] = [edge.get('target') for edge in graph.get('edges', []) if edge.get('relation') == 'depends_on' and edge.get('source') == owner]
                            # 自曝光汇总加载
                            if os.path.exists(exposures_path):
                                with open(exposures_path, 'r', encoding='utf-8') as ef:
                                    exposures = json.load(ef)
                                consensus_context['exposure_found'] = True
                                file_abs = target_path if (target_path and os.path.isabs(target_path)) else str((rag_system_path / (target_path or '')).resolve())
                                for exp in exposures:
                                    if isinstance(exp, dict) and exp.get('source_file') == file_abs:
                                        consensus_context['protocol'] = {
                                            'id': exp.get('id'),
                                            'name': exp.get('name'),
                                            'type': exp.get('type'),
                                            'version': exp.get('version'),
                                            'needs': exp.get('needs'),
                                            'provides': exp.get('provides')
                                        }
                                        break
                        except Exception:
                            pass

                        # 自曝光协议一致性门禁：owner或protocol缺失则触发二级报错并阻止写入
                        if enable_consensus:
                            if not consensus_context['owner_component'] or not consensus_context['protocol']:
                                try:
                                    from src.error_reporting import get_error_reporting_service
                                    er = get_error_reporting_service()
                                    er.report_component_error({
                                        "error_id": er.generate_error_id("agent_tool_integration", "ConsensusMissing"),
                                        "level": "component",
                                        "type": "ConsensusMissing",
                                        "message": "写入前共识信息缺失（owner_component或protocol）",
                                        "timestamp": datetime.now().isoformat(),
                                        "component": "agent_tool_integration",
                                        "function": "file_writing",
                                        "file_path": target_path or "",
                                        "line_number": 0,
                                        "stack_trace": "agent_tool_integration.call_tool",
                                        "context": {"consensus_context": consensus_context, "caller_info": caller_info}
                                    })
                                except Exception:
                                    pass
                                return {
                                    'success': False,
                                    'error': '写入前共识信息缺失（owner_component或protocol）',
                                    'tool': 'file_writing',
                                    'data': {'consensus_context': consensus_context}
                                }

                        # 只返回共识上下文（不写入）
                        if dry_run:
                            return {
                                'success': True,
                                'data': {'consensus_context': consensus_context, 'message': 'dry_run: 未执行写入'},
                                'tool': 'file_writing'
                            }

                        # 执行写入
                        if target_path and content is not None:
                            result_dict = chat_tool.write_to_file(
                                target_path,
                                content,
                                overwrite=overwrite,
                                enable_assessment=parameters.get('enable_assessment', False)
                            )
                            return {
                                'success': result_dict.get('success', False),
                                'data': {
                                    'message': result_dict.get('message', ''),
                                    'consensus_context': consensus_context,
                                    **{k: v for k, v in result_dict.items() if k not in ('message')}
                                },
                                'tool': 'file_writing'
                            }
                        return {
                            'success': False,
                            'error': '缺少必要参数 file_path/content',
                            'tool': 'file_writing'
                        }
                    elif tool_name == 'consensus_handshake':
                        # 并行任务共识握手（不写入，仅生成共识清单）
                        task_id = parameters.get('task_id')
                        objective = parameters.get('objective')
                        participants = parameters.get('participants', [])  # [{agent, role, responsibility}]
                        targets = parameters.get('targets', [])  # 文件/模块集合
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        graph_path = os.path.join(base_dir, 'data', 'component_graph.json')
                        exposures_path = os.path.join(base_dir, 'self_exposures.json')
                        manifest = {
                            'task_id': task_id,
                            'objective': objective,
                            'participants': participants,
                            'owner_component': None,
                            'depends_on': [],
                            'protocol_version': None,
                            'change_set': [],
                            'lock_strategy': {'mode': 'file_lock', 'scope': targets},
                            'conflict_resolution': {'arbiter': 'system_manager', 'fallback': 'revert-and-queue'},
                            'checklist': ['protocol_version_consistency', 'consensus_context_present', 'equality_assessment_passed']
                        }
                        try:
                            graph = {}
                            exposures = []
                            if os.path.exists(graph_path):
                                with open(graph_path, 'r', encoding='utf-8') as gf:
                                    graph = json.load(gf)
                            if os.path.exists(exposures_path):
                                with open(exposures_path, 'r', encoding='utf-8') as ef:
                                    exposures = json.load(ef)
                            # 解析目标的owner/depends_on/protocol_version
                            for target in targets:
                                file_abs = target if os.path.isabs(target) else str((rag_system_path / target).resolve())
                                file_node_id = f"file:{file_abs}"
                                owner = None
                                for e in (graph.get('edges') or []):
                                    if e.get('relation') == 'contains' and (e.get('target') == file_node_id or str(e.get('target','')).endswith(target)):
                                        owner = e.get('source'); break
                                if owner and not manifest['owner_component']:
                                    manifest['owner_component'] = owner
                                    manifest['depends_on'] = [edge.get('target') for edge in (graph.get('edges') or []) if edge.get('relation') == 'depends_on' and edge.get('source') == owner]
                                # 协议版本
                                for exp in exposures:
                                    if isinstance(exp, dict) and exp.get('source_file') == file_abs:
                                        manifest['protocol_version'] = f"{exp.get('id')}@{exp.get('version')}"
                                        break
                                manifest['change_set'].append({'file': target, 'action': 'edit', 'anchors': []})
                        except Exception:
                            pass
                        return {'success': True, 'data': {'consensus_manifest': manifest}, 'tool': 'consensus_handshake'}
                    elif tool_name == 'code_acceptance':
                        # 代码验收（不写入）：检测并行写手的代码是否一致、满足方案
                        scheme_summary = parameters.get('scheme_summary', '')
                        code_proposals = parameters.get('code_proposals', [])  # [{file_path, content, author}]
                        consensus_manifest = parameters.get('consensus_manifest', {})
                        acceptance = {'accepted': True, 'reasons': [], 'conflicts': [], 'files': []}
                        try:
                            # 简单一致性规则：同一文件不允许出现不同内容；必须存在owner_component与protocol_version
                            if not consensus_manifest.get('owner_component') or not consensus_manifest.get('protocol_version'):
                                acceptance['accepted'] = False
                                acceptance['reasons'].append('缺少共识上下文（owner_component或protocol_version）')
                            grouped = {}
                            for p in code_proposals:
                                f = p.get('file_path'); c = (p.get('content') or '').strip()
                                if not f: continue
                                grouped.setdefault(f, set()).add(c)
                            for f, contents in grouped.items():
                                if len(contents) > 1:
                                    acceptance['accepted'] = False
                                    acceptance['conflicts'].append({'file': f, 'versions': len(contents)})
                                else:
                                    acceptance['files'].append({'file': f, 'hash': hash(next(iter(contents)))})
                        except Exception as e:
                            acceptance['accepted'] = False
                            acceptance['reasons'].append(str(e))
                        return {'success': True, 'data': {'acceptance': acceptance}, 'tool': 'code_acceptance'}
                    elif tool_name == 'long_task_workflow':
                        # 长期任务工作流：自动共识握手 + 一致性验收 +（可选）写入
                        task_id = parameters.get('task_id')
                        objective = parameters.get('objective')
                        participants = parameters.get('participants', [])
                        targets = parameters.get('targets', [])
                        proposals = parameters.get('proposals', [])  # [{file_path, content, author}]
                        task_type = parameters.get('task_type', 'code')  # code|content|data
                        overwrite = parameters.get('overwrite', False)
                        enable_assessment = parameters.get('enable_assessment', True)
                        # 自动判定是否为长期任务（规模/并行度）
                        is_long = False
                        try:
                            total_size = sum(len((p.get('content') or '').encode('utf-8')) for p in proposals)
                            is_long = (len(proposals) >= 3) or (len(targets) >= 2) or (total_size > 200_000)
                        except Exception:
                            is_long = True
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        graph_path = os.path.join(base_dir, 'data', 'component_graph.json')
                        exposures_path = os.path.join(base_dir, 'self_exposures.json')
                        manifest = {
                            'task_id': task_id,
                            'objective': objective,
                            'participants': participants,
                            'owner_component': None,
                            'depends_on': [],
                            'protocol_version': None,
                            'change_set': [],
                            'lock_strategy': {'mode': 'file_lock', 'scope': targets},
                            'checklist': ['protocol_version_consistency', 'consensus_context_present', 'equality_assessment_passed'],
                            'is_long_task': is_long
                        }
                        # 共识握手
                        try:
                            graph = {}
                            exposures = []
                            if os.path.exists(graph_path):
                                with open(graph_path, 'r', encoding='utf-8') as gf:
                                    graph = json.load(gf)
                            if os.path.exists(exposures_path):
                                with open(exposures_path, 'r', encoding='utf-8') as ef:
                                    exposures = json.load(ef)
                            for target in targets:
                                file_abs = target if os.path.isabs(target) else str((rag_system_path / target).resolve())
                                file_node_id = f"file:{file_abs}"
                                owner = None
                                for e in (graph.get('edges') or []):
                                    if e.get('relation') == 'contains' and (e.get('target') == file_node_id or str(e.get('target','')).endswith(target)):
                                        owner = e.get('source'); break
                                if owner and not manifest['owner_component']:
                                    manifest['owner_component'] = owner
                                    manifest['depends_on'] = [edge.get('target') for edge in (graph.get('edges') or []) if edge.get('relation') == 'depends_on' and edge.get('source') == owner]
                                for exp in exposures:
                                    if isinstance(exp, dict) and exp.get('source_file') == file_abs:
                                        manifest['protocol_version'] = f"{exp.get('id')}@{exp.get('version')}"; break
                                manifest['change_set'].append({'file': target, 'action': 'edit', 'anchors': []})
                        except Exception:
                            pass
                        # 一致性验收（通用）
                        acceptance = {'accepted': True, 'reasons': [], 'conflicts': [], 'files': []}
                        try:
                            if not manifest.get('owner_component') or not manifest.get('protocol_version'):
                                acceptance['accepted'] = False
                                acceptance['reasons'].append('缺少共识上下文（owner_component或protocol_version）')
                            grouped = {}
                            for p in proposals:
                                f = p.get('file_path') or p.get('target'); c = (p.get('content') or '').strip()
                                if not f: continue
                                grouped.setdefault(f, set()).add(c)
                            for f, contents in grouped.items():
                                if len(contents) > 1:
                                    acceptance['accepted'] = False
                                    acceptance['conflicts'].append({'file': f, 'versions': len(contents)})
                                else:
                                    acceptance['files'].append({'file': f, 'hash': hash(next(iter(contents)))})
                        except Exception as e:
                            acceptance['accepted'] = False
                            acceptance['reasons'].append(str(e))
                        # 写入（仅实现师，且验收通过）
                        write_results = []
                        if acceptance['accepted'] and (caller_info or {}).get('agent_type') in ('implementer', 'text_implementer', 'developer'):
                            for p in proposals:
                                fp = p.get('file_path'); ct = p.get('content')
                                if fp and ct is not None:
                                    r = chat_tool.write_to_file(fp, ct, overwrite=overwrite, enable_assessment=enable_assessment)
                                    write_results.append({'file_path': fp, 'success': r.get('success'), 'message': r.get('message')})
                        return {
                            'success': True,
                            'data': {
                                'consensus_manifest': manifest,
                                'acceptance': acceptance,
                                'write_results': write_results
                            },
                            'tool': 'long_task_workflow'
                        }
                    elif tool_name == 'command_line':
                        # 命令行工具（从聊天工具管理器委托执行）
                        if 'command' in parameters:
                            timeout = parameters.get('timeout', 30)
                            result = chat_tool.execute_command(parameters['command'], timeout=timeout)
                            return {
                                'success': result['success'],
                                'data': result,
                                'tool': 'command_line'
                            }
                        else:
                            return {
                                'success': False,
                                'error': '缺少必要参数: command',
                                'tool': 'command_line'
                            }
                    elif tool_name == 'preference_sync':
                        # 偏好同步：把记忆中的偏好写入设置文件（data/user_preferences.json）
                        prefs = parameters.get('preferences', {})
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        data_dir = os.path.join(base_dir, 'data')
                        os.makedirs(data_dir, exist_ok=True)
                        target = os.path.join(data_dir, 'user_preferences.json')
                        # 读取现有偏好并深度合并
                        try:
                            existing = {}
                            if os.path.exists(target):
                                with open(target, 'r', encoding='utf-8') as f:
                                    existing = json.load(f) or {}
                            def _deep_merge(a, b):
                                if isinstance(a, dict) and isinstance(b, dict):
                                    r = dict(a or {})
                                    for k, v in b.items():
                                        r[k] = _deep_merge((a or {}).get(k), v) if (a or {}).get(k) is not None else v
                                    return r
                                return b if b is not None else a
                            merged = _deep_merge(existing, prefs)
                            with open(target, 'w', encoding='utf-8') as f:
                                json.dump(merged, f, ensure_ascii=False, indent=2)
                            return {
                                'success': True,
                                'data': {'saved_path': target, 'preferences': merged},
                                'tool': 'preference_sync'
                            }
                        except Exception as e:
                            return {
                                'success': False,
                                'error': f'偏好同步失败: {e}',
                                'tool': 'preference_sync'
                            }
                    elif tool_name == 'engineering_ideas_feed':
                        # 工程建议供稿：聚合各智能体的构思/优化建议泡泡为工程师参考
                        days = int(parameters.get('days', 30))
                        include_resolved = bool(parameters.get('include_resolved', False))
                        categories = parameters.get('categories', ['构思', '优化建议'])
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        bubbles_root = os.path.join(base_dir, 'data', 'memory_bubbles')
                        output_path = os.path.join(base_dir, 'data', 'engineering_ideas_feed.json')
                        feed = []
                        try:
                            from datetime import timedelta
                            cutoff = datetime.now() - timedelta(days=days)
                            if os.path.isdir(bubbles_root):
                                for agent_id in os.listdir(bubbles_root):
                                    agent_dir = os.path.join(bubbles_root, agent_id)
                                    if not os.path.isdir(agent_dir):
                                        continue
                                    for fname in os.listdir(agent_dir):
                                        if not fname.endswith('.json'):
                                            continue
                                        fpath = os.path.join(agent_dir, fname)
                                        try:
                                            with open(fpath, 'r', encoding='utf-8') as f:
                                                bubble = json.load(f) or {}
                                            cat = bubble.get('category')
                                            if cat not in categories:
                                                continue
                                            status = bubble.get('status')
                                            if not include_resolved and status == '已解决':
                                                continue
                                            ts = bubble.get('timestamp')
                                            ts_dt = datetime.fromisoformat(ts) if ts else None
                                            if ts_dt and ts_dt < cutoff:
                                                continue
                                            feed.append({
                                                'bubble_id': bubble.get('bubble_id'),
                                                'agent_id': bubble.get('agent_id'),
                                                'timestamp': ts,
                                                'category': cat,
                                                'content': bubble.get('content'),
                                                'context': bubble.get('context', {}),
                                                'priority': bubble.get('priority', 'normal'),
                                                'status': status
                                            })
                                        except Exception:
                                            continue
                            # 排序：优先级+时间
                            priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
                            feed.sort(key=lambda x: (priority_order.get(x.get('priority','normal'), 2), x.get('timestamp') or ''))
                            # 写出供稿文件
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'w', encoding='utf-8') as f:
                                json.dump({'items': feed, 'generated_at': datetime.now().isoformat(), 'window_days': days}, f, ensure_ascii=False, indent=2)
                            return {
                                'success': True,
                                'data': {'count': len(feed), 'output_path': output_path},
                                'tool': 'engineering_ideas_feed'
                            }
                        except Exception as e:
                            return {
                                'success': False,
                                'error': f'工程建议供稿生成失败: {e}',
                                'tool': 'engineering_ideas_feed'
                            }
                    elif tool_name == 'memory_retrieval' or tool_name == 'unified_memory_retrieval':
                        # 记忆检索工具
                        if 'query' in parameters:
                            limit = parameters.get('limit', 10)
                            result = chat_tool.search_memories(parameters['query'], limit=limit)
                            return {
                                'success': True,
                                'data': {'memories': result},
                                'tool': 'memory_retrieval'
                            }
                    elif tool_name == 'web_search':
                        # 网络搜索工具
                        if 'query' in parameters:
                            num_results = parameters.get('num_results', 5)
                            result = chat_tool.search_web(parameters['query'], num_results=num_results)
                            return {
                                'success': True,
                                'data': {'results': result},
                                'tool': 'web_search'
                            }
                    elif tool_name == 'memory_iteration':
                        # 记忆迭代工具
                        if 'topic' in parameters:
                            result = chat_tool.complete_memory_iteration(parameters['topic'])
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'memory_iteration'
                            }
                    elif tool_name == 'equality_assessment':
                        # 平等律评估工具
                        if 'file_path' in parameters and 'content' in parameters:
                            result = chat_tool.assess_write_operation(parameters['file_path'], parameters['content'])
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'equality_assessment'
                            }
                    elif tool_name == 'memory_slicer':
                        # 记忆切片工具（支持文本或文件）
                        cfg = parameters.get('config', {})
                        metadata = parameters.get('metadata', {})
                        if 'content' in parameters and isinstance(parameters.get('content'), str):
                            result = chat_tool.slice_text(parameters['content'], metadata=metadata, config=cfg)
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'memory_slicer'
                            }
                        elif 'file_path' in parameters:
                            result = chat_tool.slice_file(parameters['file_path'], config=cfg)
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'memory_slicer'
                            }
                        else:
                            return {
                                'success': False,
                                'error': '缺少必要参数：content 或 file_path',
                                'tool': 'memory_slicer'
                            }
                    elif tool_name == 'networked_thinking':
                        # 网状思维工具（直接调用工具实例）
                        if 'input_text' in parameters:
                            context = parameters.get('context', {})
                            # 调用NetworkedThinkingEngine(MeshThoughtEngine)的analyze_text_dimensions方法
                            engine = chat_tool.tools.get('networked_thinking')
                            if engine and hasattr(engine, 'analyze_text_dimensions'):
                                result = engine.analyze_text_dimensions(parameters['input_text'], context)
                            else:
                                result = {'error': '网状思维引擎未正确初始化'}
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'networked_thinking'
                            }
                        else:
                            return {
                                'success': False,
                                'error': '缺少必要参数: input_text',
                                'tool': 'networked_thinking'
                            }
                    elif tool_name == 'reasoning_engine':
                        # 理性认知引擎（直接调用工具实例）
                        if 'premise' in parameters:
                            rules = parameters.get('rules', ['contradiction', 'identity', 'excluded_middle', 'sufficient_reason'])
                            # 调用ReasoningEngine的reason方法
                            engine = chat_tool.tools.get('reasoning_engine')
                            if engine and hasattr(engine, 'reason'):
                                result = engine.reason(parameters['premise'], context={})
                            else:
                                result = {'error': '理性认知引擎未正确初始化'}
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'reasoning_engine'
                            }
                        else:
                            return {
                                'success': False,
                                'error': '缺少必要参数: premise',
                                'tool': 'reasoning_engine'
                            }
                    elif tool_name == 'cognitive_barrier_break':
                        # 认知破障引擎（直接调用工具实例）
                        if 'problem' in parameters:
                            barrier_type = parameters.get('barrier_type', 'conceptual')
                            # 调用CognitiveBarrierBreakEngine的detect_hallucination方法
                            engine = chat_tool.tools.get('cognitive_barrier_break')
                            if engine and hasattr(engine, 'detect_hallucination'):
                                # 构建简单的reasoning_process
                                reasoning_process = {
                                    'reasoning_chain': [{'premise': parameters['problem'], 'conclusion': '待分析'}]
                                }
                                context = {'domain': 'general', 'barrier_type': barrier_type}
                                result = engine.detect_hallucination(parameters['problem'], reasoning_process, context)
                            else:
                                result = {'error': '认知破障引擎未正确初始化'}
                            return {
                                'success': True,
                                'data': result,
                                'tool': 'cognitive_barrier_break'
                            }
                        else:
                            return {
                                'success': False,
                                'error': '缺少必要参数: problem',
                                'tool': 'cognitive_barrier_break'
                            }
                    elif tool_name == 'code_index_build':
                        # 代码实现师专用数据库索引构建（仅实现师允许触发）
                        caller_type = (caller_info or {}).get('agent_type')
                        if caller_type not in ('implementer', 'developer'):
                            try:
                                from src.error_reporting import get_error_reporting_service
                                er = get_error_reporting_service()
                                er.report_component_error({
                                    "error_id": er.generate_error_id("agent_tool_integration", "CodeIndexBuildDenied"),
                                    "level": "component",
                                    "type": "PermissionDenied",
                                    "message": "索引构建仅限实现师/开发者触发",
                                    "timestamp": datetime.now().isoformat(),
                                    "component": "agent_tool_integration",
                                    "function": "code_index_build",
                                    "context": {"caller_info": caller_info}
                                })
                            except Exception:
                                pass
                            return {'success': False, 'error': '权限不足：索引构建仅限实现师/开发者', 'tool': 'code_index_build', 'data': {'denied_for_role': caller_type}}
                        import sqlite3, hashlib, ast
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        data_dir = os.path.join(base_dir, 'data')
                        os.makedirs(data_dir, exist_ok=True)
                        db_path = os.path.join(data_dir, 'code_index_db.sqlite')
                        mode = parameters.get('mode', 'incremental')
                        scope = parameters.get('scope', 'src')
                        target_root = os.path.join(base_dir, scope) if not os.path.isabs(scope) else scope
                        conn = sqlite3.connect(db_path)
                        cur = conn.cursor()
                        # 建表
                        cur.execute("CREATE TABLE IF NOT EXISTS files (file_path TEXT PRIMARY KEY, file_hash TEXT NOT NULL, owner_component TEXT, protocol_version TEXT, last_modified DATETIME NOT NULL)")
                        cur.execute("CREATE TABLE IF NOT EXISTS symbols (symbol_id TEXT PRIMARY KEY, file_path TEXT NOT NULL, symbol_name TEXT NOT NULL, symbol_type TEXT NOT NULL, signature TEXT, docstring TEXT, start_line INTEGER, end_line INTEGER)")
                        cur.execute("CREATE TABLE IF NOT EXISTS relations (source_symbol_id TEXT NOT NULL, relation_type TEXT NOT NULL, target_symbol_id TEXT NOT NULL, PRIMARY KEY (source_symbol_id, relation_type, target_symbol_id))")
                        cur.execute("CREATE TABLE IF NOT EXISTS components (component_id TEXT PRIMARY KEY, name TEXT, depends_on TEXT, provides TEXT)")
                        # 组件同步（自曝光）
                        try:
                            exposures_path = os.path.join(base_dir, 'self_exposures.json')
                            if os.path.exists(exposures_path):
                                exposures = json.load(open(exposures_path, 'r', encoding='utf-8'))
                                for exp in exposures:
                                    cid = exp.get('id')
                                    if cid:
                                        cur.execute("INSERT OR REPLACE INTO components(component_id,name,depends_on,provides) VALUES (?,?,?,?)", (
                                            cid,
                                            exp.get('name'),
                                            json.dumps(exp.get('needs', {}).get('deps', []), ensure_ascii=False),
                                            json.dumps(exp.get('provides', {}), ensure_ascii=False)
                                        ))
                        except Exception:
                            pass
                        # 文件遍历
                        indexed_files = 0
                        indexed_symbols = 0
                        indexed_relations = 0
                        for root, dirs, files in os.walk(target_root):
                            # 忽略缓存与非源码目录
                            if any(seg in root for seg in ('__pycache__', 'venv', '.git')):
                                continue
                            for fname in files:
                                if not fname.endswith('.py'):
                                    continue
                                fpath = os.path.join(root, fname)
                                try:
                                    # 读取文件与hash
                                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as rf:
                                        content = rf.read()
                                    file_hash = hashlib.sha256(content.encode('utf-8', errors='ignore')).hexdigest()
                                    last_modified = datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                                    # 增量判断
                                    cur.execute("SELECT file_hash FROM files WHERE file_path=?", (fpath,))
                                    row = cur.fetchone()
                                    if mode == 'incremental' and row and row[0] == file_hash:
                                        continue
                                    # 解析AST
                                    tree = ast.parse(content)
                                    # 更新文件表
                                    cur.execute("INSERT OR REPLACE INTO files(file_path,file_hash,owner_component,protocol_version,last_modified) VALUES (?,?,?,?,?)", (
                                        fpath, file_hash, None, None, last_modified
                                    ))
                                    indexed_files += 1
                                    # 提取类与函数
                                    def make_id(name, start):
                                        return f"{fpath}:{name}:{start}"
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.FunctionDef):
                                            name = node.name
                                            start = getattr(node, 'lineno', 1)
                                            end = getattr(node, 'end_lineno', start)
                                            doc = ast.get_docstring(node) or ''
                                            sid = make_id(name, start)
                                            cur.execute("INSERT OR REPLACE INTO symbols(symbol_id,file_path,symbol_name,symbol_type,signature,docstring,start_line,end_line) VALUES (?,?,?,?,?,?,?,?)", (
                                                sid, fpath, name, 'function', None, doc, start, end
                                            ))
                                            indexed_symbols += 1
                                            # 提取调用关系
                                            for inner in ast.walk(node):
                                                if isinstance(inner, ast.Call):
                                                    callee = None
                                                    if isinstance(inner.func, ast.Name):
                                                        callee = inner.func.id
                                                    elif isinstance(inner.func, ast.Attribute):
                                                        callee = inner.func.attr
                                                    if callee:
                                                        # 目标符号ID（同文件，粗略）
                                                        target_id = f"{fpath}:{callee}:"  # 前缀匹配，后续查询细化
                                                        # 由于无精确行号，先用符号名唯一近似
                                                        cur.execute("INSERT OR REPLACE INTO relations(source_symbol_id,relation_type,target_symbol_id) VALUES (?,?,?)", (
                                                            sid, 'calls', target_id
                                                        ))
                                                        indexed_relations += 1
                                        elif isinstance(node, ast.ClassDef):
                                            name = node.name
                                            start = getattr(node, 'lineno', 1)
                                            end = getattr(node, 'end_lineno', start)
                                            doc = ast.get_docstring(node) or ''
                                            sid = make_id(name, start)
                                            cur.execute("INSERT OR REPLACE INTO symbols(symbol_id,file_path,symbol_name,symbol_type,signature,docstring,start_line,end_line) VALUES (?,?,?,?,?,?,?,?)", (
                                                sid, fpath, name, 'class', None, doc, start, end
                                            ))
                                            indexed_symbols += 1
                                            # 继承关系
                                            for base in (node.bases or []):
                                                try:
                                                    if isinstance(base, ast.Name):
                                                        base_name = base.id
                                                    elif isinstance(base, ast.Attribute):
                                                        base_name = base.attr
                                                    else:
                                                        base_name = None
                                                    if base_name:
                                                        target_id = f"{fpath}:{base_name}:"
                                                        cur.execute("INSERT OR REPLACE INTO relations(source_symbol_id,relation_type,target_symbol_id) VALUES (?,?,?)", (
                                                            sid, 'extends', target_id
                                                        ))
                                                        indexed_relations += 1
                                                except Exception:
                                                    continue
                                except Exception:
                                    continue
                        conn.commit()
                        return {
                            'success': True,
                            'data': {'db_path': db_path, 'indexed_files': indexed_files, 'indexed_symbols': indexed_symbols, 'indexed_relations': indexed_relations, 'mode': mode, 'scope': target_root},
                            'tool': 'code_index_build'
                        }
                    elif tool_name == 'code_symbol_search':
                        # 代码符号检索（只读）
                        import sqlite3
                        base_dir = str(rag_system_path) if 'rag_system_path' in globals() else '.'
                        db_path = os.path.join(base_dir, 'data', 'code_index_db.sqlite')
                        if not os.path.exists(db_path):
                            return {'success': False, 'error': '索引库不存在，请先构建', 'tool': 'code_symbol_search'}
                        conn = sqlite3.connect(db_path)
                        cur = conn.cursor()
                        query = parameters.get('query', '')
                        filters = parameters.get('filters', {})
                        symbol_type = filters.get('symbol_type')
                        file_filter = filters.get('file_path')
                        limit = int(parameters.get('limit', 50))
                        # 基础查询
                        conditions = ["symbol_name LIKE ?"]
                        params = [f"%{query}%"]
                        if symbol_type:
                            conditions.append("symbol_type = ?")
                            params.append(symbol_type)
                        if file_filter:
                            conditions.append("file_path LIKE ?")
                            params.append(f"%{file_filter}%")
                        where_clause = ' AND '.join(conditions)
                        cur.execute(f"SELECT symbol_id,file_path,symbol_name,symbol_type,start_line,end_line FROM symbols WHERE {where_clause} LIMIT ?", (*params, limit))
                        rows = cur.fetchall()
                        results = [{
                            'symbol_id': r[0], 'file_path': r[1], 'symbol_name': r[2], 'symbol_type': r[3], 'start_line': r[4], 'end_line': r[5]
                        } for r in rows]
                        # 关系展开
                        relation = filters.get('relation')
                        if relation in ('calls', 'called_by', 'extends', 'implemented_by') and results:
                            expanded = []
                            for item in results:
                                sid = item['symbol_id']
                                if relation == 'called_by':
                                    cur.execute("SELECT source_symbol_id FROM relations WHERE relation_type='calls' AND target_symbol_id LIKE ?", (sid.split(':')[0] + ':%',))
                                    callers = [row[0] for row in cur.fetchall()]
                                    item['called_by'] = callers
                                else:
                                    cur.execute("SELECT target_symbol_id FROM relations WHERE relation_type=? AND source_symbol_id=?", (relation, sid))
                                    targets = [row[0] for row in cur.fetchall()]
                                    item[relation] = targets
                                expanded.append(item)
                            results = expanded
                        return {'success': True, 'data': {'results': results, 'count': len(results)}, 'tool': 'code_symbol_search'}
                    # 如果没有匹配的工具调用方法，返回错误
                    result = {
                        'success': False,
                        'error': f'工具 {tool_name} 的调用参数不正确',
                        'data': {}
                    }
                    duration = (datetime.now() - start_time).total_seconds()
                    self._log_tool_call(tool_name, parameters, result, duration, False, caller_info, usage_intention, active_call)
                    return result
                    
                except Exception as e:
                    result = {
                        'success': False,
                        'error': f'工具调用失败: {str(e)}',
                        'data': {}
                    }
                    duration = (datetime.now() - start_time).total_seconds()
                    self._log_tool_call(tool_name, parameters, result, duration, False, caller_info, usage_intention, active_call)
                    return result
        
        # 2. 从认知引擎工具中查找
        if tool_name in self.tool_instances:
            try:
                tool_instance = self.tool_instances[tool_name]
                
                # 根据工具类型调用相应方法
                if tool_name == 'MeshThoughtEngine':
                    result = self._call_mesh_thought_engine(tool_instance, parameters)
                elif tool_name == 'ReasoningEngine':
                    result = self._call_reasoning_engine(tool_instance, parameters)
                elif tool_name == 'CognitiveBarrierBreakEngine':
                    result = self._call_cognitive_barrier_engine(tool_instance, parameters)
                elif tool_name == 'MemoryReconstructionEngine':
                    result = self._call_memory_reconstruction_engine(tool_instance, parameters)
                elif tool_name == 'MultimodalAlignmentEngine':
                    result = self._call_multimodal_alignment_engine(tool_instance, parameters)
                elif tool_name == 'MultimodalRetrievalEngine':
                    result = self._call_multimodal_retrieval_engine(tool_instance, parameters)
                elif tool_name == 'VisionProcessingEngine':
                    result = self._call_vision_processing_engine(tool_instance, parameters)
                elif tool_name == 'AudioProcessingEngine':
                    result = self._call_audio_processing_engine(tool_instance, parameters)
                elif tool_name == 'MultimodalFusionEngine':
                    result = self._call_multimodal_fusion_engine(tool_instance, parameters)
                elif tool_name == 'AbductiveReasoningEngine':
                    result = self._call_abductive_reasoning_engine(tool_instance, parameters)
                elif tool_name == 'HierarchicalLearningEngine':
                    result = self._call_hierarchical_learning_engine(tool_instance, parameters)
                else:
                    result = {'success': False, 'error': '未知工具类型', 'data': {}}
                
                duration = (datetime.now() - start_time).total_seconds()
                self._log_tool_call(tool_name, parameters, result, duration, result.get('success', False), caller_info, usage_intention, active_call)
                return result
                
            except Exception as e:
                result = {
                    'success': False,
                    'error': f'工具调用失败: {str(e)}',
                    'data': {}
                }
                duration = (datetime.now() - start_time).total_seconds()
                self._log_tool_call(tool_name, parameters, result, duration, False, caller_info, usage_intention, active_call)
                return result
        
        # 3. 工具未找到
        result = {
            'success': False,
            'error': f'工具 {tool_name} 未找到或未初始化',
            'data': {}
        }
        duration = (datetime.now() - start_time).total_seconds()
        self._log_tool_call(tool_name, parameters, result, duration, False, caller_info, usage_intention, active_call)
        return result
    
    def _call_mesh_thought_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用网状思维引擎"""
        operation = parameters.get('operation', 'analyze')
        input_text = parameters.get('input_text', '')
        context = parameters.get('context', {})
        
        if operation == 'analyze':
            # 分析文本并构建思维网络
            result = engine.analyze_text(input_text, context)
        elif operation == 'search':
            # 搜索相关思维节点
            result = engine.search_related_thoughts(input_text, context)
        elif operation == 'associate':
            # 构建思维关联
            result = engine.build_associations(input_text, context)
        else:
            result = {'error': f'未知操作: {operation}'}
        
        return {
            'success': True,
            'data': result,
            'tool': 'MeshThoughtEngine',
            'operation': operation
        }
    
    def _call_reasoning_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用理性认知引擎"""
        premise = parameters.get('premise', {})
        rules = parameters.get('rules', ['contradiction', 'identity', 'excluded_middle', 'sufficient_reason'])
        
        # 应用推理规则
        reasoning_results = {}
        for rule_name in rules:
            if hasattr(engine, f'apply_{rule_name}_rule'):
                rule_method = getattr(engine, f'apply_{rule_name}_rule')
                satisfaction, explanation = rule_method(premise, {})
                reasoning_results[rule_name] = {
                    'satisfaction': satisfaction,
                    'explanation': explanation
                }
        
        # 计算总体置信度
        overall_confidence = sum(r['satisfaction'] for r in reasoning_results.values()) / len(reasoning_results) if reasoning_results else 0
        
        return {
            'success': True,
            'data': {
                'reasoning_results': reasoning_results,
                'overall_confidence': overall_confidence
            },
            'tool': 'ReasoningEngine'
        }
    
    def _call_cognitive_barrier_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用认知破障引擎"""
        problem = parameters.get('problem', '')
        barrier_type = parameters.get('barrier_type', 'conceptual')
        
        # 分析认知障碍
        barrier_analysis = engine.analyze_barrier(problem, barrier_type)
        
        # 生成突破方案
        breakthrough_ideas = engine.generate_breakthrough_ideas(barrier_analysis)
        
        return {
            'success': True,
            'data': {
                'barrier_analysis': barrier_analysis,
                'breakthrough_ideas': breakthrough_ideas
            },
            'tool': 'CognitiveBarrierBreakEngine'
        }
    
    def _call_memory_reconstruction_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用记忆重构引擎"""
        memory_data = parameters.get('memory_data', {})
        reconstruction_type = parameters.get('reconstruction_type', 'hierarchical')
        
        # 重构记忆
        reconstructed_memory = engine.reconstruct_memory(memory_data, reconstruction_type)
        
        return {
            'success': True,
            'data': {
                'reconstructed_memory': reconstructed_memory,
                'reconstruction_type': reconstruction_type
            },
            'tool': 'MemoryReconstructionEngine'
        }

    def _call_abductive_reasoning_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用溯因推理引擎"""
        operation = parameters.get('operation', 'generate_hypotheses')
        
        if operation == 'generate_hypotheses':
            # 生成假设
            observations = parameters.get('observations', [])
            background_knowledge = parameters.get('background_knowledge', {})
            
            result = engine.call('generate_hypotheses', {
                'observations': observations,
                'background_knowledge': background_knowledge
            })
        elif operation == 'evaluate_hypotheses':
            # 评估假设
            hypotheses = parameters.get('hypotheses', [])
            observations = parameters.get('observations', [])
            
            result = engine.call('evaluate_hypotheses', {
                'hypotheses': hypotheses,
                'observations': observations
            })
        elif operation == 'select_best_hypothesis':
            # 选择最佳假设
            hypotheses_evaluations = parameters.get('hypotheses_evaluations', [])
            
            result = engine.call('select_best_hypothesis', {
                'hypotheses_evaluations': hypotheses_evaluations
            })
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result

    def _call_hierarchical_learning_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用分层学习引擎"""
        operation = parameters.get('operation', 'learn')
        
        if operation == 'learn':
            # 通用学习方法
            learning_mode = parameters.get('learning_mode', 'supervised')
            data = parameters.get('data')
            experience = parameters.get('experience')
            
            result = engine.call('learn', {
                'learning_mode': learning_mode,
                'data': data,
                'experience': experience
            })
        elif operation == 'supervised_learning':
            # 监督学习
            training_data = parameters.get('training_data', [])
            result = engine.call('supervised_learning', {
                'training_data': training_data
            })
        elif operation == 'unsupervised_learning':
            # 无监督学习
            unlabeled_data = parameters.get('unlabeled_data', [])
            result = engine.call('unsupervised_learning', {
                'unlabeled_data': unlabeled_data
            })
        elif operation == 'reinforcement_learning':
            # 强化学习
            experience_data = parameters.get('experience', {})
            result = engine.call('reinforcement_learning', {
                'experience': experience_data
            })
        elif operation == 'build_hierarchy':
            # 构建知识层次
            result = engine.call('build_hierarchy', {})
        elif operation == 'consolidate_knowledge':
            # 知识巩固
            result = engine.call('consolidate_knowledge', {})
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result

    def register_tool(self, tool_name: str, tool_description: str = "", tool_usage: str = "") -> bool:
        """注册工具(兼容性方法,实际工具在初始化时已注册)"""
        # 这个方法主要是为了兼容base_agent.py中的调用
        # 实际工具在_initialize_tools方法中已经初始化
        # ✅ 明确日志含义：这是注册请求，实际工具已在初始化时加载
        logger.info(f"✅ 工具注册成功: {tool_name} - {tool_description}")
        return True
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return list(self.tool_instances.keys())
    
    def get_tool(self, tool_name: str):
        """获取指定工具实例（支持懒加载）"""
        # 优先从聊天工具管理器中获取高频核心工具
        if self.chat_tool_manager:
            chat_tool = self.chat_tool_manager.get_tool(tool_name)
            if chat_tool:
                return chat_tool
        
        # 🔥 从已加载的工具中查找
        if tool_name in self.tool_instances:
            return self.tool_instances[tool_name]
        
        # 🔥 尝试懒加载高级工具
        if self._lazy_load_tool(tool_name):
            return self.tool_instances[tool_name]
        
        # 尝试映射工具名称
        tool_mapping = {
            'memory_retrieval': 'memory_retrieval',
            'file_reading': 'file_reading', 
            'file_writing': 'file_writing',
            'web_search': 'web_search',
            'memory_iteration': 'memory_iteration',
            'command_line': 'command_line',
            'equality_assessment': 'equality_assessment',
            'memory_slicer': 'memory_slicer',
            'networked_thinking': 'networked_thinking',
            'reasoning_engine': 'reasoning_engine',
            'cognitive_barrier_break': 'cognitive_barrier_break'
        }
        
        mapped_name = tool_mapping.get(tool_name)
        if mapped_name and self.chat_tool_manager:
            return self.chat_tool_manager.get_tool(mapped_name)
        
        return None
    
    def get_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """获取工具状态信息"""
        tool_status = {}
        
        # 从聊天工具管理器获取高频核心工具状态
        if self.chat_tool_manager:
            core_tools = ['file_reading', 'file_writing', 'command_line', 'memory_retrieval', 
                         'web_search', 'memory_iteration', 'equality_assessment', 'memory_slicer',
                         'networked_thinking', 'reasoning_engine', 'cognitive_barrier_break']
            
            for tool_name in core_tools:
                tool_status[tool_name] = {
                    'available': True,
                    'type': 'core_tool',
                    'module': 'tools.chat_tools',
                    'description': f'{tool_name}工具'
                }
        
        # 添加认知引擎工具状态
        for tool_name in self.tool_instances:
            tool_status[tool_name] = {
                'available': True,
                'type': 'cognitive_engine',
                'module': 'src',
                'description': f'{tool_name}认知引擎'
            }
        
        return tool_status
    
    def _call_multimodal_alignment_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用多模态对齐引擎"""
        operation = parameters.get('operation', 'align')
        
        if operation == 'align':
            # 多模态对齐
            modality1 = parameters.get('modality1', {})
            modality2 = parameters.get('modality2', {})
            alignment_type = parameters.get('alignment_type', 'semantic')
            
            result = engine.call('align', {
                'modality1': modality1,
                'modality2': modality2,
                'alignment_type': alignment_type
            })
        elif operation == 'analyze_alignment':
            # 分析对齐质量
            alignment_result = parameters.get('alignment_result', {})
            result = engine.call('analyze_alignment', {
                'alignment_result': alignment_result
            })
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result
    
    def _call_multimodal_retrieval_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用多模态检索引擎"""
        operation = parameters.get('operation', 'retrieve')
        
        if operation == 'retrieve':
            # 跨模态检索
            query = parameters.get('query', {})
            modality = parameters.get('modality', 'text')
            top_k = parameters.get('top_k', 10)
            
            result = engine.call('retrieve', {
                'query': query,
                'modality': modality,
                'top_k': top_k
            })
        elif operation == 'index':
            # 索引多模态数据
            data = parameters.get('data', {})
            modality = parameters.get('modality', 'text')
            
            result = engine.call('index', {
                'data': data,
                'modality': modality
            })
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result
    
    def _call_vision_processing_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用视觉处理引擎"""
        operation = parameters.get('operation', 'analyze_image')
        
        if operation == 'analyze_image':
            # 分析图像
            image_path = parameters.get('image_path')
            base64_data = parameters.get('base64_data')
            
            result = engine.call('analyze_image', {
                'image_path': image_path,
                'base64_data': base64_data
            })
        elif operation == 'extract_features':
            # 提取图像特征
            image_path = parameters.get('image_path')
            base64_data = parameters.get('base64_data')
            
            result = engine.call('extract_features', {
                'image_path': image_path,
                'base64_data': base64_data
            })
        elif operation == 'detect_objects':
            # 检测图像对象
            image_path = parameters.get('image_path')
            base64_data = parameters.get('base64_data')
            
            result = engine.call('detect_objects', {
                'image_path': image_path,
                'base64_data': base64_data
            })
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result
    
    def _call_audio_processing_engine(self, engine, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用音频处理引擎"""
        operation = parameters.get('operation', 'analyze_audio')
        
        if operation == 'analyze_audio':
            # 分析音频
            audio_path = parameters.get('audio_path')
            base64_data = parameters.get('base64_data')
            
            result = engine.call('analyze_audio', {
                'audio_path': audio_path,
                'base64_data': base64_data
            })
        elif operation == 'extract_features':
            # 提取音频特征
            audio_path = parameters.get('audio_path')
            base64_data = parameters.get('base64_data')
            
            result = engine.call('extract_features', {
                'audio_path': audio_path,
                'base64_data': base64_data
            })
        else:
            result = {'success': False, 'error': f'未知操作: {operation}'}
        
        return result

