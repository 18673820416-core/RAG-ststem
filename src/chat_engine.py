# @self-expose: {"id": "chat_engine", "name": "Chat Engine", "type": "component", "version": "2.0.0", "needs": {"deps": ["unified_memory_system", "llm_client_enhanced", "chat_tools"], "resources": []}, "provides": {"capabilities": ["Chat Engine功能", "职责分离架构"]}}
"""
RAG聊天引擎 - 三层响应机制实现

开发提示词来源：用户对话中关于智能路由和工具化思维的讨论
核心理念：本地知识 → 预训练知识 → 实时工具
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from tools.chat_tools import ChatToolManager
from src.llm_client_enhanced import LLMClientEnhanced

logger = logging.getLogger(__name__)

class ChatEngine:
    """RAG聊天引擎 - 实现三层响应机制"""
    
    def __init__(self):
        self.tool_manager = ChatToolManager()
        self.llm_client = LLMClientEnhanced()
        self.conversation_history = []
        
        # 初始化网状思维引擎
        self.mesh_thought_engine = self._initialize_mesh_thought_engine()
        
    def chat(self, user_input: str, use_tools: bool = True) -> Dict[str, Any]:
        """
        三层响应机制的聊天流程
        
        流程：
        1. 本地知识层：检索相关记忆构建上下文
        2. 预训练知识层：基于LLM的通用知识
        3. 实时工具层：调用文件、网络等工具
        """
        logger.info(f"处理用户输入: {user_input}")
        
        # 工作流程数据采集开始
        workflow_data = {
            'thinking_time': 0,
            'tools_used': [],
            'memory_retrieved': 0,
            'risk_assessment': '未评估',
            'steps_completed': [],
            'step_timings': {},
            'strategy_selection': {},
            'query_analysis': {}
        }
        
        import time
        start_time = time.time()
        
        # 第一步：本地知识层检索
        retrieval_start = time.time()
        local_context = self._retrieve_local_knowledge(user_input)
        workflow_data['step_timings']['knowledge_retrieval'] = time.time() - retrieval_start
        workflow_data['memory_retrieved'] = local_context['memory_count']
        workflow_data['steps_completed'].append('toolSelectionStep')
        
        # 第二步：构建响应策略
        strategy_start = time.time()
        response_strategy = self._determine_response_strategy(user_input, local_context)
        workflow_data['step_timings']['strategy_selection'] = time.time() - strategy_start
        workflow_data['strategy_selection'] = {
            'selected_strategy': response_strategy,
            'available_strategies': ['local_enhanced', 'hybrid', 'tool_enhanced', 'llm_only'],
            'selection_reason': self._get_strategy_reason(response_strategy, local_context)
        }
        workflow_data['steps_completed'].append('executionStep')
        
        # 第三步：生成响应
        generation_start = time.time()
        response = self._generate_response(user_input, local_context, response_strategy, use_tools)
        workflow_data['step_timings']['response_generation'] = time.time() - generation_start
        workflow_data['steps_completed'].append('validationStep')
        
        # 第四步：更新对话历史
        history_start = time.time()
        self._update_conversation_history(user_input, response)
        workflow_data['step_timings']['history_update'] = time.time() - history_start
        workflow_data['steps_completed'].append('summaryStep')
        
        # 计算总思考时间
        workflow_data['thinking_time'] = int((time.time() - start_time) * 1000)  # 转换为毫秒
        
        # 添加工作流程数据到响应
        response['workflow_data'] = workflow_data
        
        return response
    
    def _retrieve_local_knowledge(self, query: str) -> Dict[str, Any]:
        """本地知识层：智能检索相关记忆和知识图谱"""
        memory_tool = self.tool_manager.get_tool('memory_retrieval')
        
        if not memory_tool:
            return {'memories': [], 'context': '', 'knowledge_graph_context': ''}
        
        # 生成多个查询组合，智能尝试
        query_combinations = self._rewrite_query(query)
        
        memories = []
        best_query = query
        
        # 按优先级尝试不同的查询组合
        for query_variant in query_combinations:
            if not query_variant.strip():
                continue
                
            current_memories = memory_tool.search_memories(query_variant, limit=10)
            
            # 如果找到记忆，使用这个查询作为最佳查询
            if current_memories:
                memories = current_memories
                best_query = query_variant
                print(f"✅ 查询成功: '{query_variant}' 找到 {len(memories)} 条记忆")
                break
            else:
                print(f"❌ 查询失败: '{query_variant}' 未找到记忆")
        
        # 构建记忆上下文
        memory_context = memory_tool.get_context_from_memories(best_query)
        
        # 获取知识图谱上下文（为LLM提供结构化知识）
        knowledge_graph_context = self._get_knowledge_graph_context(query)
        
        # 合并上下文
        combined_context = memory_context
        if knowledge_graph_context:
            if combined_context:
                combined_context += f"\n\n{knowledge_graph_context}"
            else:
                combined_context = knowledge_graph_context
        
        return {
            'memories': memories,
            'context': combined_context,
            'memory_count': len(memories),
            'best_query': best_query,
            'knowledge_graph_context': knowledge_graph_context
        }
    
    def _get_knowledge_graph_context(self, query: str) -> str:
        """获取知识图谱上下文（为LLM提供结构化知识）"""
        try:
            # 检查是否有网状思维引擎
            if not hasattr(self, 'mesh_thought_engine') or not self.mesh_thought_engine:
                return ""
            
            # 向量化查询
            query_vector = self.mesh_thought_engine.vector_store.embed(query)
            
            # 查找相似的思维节点
            similar_nodes = self.mesh_thought_engine.find_similar_thoughts(query_vector, threshold=0.6)
            
            if not similar_nodes:
                return ""
            
            # 构建LLM友好的知识图谱上下文
            context_parts = ["知识图谱关联信息："]
            
            for i, node in enumerate(similar_nodes[:3]):  # 限制为前3个最相关的节点
                # 获取节点的关联网络
                node_network = self.mesh_thought_engine.get_thought_network(node.id, max_depth=1)
                
                # 构建节点描述
                node_desc = f"\n{i+1}. 核心概念: {node.content}"
                
                # 添加关联概念
                if node_network.get('connections'):
                    related_concepts = []
                    for conn in node_network['connections']:
                        if conn['target'] in self.mesh_thought_engine.nodes:
                            target_node = self.mesh_thought_engine.nodes[conn['target']]
                            relation_desc = f"{target_node.content}（{conn['type']}）"
                            related_concepts.append(relation_desc)
                    
                    if related_concepts:
                        node_desc += f"\n   关联概念: {', '.join(related_concepts[:2])}"
                
                context_parts.append(node_desc)
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            print(f"知识图谱上下文获取失败: {e}")
            return ""
    
    def _generate_intelligent_queries(self, query: str) -> list:
        """生成智能查询组合，按优先级排序"""
        
        # 关键词列表
        keywords = ['第一性原理', '第一性', '系统', '意识', '认知', '记忆', '意义',
                   'RAG', '知识', '学习', '思考', '推理', '逻辑', '哲学']
        
        # 疑问词列表
        question_words = ['什么', '怎么', '如何', '为什么', '为何', '怎样', '哪个', '哪些',
                         '是不是', '是否', '有没有', '能否', '可否', '可以吗', '好吗',
                         '行吗', '对不对', '对吗', '是不是', '是吗', '呢', '吗', '？', '?',
                         '请', '解释', '一下', '概念', '定义', '含义', '意思', '是什么',
                         '什么是', '什么叫', '啥是', '啥叫', '啥意思', '啥含义', '啥概念']
        
        query_combinations = []
        
        # 1. 原始查询（最高优先级）
        query_combinations.append(query)
        
        # 2. 去掉疑问词的查询
        clean_query = query
        for word in question_words:
            clean_query = clean_query.replace(word, '')
        
        clean_query = clean_query.strip().strip('，。！？；：')
        if clean_query and clean_query != query:
            query_combinations.append(clean_query)
        
        # 3. 提取包含的关键词
        found_keywords = [kw for kw in keywords if kw in query]
        
        # 单个关键词查询
        for kw in found_keywords:
            query_combinations.append(kw)
        
        # 关键词组合查询
        if len(found_keywords) > 1:
            # 按长度排序，优先尝试更长的组合
            sorted_keywords = sorted(found_keywords, key=len, reverse=True)
            query_combinations.append(' '.join(sorted_keywords))
            
            # 尝试所有关键词组合
            for i in range(len(sorted_keywords)):
                if i > 0:  # 避免重复添加单个关键词
                    query_combinations.append(' '.join(sorted_keywords[:i+1]))
        
        # 4. 如果查询包含特定模式，生成模式化查询
        if '第一性原理' in query:
            query_combinations.extend(['第一性原理', '第一性', '系统第一性原理'])
        
        # 去重并保持顺序
        seen = set()
        unique_queries = []
        for q in query_combinations:
            if q and q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries
    
    def _preprocess_query(self, query: str) -> str:
        """预处理查询：提取关键词，去掉疑问词"""
        # 这个方法现在主要用于向后兼容
        intelligent_queries = self._generate_intelligent_queries(query)
        return intelligent_queries[0] if intelligent_queries else query
    
    def _rewrite_query(self, query: str) -> List[str]:
        """
        轻量级用户问题改写，生成优化的检索查询
        
        Args:
            query: 用户原始问题
            
        Returns:
            List[str]: 改写后的查询列表
        """
        try:
            # 1. 导入必要的库
            import jieba
            from collections import Counter
            
            # 2. 分词处理
            words = jieba.lcut(query)
            
            # 3. 关键词提取（使用词频统计）
            word_counts = Counter(words)
            # 过滤停用词
            stop_words = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
            filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
            
            # 4. 生成改写查询
            rewrite_queries = []
            
            # 原始查询
            rewrite_queries.append(query)
            
            # 去掉疑问词的查询
            question_words = ['什么', '怎么', '如何', '为什么', '为何', '怎样', '哪个', '哪些',
                             '是不是', '是否', '有没有', '能否', '可否', '可以吗', '好吗',
                             '行吗', '对不对', '对吗', '是不是', '是吗', '呢', '吗', '？', '?',
                             '请', '解释', '一下', '概念', '定义', '含义', '意思', '是什么',
                             '什么是', '什么叫', '啥是', '啥叫', '啥意思', '啥含义', '啥概念']
            clean_query = query
            for word in question_words:
                clean_query = clean_query.replace(word, '')
            clean_query = clean_query.strip().strip('，。！？；：')
            if clean_query and clean_query != query:
                rewrite_queries.append(clean_query)
            
            # 关键词组合查询
            if filtered_words:
                # 生成不同长度的关键词组合
                for i in range(1, min(len(filtered_words) + 1, 4)):
                    # 获取前i个最频繁的关键词
                    top_words = [word for word, count in word_counts.most_common(i)]
                    if top_words:
                        keyword_query = ' '.join(top_words)
                        if keyword_query not in rewrite_queries:
                            rewrite_queries.append(keyword_query)
            
            # 5. 去重并保持顺序
            seen = set()
            unique_queries = []
            for q in rewrite_queries:
                if q and q not in seen:
                    seen.add(q)
                    unique_queries.append(q)
            
            return unique_queries
        except Exception as e:
            logger.error(f"查询改写失败: {e}")
            # 降级到原始查询
            return [query]
    
    def _initialize_mesh_thought_engine(self):
        """初始化网状思维引擎"""
        try:
            from src.mesh_thought_engine import MeshThoughtEngine
            
            # 创建网状思维引擎实例（会自动调用_load_from_storage()）
            mesh_engine = MeshThoughtEngine()
            
            logger.info("网状思维引擎初始化成功")
            return mesh_engine
            
        except Exception as e:
            logger.error(f"网状思维引擎初始化失败: {e}")
            # 返回None，但允许系统继续运行
            return None
    
    def _determine_response_strategy(self, query: str, local_context: Dict) -> str:
        """
        确定响应策略
        
        策略类型：
        - local_only: 仅使用本地知识
        - llm_only: 仅使用预训练知识
        - tool_enhanced: 需要工具增强
        - hybrid: 混合策略
        """
        
        # 如果有丰富的本地记忆，优先使用本地知识
        if local_context['memory_count'] >= 3:
            return 'local_enhanced'
        
        # 检查是否需要文件操作
        file_keywords = ['文件', '文档', '读取', '打开', '查看']
        if any(keyword in query for keyword in file_keywords):
            return 'tool_enhanced'
        
        # 检查是否需要网络搜索
        search_keywords = ['搜索', '查找', '最新', '实时', '新闻']
        if any(keyword in query for keyword in search_keywords):
            return 'tool_enhanced'
        
        # 默认使用混合策略
        return 'hybrid'
    
    def _generate_response(self, query: str, local_context: Dict, 
                          strategy: str, use_tools: bool) -> Dict[str, Any]:
        """生成最终响应"""
        
        # 构建基础提示词
        base_prompt = self._build_base_prompt(query, local_context, strategy)
        
        # 根据策略调用工具
        tool_results = {}
        if use_tools and strategy == 'tool_enhanced':
            tool_results = self._call_tools(query)
            base_prompt += f"\n\n工具调用结果:\n{tool_results}"
        
        # 调用LLM生成响应
        messages = [{"role": "user", "content": base_prompt}]
        
        # 如果本地记忆为空，调整策略为使用预训练知识
        if local_context['memory_count'] == 0 and strategy == 'local_enhanced':
            strategy = 'hybrid'
            print("⚠️ 本地记忆为空，切换到混合策略")
        
        llm_response = self.llm_client.chat_completion(messages)
        
        # 检查响应是否包含无法回答的提示
        if self._is_unhelpful_response(llm_response):
            print("⚠️ LLM返回了无法回答的响应，重新生成")
            # 重新构建提示词，强调使用预训练知识
            fallback_prompt = self._build_fallback_prompt(query, local_context)
            messages = [{"role": "user", "content": fallback_prompt}]
            llm_response = self.llm_client.chat_completion(messages)
        
        return {
            'response': llm_response,
            'strategy': strategy,
            'local_memories_used': local_context['memory_count'],
            'tools_used': list(tool_results.keys()) if tool_results else [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'query': query,
            'knowledge_sources': self._get_knowledge_sources(local_context, tool_results)
        }
    
    def _rewrite_retrieved_chunks(self, retrieved_text: str, query: str) -> str:
        """
        使用LLM重写检索到的文本块，移除无关内容并提高逻辑流畅性
        
        开发提示词来源：用户要求确保检索到的文本块在最终输出前被LLM重写
        """
        if not retrieved_text:
            return retrieved_text
        
        try:
            rewrite_prompt = f"""
            请重写以下检索到的文本，使其更适合回答当前用户问题。
            
            要求：
            1. 移除无关内容，如IDE命令、思考过程、代码示例等
            2. 提高文本的逻辑流畅性和连贯性
            3. 保留与当前问题相关的核心信息
            4. 不要添加新的信息，只优化现有内容
            
            当前用户问题：{query}
            
            检索到的文本：
            {retrieved_text}
            
            重写后的文本：
            """
            
            messages = [{"role": "user", "content": rewrite_prompt}]
            rewritten_text = self.llm_client.chat_completion(messages)
            
            logger.info("检索文本块重写成功")
            return rewritten_text
        except Exception as e:
            logger.error(f"检索文本块重写失败: {e}")
            # 降级到原始文本
            return retrieved_text
    
    def _build_base_prompt(self, query: str, local_context: Dict, strategy: str) -> str:
        """
        构建基础提示词
        """
        
        prompt_parts = ["你是一个基于RAG系统的智能助手，具备长期记忆能力。"]
        
        # 添加对话历史上下文
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]  # 最近5轮对话
            history_text = "\n".join([f"用户: {h['query']}\n助手: {h['response']}" 
                                    for h in recent_history])
            prompt_parts.append(f"\n最近的对话历史:\n{history_text}")
        
        # 根据策略添加不同内容
        if strategy in ['local_enhanced', 'hybrid'] and local_context['context']:
            # 重写检索到的文本块，移除无关内容并提高逻辑流畅性
            rewritten_context = self._rewrite_retrieved_chunks(local_context['context'], query)
            prompt_parts.append(f"\n相关记忆上下文:\n{rewritten_context}")
        
        prompt_parts.append(f"\n当前用户问题: {query}")
        
        # 添加响应指导
        guidance = ""
        if strategy == 'local_enhanced':
            guidance = "请主要基于提供的记忆上下文进行回答，确保回答与已有记忆保持一致。"
        elif strategy == 'tool_enhanced':
            guidance = "请结合工具调用结果进行回答，确保信息的准确性和时效性。"
        else:
            guidance = "请结合记忆上下文和你的知识进行回答，确保回答的全面性和准确性。"
        
        prompt_parts.append(f"\n回答指导: {guidance}")
        
        return "\n".join(prompt_parts)
    
    def _call_tools(self, query: str) -> Dict[str, Any]:
        """调用工具层"""
        tool_results = {}
        
        # 文件读取工具
        if '文件' in query or '文档' in query:
            file_tool = self.tool_manager.get_tool('file_reading')
            if file_tool:
                # 这里可以实现文件路径提取和读取逻辑
                tool_results['file_reading'] = "文件读取功能已准备"
        
        # 网络搜索工具
        if '搜索' in query or '查找' in query:
            search_tool = self.tool_manager.get_tool('web_search')
            if search_tool and search_tool.enabled:
                search_results = search_tool.search_web(query)
                tool_results['web_search'] = search_results
        
        return tool_results
    
    def _is_unhelpful_response(self, response: str) -> bool:
        """检查响应是否包含无法回答的提示"""
        unhelpful_phrases = [
            '抱歉', '无法回答', '不知道', '不了解', '没有相关信息',
            '暂时无法', '目前无法', '不清楚', '不明白', '不掌握'
        ]
        
        return any(phrase in response for phrase in unhelpful_phrases)
    
    def _get_strategy_reason(self, strategy: str, local_context: Dict) -> str:
        """获取策略选择的原因说明"""
        memory_count = local_context['memory_count']
        
        if strategy == 'local_enhanced':
            if memory_count > 0:
                return f"找到{memory_count}条相关记忆，优先使用本地知识"
            else:
                return "虽然策略为本地增强，但未找到相关记忆"
        elif strategy == 'hybrid':
            if memory_count > 0:
                return f"找到{memory_count}条相关记忆，结合本地知识和预训练知识"
            else:
                return "未找到相关记忆，主要依赖预训练知识"
        elif strategy == 'tool_enhanced':
            return "查询需要实时信息或工具支持，使用工具增强策略"
        else:  # llm_only
            return "查询简单，直接使用预训练知识回答"
    
    def _build_fallback_prompt(self, query: str, local_context: Dict) -> str:
        """构建回退提示词，强调使用预训练知识"""
        
        prompt_parts = [
            "你是一个基于RAG系统的智能助手，具备长期记忆能力。",
            "虽然当前查询在本地记忆库中没有找到直接匹配的内容，但请基于你的预训练知识进行回答。"
        ]
        
        # 添加对话历史上下文
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]  # 最近5轮对话
            history_text = "\n".join([f"用户: {h['query']}\n助手: {h['response']}" 
                                    for h in recent_history])
            prompt_parts.append(f"\n最近的对话历史:\n{history_text}")
        
        # 添加查询
        prompt_parts.append(f"\n当前用户问题: {query}")
        
        # 添加指导
        guidance = ""
        if local_context['memory_count'] == 0:
            guidance = "虽然本地记忆库中没有找到相关内容，但请基于你的预训练知识提供有价值的回答。"
        else:
            guidance = "请结合记忆上下文和你的知识进行回答。"
        
        prompt_parts.append(f"\n回答指导: {guidance}")
        prompt_parts.append("\n重要提示: 请不要说'抱歉无法回答'或类似的话，即使没有找到本地记忆，也要基于你的知识提供有价值的回答。")
        
        return "\n".join(prompt_parts)
    
    def _update_conversation_history(self, query: str, response: Dict):
        """更新对话历史"""
        history_entry = {
            'query': query,
            'response': response['response'],
            'timestamp': response['timestamp'],
            'strategy': response['strategy']
        }
        
        self.conversation_history.append(history_entry)
        
        # 限制历史记录长度
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        # 保存交互信息到向量数据库
        self._save_interaction_to_vector_db(query, response)
    
    def trigger_memory_iteration(self, topic: str = None) -> Optional[Dict]:
        """触发记忆迭代"""
        iteration_tool = self.tool_manager.get_tool('memory_iteration')
        
        if not iteration_tool:
            return None
        
        # 如果没有指定主题，使用最近对话的主题
        if not topic and self.conversation_history:
            # 从最近对话中提取主题
            recent_queries = [h['query'] for h in self.conversation_history[-5:]]
            topic = " ".join(recent_queries)
        
        if topic:
            return iteration_tool.summarize_related_memories(topic)
        
        return None
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """获取对话统计信息"""
        return {
            'total_conversations': len(self.conversation_history),
            'recent_strategies': [h['strategy'] for h in self.conversation_history[-10:]],
            'memory_usage_stats': self._get_memory_usage_stats()
        }
    
    def _get_knowledge_sources(self, local_context: Dict, tool_results: Dict) -> List[str]:
        """获取知识来源信息"""
        sources = []
        
        # 本地记忆来源
        if local_context['memory_count'] > 0:
            sources.append(f"本地记忆库 ({local_context['memory_count']}条相关记忆)")
        
        # 工具来源
        if tool_results:
            for tool_name in tool_results.keys():
                if tool_name == 'file_reading':
                    sources.append("文件读取工具")
                elif tool_name == 'web_search':
                    sources.append("网络搜索工具")
        
        # 预训练知识来源（如果没有其他来源）
        if not sources:
            sources.append("预训练知识库")
        else:
            sources.append("预训练知识库")
        
        return sources
    
    def _get_memory_usage_stats(self) -> Dict[str, Any]:
        """获取记忆使用统计"""
        if not self.conversation_history:
            return {
                'recent_memory_usage_rate': 0.0,
                'preferred_strategy': 'hybrid'
            }
        
        # 统计最近对话中记忆的使用情况
        recent_history = self.conversation_history[-10:]
        recent_with_memory = [h for h in recent_history 
                             if h['strategy'] in ['local_enhanced', 'hybrid']]
        
        # 避免除零错误
        denominator = min(10, len(self.conversation_history))
        memory_usage_rate = len(recent_with_memory) / denominator if denominator > 0 else 0.0
        
        # 计算最常用的策略
        strategy_counts = {}
        for h in recent_history:
            strategy = h['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        preferred_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else 'hybrid'
        
        return {
            'recent_memory_usage_rate': memory_usage_rate,
            'preferred_strategy': preferred_strategy
        }
    
    def _save_interaction_to_vector_db(self, query: str, response: Dict):
        """✅ 将交互信息保存到向量数据库（职责归位至UnifiedMemorySystem）
        
        流程：
        1. 调用UnifiedMemorySystem的统一向量化存储接口
        2. UnifiedMemorySystem调用MemorySlicerTool进行分片
        3. UnifiedMemorySystem调用MeshDatabaseInterface处理去重
        """
        try:
            # 🔍 检查response中是否已有向量化标记
            if response.get('vectorized', False):
                logger.debug(f"跳过已向量化的交互记录: {response.get('timestamp', 'unknown')}")
                return
            
            # ✅ 调用统一记忆系统（职责归位）
            from src.unified_memory_system import get_unified_memory_system
            from pathlib import Path
            
            memory_system = get_unified_memory_system(str(Path.cwd()))
            
            # 准备交互内容
            interaction_content = f"用户: {query}\n助手: {response['response']}"
            
            # ✅ 调用统一记忆系统的向量化存储接口
            result = memory_system.store_interaction_to_vector_db(
                interaction_content=interaction_content,
                metadata={
                    "source": "chat_engine",
                    "source_type": "chat_interaction",
                    "sender": "user_assistant",
                    "timestamp": response['timestamp'],
                    "topic": f"聊天交互 - {response['strategy']}",
                    "tags": ["chat", "interaction", response['strategy']]
                }
            )
            
            saved_count = result.get('saved_count', 0)
            duplicate_count = result.get('duplicate_count', 0)
            
            logger.info(f"✅ 成功保存 {saved_count} 个切片，跳过 {duplicate_count} 个重复")
            
            # ✅ 标记为已向量化
            response['vectorized'] = True
            response['saved_count'] = saved_count
            response['duplicate_count'] = duplicate_count
            
        except Exception as e:
            logger.warning(f"保存交互信息到向量库失败: {e}")
    
    def _generate_content_vector(self, text: str) -> list:
        """生成文本内容的简单向量表示"""
        # 简化的向量生成方法（实际应该使用专业的embedding模型）
        if not text:
            return [0.0] * 12  # 12维向量
        
        # 基于文本长度、关键词等生成简单向量
        vector = []
        
        # 1. 文本长度特征
        length_feature = min(len(text) / 1000, 1.0)  # 归一化到0-1
        vector.append(length_feature)
        
        # 2. 关键词特征（架构相关）
        arch_keywords = ["架构", "设计", "系统", "模块"]
        arch_score = sum(1 for word in arch_keywords if word in text) / len(arch_keywords)
        vector.append(arch_score)
        
        # 3. 关键词特征（评估相关）
        eval_keywords = ["评估", "风险", "可行性", "成本"]
        eval_score = sum(1 for word in eval_keywords if word in text) / len(eval_keywords)
        vector.append(eval_score)
        
        # 4. 关键词特征（实现相关）
        impl_keywords = ["实现", "代码", "技术", "开发"]
        impl_score = sum(1 for word in impl_keywords if word in text) / len(impl_keywords)
        vector.append(impl_score)
        
        # 5-12. 填充其他特征
        for i in range(8):
            vector.append(0.1)  # 占位特征
        
        # 归一化向量
        norm = sum(x**2 for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def close(self):
        """关闭引擎"""
        self.tool_manager.close()



def create_chat_engine() -> ChatEngine:
    """创建聊天引擎实例"""
    return ChatEngine()