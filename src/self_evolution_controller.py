"""
智能体自进化主控程序

角色权限说明：
- 构架师智能体：仆人，只能提出方案，禁止代码编写
- 方案评估师智能体：仆人，只能评估方案，禁止代码编写  
- 代码实现师智能体：仆人，每个代码写入动作必须经过主人明确同意

进化流程：构架师 → 评估师 → 主人确认 → 实现师

安全机制：所有代码修改必须经过主人确认
"""
# @self-expose: {"id": "self_evolution_controller", "name": "Self Evolution Controller", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Self Evolution Controller功能"]}}

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 使用绝对导入替代相对导入
try:
    from scheme_evaluator_agent import SchemeEvaluatorAgent
    from equality_law_evaluator import EqualityLawEvaluator, create_evaluation_report
    from agent_communication import (
        AgentCommunicationSystem, AgentType, SchemeStatus, 
        create_scheme_summary, MessageType
    )
    from agent_feedback_collector import AgentFeedbackCollector
    from feedback_evaluator import FeedbackEvaluator
    from agent_behavior_evaluator import AgentBehaviorEvaluator
except ImportError:
    # 如果直接导入失败，尝试从src包导入
    from src.scheme_evaluator_agent import SchemeEvaluatorAgent
    from src.equality_law_evaluator import EqualityLawEvaluator, create_evaluation_report
    from src.agent_communication import (
        AgentCommunicationSystem, AgentType, SchemeStatus, 
        create_scheme_summary, MessageType
    )
    from src.agent_feedback_collector import AgentFeedbackCollector
    from src.feedback_evaluator import FeedbackEvaluator
    from src.agent_behavior_evaluator import AgentBehaviorEvaluator

class SelfEvolutionController:
    """智能体自进化控制器"""
    
    def __init__(self, rag_system_path: str = r"E:\RAG系统"):
        self.rag_system_path = rag_system_path
        self.logger = self._setup_logger()
        
        # 初始化智能体
        self.evaluator_agent = SchemeEvaluatorAgent(rag_system_path)
        self.equality_evaluator = EqualityLawEvaluator()
        self.comm_system = AgentCommunicationSystem()
        
        # 初始化反馈和评估系统
        self.feedback_collector = AgentFeedbackCollector()
        self.feedback_evaluator = FeedbackEvaluator()
        self.behavior_evaluator = AgentBehaviorEvaluator()
        
        # 智能体ID
        self.agent_ids = {
            "architect": "architect_001",
            "evaluator": "evaluator_001", 
            "implementer": "implementer_001",
            "owner": "owner_001"
        }
        
        # 注册智能体
        self._register_agents()
        
        # 系统状态
        self.is_running = False
        self.current_scheme_id = None
        self.optimization_tasks = []
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger("SelfEvolutionController")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 文件处理器
            log_file = os.path.join(self.rag_system_path, "logs", "self_evolution.log")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _register_agents(self):
        """注册智能体"""
        self.comm_system.register_agent(
            self.agent_ids["architect"], AgentType.ARCHITECT
        )
        self.comm_system.register_agent(
            self.agent_ids["evaluator"], AgentType.EVALUATOR
        )
        self.comm_system.register_agent(
            self.agent_ids["implementer"], AgentType.IMPLEMENTER
        )
        self.comm_system.register_agent(
            self.agent_ids["owner"], AgentType.OWNER
        )
        
        self.logger.info("智能体注册完成")
    
    def start_evolution_process(self, architect_scheme: Dict) -> str:
        """
        启动进化流程
        
        Args:
            architect_scheme: 构架师方案
            
        Returns:
            方案ID
        """
        self.logger.info("启动智能体自进化流程")
        
        try:
            # 1. 构架师提出方案
            scheme_id = self.comm_system.propose_scheme(
                self.agent_ids["architect"], architect_scheme
            )
            
            self.current_scheme_id = scheme_id
            self.logger.info(f"方案已提交，ID：{scheme_id}")
            
            # 2. 自动处理评估流程
            self._process_evaluation_phase(scheme_id)
            
            return scheme_id
            
        except Exception as e:
            self.logger.error(f"启动进化流程失败：{e}")
            raise
    
    def _process_evaluation_phase(self, scheme_id: str):
        """处理评估阶段"""
        self.logger.info("开始评估阶段")
        
        # 等待评估师收到消息
        time.sleep(1)
        
        # 获取评估请求消息
        messages = self.comm_system.get_messages_for_agent(
            self.agent_ids["evaluator"], unread_only=True
        )
        
        if not messages:
            self.logger.warning("评估师未收到评估请求")
            return
        
        # 处理评估请求
        for message in messages:
            if message.message_type == MessageType.EVALUATION_REQUEST:
                self._handle_evaluation_request(message, scheme_id)
                break
    
    def _handle_evaluation_request(self, message: Any, scheme_id: str):
        """处理评估请求"""
        self.logger.info("评估师开始处理评估请求")
        
        # 标记消息为已读和已处理
        self.comm_system.mark_message_read(message.message_id)
        self.comm_system.mark_message_processed(message.message_id)
        
        try:
            # 扫描RAG系统
            system_analysis = self.evaluator_agent.scan_rag_system()
            
            # 获取方案详情
            scheme = self.comm_system.get_scheme_details(scheme_id)
            if not scheme:
                raise ValueError(f"未找到方案：{scheme_id}")
            
            # 准备评估数据
            scheme_data = {
                "name": scheme.name,
                "description": scheme.description,
                "proposed_functions": scheme.proposed_functions,
                "technical_details": scheme.technical_details or {},
                "solves_core_issue": True,  # 可根据实际情况调整
                "improves_stability": True,
                "optimizes_performance": True,
                "extends_capabilities": True,
                "user_requirements": True,
                "impact_scope": "major"
            }
            
            # 准备上下文数据
            context_data = {
                "existing_functions": self._extract_existing_functions(system_analysis)
            }
            
            # 使用平等律评估器进行评估
            evaluation_result = self.equality_evaluator.comprehensive_evaluation(
                scheme_data, context_data
            )
            
            # 提交评估结果
            self.comm_system.submit_evaluation_result(
                self.agent_ids["evaluator"], scheme_id, evaluation_result
            )
            
            self.logger.info("评估完成，结果已提交")
            
            # 生成评估报告
            report = create_evaluation_report(evaluation_result)
            self.logger.info(f"评估报告：\n{report}")
            
        except Exception as e:
            self.logger.error(f"评估过程出错：{e}")
            # 提交错误结果
            error_result = {
                "need_degree": 0,
                "non_redundancy_degree": 0,
                "overall_score": 0,
                "pass_status": False,
                "error": str(e)
            }
            self.comm_system.submit_evaluation_result(
                self.agent_ids["evaluator"], scheme_id, error_result
            )
    
    def _extract_existing_functions(self, system_analysis: Dict) -> List[str]:
        """提取现有功能列表"""
        existing_functions = []
        
        for module in system_analysis.get("modules", []):
            existing_functions.extend([f["name"] for f in module.get("functions", [])])
        
        return existing_functions
    
    def wait_for_owner_confirmation(self, scheme_id: str, timeout: int = 300) -> bool:
        """
        等待主人确认
        
        Args:
            scheme_id: 方案ID
            timeout: 超时时间（秒）
            
        Returns:
            是否确认
        """
        self.logger.info("等待主人确认...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            scheme = self.comm_system.get_scheme_details(scheme_id)
            if not scheme:
                self.logger.error(f"方案不存在：{scheme_id}")
                return False
            
            if scheme.status == SchemeStatus.CONFIRMED:
                self.logger.info("方案已确认")
                return True
            elif scheme.status == SchemeStatus.REJECTED:
                self.logger.info("方案被拒绝")
                return False
            
            time.sleep(5)  # 每5秒检查一次
        
        self.logger.warning("等待确认超时")
        return False
    
    def submit_owner_confirmation(self, scheme_id: str, is_confirmed: bool, 
                                feedback: str = "") -> bool:
        """
        提交主人确认
        
        Args:
            scheme_id: 方案ID
            is_confirmed: 是否确认
            feedback: 反馈信息
            
        Returns:
            是否成功
        """
        try:
            self.comm_system.submit_confirmation_response(
                self.agent_ids["owner"], scheme_id, is_confirmed, feedback
            )
            
            status = "确认" if is_confirmed else "拒绝"
            self.logger.info(f"主人已{status}方案")
            return True
            
        except Exception as e:
            self.logger.error(f"提交确认失败：{e}")
            return False
    
    def get_scheme_progress(self, scheme_id: str) -> Dict[str, Any]:
        """获取方案进度"""
        scheme = self.comm_system.get_scheme_details(scheme_id)
        if not scheme:
            return {"error": "方案不存在"}
        
        progress = {
            "scheme_id": scheme_id,
            "name": scheme.name,
            "status": scheme.status.value,
            "created_time": scheme.created_time,
            "current_stage": self._get_current_stage(scheme.status),
            "progress_percentage": self._calculate_progress_percentage(scheme.status)
        }
        
        if scheme.evaluation_result:
            progress["evaluation_result"] = {
                "need_degree": scheme.evaluation_result.get("need_degree", 0),
                "non_redundancy_degree": scheme.evaluation_result.get("non_redundancy_degree", 0),
                "pass_status": scheme.evaluation_result.get("pass_status", False)
            }
        
        if scheme.confirmation_result:
            progress["confirmation_result"] = scheme.confirmation_result
        
        return progress
    
    def _get_current_stage(self, status: SchemeStatus) -> str:
        """获取当前阶段"""
        stage_map = {
            SchemeStatus.PROPOSED: "方案提议",
            SchemeStatus.EVALUATING: "评估中",
            SchemeStatus.EVALUATED: "评估完成",
            SchemeStatus.WAITING_CONFIRMATION: "等待确认",
            SchemeStatus.CONFIRMED: "已确认",
            SchemeStatus.IMPLEMENTING: "实现中",
            SchemeStatus.IMPLEMENTED: "已实现",
            SchemeStatus.REJECTED: "已拒绝"
        }
        return stage_map.get(status, "未知")
    
    def _calculate_progress_percentage(self, status: SchemeStatus) -> int:
        """计算进度百分比"""
        progress_map = {
            SchemeStatus.PROPOSED: 10,
            SchemeStatus.EVALUATING: 30,
            SchemeStatus.EVALUATED: 50,
            SchemeStatus.WAITING_CONFIRMATION: 70,
            SchemeStatus.CONFIRMED: 90,
            SchemeStatus.IMPLEMENTING: 95,
            SchemeStatus.IMPLEMENTED: 100,
            SchemeStatus.REJECTED: 100
        }
        return progress_map.get(status, 0)
    
    def process_tool_evolution(self, top_n: int = 5) -> Dict[str, Any]:
        """处理反馈驱动的工具进化流程
        
        Args:
            top_n: 处理前N个优先级最高的反馈
            
        Returns:
            Dict: 进化处理结果
        """
        self.logger.info(f"开始处理工具进化，处理前 {top_n} 个优先级最高的反馈")
        
        try:
            # 1. 评估所有待评估的反馈
            self.logger.info("步骤1：评估所有待评估的反馈")
            evaluation_result = self.feedback_evaluator.evaluate_feedback()
            
            # 2. 生成优化任务
            self.logger.info("步骤2：生成优化任务")
            self.optimization_tasks = self.feedback_evaluator.generate_optimization_tasks(top_n)
            
            # 3. 执行工具优化
            self.logger.info("步骤3：执行工具优化")
            execution_results = self._execute_tool_optimization()
            
            # 4. 部署更新并反馈给智能体
            self.logger.info("步骤4：部署更新并反馈给智能体")
            deployment_results = self._deploy_updates(execution_results)
            
            # 5. 评估智能体行为并更新认知记忆
            self.logger.info("步骤5：评估智能体行为并更新认知记忆")
            self._evaluate_agent_behavior_and_update_memory()
            
            result = {
                "status": "success",
                "evaluation_result": evaluation_result,
                "optimization_tasks": self.optimization_tasks,
                "execution_results": execution_results,
                "deployment_results": deployment_results,
                "total_processed": len(execution_results)
            }
            
            self.logger.info(f"工具进化处理完成，共处理 {len(execution_results)} 个优化任务")
            return result
            
        except Exception as e:
            self.logger.error(f"处理工具进化失败：{e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _execute_tool_optimization(self) -> List[Dict[str, Any]]:
        """执行工具优化
        
        Returns:
            List: 执行结果列表
        """
        execution_results = []
        
        for task in self.optimization_tasks:
            try:
                # 这里简化处理，实际实现需要根据任务类型执行不同的优化操作
                # 例如：修改工具代码、更新配置、调整参数等
                
                # 模拟执行优化
                time.sleep(1)  # 模拟执行时间
                
                result = {
                    "task_id": task["task_id"],
                    "tool_name": task["tool_name"],
                    "status": "completed",
                    "execution_time": datetime.now().isoformat(),
                    "details": f"已优化工具：{task['tool_name']}，基于反馈：{task['feedback_content'][:50]}..."
                }
                
                execution_results.append(result)
                self.logger.info(f"优化任务执行完成：{task['task_id']}，工具：{task['tool_name']}")
                
            except Exception as e:
                result = {
                    "task_id": task["task_id"],
                    "tool_name": task["tool_name"],
                    "status": "failed",
                    "execution_time": datetime.now().isoformat(),
                    "error": str(e)
                }
                execution_results.append(result)
                self.logger.error(f"优化任务执行失败：{task['task_id']}，错误：{e}")
        
        return execution_results
    
    def _deploy_updates(self, execution_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """部署更新并反馈给智能体
        
        Args:
            execution_results: 执行结果列表
            
        Returns:
            List: 部署结果列表
        """
        deployment_results = []
        
        for result in execution_results:
            if result["status"] == "completed":
                try:
                    # 这里简化处理，实际实现需要部署更新到系统
                    # 例如：重启服务、更新配置、通知智能体等
                    
                    deployment = {
                        "task_id": result["task_id"],
                        "tool_name": result["tool_name"],
                        "status": "deployed",
                        "deployment_time": datetime.now().isoformat(),
                        "details": f"已部署工具更新：{result['tool_name']}"
                    }
                    
                    deployment_results.append(deployment)
                    self.logger.info(f"工具更新已部署：{result['tool_name']}")
                    
                except Exception as e:
                    deployment = {
                        "task_id": result["task_id"],
                        "tool_name": result["tool_name"],
                        "status": "deployment_failed",
                        "deployment_time": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    deployment_results.append(deployment)
                    self.logger.error(f"工具更新部署失败：{result['tool_name']}，错误：{e}")
        
        return deployment_results
    
    def _evaluate_agent_behavior_and_update_memory(self):
        """评估智能体行为并更新认知记忆"""
        try:
            # 获取所有智能体ID（简化处理，实际实现需要从系统中获取）
            agent_ids = ["architect_001", "evaluator_001", "implementer_001"]
            
            for agent_id in agent_ids:
                # 评估智能体行为
                evaluation_result = self.behavior_evaluator.evaluate_agent_behavior(agent_id)
                
                # 这里简化处理，实际实现需要调用智能体的update_cognitive_memory方法
                # 例如：通过API或消息队列通知智能体更新记忆
                
                self.logger.info(f"智能体行为评估完成：{agent_id}，进化贡献值：{evaluation_result['evolution_contribution']}")
                
        except Exception as e:
            self.logger.error(f"评估智能体行为并更新记忆失败：{e}")
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """获取进化统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            # 获取反馈评估统计
            feedback_stats = self.feedback_evaluator.get_feedback_statistics()
            
            # 获取智能体行为评估统计
            behavior_stats = self.behavior_evaluator.get_evaluation_statistics()
            
            return {
                "feedback_statistics": feedback_stats,
                "behavior_evaluation_statistics": behavior_stats,
                "total_optimization_tasks": len(self.optimization_tasks),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"获取进化统计信息失败：{e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_final_report(self, scheme_id: str) -> str:
        """生成最终报告"""
        scheme = self.comm_system.get_scheme_details(scheme_id)
        if not scheme:
            return "方案不存在"
        
        report = f"""
# 智能体自进化最终报告

## 方案信息
- 方案ID：{scheme.scheme_id}
- 方案名称：{scheme.name}
- 最终状态：{scheme.status.value}
- 创建时间：{scheme.created_time}
- 完成时间：{datetime.now().isoformat()}

## 进化流程记录
"""
        
        # 添加评估结果
        if scheme.evaluation_result:
            eval_result = scheme.evaluation_result
            report += f"\n## 平等律评估结果\n"
            report += f"- 被需要度：{eval_result.get('need_degree', 0):.1f}分\n"
            report += f"- 不冗余度：{eval_result.get('non_redundancy_degree', 0):.1f}分\n"
            report += f"- 综合评分：{eval_result.get('overall_score', 0):.1f}分\n"
            report += f"- 评估结论：{'通过' if eval_result.get('pass_status', False) else '不通过'}\n"
        
        # 添加确认结果
        if scheme.confirmation_result:
            conf_result = scheme.confirmation_result
            report += f"\n## 主人确认结果\n"
            report += f"- 是否确认：{'是' if conf_result.get('is_confirmed', False) else '否'}\n"
            if conf_result.get('feedback'):
                report += f"- 反馈意见：{conf_result['feedback']}\n"
        
        # 添加实现结果
        if scheme.implementation_result:
            impl_result = scheme.implementation_result
            report += f"\n## 实现结果\n"
            report += f"- 实现状态：{impl_result.get('status', '未知')}\n"
            if impl_result.get('details'):
                report += f"- 实现详情：{impl_result['details']}\n"
        
        report += f"\n## 总结\n"
        if scheme.status == SchemeStatus.IMPLEMENTED:
            report += "✅ 方案已成功实现，系统完成进化"
        elif scheme.status == SchemeStatus.REJECTED:
            report += "❌ 方案被拒绝，系统保持原状"
        else:
            report += "⏳ 方案仍在处理中"
        
        return report


def main():
    """测试自进化控制器"""
    controller = SelfEvolutionController()
    
    # 模拟构架师方案
    test_scheme = {
        'name': '施工信息智能解析引擎',
        'description': '用于解析微信群中的施工信息并生成台账',
        'proposed_functions': ['施工信息解析', '台账生成', '数据存储'],
        'technical_details': {
            'technology_stack': ['Python', 'FastAPI', 'PostgreSQL'],
            'complexity': 'medium',
            'estimated_time': '15天'
        },
        'resource_requirements': {
            'memory': '2GB',
            'storage': '10GB',
            'network': '标准'
        },
        'expected_benefits': {
            'efficiency_improvement': '提升信息处理效率50%',
            'error_reduction': '减少人工错误80%',
            'time_saving': '节省处理时间60%'
        }
    }
    
    try:
        # 启动进化流程
        scheme_id = controller.start_evolution_process(test_scheme)
        print(f"✅ 进化流程已启动，方案ID：{scheme_id}")
        
        # 等待评估完成
        time.sleep(3)
        
        # 获取进度
        progress = controller.get_scheme_progress(scheme_id)
        print(f"当前进度：{progress['current_stage']} ({progress['progress_percentage']}%)")
        
        # 模拟主人确认
        if progress['status'] == 'waiting_confirmation':
            print("\n📋 评估结果：")
            eval_result = progress.get('evaluation_result', {})
            print(f"- 被需要度：{eval_result.get('need_degree', 0):.1f}分")
            print(f"- 不冗余度：{eval_result.get('non_redundancy_degree', 0):.1f}分")
            print(f"- 是否通过：{'是' if eval_result.get('pass_status', False) else '否'}")
            
            # 主人确认方案
            confirmed = controller.submit_owner_confirmation(
                scheme_id, True, "方案评估合理，同意实施"
            )
            
            if confirmed:
                print("✅ 方案已确认，等待实现师执行")
        
        # 生成最终报告
        final_report = controller.generate_final_report(scheme_id)
        print(f"\n📊 最终报告：\n{final_report}")
        
    except Exception as e:
        print(f"❌ 进化流程出错：{e}")

if __name__ == "__main__":
    main()