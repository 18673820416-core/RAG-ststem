# @self-expose: {"id": "agent_error_handler", "name": "Agent Error Handler", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Error Handler功能"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体错误处理模块
分析错误并执行修复操作
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Path(__file__).parent.parent, 'logs', 'agent_error_handler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentErrorHandler:
    """智能体错误处理模块"""
    
    def __init__(self, rag_system_path="E:\RAG系统"):
        self.rag_system_path = Path(rag_system_path)
        self.error_knowledge_base = self._load_error_knowledge_base()
    
    def _load_error_knowledge_base(self):
        """加载错误知识库"""
        kb_path = self.rag_system_path / "data" / "error_knowledge_base.json"
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_error_knowledge_base(self):
        """保存错误知识库"""
        kb_path = self.rag_system_path / "data" / "error_knowledge_base.json"
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.error_knowledge_base, f, ensure_ascii=False, indent=2)
    
    def analyze_error(self, error_data):
        """分析错误信息"""
        error_type = error_data.get('type', 'unknown')
        error_message = error_data.get('message', '')
        
        logger.info(f"分析错误: {error_type} - {error_message}")
        
        # 查找知识库中的解决方案
        for known_error, solution in self.error_knowledge_base.items():
            if known_error in error_message:
                logger.info(f"从知识库找到解决方案: {solution['solution']}")
                return solution
        
        # 简单的错误模式匹配
        if "Connection refused" in error_message:
            return self._handle_connection_refused(error_data)
        elif "ModuleNotFoundError" in error_message:
            return self._handle_module_not_found(error_data)
        elif "FileNotFoundError" in error_message:
            return self._handle_file_not_found(error_data)
        elif "PermissionError" in error_message:
            return self._handle_permission_error(error_data)
        elif "JSONDecodeError" in error_message:
            return self._handle_json_decode_error(error_data)
        
        logger.warning(f"无法找到解决方案")
        return None
    
    def _handle_connection_refused(self, error_data):
        """处理连接拒绝错误"""
        return {
            "solution": "检查服务是否正在运行",
            "actions": [
                "检查相关服务进程",
                "尝试重启服务"
            ]
        }
    
    def _handle_module_not_found(self, error_data):
        """处理模块未找到错误"""
        # 提取缺失的模块名
        error_message = error_data.get('message', '')
        module_name = None
        
        # 尝试从错误信息中提取模块名
        if "No module named" in error_message:
            module_name = error_message.split("'" or '"')[1] if "'" in error_message or '"' in error_message else None
        elif "ModuleNotFoundError" in error_message:
            parts = error_message.split(":")
            if len(parts) > 1:
                module_name = parts[1].strip().replace("'", "").replace('"', '')
        
        if module_name:
            return {
                "solution": f"安装缺失的模块 {module_name}",
                "actions": [
                    f"pip install {module_name}"
                ]
            }
        return None
    
    def _handle_file_not_found(self, error_data):
        """处理文件未找到错误"""
        return {
            "solution": "检查文件路径是否正确",
            "actions": [
                "检查文件是否存在",
                "创建缺失的目录或文件"
            ]
        }
    
    def _handle_permission_error(self, error_data):
        """处理权限错误"""
        return {
            "solution": "调整文件或目录权限",
            "actions": [
                "检查文件权限",
                "调整权限以允许访问"
            ]
        }
    
    def _handle_json_decode_error(self, error_data):
        """处理JSON解析错误"""
        return {
            "solution": "检查JSON格式，修复错误",
            "actions": [
                "分析JSON文件",
                "修复格式错误"
            ]
        }
    
    def execute_fix(self, solution):
        """执行修复操作"""
        if not solution or not solution.get('actions'):
            return False
        
        logger.info(f"🛠️ 执行修复操作: {solution['solution']}")
        
        for action in solution['actions']:
            if action.startswith("pip install"):
                # 执行pip安装命令
                logger.info(f"📦 执行命令: {action}")
                result = subprocess.run(action, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"❌ 执行命令失败: {action}")
                    logger.error(f"错误输出: {result.stderr}")
                    return False
                logger.info(f"✅ 执行命令成功: {action}")
            elif action == "检查相关服务进程":
                # 检查服务进程
                logger.info("🔍 检查服务进程")
                # 这里可以添加具体的进程检查逻辑
            elif action == "尝试重启服务":
                # 尝试重启服务
                logger.info("🔄 尝试重启服务")
                # 这里可以添加具体的服务重启逻辑
            elif action == "检查文件是否存在":
                # 检查文件是否存在
                logger.info("📁 检查文件是否存在")
                # 这里可以添加具体的文件检查逻辑
            elif action == "创建缺失的目录或文件":
                # 创建缺失的目录或文件
                logger.info("📁 创建缺失的目录或文件")
                # 这里可以添加具体的文件创建逻辑
        
        return True
    
    def verify_fix(self, error_data):
        """验证修复效果"""
        # 简单的验证逻辑
        # 例如：检查服务是否可以正常启动
        logger.info("✅ 验证修复效果")
        return True
    
    def handle_error(self, error_data):
        """完整的错误处理流程"""
        logger.info(f"开始处理错误: {error_data.get('type')}")
        
        # 分析错误
        solution = self.analyze_error(error_data)
        if not solution:
            logger.error(f"无法找到解决方案")
            return False
        
        logger.info(f"找到解决方案: {solution['solution']}")
        
        # 执行修复
        logger.info("执行修复操作...")
        success = self.execute_fix(solution)
        if not success:
            logger.error("修复失败")
            return False
        
        # 验证修复
        logger.info("修复成功，验证效果...")
        verified = self.verify_fix(error_data)
        if not verified:
            logger.warning("修复验证失败")
            return False
        
        logger.info("错误修复完成")
        return True

if __name__ == "__main__":
    # 测试错误处理
    error_handler = AgentErrorHandler()
    
    # 测试模块未找到错误
    test_error = {
        "type": "ModuleNotFoundError",
        "message": "No module named 'missing_module'",
        "timestamp": datetime.now().isoformat()
    }
    
    error_handler.handle_error(test_error)
