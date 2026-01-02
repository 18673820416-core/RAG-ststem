# @self-expose: {"id": "code_implementer_agent", "name": "Code Implementer Agent", "type": "agent", "version": "1.0.0", "needs": {"deps": ["base_agent"], "resources": []}, "provides": {"capabilities": ["文本实现", "代码生成", "代码审核", "代码质量分析"], "methods": {"process_user_query": {"signature": "(query: str) -> Dict[str, Any]", "description": "处理用户查询"}}}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文本实现师智能体 - 基于统一模板的文本实现助手
开发提示词来源：用户建议统一智能体模板，将提示词外部化
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import difflib

from base_agent import BaseAgent
from llm_client_enhanced import LLMClientEnhanced
from config.api_keys import api_key_manager

logger = logging.getLogger(__name__)

class TextImplementerAgent(BaseAgent):
    """文本实现师智能体 - 基于统一模板的文本实现助手"""
    
    def __init__(self, agent_id: str = "implementer_001"):
        """初始化文本实现师智能体"""
        super().__init__(
            agent_id=agent_id,
            agent_type="text_implementer",
            prompt_file="src/agent_prompts/code_implementer_prompt.txt"
        )
        
        # 设置智能体目的（角色由系统提示词定义）
        self.purpose = "负责将设计方案转化为可执行的文本实现，确保文本质量和系统稳定性"
        
        # 待审核文本队列
        self.pending_approvals = []
        
        # 记录启动日志
        self._write_work_log("文本实现师智能体启动 - 角色：文本实现师，权限：自主实现", "系统启动")
    
    def generate_implementation(self, scheme_data: Dict) -> Dict:
        """
        生成实现代码（不直接写入文件）
        
        Args:
            scheme_data: 通过评估的方案数据
            
        Returns:
            包含生成代码和差异信息的字典
        """
        logger.info(f"开始生成方案实现: {scheme_data.get('title', '未知方案')}")
        
        # 生成代码实现（示例）
        implementation = {
            "scheme_id": scheme_data.get("id", "unknown"),
            "title": scheme_data.get("title", "未知方案"),
            "generated_code": "# 这是生成的代码示例\n# 实际实现需要根据具体方案生成",
            "target_files": ["src/example.py"],
            "dependencies": [],
            "estimated_time": "1小时",
            "risk_level": "低",
            "generated_at": datetime.now().isoformat()
        }
        
        # 记录生成过程
        self._write_work_log(f"方案 {implementation['title']} 代码生成完成", "代码生成")
        
        # 记录到日记
        self._record_implementation_generation(scheme_data, implementation)
        
        return implementation
    
    def submit_for_approval(self, implementation: Dict) -> str:
        """
        提交代码给审核
        
        Args:
            implementation: 生成的实现代码
            
        Returns:
            审核请求ID
        """
        approval_id = f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        approval_request = {
            "id": approval_id,
            "implementation": implementation,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "feedback": None,
            "approved_at": None
        }
        
        # 添加到待审核队列
        self.pending_approvals.append(approval_request)
        
        logger.info(f"提交代码审核请求: {approval_id} - {implementation['title']}")
        
        # 记录审核提交
        self._record_approval_submission(approval_request)
        
        return approval_id
    
    def get_approval_status(self, approval_id: str) -> Optional[Dict]:
        """获取审核状态"""
        for request in self.pending_approvals:
            if request["id"] == approval_id:
                return request
        return None
    
    def execute_approved_implementation(self, approval_id: str) -> bool:
        """
        执行批准的代码实现
        
        Args:
            approval_id: 审核请求ID
            
        Returns:
            执行是否成功
        """
        approval_request = self.get_approval_status(approval_id)
        
        if not approval_request or approval_request["status"] != "approved":
            logger.error(f"执行失败：审核请求 {approval_id} 未批准")
            return False
        
        try:
            implementation = approval_request["implementation"]
            
            # 这里应该执行实际的代码写入
            # 但为了安全，我们只记录执行意图
            
            logger.info(f"执行批准的代码实现: {implementation['title']}")
            
            # 标记为已执行
            approval_request["executed_at"] = datetime.now().isoformat()
            approval_request["status"] = "executed"
            
            # 记录执行结果
            self._record_implementation_execution(approval_request)
            
            return True
            
        except Exception as e:
            logger.error(f"执行代码时出错: {e}")
            return False
    
    def preview_changes(self, implementation: Dict) -> str:
        """
        生成代码变更预览
        
        Args:
            implementation: 生成的实现代码
            
        Returns:
            变更预览文本
        """
        # 生成变更预览
        preview = f"""# 代码变更预览

## 方案信息
- 方案标题: {implementation['title']}
- 目标文件: {', '.join(implementation['target_files'])}
- 预估时间: {implementation['estimated_time']}
- 风险等级: {implementation['risk_level']}

## 生成代码
```python
{implementation['generated_code']}
```

## 依赖项
{chr(10).join(['- ' + dep for dep in implementation['dependencies']]) if implementation['dependencies'] else '无依赖项'}
"""
        
        return preview
    
    def analyze_code_quality(self, code: str) -> Dict:
        """
        分析代码质量
        
        Args:
            code: 要分析的代码
            
        Returns:
            代码质量分析结果
        """
        quality_analysis = {
            "lines_of_code": len(code.split('\n')),
            "has_docstrings": '"""' in code,
            "has_comments": "#" in code,
            "complexity_indicators": [],
            "style_issues": [],
            "security_concerns": []
        }
        
        # 简单的复杂度分析
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 检查嵌套深度
            if line.count('    ') > 3:
                quality_analysis["complexity_indicators"].append(f"第{i+1}行嵌套过深")
            
            # 检查行长度
            if len(line) > 100:
                quality_analysis["style_issues"].append(f"第{i+1}行过长")
            
            # 检查潜在安全问题
            if any(keyword in line for keyword in ['eval', 'exec', 'input']):
                quality_analysis["security_concerns"].append(f"第{i+1}行使用潜在危险函数")
        
        # 记录质量分析
        self._record_code_quality_analysis(code, quality_analysis)
        
        return quality_analysis
    
    def generate_test_cases(self, implementation: Dict) -> List[Dict]:
        """
        生成测试用例
        
        Args:
            implementation: 实现代码
            
        Returns:
            测试用例列表
        """
        test_cases = [
            {
                "name": "基本功能测试",
                "description": "测试代码的基本功能是否正常",
                "expected_result": "功能正常执行",
                "priority": "高"
            },
            {
                "name": "边界条件测试",
                "description": "测试边界条件下的代码行为",
                "expected_result": "正确处理边界情况",
                "priority": "中"
            },
            {
                "name": "错误处理测试",
                "description": "测试代码的错误处理能力",
                "expected_result": "正确捕获和处理错误",
                "priority": "中"
            }
        ]
        
        # 记录测试用例生成
        self._record_test_case_generation(implementation, test_cases)
        
        return test_cases
    
    def process_user_query(self, query: str) -> Dict[str, Any]:
        """
        处理用户查询 - 基于代码实现的工作流程
        
        Args:
            query: 用户查询
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"处理用户查询: {query}")
        
        # 记录对话历史
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'user',
            'content': query
        })
        
        # 分析查询类型
        query_analysis = self._analyze_implementation_query(query)
        
        # 根据查询类型执行相应操作
        if query_analysis['query_type'] == 'code_generation':
            # 模拟方案数据
            scheme_data = {
                'id': 'test_scheme_001',
                'title': '测试方案',
                'description': query
            }
            result = self.generate_implementation(scheme_data)
        elif query_analysis['query_type'] == 'code_analysis':
            result = {'analysis': self.analyze_code_quality(query)}
        elif query_analysis['query_type'] == 'test_generation':
            # 模拟实现数据
            implementation = {
                'title': '测试实现',
                'generated_code': query
            }
            result = {'test_cases': self.generate_test_cases(implementation)}
        else:
            result = {'message': '暂不支持该类型的查询'}
        
        # 记录处理结果
        self._record_query_processing(query, query_analysis, result)
        
        return {
            'query': query,
            'query_analysis': query_analysis,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_implementation_query(self, query: str) -> Dict:
        """分析实现查询类型"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['生成', '实现', '编写', 'generate']):
            return {
                'query_type': 'code_generation',
                'description': '代码生成'
            }
        elif any(keyword in query_lower for keyword in ['分析', '检查', '质量', 'analyze']):
            return {
                'query_type': 'code_analysis',
                'description': '代码分析'
            }
        elif any(keyword in query_lower for keyword in ['测试', '用例', 'test']):
            return {
                'query_type': 'test_generation',
                'description': '测试生成'
            }
        else:
            return {
                'query_type': 'general',
                'description': '一般查询'
            }
    
    def _record_implementation_generation(self, scheme_data: Dict, implementation: Dict):
        """记录代码生成过程"""
        generation_entry = {
            'type': 'implementation_generation',
            'scheme_data': scheme_data,
            'implementation': implementation,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(generation_entry)
    
    def _record_approval_submission(self, approval_request: Dict):
        """记录审核提交"""
        approval_entry = {
            'type': 'approval_submission',
            'approval_request': approval_request,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(approval_entry)
    
    def _record_implementation_execution(self, approval_request: Dict):
        """记录代码执行"""
        execution_entry = {
            'type': 'implementation_execution',
            'approval_request': approval_request,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(execution_entry)
    
    def _record_code_quality_analysis(self, code: str, quality_analysis: Dict):
        """记录代码质量分析"""
        analysis_entry = {
            'type': 'code_quality_analysis',
            'code_preview': code[:500],  # 只记录前500字符
            'quality_analysis': quality_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(analysis_entry)
    
    def _record_test_case_generation(self, implementation: Dict, test_cases: List[Dict]):
        """记录测试用例生成"""
        test_entry = {
            'type': 'test_case_generation',
            'implementation': implementation,
            'test_cases': test_cases,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(test_entry)
    
    def _record_query_processing(self, query: str, query_analysis: Dict, result: Dict):
        """记录查询处理过程"""
        processing_entry = {
            'type': 'query_processing',
            'query': query,
            'query_analysis': query_analysis,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_to_diary(processing_entry)

# 全局智能体实例(懒加载)
_implementer_agent = None

def get_text_implementer() -> TextImplementerAgent:
    """获取文本实现师智能体实例(懒加载)"""
    global _implementer_agent
    if _implementer_agent is None:
        _implementer_agent = TextImplementerAgent()
    return _implementer_agent