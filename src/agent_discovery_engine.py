# @self-expose: {"id": "agent_discovery_engine", "name": "Agent Discovery Engine", "type": "component", "version": "2.1.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["协议驱动的智能体发现", "协议驱动的工具发现", "支持相对导入", "支持智能体自繁殖", "BaseAgent特征验证", "无需物理导入", "嵌套JSON解析"], "methods": {"discover_agents": {"signature": "() -> Dict[str, Dict]", "description": "基于@self-expose协议发现智能体"}, "discover_tools": {"signature": "() -> Dict[str, Dict]", "description": "基于@self-expose协议发现工具"}, "_is_based_on_base_agent": {"signature": "(provides: Dict, content: str) -> bool", "description": "验证是否基于BaseAgent模板"}, "_extract_agent_info_from_protocol": {"signature": "(expose_data: Dict, file_path: Path, content: str) -> Optional[Dict]", "description": "从协议提取智能体信息"}, "_extract_tool_info_from_protocol": {"signature": "(expose_data: Dict, file_path: Path, content: str) -> Optional[Dict]", "description": "从协议提取工具信息"}, "_extract_self_expose_protocol": {"signature": "(content: str) -> List[str]", "description": "提取文件中的@self-expose协议（支持嵌套JSON）"}}}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体自动发现引擎 - 基于协议驱动，支持智能体自繁殖

重构说明（v2.0.0）：
- 从物理路径导入 → 协议驱动发现
- 支持相对导入（不再触发 attempted relative import 错误）
- 支持智能体自繁殖和无实体智能体
- 基于@self-expose协议和BaseAgent特征验证

开发提示词来源：用户要求解决智能体和工具的自动发现问题，支持智能体自繁殖
重构依据：用户洞察 - 智能体发现应基于BaseAgent模板设计原理，而非物理地址
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)

class AgentDiscoveryEngine:
    """智能体自动发现引擎 - 自动发现和注册系统中的智能体和工具"""
    
    def __init__(self, base_path: str = "src"):
        self.base_path = Path(base_path)
        self.discovered_agents: Dict[str, Dict] = {}
        self.discovered_tools: Dict[str, Dict] = {}
        
        # 智能体识别模式
        self.agent_patterns = {
            "class_suffix": ["Agent", "智能体"],
            "base_class": "BaseAgent",
            "get_function_prefix": "get_",
            "file_patterns": ["*agent*.py", "*智能体*.py"]
        }
        
        # 工具识别模式
        self.tool_patterns = {
            "class_suffix": ["Tool", "工具"],
            "function_suffix": ["_tool", "_工具"],
            "file_patterns": ["*tool*.py", "*工具*.py"]
        }
    
    def discover_agents(self) -> Dict[str, Dict]:
        """自动发现系统中的所有智能体"""
        self.discovered_agents.clear()
        
        # 检查基础路径是否存在
        if not self.base_path.exists():
            logger.error(f"基础路径不存在: {self.base_path}")
            return {
                "error": "基础路径不存在",
                "status": "配置错误",
                "message": f"指定的基础路径 {self.base_path} 不存在",
                "recommendation": "请检查base_path参数配置"
            }
        
        try:
            # 递归扫描Python文件
            python_files = list(self.base_path.rglob("*.py"))
            logger.info(f"扫描到 {len(python_files)} 个Python文件")
            
            if not python_files:
                logger.warning("未找到任何Python文件")
                return {
                    "error": "未找到Python文件",
                    "status": "扫描完成",
                    "message": f"在路径 {self.base_path} 下未找到任何Python文件",
                    "recommendation": "请检查文件路径和文件扩展名"
                }
            
            # 分析每个文件
            for file_path in python_files:
                if self._is_agent_file(file_path):
                    self._analyze_agent_file(file_path)
            
            logger.info(f"发现 {len(self.discovered_agents)} 个智能体")
            
            if self.discovered_agents:
                return self.discovered_agents
            else:
                return {
                    "error": "未发现智能体",
                    "status": "扫描完成",
                    "message": "文件扫描完成，但未发现符合智能体模式的文件",
                    "recommendation": "请检查智能体命名规范或手动配置智能体"
                }
                
        except Exception as e:
            logger.error(f"智能体发现过程出错: {e}")
            return {
                "error": "发现过程异常",
                "status": "执行错误",
                "message": f"智能体发现过程中出现异常: {str(e)}",
                "recommendation": "请检查文件权限和Python语法"
            }
    
    def discover_tools(self, base_path: str = None, auto_submit_review: bool = True) -> Dict[str, Dict]:
        """
        自动发现系统中的所有工具，并自动提交审核
        
        Args:
            base_path: 基础路径，如果为None则使用初始化时设置的路径
            auto_submit_review: 是否自动提交发现的工具进行审核
            
        Returns:
            工具信息字典
        """
        self.discovered_tools.clear()
        
        # 使用指定的基础路径或默认路径
        scan_path = Path(base_path) if base_path else self.base_path
        
        # 检查基础路径是否存在
        if not scan_path.exists():
            logger.error(f"基础路径不存在: {scan_path}")
            return {
                "error": "基础路径不存在",
                "status": "配置错误",
                "message": f"指定的基础路径 {scan_path} 不存在",
                "recommendation": "请检查base_path参数配置"
            }
        
        try:
            # 递归扫描Python文件
            python_files = list(scan_path.rglob("*.py"))
            logger.info(f"扫描到 {len(python_files)} 个Python文件")
            
            if not python_files:
                logger.warning("未找到任何Python文件")
                return {
                    "error": "未找到Python文件",
                    "status": "扫描完成",
                    "message": f"在路径 {scan_path} 下未找到任何Python文件",
                    "recommendation": "请检查文件路径和文件扩展名"
                }
            
            # 分析每个文件
            for file_path in python_files:
                if self._is_tool_file(file_path):
                    self._analyze_tool_file(file_path)
            
            logger.info(f"发现 {len(self.discovered_tools)} 个工具")
            
            # 自动提交审核（如果启用）
            if auto_submit_review and self.discovered_tools:
                for tool_info in self.discovered_tools.values():
                    self._submit_tool_for_review(tool_info)
            
            if self.discovered_tools:
                return self.discovered_tools
            else:
                return {
                    "error": "未发现工具",
                    "status": "扫描完成",
                    "message": "文件扫描完成，但未发现符合工具模式的文件",
                    "recommendation": "请检查工具命名规范或手动配置工具"
                }
                
        except Exception as e:
            logger.error(f"工具发现过程出错: {e}")
            return {
                "error": "发现过程异常",
                "status": "执行错误",
                "message": f"工具发现过程中出现异常: {str(e)}",
                "recommendation": "请检查文件权限和Python语法"
            }
    
    def _submit_tool_for_review(self, tool_info: Dict[str, Any]):
        """提交工具进行审核"""
        try:
            # 修复导入路径
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from tool_review_manager import get_tool_review_manager
            
            review_manager = get_tool_review_manager()
            
            # 确保工具信息包含必要字段
            if 'tool_id' not in tool_info:
                tool_info['tool_id'] = f"tool_{tool_info.get('tool_name', 'unknown').replace(' ', '_').lower()}"
            
            if 'tool_name' not in tool_info:
                tool_info['tool_name'] = tool_info.get('class_name', tool_info.get('function_name', 'unknown'))
            
            # 添加发现信息
            tool_info['discovery_timestamp'] = self._get_timestamp()
            tool_info['discovery_source'] = 'agent_discovery_engine'
            
            # 提交审核
            review_manager.submit_tool_for_review(tool_info)
            logger.info(f"工具 {tool_info['tool_name']} 已提交审核")
            
        except Exception as e:
            logger.error(f"提交工具审核失败: {e}")
    
    def _extract_self_expose_protocol(self, content: str) -> List[str]:
        """提取文件中的@self-expose协议（支持嵌套JSON）
        
        Args:
            content: 文件内容
            
        Returns:
            List[str]: 提取到的JSON字符串列表
        """
        import re
        
        # 找到所有@self-expose:的位置
        expose_pattern = r'#\s*@self-expose:\s*'
        matches = []
        
        for match in re.finditer(expose_pattern, content):
            start_pos = match.end()
            
            # 从起始位置开始，手动解析完整的JSON对象
            brace_count = 0
            json_start = -1
            
            for i in range(start_pos, len(content)):
                char = content[i]
                
                if char == '{':
                    if json_start == -1:
                        json_start = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    
                    if brace_count == 0 and json_start != -1:
                        # 找到完整的JSON对象
                        json_str = content[json_start:i+1]
                        matches.append(json_str)
                        break
                elif char == '\n' and json_start == -1:
                    # 如果在找到{之前就换行，说明格式错误
                    break
        
        return matches
    
    def _is_agent_file(self, file_path: Path) -> bool:
        """判断文件是否为智能体文件"""
        filename = file_path.name.lower()
        
        # 检查文件名模式
        for pattern in self.agent_patterns["file_patterns"]:
            if pattern.replace("*", "") in filename:
                return True
        
        # 检查文件内容（简化版）
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否包含智能体相关关键词
            agent_keywords = ["Agent", "智能体", "get_", "BaseAgent"]
            return any(keyword in content for keyword in agent_keywords)
        except:
            return False
    
    def _is_tool_file(self, file_path: Path) -> bool:
        """判断文件是否为工具文件"""
        filename = file_path.name.lower()
        
        # 检查文件名模式
        for pattern in self.tool_patterns["file_patterns"]:
            if pattern.replace("*", "") in filename:
                return True
        
        # 检查文件内容（简化版）
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否包含工具相关关键词
            tool_keywords = ["Tool", "工具", "_tool", "_工具"]
            return any(keyword in content for keyword in tool_keywords)
        except:
            return False
    
    def _analyze_agent_file(self, file_path: Path):
        """分析智能体文件并提取信息（基于组件自曝光协议，不依赖导入）"""
        try:
            # 新方法：读取文件内容，解析@self-expose协议
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用通用提取函数（支持嵌套JSON）
            import json
            matches = self._extract_self_expose_protocol(content)
            
            if not matches:
                # 没有自曝光协议，不是标准组件
                logger.debug(f"文件 {file_path.name} 未声明@self-expose协议，跳过")
                return
            
            # 解析协议内容
            for expose_str in matches:
                try:
                    expose_data = json.loads(expose_str)
                    
                    # 检查是否为智能体（type="agent"）
                    if expose_data.get('type') != 'agent':
                        continue
                    
                    # 验证是否基于BaseAgent模板（检查provides.capabilities）
                    provides = expose_data.get('provides', {})
                    if not self._is_based_on_base_agent(provides, content):
                        logger.debug(f"组件 {expose_data.get('id')} 不是BaseAgent智能体")
                        continue
                    
                    # 提取智能体信息（无需导入！）
                    agent_info = self._extract_agent_info_from_protocol(
                        expose_data, file_path, content
                    )
                    
                    if agent_info:
                        self.discovered_agents[agent_info["agent_id"]] = agent_info
                        logger.info(f"✅ 发现智能体: {agent_info['agent_id']} ({file_path.name})")
                        
                except json.JSONDecodeError as je:
                    logger.warning(f"解析@self-expose协议失败 ({file_path.name}): {je}")
                    continue
                        
        except Exception as e:
            logger.warning(f"分析智能体文件 {file_path} 失败: {e}")
    
    def _is_based_on_base_agent(self, provides: Dict, content: str) -> bool:
        """检查是否基于BaseAgent模板（不需导入，基于特征匹配）
        
        检查逻辑：
        1. 检查provides.capabilities是否包含BaseAgent核心能力
        2. 检查provides.methods是否包含BaseAgent标志性方法
        3. 检查文件内容是否包含'class XXX(BaseAgent)'或'from .base_agent import BaseAgent'
        """
        # 检查1：核心能力
        capabilities = provides.get('capabilities', [])
        base_agent_capabilities = [
            '基础智能体能力', '工具调用', '记忆管理', 
            '泡泡系统', '反馈系统'
        ]
        
        # 如果包含2个以上的BaseAgent核心能力，则认为是BaseAgent
        matches = sum(1 for cap in base_agent_capabilities if cap in capabilities)
        if matches >= 2:
            return True
        
        # 检查2：标志性方法
        methods = provides.get('methods', {})
        base_agent_methods = ['respond', 'call_tool', 'create_memory', 'note_bubble', 'write_daily_diary']
        
        # 如果包含3个以上的BaseAgent方法，则认为是BaseAgent
        method_matches = sum(1 for method in base_agent_methods if method in methods)
        if method_matches >= 3:
            return True
        
        # 检查3：文件内容检查（继承关系）
        inheritance_patterns = [
            r'class\s+\w+\(BaseAgent\)',  # class XXX(BaseAgent)
            r'from\s+\.base_agent\s+import\s+BaseAgent',  # from .base_agent import BaseAgent
            r'from\s+src\.base_agent\s+import\s+BaseAgent',  # from src.base_agent import BaseAgent
        ]
        
        import re
        for pattern in inheritance_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _extract_agent_info_from_protocol(self, expose_data: Dict, file_path: Path, content: str) -> Optional[Dict]:
        """从自曝光协议提取智能体信息（无需导入）
        
        Args:
            expose_data: 自曝光协议数据
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            智能体信息字典
        """
        try:
            agent_id = expose_data.get('id')
            agent_name = expose_data.get('name', agent_id)
            
            if not agent_id:
                return None
            
            # 提取模块名（用于后续导入）
            module_path = str(file_path.relative_to(self.base_path)).replace("/", ".").replace("\\", ".")
            module_name = f"src.{module_path[:-3]}" if not module_path.startswith('src') else module_path[:-3]
            
            # 提取get_函数名（如果有）
            import re
            get_function_pattern = r'def\s+(get_\w+)\(\)'
            get_functions = re.findall(get_function_pattern, content)
            
            # 提取类名（如果有）
            class_pattern = r'class\s+(\w+Agent)\(BaseAgent\)'
            class_names = re.findall(class_pattern, content)
            
            # 确定智能体类型（function 或 class）
            agent_type = "unknown"
            agent_accessor = None
            
            if get_functions:
                agent_type = "function"
                agent_accessor = get_functions[0]
            elif class_names:
                agent_type = "class"
                agent_accessor = class_names[0]
            
            # 构建智能体信息
            agent_info = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "type": agent_type,
                "module_name": module_name,
                "file_path": str(file_path),
                "version": expose_data.get('version', '1.0.0'),
                "capabilities": expose_data.get('provides', {}).get('capabilities', []),
                "methods": expose_data.get('provides', {}).get('methods', {}),
                "dependencies": expose_data.get('needs', {}).get('deps', []),
                "discovery_method": "protocol_based",  # 关键：基于协议
                "discovery_time": self._get_timestamp(),
                "supports_relative_import": True,  # 支持相对导入
            }
            
            # 添加访问器信息
            if agent_type == "function":
                agent_info["function_name"] = agent_accessor
            elif agent_type == "class":
                agent_info["class_name"] = agent_accessor
            
            return agent_info
            
        except Exception as e:
            logger.error(f"提取智能体信息失败: {e}")
            return None
    
    def _analyze_tool_file(self, file_path: Path):
        """分析工具文件并提取信息（基于组件自曝光协议，不依赖导入）"""
        try:
            # 新方法：读取文件内容，解析@self-expose协议
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用通用提取函数（支持嵌套JSON）
            import json
            matches = self._extract_self_expose_protocol(content)
            
            if not matches:
                # 没有自曝光协议，不是标准组件
                logger.debug(f"文件 {file_path.name} 未声明@self-expose协议，跳过")
                return
            
            # 解析协议内容
            for expose_str in matches:
                try:
                    expose_data = json.loads(expose_str)
                    
                    # 检查是否为工具（type="tool"）
                    if expose_data.get('type') != 'tool':
                        continue
                    
                    # 提取工具信息（无需导入！）
                    tool_info = self._extract_tool_info_from_protocol(
                        expose_data, file_path, content
                    )
                    
                    if tool_info:
                        self.discovered_tools[tool_info["tool_id"]] = tool_info
                        logger.info(f"✅ 发现工具: {tool_info['tool_id']} ({file_path.name})")
                        
                except json.JSONDecodeError as je:
                    logger.warning(f"解析@self-expose协议失败 ({file_path.name}): {je}")
                    continue
                        
        except Exception as e:
            logger.warning(f"分析工具文件 {file_path} 失败: {e}")
    
    def _extract_tool_info_from_protocol(self, expose_data: Dict, file_path: Path, content: str) -> Optional[Dict]:
        """从自曝光协议提取工具信息（无需导入）"""
        try:
            tool_id = expose_data.get('id')
            tool_name = expose_data.get('name', tool_id)
            
            # 提取模块名（用于后续导入）
            module_path = str(file_path.relative_to(self.base_path)).replace("/", ".").replace("\\", ".")
            module_name = f"src.{module_path[:-3]}" if not module_path.startswith('src') else module_path[:-3]
            
            # 检测工具类型（类/函数）
            import re
            class_pattern = r'class\s+(\w+Tool|\w+Manager)\('
            function_pattern = r'def\s+(\w+_tool)\('
            
            tool_classes = re.findall(class_pattern, content)
            tool_functions = re.findall(function_pattern, content)
            
            # 确定工具类型和访问者
            tool_type = "unknown"
            tool_accessor = None
            
            if tool_classes:
                tool_type = "class"
                tool_accessor = tool_classes[0]
            elif tool_functions:
                tool_type = "function"
                tool_accessor = tool_functions[0]
            
            # 构建工具信息
            tool_info = {
                "tool_id": tool_id,
                "tool_name": tool_name,
                "type": tool_type,
                "module_name": module_name,
                "file_path": str(file_path),
                "version": expose_data.get('version', '1.0.0'),
                "capabilities": expose_data.get('provides', {}).get('capabilities', []),
                "methods": expose_data.get('provides', {}).get('methods', {}),
                "dependencies": expose_data.get('needs', {}).get('deps', []),
                "discovery_method": "protocol_based",  # 关键：基于协议
                "discovery_time": self._get_timestamp(),
                "supports_relative_import": True,  # 支持相对导入
            }
            
            if tool_accessor:
                if tool_type == "class":
                    tool_info["class_name"] = tool_accessor
                elif tool_type == "function":
                    tool_info["function_name"] = tool_accessor
            
            return tool_info
            
        except Exception as e:
            logger.error(f"提取工具信息失败: {e}")
            return None
    
    def _is_agent_class(self, obj) -> bool:
        """判断是否为智能体类（必须满足LLM核心大脑特征）"""
        class_name = obj.__name__
        
        # 检查继承关系 - 必须继承BaseAgent
        try:
            from .base_agent import BaseAgent
            if not issubclass(obj, BaseAgent):
                return False
            
            # 关键修复：过滤掉BaseAgent本身，它只是基类模板，不是真正的智能体
            if obj == BaseAgent:
                return False
        except:
            return False
        
        # 检查是否具有LLM集成特征
        if not self._has_llm_integration(obj):
            return False
            
        # 检查是否具有自主决策能力
        if not self._has_autonomous_decision_making(obj):
            return False
            
        return True
    
    def _has_llm_integration(self, obj) -> bool:
        """检查类是否具有LLM集成特征"""
        try:
            # 检查是否导入LLM相关模块
            import inspect
            source = inspect.getsource(obj)
            
            # 检查LLM相关的导入和引用
            llm_indicators = [
                'LLMClientEnhanced', 'llm_client_enhanced',
                'api_key_manager', 'config.api_keys',
                'process_user_query', 'get_system_prompt'
            ]
            
            for indicator in llm_indicators:
                if indicator in source:
                    return True
                    
            # 检查是否有LLM相关的方法或属性
            if hasattr(obj, 'llm_client') or hasattr(obj, '_llm_client'):
                return True
                
            return False
        except:
            return False
    
    def _has_autonomous_decision_making(self, obj) -> bool:
        """检查类是否具有自主决策能力"""
        try:
            import inspect
            source = inspect.getsource(obj)
            
            # 检查自主决策相关的特征
            decision_indicators = [
                'process_user_query', 'handle_request', 'make_decision',
                'autonomous', 'decision_making', 'tool_integrator'
            ]
            
            for indicator in decision_indicators:
                if indicator in source:
                    return True
                    
            # 检查是否有工具集成器
            if hasattr(obj, 'tool_integrator') or hasattr(obj, '_tool_integrator'):
                return True
                
            return False
        except:
            return False
    
    def _is_get_agent_function(self, obj) -> bool:
        """判断是否为获取智能体函数（必须返回真正的智能体实例）"""
        func_name = obj.__name__
        
        # 检查函数名前缀
        if not func_name.startswith(self.agent_patterns["get_function_prefix"]):
            return False
            
        # 检查函数是否返回智能体实例
        try:
            import inspect
            source = inspect.getsource(obj)
            
            # 检查是否返回BaseAgent实例
            if 'BaseAgent' in source and 'return' in source:
                return True
                
            return False
        except:
            return False
    
    def _is_tool_class(self, obj) -> bool:
        """判断是否为工具类"""
        class_name = obj.__name__
        
        # 检查类名后缀
        for suffix in self.tool_patterns["class_suffix"]:
            if class_name.endswith(suffix):
                return True
        return False
    
    def _is_tool_function(self, obj) -> bool:
        """判断是否为工具函数"""
        func_name = obj.__name__
        
        # 检查函数名后缀
        for suffix in self.tool_patterns["function_suffix"]:
            if func_name.endswith(suffix):
                return True
        return False
    
    def _extract_agent_info(self, agent_class, module_name: str) -> Optional[Dict]:
        """从智能体类中提取信息"""
        try:
            # 获取智能体ID（类名转换为小写蛇形）
            class_name = agent_class.__name__
            agent_id = self._to_snake_case(class_name).replace('_agent', '')
            
            # 提取文档字符串
            docstring = inspect.getdoc(agent_class) or ""
            
            return {
                "agent_id": agent_id,
                "class_name": class_name,
                "module_name": module_name,
                "type": "class",
                "description": docstring.split('\n')[0] if docstring else f"{class_name} 智能体",
                "file_path": f"{module_name.replace('.', '/')}.py",
                "discovery_time": self._get_timestamp()
            }
        except Exception as e:
            logger.warning(f"提取智能体信息失败: {e}")
            return None
    
    def _extract_agent_from_function(self, func, module_name: str) -> Optional[Dict]:
        """从获取函数中提取智能体信息"""
        try:
            func_name = func.__name__
            agent_id = func_name.replace('get_', '')
            
            # 提取文档字符串
            docstring = inspect.getdoc(func) or ""
            
            return {
                "agent_id": agent_id,
                "function_name": func_name,
                "module_name": module_name,
                "type": "function",
                "description": docstring.split('\n')[0] if docstring else f"{func_name} 智能体",
                "file_path": f"{module_name.replace('.', '/')}.py",
                "discovery_time": self._get_timestamp()
            }
        except Exception as e:
            logger.warning(f"从函数提取智能体信息失败: {e}")
            return None
    
    def _extract_tool_info(self, tool_class, module_name: str) -> Optional[Dict]:
        """从工具类中提取信息"""
        try:
            class_name = tool_class.__name__
            tool_id = self._to_snake_case(class_name).replace('_tool', '')
            
            # 提取文档字符串
            docstring = inspect.getdoc(tool_class) or ""
            
            return {
                "tool_id": tool_id,
                "class_name": class_name,
                "module_name": module_name,
                "type": "class",
                "description": docstring.split('\n')[0] if docstring else f"{class_name} 工具",
                "file_path": f"{module_name.replace('.', '/')}.py",
                "discovery_time": self._get_timestamp()
            }
        except Exception as e:
            logger.warning(f"提取工具信息失败: {e}")
            return None
    
    def _extract_tool_from_function(self, func, module_name: str) -> Optional[Dict]:
        """从工具函数中提取信息"""
        try:
            func_name = func.__name__
            tool_id = func_name.replace('_tool', '').replace('_工具', '')
            
            # 提取文档字符串
            docstring = inspect.getdoc(func) or ""
            
            return {
                "tool_id": tool_id,
                "function_name": func_name,
                "module_name": module_name,
                "type": "function",
                "description": docstring.split('\n')[0] if docstring else f"{func_name} 工具",
                "file_path": f"{module_name.replace('.', '/')}.py",
                "discovery_time": self._get_timestamp()
            }
        except Exception as e:
            logger.warning(f"从函数提取工具信息失败: {e}")
            return None
    
    def _to_snake_case(self, text: str) -> str:
        """转换为蛇形命名"""
        import re
        # 将驼峰命名转换为蛇形命名
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
        return text.lower()
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_registration_code(self) -> str:
        """生成自动注册代码"""
        code_lines = []
        
        # 智能体注册代码
        code_lines.append("# 智能体自动注册代码")
        code_lines.append("def auto_register_agents(agent_manager):")
        
        for agent_id, agent_info in self.discovered_agents.items():
            if agent_info["type"] == "function":
                code_lines.append(f"    # 注册 {agent_id} 智能体")
                code_lines.append(f"    from {agent_info['module_name']} import {agent_info['function_name']}")
                code_lines.append(f"    agent_instance = {agent_info['function_name']}()")
                code_lines.append(f"    agent_manager.agents['{agent_id}'] = agent_instance")
                code_lines.append(f"    agent_manager.agent_status['{agent_id}'] = {{")
                code_lines.append(f"        'status': 'active',")
                code_lines.append(f"        'last_active': '{agent_info['discovery_time']}',")
                code_lines.append(f"        'request_count': 0")
                code_lines.append(f"    }}")
                code_lines.append("")
        
        code_lines.append("    return agent_manager")
        
        return "\n".join(code_lines)

# 全局发现引擎实例
_discovery_engine = None

def get_discovery_engine() -> AgentDiscoveryEngine:
    """获取发现引擎实例（单例模式）"""
    global _discovery_engine
    if _discovery_engine is None:
        _discovery_engine = AgentDiscoveryEngine()
    return _discovery_engine

def discover_all_components() -> Dict[str, Dict]:
    """发现所有组件（智能体和工具）
    
    Returns:
        Dict: {
            "agents": {agent_id: agent_info, ...},
            "tools": {tool_id: tool_info, ...},
            "summary": {...}
        }
        注意：如果发现失败，返回空字典而非错误信息
    """
    engine = get_discovery_engine()
    
    agents = engine.discover_agents()
    tools = engine.discover_tools(auto_submit_review=False)
    
    # 过滤掉错误信息，只返回有效的组件
    valid_agents = {k: v for k, v in agents.items() if k not in ["error", "status", "message", "recommendation"]}
    valid_tools = {k: v for k, v in tools.items() if k not in ["error", "status", "message", "recommendation"]}
    
    return {
        "agents": valid_agents,
        "tools": valid_tools,
        "summary": {
            "total_agents": len(valid_agents),
            "total_tools": len(valid_tools),
            "discovery_time": engine._get_timestamp()
        }
    }