# @self-expose: {"id": "agent_manager", "name": "Agent Manager", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Manager功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体管理器 - 统一管理所有智能体实例
开发提示词来源：用户建议统一智能体模板，实现智能体统一管理
新增功能：支持智能体和工具的自动发现机制
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 导入智能体
try:
    from .system_architect_agent import get_system_manager
    from .scheme_evaluator_agent import get_scheme_evaluator
    from .code_implementer_agent import get_text_implementer
    from .data_collector_agent import get_data_collector
except ImportError:
    from src.system_architect_agent import get_system_manager
    from src.scheme_evaluator_agent import get_scheme_evaluator
    from src.code_implementer_agent import get_text_implementer
    from src.data_collector_agent import get_data_collector

# 导入自动发现引擎
try:
    from .agent_discovery_engine import discover_all_components, get_discovery_engine
    AUTO_DISCOVERY_ENABLED = True
except ImportError:
    try:
        from src.agent_discovery_engine import discover_all_components, get_discovery_engine
        AUTO_DISCOVERY_ENABLED = True
    except ImportError:
        AUTO_DISCOVERY_ENABLED = False
        logger = logging.getLogger(__name__)
        logger.warning("自动发现引擎不可用，将使用手动注册模式")

logger = logging.getLogger(__name__)

class AgentManager:
    """智能体管理器 - 统一管理所有智能体实例"""
    
    def __init__(self, enable_auto_discovery: bool = True):
        """初始化智能体管理器
        
        Args:
            enable_auto_discovery: 是否启用自动发现机制
        """
        self.agents = {}
        self.agent_status = {}
        self.workflow_history = []
        self.auto_discovery_enabled = enable_auto_discovery and AUTO_DISCOVERY_ENABLED
        
        # 初始化所有智能体
        if self.auto_discovery_enabled:
            self._initialize_agents_with_discovery()
        else:
            self._initialize_agents()
        
        logger.info(f"智能体管理器初始化完成 (自动发现: {'启用' if self.auto_discovery_enabled else '禁用'})")
    
    def _initialize_agents(self):
        """初始化所有智能体实例"""
        # 系统管家智能体
        self.agents["system_manager"] = get_system_manager()
        self.agent_status["system_manager"] = {
            "status": "active",
            "last_active": datetime.now().isoformat(),
            "request_count": 0
        }
        
        # 方案评估师智能体
        self.agents["scheme_evaluator"] = get_scheme_evaluator()
        self.agent_status["scheme_evaluator"] = {
            "status": "active", 
            "last_active": datetime.now().isoformat(),
            "request_count": 0
        }
        
        # 文本实现师智能体
        self.agents["text_implementer"] = get_text_implementer()
        self.agent_status["text_implementer"] = {
            "status": "active",
            "last_active": datetime.now().isoformat(),
            "request_count": 0
        }
        
        # 数据收集者智能体
        self.agents["data_collector"] = get_data_collector()
        self.agent_status["data_collector"] = {
            "status": "active",
            "last_active": datetime.now().isoformat(),
            "request_count": 0
        }
        
        logger.info(f"已初始化 {len(self.agents)} 个智能体")
    
    def _initialize_agents_with_discovery(self):
        """使用自动发现机制初始化智能体"""
        logger.info("开始自动发现智能体...")
        
        try:
            # 发现所有组件
            discovery_result = discover_all_components()
            
            agents = discovery_result.get("agents", {})
            tools = discovery_result.get("tools", {})
            
            logger.info(f"发现 {len(agents)} 个智能体和 {len(tools)} 个工具")
            
            # 自动注册发现的智能体
            for agent_id, agent_info in agents.items():
                self._auto_register_agent(agent_id, agent_info)
            
            # 如果自动发现没有找到智能体，回退到手动注册
            if not self.agents:
                logger.warning("自动发现未找到智能体，回退到手动注册")
                self._initialize_agents()
            else:
                logger.info(f"通过自动发现机制初始化了 {len(self.agents)} 个智能体")
                
        except Exception as e:
            logger.error(f"自动发现失败: {e}，回退到手动注册")
            self._initialize_agents()
    
    def _auto_register_agent(self, agent_id: str, agent_info: Dict):
        """自动注册智能体"""
        try:
            module_name = agent_info["module_name"]
            
            if agent_info["type"] == "function":
                # 通过获取函数注册
                function_name = agent_info["function_name"]
                
                # 动态导入
                module = __import__(module_name, fromlist=[function_name])
                get_agent_func = getattr(module, function_name)
                
                # 获取智能体实例
                agent_instance = get_agent_func()
                
                # 注册到管理器
                self.agents[agent_id] = agent_instance
                self.agent_status[agent_id] = {
                    "status": "active",
                    "last_active": datetime.now().isoformat(),
                    "request_count": 0,
                    "discovery_source": "auto",
                    "discovery_time": agent_info.get("discovery_time", "")
                }
                
                logger.info(f"自动注册智能体: {agent_id} (来自 {module_name})")
                
            elif agent_info["type"] == "class":
                # 通过类注册（需要实例化）
                class_name = agent_info["class_name"]
                
                # 动态导入
                module = __import__(module_name, fromlist=[class_name])
                agent_class = getattr(module, class_name)
                
                # 实例化智能体
                agent_instance = agent_class()
                
                # 注册到管理器
                self.agents[agent_id] = agent_instance
                self.agent_status[agent_id] = {
                    "status": "active",
                    "last_active": datetime.now().isoformat(),
                    "request_count": 0,
                    "discovery_source": "auto",
                    "discovery_time": agent_info.get("discovery_time", "")
                }
                
                logger.info(f"自动注册智能体: {agent_id} (来自 {module_name}.{class_name})")
                
        except Exception as e:
            logger.warning(f"自动注册智能体 {agent_id} 失败: {e}")
    
    def get_agent(self, agent_type: str) -> Optional[Any]:
        """
        获取指定类型的智能体
        
        Args:
            agent_type: 智能体类型
            
        Returns:
            智能体实例，如果不存在返回None
        """
        if agent_type in self.agents:
            # 更新状态
            self.agent_status[agent_type]["last_active"] = datetime.now().isoformat()
            self.agent_status[agent_type]["request_count"] += 1
            
            return self.agents[agent_type]
        
        logger.warning(f"未找到智能体类型: {agent_type}")
        return None
    
    def get_all_agents(self) -> Dict[str, Any]:
        """获取所有智能体（字典形式）
        
        Returns:
            Dict[str, Any]: 智能体字典 {agent_id: agent_instance}
        """
        return self.agents.copy()
    
    def get_all_agent_instances(self) -> List[Any]:
        """获取所有智能体实例（列表形式）
        
        用于夜间维护等需要遍历所有智能体的场景
        
        Returns:
            List[Any]: 智能体实例列表
        """
        return list(self.agents.values())
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """获取智能体统计信息
        
        Returns:
            Dict: 统计信息
        """
        agent_types = {}
        for agent_id, agent in self.agents.items():
            agent_type = getattr(agent, 'agent_type', 'unknown')
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        
        return {
            "total_agents": len(self.agents),
            "agents_by_type": agent_types,
            "agent_ids": list(self.agents.keys()),
            "agent_status_summary": {
                "active": sum(1 for s in self.agent_status.values() if s["status"] == "active"),
                "inactive": sum(1 for s in self.agent_status.values() if s["status"] == "inactive")
            }
        }
    
    def refresh_agents(self) -> Dict[str, Any]:
        """刷新智能体列表（重新发现）"""
        if not self.auto_discovery_enabled:
            logger.warning("自动发现未启用，无法刷新智能体列表")
            return self.agents.copy()
        
        logger.info("开始刷新智能体列表...")
        
        # 备份当前智能体
        old_agents = self.agents.copy()
        old_status = self.agent_status.copy()
        
        # 清空当前列表
        self.agents = {}
        self.agent_status = {}
        
        try:
            # 重新发现
            self._initialize_agents_with_discovery()
            
            # 统计变化
            new_count = len(self.agents)
            old_count = len(old_agents)
            
            # 找出新增的智能体
            new_agents = set(self.agents.keys()) - set(old_agents.keys())
            removed_agents = set(old_agents.keys()) - set(self.agents.keys())
            
            logger.info(f"智能体刷新完成: 新增 {len(new_agents)} 个，移除 {len(removed_agents)} 个")
            
            if new_agents:
                logger.info(f"新增智能体: {list(new_agents)}")
            if removed_agents:
                logger.info(f"移除智能体: {list(removed_agents)}")
                
            return self.agents.copy()
            
        except Exception as e:
            # 恢复备份
            logger.error(f"刷新失败: {e}，恢复原有智能体列表")
            self.agents = old_agents
            self.agent_status = old_status
            return self.agents.copy()
    
    def get_discovery_info(self) -> Dict[str, Any]:
        """获取自动发现相关信息"""
        return {
            "auto_discovery_enabled": self.auto_discovery_enabled,
            "total_agents": len(self.agents),
            "discovery_sources": {
                agent_id: status.get("discovery_source", "manual") 
                for agent_id, status in self.agent_status.items()
            },
            "agent_types": list(self.agents.keys())
        }
    
    def route_request(self, query: str, agent_type: str = None) -> Dict[str, Any]:
        """
        路由请求到合适的智能体
        
        Args:
            query: 用户查询
            agent_type: 指定智能体类型（可选）
            
        Returns:
            处理结果
        """
        # 记录请求历史
        request_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "agent_type": agent_type,
            "status": "processing"
        }
        
        # 确定目标智能体
        target_agent_type = agent_type or self._determine_agent_type(query)
        
        if target_agent_type:
            agent = self.get_agent(target_agent_type)
            if agent:
                try:
                    # 调用智能体处理查询
                    result = agent.process_user_query(query)
                    
                    # 更新请求状态
                    request_entry["agent_type"] = target_agent_type
                    request_entry["status"] = "completed"
                    request_entry["result"] = result
                    
                    logger.info(f"请求路由到 {target_agent_type} 处理完成")
                    
                except Exception as e:
                    # 处理异常
                    request_entry["status"] = "error"
                    request_entry["error"] = str(e)
                    
                    logger.error(f"智能体 {target_agent_type} 处理请求时出错: {e}")
                    
                    result = {
                        "error": f"智能体处理失败: {str(e)}",
                        "agent_type": target_agent_type,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                result = {
                    "error": f"智能体 {target_agent_type} 不可用",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            result = {
                "error": "无法确定合适的智能体类型",
                "timestamp": datetime.now().isoformat()
            }
        
        # 保存请求历史
        self.workflow_history.append(request_entry)
        
        return result
    
    def _determine_agent_type(self, query: str) -> Optional[str]:
        """
        根据查询内容确定合适的智能体类型
        
        Args:
            query: 用户查询
            
        Returns:
            智能体类型
        """
        query_lower = query.lower()
        
        # 系统管理相关查询
        if any(keyword in query_lower for keyword in [
            '架构', '设计', '系统', '框架', '结构', '管理', '管家', 'architect', 'design', 'system', 'manager'
        ]):
            return "system_manager"
        
        # 方案评估相关查询
        elif any(keyword in query_lower for keyword in [
            '评估', '评价', '打分', '方案', 'scheme', 'evaluate', 'score'
        ]):
            return "scheme_evaluator"
        
        # 文本实现相关查询
        elif any(keyword in query_lower for keyword in [
            '代码', '实现', '编写', '生成', '文本', 'code', 'implement', 'generate', 'text'
        ]):
            return "text_implementer"
        
        # 数据收集相关查询
        elif any(keyword in query_lower for keyword in [
            '数据', '收集', '采集', '吃饭', 'data', 'collect', 'gather'
        ]):
            return "data_collector"
        
        return None
    
    def get_agent_status(self) -> Dict[str, Dict]:
        """
        获取所有智能体状态
        
        Returns:
            智能体状态字典
        """
        return self.agent_status.copy()
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict]:
        """
        获取工作流历史
        
        Args:
            limit: 返回的历史记录数量限制
            
        Returns:
            工作流历史记录
        """
        return self.workflow_history[-limit:]
    
    def execute_workflow(self, workflow_steps: List[Dict]) -> Dict[str, Any]:
        """
        执行多步骤工作流
        
        Args:
            workflow_steps: 工作流步骤列表
            
        Returns:
            工作流执行结果
        """
        workflow_result = {
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "steps": [],
            "status": "started",
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        logger.info(f"开始执行工作流: {workflow_result['workflow_id']}")
        
        try:
            for i, step in enumerate(workflow_steps):
                step_result = {
                    "step_number": i + 1,
                    "agent_type": step.get("agent_type"),
                    "query": step.get("query"),
                    "status": "processing",
                    "start_time": datetime.now().isoformat()
                }
                
                # 执行步骤
                result = self.route_request(step["query"], step.get("agent_type"))
                
                step_result["status"] = "completed"
                step_result["end_time"] = datetime.now().isoformat()
                step_result["result"] = result
                
                workflow_result["steps"].append(step_result)
                
                # 检查是否需要停止
                if step.get("stop_on_error") and "error" in result:
                    workflow_result["status"] = "stopped_on_error"
                    break
            
            workflow_result["status"] = "completed"
            
        except Exception as e:
            workflow_result["status"] = "error"
            workflow_result["error"] = str(e)
            logger.error(f"工作流执行出错: {e}")
        
        workflow_result["end_time"] = datetime.now().isoformat()
        
        logger.info(f"工作流执行完成: {workflow_result['status']}")
        
        return workflow_result
    
    def get_agent_diaries(self, agent_type: str = None, limit: int = 20) -> Dict[str, Any]:
        """
        获取智能体日记
        
        Args:
            agent_type: 智能体类型（None表示所有智能体）
            limit: 日记条目数量限制
            
        Returns:
            日记数据
        """
        diaries = {}
        
        if agent_type:
            # 获取指定智能体的日记
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                diaries[agent_type] = agent.get_diary_summary(limit)
        else:
            # 获取所有智能体的日记
            for agent_type, agent in self.agents.items():
                diaries[agent_type] = agent.get_diary_summary(limit)
        
        return diaries
    
    def create_temporary_agent(self, agent_template: str, agent_id: str = None) -> Optional[str]:
        """
        创建临时智能体（八爪鱼架构的动态腕足）
        
        核心设计：
        - 仅在内存中创建LLM实例，不创建新的代码文件
        - 通过注入系统提示词获得智能体能力
        - 轻量级，可大规模并行（内存允许情况下可创建数百个）
        
        Args:
            agent_template: 智能体模板类型（如：system_architect、scheme_evaluator）
            agent_id: 自定义智能体ID（可选，默认自动生成）
            
        Returns:
            str: 临时智能体ID，创建失败返回None
        """
        try:
            logger.info(f"开始创建临时智能体，模板: {agent_template}")
            
            # 检查模板是否存在
            if agent_template not in self.agents:
                logger.warning(f"智能体模板不存在: {agent_template}")
                return None
            
            # 创建临时智能体ID（带微秒时间戳，确保唯一性）
            temp_agent_id = agent_id or f"temp_{agent_template}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # 获取模板智能体
            template_agent = self.agents[agent_template]
            
            # 从模板智能体提取系统提示词
            system_prompt = template_agent.get_system_prompt() if hasattr(template_agent, 'get_system_prompt') else template_agent.full_system_prompt
            
            # 创建轻量级临时智能体（内存实例）
            from src.temporary_agent import TemporaryAgent
            temp_agent = TemporaryAgent(
                agent_id=temp_agent_id,
                template_name=agent_template,
                system_prompt=system_prompt,
                llm_client=template_agent.llm_client if hasattr(template_agent, 'llm_client') else None,
                tool_integrator=template_agent.tool_integrator if hasattr(template_agent, 'tool_integrator') else None
            )
            
            # 注册临时智能体
            self.agents[temp_agent_id] = temp_agent
            self.agent_status[temp_agent_id] = {
                "status": "active",
                "last_active": datetime.now().isoformat(),
                "request_count": 0,
                "is_temporary": True,
                "template": agent_template,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"✓ 临时智能体创建成功: {temp_agent_id} (模板: {agent_template}, 内存实例模式)")
            return temp_agent_id
            
        except Exception as e:
            logger.error(f"创建临时智能体失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_temporary_agent(self, agent_id: str) -> bool:
        """
        移除临时智能体
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            bool: 是否成功移除
        """
        try:
            # 检查智能体是否存在
            if agent_id not in self.agents:
                logger.warning(f"智能体不存在: {agent_id}")
                return False
            
            # 检查是否为临时智能体
            if agent_id.startswith("temp_") or self.agent_status.get(agent_id, {}).get("is_temporary", False):
                # 移除智能体
                del self.agents[agent_id]
                del self.agent_status[agent_id]
                logger.info(f"临时智能体移除成功: {agent_id}")
                return True
            else:
                logger.warning(f"智能体 {agent_id} 不是临时智能体，无法移除")
                return False
                
        except Exception as e:
            logger.error(f"移除临时智能体失败: {e}")
            return False
    
    def get_temporary_agents(self) -> Dict[str, Any]:
        """
        获取所有临时智能体
        
        Returns:
            Dict: 临时智能体字典
        """
        temp_agents = {}
        for agent_id, agent in self.agents.items():
            if agent_id.startswith("temp_") or self.agent_status.get(agent_id, {}).get("is_temporary", False):
                temp_agents[agent_id] = agent
        return temp_agents
    
    def clear_all_temporary_agents(self) -> Dict[str, int]:
        """
        清理所有临时智能体
        
        Returns:
            Dict: 清理结果统计
        """
        stats = {
            "total_agents": len(self.agents),
            "temporary_agents": 0,
            "removed_agents": 0
        }
        
        # 收集所有临时智能体ID
        temp_agent_ids = []
        for agent_id in self.agents.keys():
            if agent_id.startswith("temp_") or self.agent_status.get(agent_id, {}).get("is_temporary", False):
                temp_agent_ids.append(agent_id)
        
        stats["temporary_agents"] = len(temp_agent_ids)
        
        # 移除所有临时智能体
        for agent_id in temp_agent_ids:
            if self.remove_temporary_agent(agent_id):
                stats["removed_agents"] += 1
        
        logger.info(f"清理临时智能体完成: 共 {stats['temporary_agents']} 个临时智能体，移除了 {stats['removed_agents']} 个")
        return stats

# 全局智能体管理器实例(懒加载)
_agent_manager = None

def get_agent_manager() -> AgentManager:
    """获取智能体管理器实例(懒加载)"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager

def route_user_query(query: str, agent_type: str = None) -> Dict[str, Any]:
    """
    路由用户查询到合适的智能体（便捷函数）
    
    Args:
        query: 用户查询
        agent_type: 指定智能体类型（可选）
        
    Returns:
        处理结果
    """
    return get_agent_manager().route_request(query, agent_type)

def execute_multi_agent_workflow(workflow_steps: List[Dict]) -> Dict[str, Any]:
    """
    执行多智能体工作流（便捷函数）
    
    Args:
        workflow_steps: 工作流步骤列表
        
    Returns:
        工作流执行结果
    """
    return get_agent_manager().execute_workflow(workflow_steps)