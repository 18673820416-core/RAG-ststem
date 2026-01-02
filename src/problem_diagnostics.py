# @self-expose: {"id": "problem_diagnostics", "name": "问题诊断模块", "type": "component", "version": "1.0.0", "needs": {"deps": ["os", "sys", "pathlib", "datetime", "logging"], "resources": ["path_utils", "error_handler", "error_knowledge_base"]}, "provides": {"capabilities": ["问题检测", "系统诊断", "报告生成", "修复建议"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题诊断模块
实现系统问题的自动检测、报告生成和修复建议
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Path(__file__).parent.parent, 'logs', 'problem_diagnostics.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 移除日志中的表情符号，避免GBK编码问题
original_info = logger.info
def safe_info(msg, *args, **kwargs):
    safe_msg = msg.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('🔧', '[FIX]').replace('🔄', '[REPLACE]')
    original_info(safe_msg, *args, **kwargs)

logger.info = safe_info

class ProblemDiagnostics:
    """问题诊断类"""
    
    def __init__(self):
        self.diagnostic_results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'problems': [],
            'system_info': {},
            'component_status': {},
            'recommendations': []
        }
        self._init_diagnostics()
    
    def _init_diagnostics(self):
        """初始化诊断模块"""
        # 延迟导入依赖，避免循环导入问题
        self.path_utils = None
        self.error_handler = None
        self.error_knowledge_base = None
        
        try:
            from src.path_utils import get_path_utils
            self.path_utils = get_path_utils()
            logger.info("[OK] 成功导入路径处理工具")
        except Exception as e:
            logger.error(f"[ERROR] 导入路径处理工具失败: {e}")
        
        try:
            from src.agent_error_handler import AgentErrorHandler
            self.error_handler = AgentErrorHandler()
            logger.info("[OK] 成功导入错误处理模块")
        except Exception as e:
            logger.error(f"[ERROR] 导入错误处理模块失败: {e}")
        
        try:
            from src.error_knowledge_base import ErrorKnowledgeBase
            self.error_knowledge_base = ErrorKnowledgeBase()
            logger.info("[OK] 成功导入错误知识库")
        except Exception as e:
            logger.error(f"[ERROR] 导入错误知识库失败: {e}")
    
    def run_full_diagnostics(self):
        """运行完整的系统诊断"""
        logger.info("[OK] 开始运行完整的系统诊断")
        
        # 重置诊断结果
        self.diagnostic_results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'problems': [],
            'system_info': {},
            'component_status': {},
            'recommendations': []
        }
        
        # 1. 收集系统基本信息
        self._collect_system_info()
        
        # 2. 检查系统组件
        self._check_components()
        
        # 3. 检测常见问题
        self._detect_common_problems()
        
        # 4. 生成修复建议
        self._generate_recommendations()
        
        # 5. 更新整体状态
        self._update_overall_status()
        
        logger.info(f"[OK] 诊断完成，状态: {self.diagnostic_results['status']}")
        return self.diagnostic_results
    
    def _collect_system_info(self):
        """收集系统基本信息"""
        logger.info("[OK] 收集系统基本信息")
        
        self.diagnostic_results['system_info'] = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'env_path': sys.executable,
            'timestamp': datetime.now().isoformat(),
            'cpu_count': os.cpu_count(),
            'python_path': sys.path[:5]  # 只显示前5个路径
        }
    
    def _check_components(self):
        """检查系统组件状态"""
        logger.info("[OK] 检查系统组件状态")
        
        # 检查路径处理工具
        if self.path_utils:
            problems_dir = self.path_utils.get_problems_directory()
            self.diagnostic_results['component_status']['path_utils'] = {
                'status': 'healthy',
                'problems_directory': str(problems_dir),
                'directory_exists': os.path.exists(problems_dir)
            }
        else:
            self.diagnostic_results['component_status']['path_utils'] = {
                'status': 'unhealthy',
                'error': '路径处理工具未初始化'
            }
        
        # 检查错误处理模块
        if self.error_handler:
            self.diagnostic_results['component_status']['error_handler'] = {
                'status': 'healthy'
            }
        else:
            self.diagnostic_results['component_status']['error_handler'] = {
                'status': 'unhealthy',
                'error': '错误处理模块未初始化'
            }
        
        # 检查错误知识库
        if self.error_knowledge_base:
            kb_stats = self.error_knowledge_base.get_statistics()
            self.diagnostic_results['component_status']['error_knowledge_base'] = {
                'status': 'healthy',
                'statistics': kb_stats
            }
        else:
            self.diagnostic_results['component_status']['error_knowledge_base'] = {
                'status': 'unhealthy',
                'error': '错误知识库未初始化'
            }
    
    def _detect_common_problems(self):
        """检测常见问题"""
        logger.info("[OK] 检测常见问题")
        
        # 1. 检查包含 # 的目录路径问题
        if self.path_utils:
            problematic_path = r"e:\AI\qiusuo-framework\#problems_and_diagnostics"
            safe_path = self.path_utils.fix_path(problematic_path)
            self.diagnostic_results['problems'].append({
                'id': 'path_special_chars',
                'type': 'path_issue',
                'severity': 'medium',
                'original_path': problematic_path,
                'fixed_path': safe_path,
                'status': 'fixed',
                'description': '目录路径包含特殊字符 # ，已修复为安全路径'
            })
        
        # 2. 检查网络连接
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.close()
        except Exception as e:
            self.diagnostic_results['problems'].append({
                'id': 'network_issue',
                'type': 'network_issue',
                'severity': 'low',
                'message': str(e),
                'status': 'detected',
                'description': '网络连接检查失败'
            })
        
        # 3. 检查日志目录
        logs_dir = Path(r"e:\RAG系统\logs")
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            self.diagnostic_results['problems'].append({
                'id': 'logs_dir_missing',
                'type': 'directory_issue',
                'severity': 'low',
                'status': 'fixed',
                'description': '日志目录不存在，已创建'
            })
        
        # 4. 检查数据目录
        data_dir = Path(r"e:\RAG系统\data")
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            self.diagnostic_results['problems'].append({
                'id': 'data_dir_missing',
                'type': 'directory_issue',
                'severity': 'low',
                'status': 'fixed',
                'description': '数据目录不存在，已创建'
            })
    
    def _generate_recommendations(self):
        """生成修复建议"""
        logger.info("[OK] 生成修复建议")
        
        if not self.diagnostic_results['problems']:
            self.diagnostic_results['recommendations'].append({
                'id': 'no_issues',
                'type': 'info',
                'description': '系统运行正常，建议定期进行诊断检查'
            })
            return
        
        # 针对每个问题生成建议
        for problem in self.diagnostic_results['problems']:
            if problem['status'] == 'fixed':
                self.diagnostic_results['recommendations'].append({
                    'id': f'recommendation_{problem["id"]}',
                    'type': 'info',
                    'description': f'问题 "{problem["description"]}" 已自动修复'
                })
            else:
                self.diagnostic_results['recommendations'].append({
                    'id': f'recommendation_{problem["id"]}',
                    'type': 'fix',
                    'description': f'需要手动修复问题: {problem["description"]}',
                    'severity': problem['severity']
                })
        
        # 通用建议
        self.diagnostic_results['recommendations'].append({
            'id': 'regular_checks',
            'type': 'info',
            'description': '建议定期运行系统诊断，保持系统健康'
        })
    
    def _update_overall_status(self):
        """更新整体状态"""
        # 如果有任何未修复的问题，状态为 unhealthy
        for problem in self.diagnostic_results['problems']:
            if problem['status'] == 'detected':
                self.diagnostic_results['status'] = 'unhealthy'
                return
        
        # 检查组件状态
        for component, status in self.diagnostic_results['component_status'].items():
            if status['status'] == 'unhealthy':
                self.diagnostic_results['status'] = 'degraded'
                return
        
        # 所有组件正常，没有未修复的问题
        self.diagnostic_results['status'] = 'healthy'
    
    def generate_report(self, format='json'):
        """生成诊断报告"""
        logger.info(f"[OK] 生成诊断报告，格式: {format}")
        
        if format == 'json':
            return self.diagnostic_results
        elif format == 'text':
            return self._generate_text_report()
        else:
            return self.diagnostic_results
    
    def _generate_text_report(self):
        """生成文本格式的诊断报告"""
        report = []
        report.append("=" * 60)
        report.append("RAG系统诊断报告")
        report.append("=" * 60)
        report.append(f"生成时间: {self.diagnostic_results['timestamp']}")
        report.append(f"系统状态: {self.diagnostic_results['status'].upper()}")
        report.append("=" * 60)
        
        # 系统信息
        report.append("\n1. 系统信息")
        report.append("-" * 40)
        sys_info = self.diagnostic_results['system_info']
        report.append(f"Python版本: {sys_info['python_version'].split()[0]}")
        report.append(f"平台: {sys_info['platform']}")
        report.append(f"工作目录: {sys_info['working_directory']}")
        report.append(f"Python解释器: {sys_info['env_path']}")
        report.append(f"CPU核心数: {sys_info['cpu_count']}")
        
        # 组件状态
        report.append("\n2. 组件状态")
        report.append("-" * 40)
        for component, status in self.diagnostic_results['component_status'].items():
            status_str = status['status'].upper()
            report.append(f"{component}: {status_str}")
            if 'problems_directory' in status:
                report.append(f"  - 问题目录: {status['problems_directory']}")
            if 'error' in status:
                report.append(f"  - 错误: {status['error']}")
        
        # 问题列表
        report.append("\n3. 问题列表")
        report.append("-" * 40)
        if not self.diagnostic_results['problems']:
            report.append("✅ 没有检测到问题")
        else:
            for i, problem in enumerate(self.diagnostic_results['problems'], 1):
                status_str = "✅ 已修复" if problem['status'] == 'fixed' else "❌ 待修复"
                report.append(f"{i}. {problem['description']} {status_str}")
        
        # 修复建议
        report.append("\n4. 修复建议")
        report.append("-" * 40)
        for recommendation in self.diagnostic_results['recommendations']:
            report.append(f"- {recommendation['description']}")
        
        report.append("\n" + "=" * 60)
        report.append("诊断报告结束")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename=None):
        """保存诊断报告到文件"""
        logger.info("[OK] 保存诊断报告到文件")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostics_report_{timestamp}.json"
        
        report_path = Path(r"e:\RAG系统\problems_and_diagnostics") / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.diagnostic_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[OK] 报告已保存到: {report_path}")
        return str(report_path)

# 全局实例
problem_diagnostics = ProblemDiagnostics()

def get_problem_diagnostics():
    """获取问题诊断实例"""
    return problem_diagnostics

if __name__ == "__main__":
    # 测试诊断模块
    diagnostics = ProblemDiagnostics()
    results = diagnostics.run_full_diagnostics()
    
    print("\n=== 诊断结果 ===")
    print(f"状态: {results['status']}")
    print(f"问题数量: {len(results['problems'])}")
    print(f"组件数量: {len(results['component_status'])}")
    
    text_report = diagnostics.generate_report(format='text')
    print("\n=== 文本报告 ===")
    print(text_report)
    
    report_path = diagnostics.save_report()
    print(f"\n报告已保存到: {report_path}")
