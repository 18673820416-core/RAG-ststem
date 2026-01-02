#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误知识库管理
"""
# @self-expose: {"id": "error_knowledge_base", "name": "Error Knowledge Base", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Error Knowledge Base功能"]}}

import os
import json
from pathlib import Path
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Path(__file__).parent.parent, 'logs', 'error_knowledge_base.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ErrorKnowledgeBase:
    """错误知识库"""
    
    def __init__(self, rag_system_path=r"E:\RAG系统"):
        self.rag_system_path = Path(rag_system_path)
        self.kb_path = self.rag_system_path / "data" / "error_knowledge_base.json"
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加载知识库"""
        if self.kb_path.exists():
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_knowledge_base(self):
        """保存知识库"""
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        logger.info(f"知识库已保存到: {self.kb_path}")
    
    def add_solution(self, error_pattern, solution):
        """添加错误解决方案"""
        self.knowledge_base[error_pattern] = solution
        self.save_knowledge_base()
        logger.info(f"添加解决方案到知识库: {error_pattern}")
    
    def get_solution(self, error_message):
        """获取错误解决方案"""
        for pattern, solution in self.knowledge_base.items():
            if pattern in error_message:
                logger.info(f"从知识库找到解决方案: {pattern}")
                return solution
        return None
    
    def learn_from_fix(self, error_data, solution, success):
        """从修复中学习"""
        error_message = error_data.get('message', '')
        
        # 提取错误模式
        error_pattern = self._extract_error_pattern(error_message)
        
        if error_pattern:
            # 添加或更新解决方案
            self.knowledge_base[error_pattern] = {
                "solution": solution,
                "success_rate": self._calculate_success_rate(error_pattern, success),
                "last_used": datetime.now().isoformat(),
                "usage_count": self.knowledge_base.get(error_pattern, {}).get("usage_count", 0) + 1
            }
            self.save_knowledge_base()
            logger.info(f"🧠 从修复中学习: {error_pattern}")
    
    def _extract_error_pattern(self, error_message):
        """提取错误模式"""
        # 简单的错误模式提取
        if "Connection refused" in error_message:
            return "Connection refused"
        elif "ModuleNotFoundError" in error_message:
            return "ModuleNotFoundError"
        elif "FileNotFoundError" in error_message:
            return "FileNotFoundError"
        elif "PermissionError" in error_message:
            return "PermissionError"
        elif "JSONDecodeError" in error_message:
            return "JSONDecodeError"
        elif "AttributeError" in error_message:
            return "AttributeError"
        elif "TypeError" in error_message:
            return "TypeError"
        elif "ValueError" in error_message:
            return "ValueError"
        
        return None
    
    def _calculate_success_rate(self, error_pattern, success):
        """计算成功率"""
        current_entry = self.knowledge_base.get(error_pattern, {})
        usage_count = current_entry.get("usage_count", 0)
        success_count = current_entry.get("success_count", 0)
        
        if success:
            success_count += 1
        
        if usage_count + 1 == 0:
            return 0.0
        
        return success_count / (usage_count + 1)
    
    def get_statistics(self):
        """获取知识库统计信息"""
        total_entries = len(self.knowledge_base)
        total_usage = sum(entry.get("usage_count", 0) for entry in self.knowledge_base.values())
        avg_success_rate = sum(entry.get("success_rate", 0) for entry in self.knowledge_base.values()) / total_entries if total_entries > 0 else 0
        
        return {
            "total_entries": total_entries,
            "total_usage": total_usage,
            "average_success_rate": avg_success_rate,
            "last_updated": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # 测试错误知识库
    kb = ErrorKnowledgeBase()
    
    # 添加测试解决方案
    kb.add_solution("Connection refused", {
        "solution": "检查服务是否正在运行",
        "actions": ["检查相关服务进程", "尝试重启服务"],
        "success_rate": 0.8,
        "last_used": datetime.now().isoformat(),
        "usage_count": 1
    })
    
    # 测试获取解决方案
    error_message = "Connection refused"
    solution = kb.get_solution(error_message)
    print(f"获取解决方案: {solution}")
    
    # 测试从修复中学习
    test_error = {
        "type": "ConnectionError",
        "message": "Connection refused",
        "timestamp": datetime.now().isoformat()
    }
    
    kb.learn_from_fix(test_error, "检查服务是否正在运行", True)
    
    # 打印统计信息
    print(f"知识库统计: {kb.get_statistics()}")
