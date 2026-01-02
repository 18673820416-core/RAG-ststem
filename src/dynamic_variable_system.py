# @self-expose: {"id": "dynamic_variable_system", "name": "Dynamic Variable System", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Dynamic Variable System功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
动态变量替换系统
基于VCP系统设计理念实现
来源：VCP系统Nova设计理念
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class DynamicVariableSystem:
    """动态变量替换系统"""
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = base_path
        self.variables = {}
        self.tool_registry = {}
        self.memory_systems = {}
        
        # 初始化基础变量
        self._initialize_base_variables()
    
    def _initialize_base_variables(self):
        """初始化基础变量"""
        # 系统信息变量
        self.variables.update({
            '{{VarUser}}': '系统架构师',
            '{{VarSystemInfo}}': 'RAG系统架构师智能体',
            '{{VarTimestamp}}': datetime.now().isoformat(),
            '{{VarSystemPath}}': self.base_path,
        })
    
    def register_tool(self, tool_name: str, tool_description: str, 
                     tool_usage: str, tool_parameters: Dict[str, Any]):
        """注册工具到变量系统"""
        tool_key = f"{{{{Tool_{tool_name}}}}}"
        self.tool_registry[tool_name] = {
            'description': tool_description,
            'usage': tool_usage,
            'parameters': tool_parameters
        }
        
        # 更新工具列表变量
        self._update_tool_list_variable()
    
    def register_memory_system(self, system_name: str, system_config: Dict[str, Any]):
        """注册记忆系统"""
        self.memory_systems[system_name] = system_config
        
        # 更新记忆系统变量
        self._update_memory_system_variables()
    
    def _update_tool_list_variable(self):
        """更新工具列表变量"""
        tool_list = []
        for tool_name, tool_info in self.tool_registry.items():
            tool_list.append({
                'name': tool_name,
                'description': tool_info['description'],
                'usage': tool_info['usage']
            })
        
        self.variables['{{VarToolList}}'] = json.dumps(tool_list, ensure_ascii=False, indent=2)
    
    def _update_memory_system_variables(self):
        """更新记忆系统变量"""
        memory_info = []
        for system_name, config in self.memory_systems.items():
            memory_info.append({
                'system': system_name,
                'config': config
            })
        
        self.variables['{{VarMemorySystems}}'] = json.dumps(memory_info, ensure_ascii=False, indent=2)
    
    def inject_context(self, context_data: Dict[str, Any]):
        """注入上下文数据"""
        for key, value in context_data.items():
            var_key = f"{{{{Context_{key}}}}}"
            self.variables[var_key] = str(value)
    
    def replace_variables(self, template: str) -> str:
        """替换模板中的变量"""
        result = template
        
        # 按变量长度降序排序，避免嵌套替换问题
        sorted_vars = sorted(self.variables.keys(), key=len, reverse=True)
        
        for var_key in sorted_vars:
            if var_key in result:
                result = result.replace(var_key, str(self.variables[var_key]))
        
        return result
    
    def get_tool_call_template(self, tool_name: str) -> Optional[str]:
        """获取工具调用模板"""
        if tool_name not in self.tool_registry:
            return None
        
        tool_info = self.tool_registry[tool_name]
        template = f"""
<<<[TOOL_REQUEST]>>>
tool_name:『始』{tool_name}『末』,
"""
        
        # 添加参数模板
        for param_name, param_info in tool_info['parameters'].items():
            template += f"{param_name}:『始』{param_info.get('default', '')}『末』,\n"
        
        template += "<<<[END_TOOL_REQUEST]>>>"
        return template
    
    def parse_tool_response(self, response_text: str) -> Dict[str, Any]:
        """解析工具响应"""
        # 简单的响应解析逻辑
        result = {
            'success': False,
            'data': {},
            'message': ''
        }
        
        try:
            # 尝试解析JSON响应
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                result.update({
                    'success': True,
                    'data': data,
                    'message': '工具调用成功'
                })
            else:
                # 文本响应
                result.update({
                    'success': True,
                    'data': {'text': response_text},
                    'message': '工具调用成功'
                })
        except Exception as e:
            result['message'] = f'工具响应解析失败: {str(e)}'
        
        return result

# 全局变量系统实例
variable_system = DynamicVariableSystem()

def get_variable_system() -> DynamicVariableSystem:
    """获取全局变量系统实例"""
    return variable_system