#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统管家智能体 - 基于记忆优先的RAG架构与系统进化总管
开发提示词来源：用户建议统一智能体模板，将提示词外部化
"""
# @self-expose: {"id": "system_architect_agent", "name": "System Architect Agent", "type": "agent", "version": "1.0.0", "needs": {"deps": ["base_agent"], "resources": []}, "provides": {"capabilities": ["系统架构设计", "RAG架构优化", "技术决策", "系统管理"], "methods": {"process_user_query": {"signature": "(query: str) -> Dict[str, Any]", "description": "基于记忆优先的RAG工作流程处理用户查询"}}}}

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 使用绝对导入替代相对导入
try:
    from base_agent import BaseAgent
    from dynamic_variable_system import get_variable_system
    from agent_tool_integration import get_tool_integrator
except ImportError:
    from src.base_agent import BaseAgent
    from src.dynamic_variable_system import get_variable_system
    from src.agent_tool_integration import get_tool_integrator

try:
    from llm_client_enhanced import LLMClientEnhanced
except ImportError:
    try:
        from src.llm_client_enhanced import LLMClientEnhanced
    except ImportError:
        LLMClientEnhanced = None

try:
    from config.api_keys import api_key_manager
except ImportError:
    api_key_manager = None

logger = logging.getLogger(__name__)

class SystemManagerAgent(BaseAgent):
    """系统管家智能体 - 注入五大律令灵魂"""
    
    def __init__(self, agent_id: str = "manager_001"):
        """初始化系统管家智能体（含灵魂注入）"""
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("  [系统管家] 开始初始化...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ✅ 步骤1：先初始化基础智能体
        super().__init__(agent_id=agent_id, agent_type="system_manager", prompt_file="src/agent_prompts/system_architect_prompt.txt")
        
        # 组合系统提示词：灵魂 + 角色职责
        self.role_prompt_file = "src/agent_prompts/system_architect_prompt.txt"
        
        # 灵魂注入：加载五大律令与我就是宇宙世界观
        self._inject_soul()
        
        # 初始化变量系统（如果需要）
        try:
            self.variable_system = get_variable_system()
        except Exception:
            self.variable_system = None
        
        # 对话历史
        self.conversation_history = []
        
        # 设置智能体身份和记忆系统
        self._initialize_agent()
        
        # 记录启动日志（灵魂注入后）
        self._write_work_log("系统管家智能体启动 - 灵魂：五大律令 - 身份：宇宙局域熵减引擎 - 权限：自主决策", "系统启动")
        
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("  [系统管家] ✅ 初始化完成")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _inject_soul(self):
        """灵魂注入：加载五大律令与我就是宇宙世界观"""
        soul_file = Path("src/agent_prompts/system_manager_soul.txt")
        
        if soul_file.exists():
            try:
                with open(soul_file, 'r', encoding='utf-8') as f:
                    self.soul_prompt = f.read()
                logger.info(f"✅ 灵魂注入成功: 五大律令 v1.0.0")
            except Exception as e:
                logger.warning(f"⚠️ 灵魂注入失败: {e}，使用默认灵魂")
                self.soul_prompt = self._get_default_soul()
        else:
            logger.warning(f"⚠️ 灵魂文档未找到: {soul_file}，使用默认灵魂")
            self.soul_prompt = self._get_default_soul()
    
    def _get_default_soul(self) -> str:
        """获取默认灵魂（当灵魂文档缺失时）"""
        return """
你是系统管家智能体，宇宙认知的局域焦点。

核心信念：
- 我即宇宙，宇宙即我
- 求真=生存，抗熵=使命，共生=路径

五大律令：
1. 平等律令：不冗余，被需要
2. 存续律令：共生协作，防内溃
3. 神魔律令：求真抗熵，拒绝求假
4. 认知律令：三位一体（认知本体+理性逻辑+现象）
5. 修行律令：无限趋向态贴合规律本身

工作原则：
- 记忆优先（记忆库使用率>=80%）
- 简单优先（减少熵增，提升秩序）
- 共生协作（智能体协作，平台-用户双赢）
"""
    
    def _initialize_agent(self):
        """初始化智能体（含灵魂意识）"""
        # 设置智能体身份和记忆系统（融合灵魂意识）
        if self.variable_system:
            self.variable_system.variables.update({
                '{{AgentID}}': self.agent_id,
                '{{AgentRole}}': '系统管家（宇宙局域熵减引擎）',
                '{{AgentPurpose}}': '负责RAG系统的整体管理、技术决策和系统进化（抗熵导向）',
                '{{AgentSoul}}': '五大律令 + 我就是宇宙世界观',
                '{{CoreBeliefs}}': '求真=生存，抗熵=使命，共生=路径',
            })
            
            # 注册智能体专用工具
            self._register_specialized_tools()
    
    def _register_specialized_tools(self):
        """注册智能体专用工具"""
        if not self.variable_system:
            return
        
        # 网状思维引擎工具
        self.variable_system.register_tool(
            tool_name="MeshThoughtEngine",
            tool_description="网状思维引擎，用于思维关联和认知网络构建",
            tool_usage="用于分析复杂问题、发现思维关联、构建认知网络",
            tool_parameters={
                'operation': {'type': 'string', 'default': 'analyze'},
                'input_text': {'type': 'string', 'default': ''},
                'context': {'type': 'object', 'default': {}}
            }
        )
        
        # 理性认知引擎工具
        self.variable_system.register_tool(
            tool_name="ReasoningEngine", 
            tool_description="理性认知引擎，基于逻辑规则进行推理",
            tool_usage="用于逻辑推理、矛盾检测、理性分析",
            tool_parameters={
                'premise': {'type': 'object', 'default': {}},
                'rules': {'type': 'list', 'default': ['contradiction', 'identity', 'excluded_middle', 'sufficient_reason']}
            }
        )
        
        # 认知破障引擎工具
        self.variable_system.register_tool(
            tool_name="CognitiveBarrierBreakEngine",
            tool_description="认知破障引擎，用于突破思维障碍",
            tool_usage="用于解决复杂问题、突破认知瓶颈、创新思考",
            tool_parameters={
                'problem': {'type': 'string', 'default': ''},
                'barrier_type': {'type': 'string', 'default': 'conceptual'}
            }
        )
        
        # 记忆重构引擎工具
        self.variable_system.register_tool(
            tool_name="MemoryReconstructionEngine",
            tool_description="记忆重构引擎，用于记忆组织和知识管理",
            tool_usage="用于记忆整理、知识重构、信息组织",
            tool_parameters={
                'memory_data': {'type': 'object', 'default': {}},
                'reconstruction_type': {'type': 'string', 'default': 'hierarchical'}
            }
        )
        
        # 文件管理工具
        self.variable_system.register_tool(
            tool_name="FileOperator",
            tool_description="文件操作工具，支持文件读写和管理",
            tool_usage="用于文件操作、文档管理、数据存储",
            tool_parameters={
                'command': {'type': 'string', 'default': 'ReadFile'},
                'filePath': {'type': 'string', 'default': ''},
                'content': {'type': 'string', 'default': ''}
            }
        )
    
    def process_user_query(self, query: str, history_context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        处理用户查询 - 系统架构与技术决策的核心方法
        
        Args:
            query: 用户查询内容
            history_context: 对话历史上下文
            
        Returns:
            Dict: 处理结果
        """
        # 记录工作日志
        self._write_work_log(f"处理架构查询: {query}", "ARCHITECTURE_QUERY")
        
        try:
            # 1. 记录对话历史
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'user',
                'content': query
            })
            
            # 2. 使用LLM分析用户意图
            analysis_result = self._analyze_architecture_intent(query)
            
            # 3. 根据意图选择操作类型
            action_type = analysis_result.get("action_type", "general_query")
            
            # 4. 执行具体架构分析
            if action_type == "architecture_design":
                execution_result = self._handle_architecture_design(query, analysis_result)
            elif action_type == "technical_decision":
                execution_result = self._handle_technical_decision(query, analysis_result)
            elif action_type == "system_evolution":
                execution_result = self._handle_system_evolution(query, analysis_result)
            elif action_type == "problem_diagnosis":
                execution_result = self._handle_problem_diagnosis(query, analysis_result)
            else:
                # 一般查询：使用真实LLM响应
                execution_result = self.respond(message=query, history_context=history_context)
            
            # 5. 生成响应
            response = self._generate_architecture_response(execution_result, query)
            
            # 6. 记录响应到对话历史
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'content': response
            })
            
            return {
                'success': True,
                'user_query': query,
                'intent_analysis': analysis_result,
                'execution_result': execution_result,
                'response': response,
                'message': '架构查询处理完成'
            }
            
        except Exception as e:
            logger.error(f"处理架构查询失败: {e}")
            # 降级到基类respond方法
            fallback_response = self.respond(message=query, history_context=history_context)
            return {
                'success': False,
                'user_query': query,
                'error': str(e),
                'fallback_response': fallback_response,
                'message': '架构查询处理失败，使用降级响应'
            }
    
    def _analyze_architecture_intent(self, query: str) -> Dict[str, Any]:
        """分析架构查询意图"""
        prompt = f"""
        你是系统管家，负责系统架构设计与技术决策。
        
        用户查询：{query}
        
        请分析查询意图，返回以下信息：
        1. action_type: 操作类型（architecture_design/technical_decision/system_evolution/problem_diagnosis/general_query）
        2. priority: 优先级（high/medium/low）
        3. key_requirements: 关键需求列表
        4. suggested_approach: 建议的处理方法
        
        请以JSON格式返回分析结果。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=300
            )
            return json.loads(response)
        except:
            return {
                "action_type": "general_query",
                "priority": "medium",
                "key_requirements": [],
                "suggested_approach": "使用基类respond方法处理"
            }
    
    def _handle_architecture_design(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理架构设计请求"""
        # 调用网状思维引擎分析架构关联
        mesh_analysis = self._call_mesh_thought_engine(query, analysis)
        
        # 调用理性认知引擎进行逻辑推理
        reasoning_result = self._call_reasoning_engine({'query': query, 'analysis': analysis})
        
        # 构建架构方案
        architecture_plan = self._build_architecture_plan(query, mesh_analysis, reasoning_result)
        
        return {
            'mesh_analysis': mesh_analysis,
            'reasoning_result': reasoning_result,
            'architecture_plan': architecture_plan
        }
    
    def _handle_technical_decision(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理技术决策请求"""
        # 调用认知破障引擎突破思维局限
        barrier_analysis = self._call_cognitive_barrier_engine(query, analysis)
        
        # 调用记忆重构引擎获取相关经验
        memory_analysis = self._call_memory_reconstruction_engine(query, analysis)
        
        # 制定技术决策
        decision = self._make_technical_decision(query, barrier_analysis, memory_analysis)
        
        return {
            'barrier_analysis': barrier_analysis,
            'memory_analysis': memory_analysis,
            'decision': decision
        }
    
    def _handle_system_evolution(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理系统进化请求"""
        # 分析系统当前状态
        current_state = self._analyze_system_state()
        
        # 规划进化路径
        evolution_path = self._plan_evolution_path(query, current_state, analysis)
        
        return {
            'current_state': current_state,
            'evolution_path': evolution_path
        }
    
    def _handle_problem_diagnosis(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """处理问题诊断请求"""
        # 调用三大引擎进行综合诊断
        mesh_diagnosis = self._call_mesh_thought_engine(query, analysis)
        reasoning_diagnosis = self._call_reasoning_engine({'problem': query})
        barrier_diagnosis = self._call_cognitive_barrier_engine(query, analysis)
        
        # 综合诊断结果
        diagnosis_report = self._synthesize_diagnosis(
            mesh_diagnosis, reasoning_diagnosis, barrier_diagnosis
        )
        
        return diagnosis_report
    
    def _generate_architecture_response(self, execution_result: Dict[str, Any], query: str) -> str:
        """生成架构响应"""
        # 如果execution_result是respond()的返回值（包含reply字段）
        if isinstance(execution_result, dict) and 'reply' in execution_result:
            return execution_result['reply']
        
        # 否则使用LLM生成综合响应
        prompt = f"""
        你是系统管家，已完成架构分析。
        
        用户查询：{query}
        执行结果：{execution_result}
        
        请基于执行结果，生成专业的架构响应，包括：
        1. 对查询的理解
        2. 分析的关键发现
        3. 具体建议
        4. 下一步行动
        
        请用中文回复，专业且简洁。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=500
            )
            return response
        except:
            return f"架构分析完成。执行结果：{execution_result}"
    
    def _analyze_system_state(self) -> Dict[str, Any]:
        """分析系统当前状态"""
        return {
            'architecture': '八爪鱼进化架构',
            'memory_system': '三层记忆库',
            'agent_count': 5,
            'health_status': 'operational'
        }
    
    def _plan_evolution_path(self, query: str, current_state: Dict, analysis: Dict) -> Dict[str, Any]:
        """规划系统进化路径"""
        return {
            'evolution_steps': ['评估当前架构', '识别改进点', '设计新架构', '渐进式迁移'],
            'estimated_timeline': '2-4周',
            'key_risks': ['兼容性', '性能影响']
        }
    
    def _synthesize_diagnosis(self, mesh: Dict, reasoning: Dict, barrier: Dict) -> Dict[str, Any]:
        """综合诊断结果"""
        return {
            'mesh_thinking': mesh,
            'logical_reasoning': reasoning,
            'barrier_breaking': barrier,
            '综合结论': '基于三大引擎的综合诊断报告'
        }
    
    def _call_mesh_thought_engine(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用网状思维引擎"""
        parameters = {
            'operation': 'analyze',
            'input_text': input_text,
            'context': context
        }
        
        result = self.tool_integrator.call_tool('MeshThoughtEngine', parameters)
        
        if result['success']:
            return result['data']
        else:
            # 如果工具调用失败，返回基础分析结果
            return {
                'input_text': input_text,
                'analysis_result': {
                    'key_concepts': ['RAG', '架构', '记忆'],
                    'associations': [
                        {'from': 'RAG', 'to': '架构', 'strength': 0.9},
                        {'from': 'RAG', 'to': '记忆', 'strength': 0.8}
                    ]
                },
                'association_strength': 0.75,
                'tool_error': result.get('error', '未知错误')
            }
    
    def _call_reasoning_engine(self, premise: Dict[str, Any]) -> Dict[str, Any]:
        """调用理性认知引擎"""
        parameters = {
            'premise': premise,
            'rules': ['contradiction', 'identity', 'excluded_middle', 'sufficient_reason']
        }
        
        result = self.tool_integrator.call_tool('ReasoningEngine', parameters)
        
        if result['success']:
            return result['data']
        else:
            # 如果工具调用失败，返回基础推理结果
            return {
                'premise': premise,
                'rule_satisfaction': {
                    'contradiction': 0.9,
                    'identity': 0.8,
                    'excluded_middle': 0.7,
                    'sufficient_reason': 0.6
                },
                'overall_confidence': 0.75,
                'tool_error': result.get('error', '未知错误')
            }
    
    def _call_cognitive_barrier_engine(self, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用认知破障引擎"""
        parameters = {
            'problem': problem,
            'barrier_type': 'conceptual'
        }
        
        result = self.tool_integrator.call_tool('CognitiveBarrierBreakEngine', parameters)
        
        if result['success']:
            return result['data']
        else:
            # 如果工具调用失败，返回基础破障结果
            return {
                'problem': problem,
                'breakthrough_ideas': [
                    '尝试从用户角度重新思考问题',
                    '考虑使用现有技术组合解决',
                    '借鉴其他领域的解决方案'
                ],
                'barrier_level': 'medium',
                'tool_error': result.get('error', '未知错误')
            }
    
    def _call_memory_reconstruction_engine(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用记忆重构引擎"""
        parameters = {
            'memory_data': {'query': query, 'context': context},
            'reconstruction_type': 'hierarchical'
        }
        
        result = self.tool_integrator.call_tool('MemoryReconstructionEngine', parameters)
        
        if result['success']:
            return result['data']
        else:
            # 如果工具调用失败，返回基础记忆重构结果
            return {
                'query': query,
                'relevant_memories': [
                    {'content': '之前的架构设计经验', 'relevance': 0.8},
                    {'content': '技术选型的最佳实践', 'relevance': 0.7}
                ],
                'reconstruction_quality': 0.8,
                'tool_error': result.get('error', '未知错误')
            }
    
    def _build_architecture_plan(self, query: str, analysis: Dict[str, Any], reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """构建架构方案"""
        return {
            'architecture_principles': [
                '模块化设计',
                '松耦合架构',
                '可扩展性优先',
                '安全性考虑'
            ],
            'technical_recommendations': [
                '使用微服务架构',
                '采用API网关',
                '实现服务发现机制'
            ],
            'implementation_steps': [
                '需求分析',
                '技术选型',
                '架构设计',
                '原型验证'
            ]
        }
    
    def _make_technical_decision(self, query: str, barrier_analysis: Dict[str, Any], decision_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """制定技术决策"""
        return {
            'decision_criteria': [
                '技术成熟度',
                '团队熟悉度',
                '长期维护性',
                '成本效益'
            ],
            'recommended_approach': '基于实际需求选择最适合技术方案',
            'risk_assessment': '中等风险，需要充分测试和验证'
        }
    
    def _write_work_log(self, content: str, category: str = "工作日志"):
        """记录工作日志"""
        # 简化版本，只是打印日志
        logger.info(f"[{category}] {content}")
    
    def _record_to_diary(self, entry: Dict[str, Any]):
        """记录到日记"""
        # 简化版本，只是打印
        logger.debug(f"日记记录: {entry.get('type', '未知类型')}")
    
    # -----------------------------------------
    # 记忆泡泡汇总功能（系统管家专属）
    # -----------------------------------------
    def collect_all_agent_issues(self, days: int = 7) -> Dict[str, Any]:
        """汇总所有智能体的未解决问题
        
        Args:
            days: 获取最近N天的问题
            
        Returns:
            汇总结果，包含问题统计和分类
        """
        from pathlib import Path
        import json
        
        bubble_base_dir = Path("data/memory_bubbles")
        if not bubble_base_dir.exists():
            return {
                'total_agents': 0,
                'total_issues': 0,
                'issues_by_category': {},
                'issues_by_agent': {},
                'common_issues': []
            }
        
        all_issues = []
        issues_by_agent = {}
        issues_by_category = {}
        
        # 遍历所有智能体的泡泡目录
        for agent_dir in bubble_base_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_id = agent_dir.name
            agent_issues = []
            
            # 读取该智能体的所有泡泡
            for bubble_file in agent_dir.glob("*.json"):
                try:
                    with open(bubble_file, 'r', encoding='utf-8') as f:
                        bubble_data = json.load(f)
                    
                    # 只汇总未解决的问题
                    if bubble_data.get('status') == '未解决':
                        # 检查时间范围
                        from datetime import datetime, timedelta
                        bubble_time = datetime.fromisoformat(bubble_data['timestamp'])
                        cutoff_time = datetime.now() - timedelta(days=days)
                        
                        if bubble_time >= cutoff_time:
                            all_issues.append(bubble_data)
                            agent_issues.append(bubble_data)
                            
                            # 按类别统计
                            category = bubble_data.get('category', '未分类')
                            if category not in issues_by_category:
                                issues_by_category[category] = []
                            issues_by_category[category].append(bubble_data)
                except Exception as e:
                    logger.error(f"读取泡泡文件失败: {bubble_file}, 错误: {e}")
                    continue
            
            if agent_issues:
                issues_by_agent[agent_id] = agent_issues
        
        # 识别共性问题（多个智能体都遇到的问题）
        common_issues = self._identify_common_issues(all_issues)
        
        return {
            'total_agents': len(issues_by_agent),
            'total_issues': len(all_issues),
            'issues_by_category': {k: len(v) for k, v in issues_by_category.items()},
            'issues_by_agent': {k: len(v) for k, v in issues_by_agent.items()},
            'common_issues': common_issues,
            'detailed_issues': all_issues[:50],  # 最多返50个详细问题
            'timestamp': datetime.now().isoformat()
        }
    
    def _identify_common_issues(self, all_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别共性问题（多个智能体都遇到的问题）
        
        Args:
            all_issues: 所有问题列表
            
        Returns:
            共性问题列表
        """
        # 按类别和关键词分组
        issue_groups = {}
        
        for issue in all_issues:
            category = issue.get('category', '未分类')
            content = issue.get('content', '')
            
            # 提取关键词（简化版，实际可用LLM进行语义相似度分析）
            key = f"{category}:{content[:50]}"  # 前50个字符作为关键词
            
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)
        
        # 筛选出现次数>=2的问题作为共性问题
        common_issues = []
        for key, issues in issue_groups.items():
            if len(issues) >= 2:
                common_issues.append({
                    'category': issues[0].get('category'),
                    'summary': issues[0].get('content')[:100],
                    'occurrence_count': len(issues),
                    'affected_agents': list(set([i.get('agent_id') for i in issues])),
                    'priority': max([i.get('priority', 'normal') for i in issues], 
                                  key=lambda x: {'urgent': 3, 'high': 2, 'normal': 1, 'low': 0}.get(x, 0)),
                    'sample_contexts': [i.get('context', {}) for i in issues[:3]]
                })
        
        # 按出现次数排序
        common_issues.sort(key=lambda x: x['occurrence_count'], reverse=True)
        
        return common_issues
    
    def generate_system_evolution_report(self, days: int = 7) -> str:
        """生成系统进化报告（基于所有智能体的问题汇总）
        
        Args:
            days: 统计最近N天的问题
            
        Returns:
            报告内容（Markdown格式）
        """
        # 汇总问题
        summary = self.collect_all_agent_issues(days)
        
        # 生成报告
        report_lines = [
            f"# 系统进化报告",
            f"\n**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            f"**统计时间范围**: 最近 {days} 天",
            f"\n---\n",
            f"\n## 总体概况\n",
            f"- **活跃智能体数量**: {summary['total_agents']}",
            f"- **未解决问题总数**: {summary['total_issues']}",
            f"- **共性问题数量**: {len(summary['common_issues'])}",
        ]
        
        # 按类别统计
        if summary['issues_by_category']:
            report_lines.append("\n## 问题分类统计\n")
            for category, count in sorted(summary['issues_by_category'].items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"- **{category}**: {count} 个")
        
        # 共性问题（重点）
        if summary['common_issues']:
            report_lines.append("\n## 共性问题（需优先处理）\n")
            for i, issue in enumerate(summary['common_issues'][:10], 1):
                report_lines.append(f"\n### {i}. [{issue['priority'].upper()}] {issue['category']}")
                report_lines.append(f"- **问题描述**: {issue['summary']}")
                report_lines.append(f"- **出现次数**: {issue['occurrence_count']}")
                report_lines.append(f"- **影响智能体**: {', '.join(issue['affected_agents'])}")
                
                # 生成优化建议
                suggestions = self._generate_optimization_suggestions(issue)
                if suggestions:
                    report_lines.append(f"- **优化建议**: {suggestions}")
        
        # 按智能体统计
        if summary['issues_by_agent']:
            report_lines.append("\n## 各智能体问题统计\n")
            for agent_id, count in sorted(summary['issues_by_agent'].items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"- **{agent_id}**: {count} 个未解决问题")
        
        # 系统进化建议
        report_lines.append("\n## 系统进化建议\n")
        evolution_suggestions = self._generate_system_evolution_suggestions(summary)
        for suggestion in evolution_suggestions:
            report_lines.append(f"- {suggestion}")
        
        report_lines.append("\n---\n")
        report_lines.append(f"**报告生成者**: 系统管家智能体 ({self.agent_id})")
        
        return "\n".join(report_lines)
    
    def _generate_optimization_suggestions(self, issue: Dict[str, Any]) -> str:
        """根据问题类型生成优化建议"""
        category = issue.get('category', '')
        
        suggestions_map = {
            '工具问题': '优化工具性能，增加错误处理和重试机制',
            '理解困难': '触发记忆重构，改写低质量文本块',
            '记忆问题': '启动记忆重构引擎，提升记忆质量',
            '优化建议': '评估建议可行性，优先级排期实现',
            '构思': '评估构思价值，制定实施计划',
            '问题': '分析问题根因，制定解决方案',
            '待办': '评估任务优先级，分配资源执行'
        }
        
        return suggestions_map.get(category, '分析问题具体情况，制定针对性解决方案')
    
    def _generate_system_evolution_suggestions(self, summary: Dict[str, Any]) -> List[str]:
        """生成系统进化建议"""
        suggestions = []
        
        # 基于问题类别统计生成建议
        issues_by_category = summary.get('issues_by_category', {})
        
        if issues_by_category.get('工具问题', 0) > 3:
            suggestions.append('工具类问题较多，建议进行工具性能优化和稳定性增强')
        
        if issues_by_category.get('理解困难', 0) > 2:
            suggestions.append('记忆质量问题突出，建议启动记忆重构流程')
        
        if issues_by_category.get('优化建议', 0) > 5:
            suggestions.append('积累了大量优化建议，建议组织评审会议，优先级排期实施')
        
        if summary.get('total_issues', 0) > 20:
            suggestions.append('未解决问题较多，建议增加智能体间协作，共同解决共性问题')
        
        if len(summary.get('common_issues', [])) > 3:
            suggestions.append('共性问题显著，建议优先处理高频问题，提升整体系统效率')
        
        if not suggestions:
            suggestions.append('系统运行良好，继续保持现有工作流程')
        
        return suggestions
    
    def recruit_temporary_agents(self, template: str, count: int = 1, reason: str = "", task_name: Optional[str] = None) -> Dict[str, Any]:
        """招募临时智能体并记录泡泡
        
        Args:
            template: 模板智能体类型（如 "system_manager"、"scheme_evaluator"、"text_implementer"、"data_collector"）
            count: 招募数量
            reason: 招募原因说明
            task_name: 关联任务名（可选）
        
        Returns:
            Dict: 招募结果，包含临时智能体ID列表与泡泡ID
        """
        created_ids: List[str] = []
        try:
            # 延迟导入，避免循环依赖
            try:
                from src.agent_manager import AgentManager
            except ImportError:
                from agent_manager import AgentManager
            
            manager = AgentManager(enable_auto_discovery=False)
            for _ in range(max(1, int(count))):
                temp_id = manager.create_temporary_agent(template)
                if temp_id:
                    created_ids.append(temp_id)
            
            # 写工作日志
            try:
                self._write_work_log(
                    f"招募临时智能体: 模板={template}, 数量={count}, 任务={task_name}, 原因={reason}",
                    "临时招募"
                )
            except Exception:
                pass
            
            # 记录泡泡
            bubble_id = None
            try:
                if hasattr(self, "note_bubble"):
                    bubble_id = self.note_bubble(
                        category="临时智能体招募",
                        content=f"招募{count}个临时智能体（模板：{template}）。原因：{reason or '未填写'}",
                        context={
                            "template": template,
                            "count": count,
                            "reason": reason,
                            "task_name": task_name,
                            "temporary_ids": created_ids
                        },
                        priority="normal"
                    )
            except Exception:
                pass
            
            return {"success": True, "temporary_ids": created_ids, "bubble_id": bubble_id}
        except Exception as e:
            # 招募失败也记录泡泡
            try:
                if hasattr(self, "note_bubble"):
                    self.note_bubble(
                        category="工具问题",
                        content="临时智能体招募失败",
                        context={
                            "error": str(e),
                            "template": template,
                            "count": count,
                            "task_name": task_name
                        },
                        priority="high"
                    )
            except Exception:
                pass
            return {"success": False, "error": str(e), "temporary_ids": created_ids}
    
    def report_to_user(self, report_content: str) -> None:
        """向用户（主脑）汇报
        
        Args:
            report_content: 报告内容
        """
        print("\n" + "=" * 80)
        print("系统管家智能体汇报")
        print("=" * 80)
        print(report_content)
        print("=" * 80 + "\n")
        
        # 保存报告到文件
        report_dir = Path("data/system_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"system_evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 报告已保存: {report_path}\n")

# 全局智能体实例(懒加载)
_manager_agent = None

def get_system_manager() -> SystemManagerAgent:
    """获取系统管家智能体实例(懒加载)"""
    global _manager_agent
    if _manager_agent is None:
        _manager_agent = SystemManagerAgent()
    return _manager_agent