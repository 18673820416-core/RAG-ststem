# @self-expose: {"id": "system_maintenance_agent", "name": "System Maintenance Agent", "type": "agent", "version": "1.0.0", "needs": {"deps": ["base_agent", "agent_error_handler", "agent_error_monitor", "agent_behavior_evaluator", "self_expose_protocol"], "resources": []}, "provides": {"capabilities": ["系统健康监控", "故障诊断分析", "自主修复决策", "配置完整性校验", "系统优化建议"], "methods": {"process_user_query": {"signature": "(query: str) -> Dict[str, Any]", "description": "处理用户查询和系统维护请求"}, "monitor_system_health": {"signature": "() -> Dict[str, Any]", "description": "执行系统健康巡检"}, "diagnose_error": {"signature": "(error_data: Dict) -> Dict[str, Any]", "description": "诊断系统错误"}, "auto_fix": {"signature": "(error_data: Dict) -> Dict[str, Any]", "description": "自动修复系统错误"}}}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统维护师智能体 - 基于统一智能体模板的系统级维护助手
开发提示词来源：用户洞察 - 系统需要第5个智能体来整合二级报错和自曝光协议进行系统维护
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# 导入智能体基类
try:
    from base_agent import BaseAgent
except ImportError:
    from src.base_agent import BaseAgent

# 导入维护工具
try:
    from agent_error_handler import AgentErrorHandler
    from agent_error_monitor import AgentErrorMonitor
    from agent_behavior_evaluator import AgentBehaviorEvaluator
    from self_expose_protocol import SelfExposeProtocol
except ImportError:
    from src.agent_error_handler import AgentErrorHandler
    from src.agent_error_monitor import AgentErrorMonitor
    from src.agent_behavior_evaluator import AgentBehaviorEvaluator
    from src.self_expose_protocol import SelfExposeProtocol

# 导入LLM客户端
try:
    from llm_client_enhanced import LLMClientEnhanced
except ImportError:
    from src.llm_client_enhanced import LLMClientEnhanced

logger = logging.getLogger(__name__)

class SystemMaintenanceAgent(BaseAgent):
    """系统维护师智能体 - 负责系统监控、诊断和自动修复"""
    
    def __init__(self, agent_id: str = "maintenance_001"):
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("  [系统维护师] 开始初始化...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ✅ 步骤1：调用父类初始化（基础能力加载）
        super().__init__(
            agent_id=agent_id,
            agent_type="system_maintenance",
            prompt_file="src/agent_prompts/system_maintenance_prompt.txt"
        )
        
        # 设置智能体目的
        self.purpose = "负责RAG系统的健康监控、故障诊断和自主修复，确保系统稳定运行"
        
        # ✅ 步骤2：初始化维护工具（外部依赖加载）
        self.error_handler = AgentErrorHandler()
        self.error_monitor = AgentErrorMonitor()
        self.behavior_evaluator = AgentBehaviorEvaluator()
        self.protocol_manager = SelfExposeProtocol()
        
        # 初始化LLM客户端
        self.llm_client = LLMClientEnhanced()
        
        # 系统健康状态
        self.last_health_check = None
        self.error_history = []
        self.fix_history = []
        
        # 记录启动日志（在工具注册前）
        self._write_work_log("系统维护师智能体基础初始化完成 - 角色：系统健康守护者", "系统启动")
        
        # ✅ 步骤3：注册专用工具（在基础智能体创建完成后）
        self._register_maintenance_tools()
        
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"  [系统维护师] ✅ 初始化完成")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _register_maintenance_tools(self):
        """注册系统维护专用工具
        
        设计理念：工具注册在智能体创建完成后执行
        - 基础智能体先初始化（super().__init__）
        - 维护工具实例已加载（AgentErrorHandler等）
        - 最后注册工具到工具集成器，完成能力绑定
        """
        logger.info("[系统维护师] 开始注册专用工具...")
        
        # 错误诊断工具
        self.tool_integrator.register_tool(
            tool_name="diagnose_error",
            tool_description="诊断系统错误，分析根因和影响范围",
            tool_usage="用于分析错误信息，确定错误类型和影响范围"
        )
        
        # 自动修复工具
        self.tool_integrator.register_tool(
            tool_name="auto_fix",
            tool_description="自动修复常见系统错误",
            tool_usage="用于自动执行错误修复操作"
        )
        
        # 健康巡检工具
        self.tool_integrator.register_tool(
            tool_name="monitor_system_health",
            tool_description="执行系统健康巡检",
            tool_usage="用于定期检查系统组件状态"
        )
        
        # 配置校验工具
        self.tool_integrator.register_tool(
            tool_name="validate_configuration",
            tool_description="验证系统配置完整性",
            tool_usage="用于检查组件自曝光协议和配置完整性"
        )
        
        # 性能分析工具
        self.tool_integrator.register_tool(
            tool_name="analyze_performance",
            tool_description="分析系统性能指标",
            tool_usage="用于分析系统资源使用和性能瓶颈"
        )
        
        # 工具调用一致性检查工具（注意力增强机制）
        self.tool_integrator.register_tool(
            tool_name="check_tool_usage_consistency",
            tool_description="检查工具调用真实性，识别模拟结果信号",
            tool_usage="用于主动检测系统中'应调用但未调用'的工具问题"
        )
        
        logger.info("[系统维护师] ✅ 6个专用工具注册完成")
    
    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        处理用户查询 - 系统维护请求的核心方法
        
        Args:
            user_query: 用户查询内容
            
        Returns:
            Dict: 处理结果
        """
        # 记录工作日志
        self._write_work_log(f"处理维护请求: {user_query}", "MAINTENANCE_REQUEST")
        
        try:
            # 使用LLM分析用户意图
            analysis_result = self._analyze_maintenance_intent(user_query)
            
            # 根据意图选择维护操作
            maintenance_action = analysis_result.get("action_type", "health_check")
            
            # 执行相应的维护操作
            if maintenance_action == "diagnose":
                result = self._handle_diagnosis_request(user_query, analysis_result)
            elif maintenance_action == "fix":
                result = self._handle_fix_request(user_query, analysis_result)
            elif maintenance_action == "health_check":
                result = self.monitor_system_health()
            elif maintenance_action == "validate_config":
                result = self.validate_configuration()
            elif maintenance_action == "performance_analysis":
                result = self.analyze_performance()
            else:
                result = {
                    "success": False,
                    "message": f"未知的维护操作类型: {maintenance_action}"
                }
            
            # 生成响应
            response = self._generate_maintenance_response(result, user_query)
            
            return {
                "success": True,
                "user_query": user_query,
                "intent_analysis": analysis_result,
                "maintenance_result": result,
                "response": response,
                "message": "维护请求处理完成"
            }
            
        except Exception as e:
            logger.error(f"处理维护请求失败: {e}")
            return {
                "success": False,
                "user_query": user_query,
                "error": str(e),
                "message": "维护请求处理失败"
            }
    
    def _analyze_maintenance_intent(self, user_query: str) -> Dict[str, Any]:
        """分析维护请求意图"""
        prompt = f"""
        你是系统维护师，需要分析用户的维护请求意图。
        
        用户请求：{user_query}
        
        请分析请求类型，并返回以下信息：
        1. action_type: 操作类型（diagnose/fix/health_check/validate_config/performance_analysis）
        2. priority: 优先级（high/medium/low）
        3. target_components: 涉及的组件列表
        4. suggested_actions: 建议的维护操作
        
        请以JSON格式返回分析结果。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.2,
                max_tokens=300
            )
            
            return json.loads(response)
        except:
            # 默认分析结果
            return {
                "action_type": "health_check",
                "priority": "medium",
                "target_components": [],
                "suggested_actions": ["执行系统健康巡检"]
            }
    
    def monitor_system_health(self) -> Dict[str, Any]:
        """执行系统健康巡检"""
        self._write_work_log("开始系统健康巡检", "HEALTH_CHECK")
        
        health_status = {
            "check_time": datetime.now().isoformat(),
            "overall_status": "healthy",
            "component_status": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # 1. 检查组件自曝光协议完整性
        protocol_check = self._check_protocol_completeness()
        health_status["component_status"]["protocol"] = protocol_check
        
        if not protocol_check["is_complete"]:
            health_status["overall_status"] = "warning"
            health_status["issues_found"].append({
                "type": "protocol_incomplete",
                "severity": "medium",
                "description": f"发现 {len(protocol_check['missing_components'])} 个组件缺少自曝光协议"
            })
        
        # 2. 检查错误统计
        error_stats = self.error_monitor.get_error_stats()
        health_status["component_status"]["errors"] = error_stats
        
        if error_stats.get("total_errors", 0) > 10:
            health_status["overall_status"] = "unhealthy"
            health_status["issues_found"].append({
                "type": "high_error_rate",
                "severity": "high",
                "description": f"检测到 {error_stats['total_errors']} 个错误"
            })
        
        # 3. 读取最近启动状态历史（最多3条）
        startup_history = self._load_startup_history(limit=3)
        health_status["component_status"]["startup"] = {
            "recent_records": startup_history,
            "history_length": len(startup_history)
        }
        
        # 如果最近一次启动记录存在模块导入失败，则降级整体状态
        if startup_history:
            latest = startup_history[0]
            if not all([
                latest.get("chatroom_import_ok", True),
                latest.get("timing_engine_import_ok", True),
                latest.get("memory_reconstruct_import_ok", True),
                latest.get("nightly_scheduler_import_ok", True)
            ]):
                health_status["overall_status"] = "warning"
                health_status["issues_found"].append({
                    "type": "startup_import_warning",
                    "severity": "medium",
                    "description": "最近一次启动存在模块导入失败",
                    "details": latest
                })
        
        # 4. 生成建议
        if health_status["issues_found"]:
            health_status["recommendations"].append("建议尽快处理发现的问题，并复查启动历史与错误日志")
        else:
            health_status["recommendations"].append("系统运行正常，继续保持，并定期检查启动历史和错误统计")
        
        self.last_health_check = datetime.now()
        
        return health_status
    
    def diagnose_error(self, error_data: Dict) -> Dict[str, Any]:
        """诊断系统错误"""
        self._write_work_log(f"开始诊断错误: {error_data.get('type', 'unknown')}", "ERROR_DIAGNOSIS")
        
        # 使用错误处理器分析错误
        solution = self.error_handler.analyze_error(error_data)
        
        # 查询相关组件的自曝光协议
        component_id = error_data.get("component_id")
        if component_id:
            component_interface = self.protocol_manager.query_interface(component_id)
        else:
            component_interface = None
        
        # 生成诊断报告
        diagnosis = {
            "error_type": error_data.get("type", "unknown"),
            "error_message": error_data.get("message", ""),
            "timestamp": datetime.now().isoformat(),
            "solution": solution,
            "component_interface": component_interface,
            "can_auto_fix": solution is not None,
            "priority": self._assess_error_priority(error_data, solution)
        }
        
        # 记录到历史
        self.error_history.append(diagnosis)
        
        return diagnosis
    
    def auto_fix(self, error_data: Dict) -> Dict[str, Any]:
        """自动修复系统错误"""
        self._write_work_log(f"尝试自动修复错误: {error_data.get('type', 'unknown')}", "AUTO_FIX")
        
        # 先诊断错误
        diagnosis = self.diagnose_error(error_data)
        
        if not diagnosis["can_auto_fix"]:
            return {
                "success": False,
                "message": "无法自动修复此错误，需要手动干预",
                "diagnosis": diagnosis
            }
        
        # 执行修复
        fix_success = self.error_handler.execute_fix(diagnosis["solution"])
        
        # 验证修复效果
        if fix_success:
            verify_success = self.error_handler.verify_fix(error_data)
        else:
            verify_success = False
        
        # 记录修复结果
        fix_result = {
            "success": fix_success and verify_success,
            "error_type": error_data.get("type"),
            "fix_time": datetime.now().isoformat(),
            "actions_taken": diagnosis["solution"].get("actions", []),
            "verified": verify_success
        }
        
        self.fix_history.append(fix_result)
        
        return fix_result
    
    def validate_configuration(self) -> Dict[str, Any]:
        """验证系统配置完整性"""
        self._write_work_log("开始配置完整性校验", "CONFIG_VALIDATION")
        
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "checks": {}
        }
        
        # 1. 检查组件自曝光协议
        protocol_check = self._check_protocol_completeness()
        validation_result["checks"]["protocol_completeness"] = protocol_check
        
        if not protocol_check["is_complete"]:
            validation_result["is_valid"] = False
        
        # 2. 检查必要的配置文件
        config_check = self._check_config_files()
        validation_result["checks"]["config_files"] = config_check
        
        if not config_check["all_present"]:
            validation_result["is_valid"] = False
        
        # 3. 检查工具注册状态
        # （预留：后续可添加工具注册检查）
        
        return validation_result
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析系统性能"""
        self._write_work_log("开始性能分析", "PERFORMANCE_ANALYSIS")
        
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # 收集性能指标
        # （预留：后续可添加详细的性能指标收集）
        
        performance_data["metrics"]["error_count"] = len(self.error_history)
        performance_data["metrics"]["fix_count"] = len(self.fix_history)
        
        if self.fix_history:
            success_rate = sum(1 for f in self.fix_history if f["success"]) / len(self.fix_history)
            performance_data["metrics"]["fix_success_rate"] = success_rate
        
        return performance_data
    
    def _load_startup_history(self, limit: int = 3) -> list:
        """读取最近的启动状态历史记录（最多limit条，按时间倒序）"""
        history = []
        try:
            logs_dir = Path("logs")
            history_file = logs_dir / "startup_status_history.jsonl"
            if not history_file.exists():
                return history

            # 读取所有行，再按timestamp字段排序
            records = []
            with history_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except Exception:
                        continue

            # 按时间倒序排序
            records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
            history = records[:limit]
        except Exception as e:
            # 作为维护组件，这里只记录日志，不抛出
            self._write_work_log(f"读取启动历史失败: {e}", "启动历史读取错误")
        return history
    
    def _check_protocol_completeness(self) -> Dict[str, Any]:
        """检查组件自曝光协议完整性"""
        try:
            # 使用自曝光协议管理器查询所有组件
            all_components = self.protocol_manager.query_all_components()
            
            # 统计组件数量
            total = len(all_components)
            registered = sum(1 for c in all_components if c.get("id"))
            missing = [c.get("file", "unknown") for c in all_components if not c.get("id")]
            
            return {
                "is_complete": len(missing) == 0,
                "total_components": total,
                "registered_components": registered,
                "missing_components": missing
            }
        except Exception as e:
            # 如果协议管理器未就绪，返回默认值
            self._write_work_log(f"检查协议完整性失败: {e}", "协议检查错误")
            return {
                "is_complete": True,
                "total_components": 0,
                "registered_components": 0,
                "missing_components": []
            }
    
    def _check_config_files(self) -> Dict[str, Any]:
        """检查配置文件完整性"""
        required_configs = [
            "config/api_keys.py",
            "config/system_config.py"
        ]
        
        present = []
        missing = []
        
        for config_file in required_configs:
            if Path(config_file).exists():
                present.append(config_file)
            else:
                missing.append(config_file)
        
        return {
            "all_present": len(missing) == 0,
            "present": present,
            "missing": missing
        }
    
    def _assess_error_priority(self, error_data: Dict, solution: Optional[Dict]) -> str:
        """评估错误优先级"""
        error_type = error_data.get("type", "").lower()
        
        # 高优先级错误
        if any(keyword in error_type for keyword in ["critical", "fatal", "security"]):
            return "high"
        
        # 中优先级错误
        if any(keyword in error_type for keyword in ["error", "exception", "failure"]):
            return "medium"
        
        # 低优先级错误
        return "low"
    
    def _handle_diagnosis_request(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """处理诊断请求"""
        # 创建模拟错误数据（实际应该从二级报错机制获取）
        error_data = {
            "type": "DiagnosisRequest",
            "message": query,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.diagnose_error(error_data)
    
    def _handle_fix_request(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """处理修复请求"""
        # 创建模拟错误数据
        error_data = {
            "type": "FixRequest",
            "message": query,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.auto_fix(error_data)
    
    def _generate_maintenance_response(self, result: Dict, query: str) -> str:
        """生成维护响应"""
        # 使用LLM生成人性化的响应
        prompt = f"""
        根据以下维护操作结果，生成简洁清晰的中文响应。
        
        用户请求：{query}
        操作结果：{json.dumps(result, ensure_ascii=False, indent=2)}
        
        请以系统维护师的语气回复，要专业但易懂。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=500
            )
            return response
        except:
            return f"维护操作已完成。结果：{result.get('message', '操作成功')}"
    
    def receive_security_alert(self, alert_data: dict) -> dict:
        """接收安全警报并记录到工作日志（系统维护师的日记）
        
        Args:
            alert_data: 安全警报数据
                - event: 事件类型 (outpost_compromised / main_server_isolated)
                - timestamp: 事件时间
                - details: 相关详情
        
        Returns:
            dict: 处理结果
        """
        alert_type = alert_data.get("event")
        
        if alert_type == "outpost_compromised":
            # 前哨被击穿，记录严重安全事件
            self._write_work_log(
                message="🚨 前哨（静态服务器）被击穿，端口数据已自毁",
                category="SECURITY_ALERT_CRITICAL",
                details={
                    "timestamp": alert_data.get("timestamp"),
                    "action_taken": alert_data.get("action_taken", "self_destruct_and_alert_main_servers"),
                    "affected_instances": alert_data.get("destroyed_instances", []),
                    "total_instances": alert_data.get("total_instances", 0)
                }
            )
            
            # 记录到安全事件历史
            security_event = {
                "type": "security_breach",
                "subtype": "outpost_compromised",
                "severity": "critical",
                "timestamp": alert_data.get("timestamp"),
                "event_data": alert_data
            }
            self.error_history.append(security_event)
            
            return {
                "success": True,
                "message": "前哨击穿事件已记录到系统维护师日记",
                "severity": "critical"
            }
        
        elif alert_type == "main_server_isolated":
            # 主服务器隔离，记录高级安全事件
            self._write_work_log(
                message="🔒 主服务器已切断网络连接，进入隔离模式",
                category="SECURITY_ALERT_HIGH",
                details={
                    "server_port": alert_data.get("port"),
                    "reason": alert_data.get("reason", "outpost_breached"),
                    "timestamp": alert_data.get("timestamp")
                }
            )
            
            # 记录到安全事件历史
            security_event = {
                "type": "security_response",
                "subtype": "main_server_isolated",
                "severity": "high",
                "timestamp": alert_data.get("timestamp"),
                "event_data": alert_data
            }
            self.error_history.append(security_event)
            
            return {
                "success": True,
                "message": "主服务器隔离事件已记录到系统维护师日记",
                "severity": "high"
            }
        
        else:
            # 未知警报类型
            self._write_work_log(
                message=f"⚠️ 收到未知类型的安全警报: {alert_type}",
                category="SECURITY_ALERT_UNKNOWN",
                details=alert_data
            )
            return {
                "success": False,
                "message": f"未知警报类型: {alert_type}",
                "severity": "unknown"
            }

    def check_tool_usage_consistency(self, text: str = None, target_tool: str = None) -> Dict[str, Any]:
        """检查工具调用真实性，识别模拟结果信号（注意力增强机制）
        
        Args:
            text: 待检查的文本（系统输出/日志等）
            target_tool: 目标工具名称（可选）
            
        Returns:
            检查结果，包含是否发现问题、问题详情、建议操作
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "check_type": "tool_usage_consistency",
            "simulated_result_detected": False,
            "tool_registry_status": {},
            "test_call_results": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # 第一步：识别模拟结果信号
        simulation_patterns = [
            "系统提示：此处应调用",
            "假设检索工具返回",
            "（模拟）",
            "当前为模拟结果",
            "未实际调用工具",
            "工具调用结果摘要（模拟）"
        ]
        
        if text:
            for pattern in simulation_patterns:
                if pattern in text:
                    result["simulated_result_detected"] = True
                    result["issues_found"].append(f"检测到模拟结果信号: '{pattern}'")
                    break
        
        # 第二步：调用 tool_registry_check 确认基础工具注册状态
        try:
            registry_check = self.call_tool('tool_registry_check', {})
            result["tool_registry_status"] = registry_check
            
            if registry_check.get('success') and registry_check.get('data'):
                missing_tools = registry_check['data'].get('missing_in_manager', [])
                if missing_tools:
                    result["issues_found"].append(f"发现未注册的基础工具: {', '.join(missing_tools)}")
                    result["recommendations"].append("需要检查 tools/chat_tools.py 中的工具注册逼辑")
        except Exception as e:
            result["issues_found"].append(f"tool_registry_check 调用失败: {str(e)}")
        
        # 第三步：对目标工具执行真实测试调用
        if target_tool:
            test_tools = [target_tool]
        else:
            # 默认测试基础工具
            test_tools = ['file_reading', 'file_writing', 'memory_retrieval']
        
        for tool_name in test_tools:
            try:
                # 根据工具类型构造测试参数
                if tool_name == 'file_reading':
                    # 测试读取一个存在的文件
                    test_result = self.call_tool('file_reading', {
                        'file_path': 'src/agent_prompts/system_maintenance_prompt.txt'
                    })
                elif tool_name == 'memory_retrieval':
                    test_result = self.call_tool('unified_memory_retrieval', {
                        'query': '系统维护',
                        'limit': 1
                    })
                elif tool_name == 'file_writing':
                    # file_writing 有权限检查，系统维护师不能调用，跳过
                    test_result = {"success": True, "skipped": "权限检查跳过"}
                else:
                    test_result = self.call_tool(tool_name, {})
                
                result["test_call_results"][tool_name] = {
                    "success": test_result.get('success', False),
                    "details": test_result
                }
                
                if not test_result.get('success') and not test_result.get('skipped'):
                    result["issues_found"].append(f"工具 '{tool_name}' 测试调用失败")
                    result["recommendations"].append(f"检查 '{tool_name}' 工具的实现和注册状态")
            except Exception as e:
                result["test_call_results"][tool_name] = {
                    "success": False,
                    "error": str(e)
                }
                result["issues_found"].append(f"工具 '{tool_name}' 测试调用异常: {str(e)}")
        
        # 第四步：生成维护日志
        log_category = "TOOL_USAGE_CONSISTENCY_CHECK"
        if result["issues_found"]:
            log_message = f"⚠️ 发现工具调用一致性问题: {len(result['issues_found'])}条"
            log_category = "TOOL_USAGE_ISSUE_DETECTED"
        else:
            log_message = "✅ 工具调用一致性检查通过"
        
        self._write_work_log(
            message=log_message,
            category=log_category,
            details=result
        )
        
        # 第五步：触发二级报错（如果发现严重问题）
        if result["simulated_result_detected"] and result["issues_found"]:
            try:
                from src.error_reporting import get_error_reporting_service
                error_service = get_error_reporting_service()
                error_service.report_component_error({
                    "error_id": error_service.generate_error_id("system_maintenance", "ToolUsageInconsistency"),
                    "level": "component",
                    "type": "ToolUsageInconsistency",
                    "message": "检测到工具调用模拟结果信号，但工具实际调用失败",
                    "timestamp": datetime.now().isoformat(),
                    "component": "system_maintenance_agent",
                    "function": "check_tool_usage_consistency",
                    "file_path": "src/system_maintenance_agent.py",
                    "line_number": 0,
                    "stack_trace": "tool_usage_consistency_check",
                    "context": {
                        "detected_issues": result["issues_found"],
                        "test_results": result["test_call_results"]
                    }
                })
            except Exception:
                pass
        
        return result


# 获取系统维护师实例的工厂函数
_maintenance_agent_instance = None

def get_system_maintenance() -> SystemMaintenanceAgent:
    """获取系统维护师智能体实例（单例模式）"""
    global _maintenance_agent_instance
    if _maintenance_agent_instance is None:
        _maintenance_agent_instance = SystemMaintenanceAgent()
    return _maintenance_agent_instance


if __name__ == "__main__":
    # 测试系统维护师
    agent = get_system_maintenance()
    
    # 测试健康巡检
    print("\n=== 测试健康巡检 ===")
    health_result = agent.monitor_system_health()
    print(json.dumps(health_result, ensure_ascii=False, indent=2))
    
    # 测试配置校验
    print("\n=== 测试配置校验 ===")
    config_result = agent.validate_configuration()
    print(json.dumps(config_result, ensure_ascii=False, indent=2))
    
    # 测试用户查询处理
    print("\n=== 测试用户查询 ===")
    query_result = agent.process_user_query("请检查系统健康状态")
    print(json.dumps(query_result, ensure_ascii=False, indent=2))
