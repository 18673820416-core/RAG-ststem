# @self-expose: {"id": "reasoning_engine", "name": "Reasoning Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Reasoning Engine功能"]}}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python源代码文件 - reasoning_engine.py
"""


# -*- coding: utf-8 -*-
"""
QiuSuo Framework AI Core - 推理引擎模块
实现基于理性逻辑四规则的推理引擎
"""

import os
import sys
import logging
import threading
import datetime
import json
from typing import Dict, Any, List, Tuple, Optional, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ReasoningEngine")

class ReasoningRule:
    """
    推理规则基类
    所有推理规则都应该继承这个类
    """
    def __init__(self, name: str, description: str, weight: float = 1.0):
        """
        初始化推理规则
        
        参数:
            name: 规则名称
            description: 规则描述
            weight: 规则权重
        """
        self.name = name
        self.description = description
        self.weight = max(0.0, min(2.0, weight))  # 权重范围0.0-2.0
        
    def apply(self, premise: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, str]:
        """
        应用规则进行推理
        
        参数:
            premise: 前提条件
            context: 上下文信息
            
        返回:
            Tuple[float, str]: 规则满足度(0.0-1.0)和推理说明
        """
        raise NotImplementedError("子类必须实现apply方法")

class ContradictionRule(ReasoningRule):
    """
    矛盾律规则：一个命题不能同时为真和为假
    """
    def __init__(self):
        super().__init__(
            name="矛盾律",
            description="一个命题不能同时为真和为假"
        )
    
    def apply(self, premise: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, str]:
        """
        应用矛盾律进行推理
        """
        try:
            # 提取命题内容
            content = premise.get("content", {})
            propositions = content.get("propositions", [])
            
            # 简单实现：检查是否存在明显矛盾的命题
            contradictions = []
            for i, prop1 in enumerate(propositions):
                for j, prop2 in enumerate(propositions[i+1:], i+1):
                    # 检查命题1的结论和命题2的结论是否矛盾
                    if ("conclusion" in prop1 and "conclusion" in prop2 and 
                        prop1["conclusion"] == f"!{prop2['conclusion']}" or 
                        prop2["conclusion"] == f"!{prop1['conclusion']}"):
                        contradictions.append((i, j))
            
            if contradictions:
                contradiction_count = len(contradictions)
                max_possible = len(propositions) * (len(propositions) - 1) / 2
                contradiction_ratio = contradiction_count / max_possible if max_possible > 0 else 0
                
                # 矛盾越多，满足度越低
                satisfaction = max(0.0, 1.0 - contradiction_ratio * 2)
                return satisfaction, f"检测到{contradiction_count}对矛盾命题，矛盾度: {contradiction_ratio:.2f}"
            else:
                return 1.0, "未检测到矛盾命题"
        except Exception as e:
            logger.error(f"应用矛盾律失败: {e}")
            return 0.5, f"规则应用出错: {str(e)}"

class IdentityRule(ReasoningRule):
    """
    同一律规则：一个命题必须与其自身保持一致
    """
    def __init__(self):
        super().__init__(
            name="同一律",
            description="一个命题必须与其自身保持一致"
        )
    
    def apply(self, premise: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, str]:
        """
        应用同一律进行推理
        """
        try:
            # 提取命题内容
            content = premise.get("content", {})
            propositions = content.get("propositions", [])
            
            # 检查是否存在自我矛盾或定义不一致的情况
            inconsistencies = 0
            
            # 检查命题中的概念是否前后一致
            concept_definitions = {}
            for i, prop in enumerate(propositions):
                if "concepts" in prop:
                    for concept_name, concept_def in prop["concepts"].items():
                        if concept_name in concept_definitions:
                            # 如果概念已经被定义过，检查是否一致
                            if concept_definitions[concept_name] != concept_def:
                                inconsistencies += 1
                        else:
                            concept_definitions[concept_name] = concept_def
            
            if inconsistencies > 0:
                # 不一致的概念越多，满足度越低
                satisfaction = max(0.0, 1.0 - inconsistencies / len(propositions) if len(propositions) > 0 else 0)
                return satisfaction, f"检测到{inconsistencies}个不一致的概念定义"
            else:
                return 1.0, "概念定义一致，满足同一律"
        except Exception as e:
            logger.error(f"应用同一律失败: {e}")
            return 0.5, f"规则应用出错: {str(e)}"

class ExcludedMiddleRule(ReasoningRule):
    """
    排中律规则：一个命题要么为真，要么为假，没有中间状态
    """
    def __init__(self):
        super().__init__(
            name="排中律",
            description="一个命题要么为真，要么为假，没有中间状态"
        )
    
    def apply(self, premise: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, str]:
        """
        应用排中律进行推理
        """
        try:
            # 提取命题内容
            content = premise.get("content", {})
            propositions = content.get("propositions", [])
            
            # 检查是否存在模糊或中间状态的命题
            vague_propositions = []
            
            for i, prop in enumerate(propositions):
                if "conclusion" in prop:
                    conclusion = prop["conclusion"]
                    # 简单判断：检查是否包含模糊词语
                    vague_terms = ["可能", "也许", "大概", "似乎", "说不定", "maybe", "perhaps", "probably", "likely"]
                    conclusion_lower = conclusion.lower()
                    
                    for term in vague_terms:
                        if term in conclusion_lower:
                            vague_propositions.append(i)
                            break
            
            if vague_propositions:
                vague_count = len(vague_propositions)
                # 模糊命题越多，满足度越低
                satisfaction = max(0.0, 1.0 - vague_count / len(propositions) if len(propositions) > 0 else 0)
                return satisfaction, f"检测到{vague_count}个模糊命题，违反排中律"
            else:
                return 1.0, "命题明确，满足排中律"
        except Exception as e:
            logger.error(f"应用排中律失败: {e}")
            return 0.5, f"规则应用出错: {str(e)}"

class SufficientReasonRule(ReasoningRule):
    """
    充足理由律规则：任何命题都必须有充足的理由支持
    """
    def __init__(self):
        super().__init__(
            name="充足理由律",
            description="任何命题都必须有充足的理由支持"
        )
    
    def apply(self, premise: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, str]:
        """
        应用充足理由律进行推理
        """
        try:
            # 提取命题内容
            content = premise.get("content", {})
            propositions = content.get("propositions", [])
            
            # 检查每个命题是否有充分的理由支持
            insufficient_propositions = []
            
            for i, prop in enumerate(propositions):
                # 检查是否有前提和证据
                has_premises = "premises" in prop and len(prop["premises"]) > 0
                has_evidence = "evidence" in prop and len(prop["evidence"]) > 0
                
                if not has_premises and not has_evidence:
                    insufficient_propositions.append(i)
            
            if insufficient_propositions:
                insufficient_count = len(insufficient_propositions)
                # 缺乏理由的命题越多，满足度越低
                satisfaction = max(0.0, 1.0 - insufficient_count / len(propositions) if len(propositions) > 0 else 0)
                return satisfaction, f"检测到{insufficient_count}个命题缺乏足够支持理由"
            else:
                return 1.0, "所有命题都有足够的支持理由，满足充足理由律"
        except Exception as e:
            logger.error(f"应用充足理由律失败: {e}")
            return 0.5, f"规则应用出错: {str(e)}"

class ReasoningEngine:
    """
    推理引擎类
    实现基于理性逻辑四规则的推理功能
    """
    # 类属性，确保全局唯一实例
    _instance = None
    _lock = threading.RLock()
    _initialized = False
    _version = "1.0.0"
    
    def __new__(cls):
        """确保单例模式"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ReasoningEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化推理引擎
        """
        with self.__class__._lock:
            if not self.__class__._initialized:
                # 初始化工作内存
                self._working_memory = {}
                
                # 初始化推理规则
                self._rules = {
                    "contradiction": ContradictionRule(),
                    "identity": IdentityRule(),
                    "excluded_middle": ExcludedMiddleRule(),
                    "sufficient_reason": SufficientReasonRule()
                }
                
                # 初始化元数据
                self._status = {
                    "is_alive": True,
                    "version": self.__class__._version,
                    "start_time": datetime.datetime.now().isoformat(),
                    "rule_count": len(self._rules),
                    "推理次数": 0
                }
                
                logger.info("推理引擎已初始化，版本: %s", self.__class__._version)
                self.__class__._initialized = True
    
    def set_rule_weight(self, rule_name: str, weight: float) -> bool:
        """
        设置推理规则的权重
        
        参数:
            rule_name: 规则名称
            weight: 权重值(0.0-2.0)
            
        返回:
            bool: 是否设置成功
        """
        try:
            with self.__class__._lock:
                if rule_name in self._rules:
                    self._rules[rule_name].weight = max(0.0, min(2.0, weight))
                    logger.info(f"已设置规则'{rule_name}'的权重为{weight}")
                    return True
                else:
                    logger.warning(f"未找到规则'{rule_name}'")
                    return False
        except Exception as e:
            logger.error(f"设置规则权重失败: {e}")
            return False
    
    def get_rule_weight(self, rule_name: str) -> Optional[float]:
        """
        获取推理规则的权重
        
        参数:
            rule_name: 规则名称
            
        返回:
            float或None: 权重值或None（如果未找到规则）
        """
        try:
            with self.__class__._lock:
                if rule_name in self._rules:
                    return self._rules[rule_name].weight
                else:
                    logger.warning(f"未找到规则'{rule_name}'")
                    return None
        except Exception as e:
            logger.error(f"获取规则权重失败: {e}")
            return None
    
    def add_working_memory(self, key: str, value: Any) -> bool:
        """
        添加工作记忆
        
        参数:
            key: 记忆键名
            value: 记忆值
            
        返回:
            bool: 是否添加成功
        """
        try:
            with self.__class__._lock:
                self._working_memory[key] = value
                logger.debug(f"已添加工作记忆，键: {key}")
                return True
        except Exception as e:
            logger.error(f"添加工作记忆失败: {e}")
            return False
    
    def get_working_memory(self, key: str) -> Optional[Any]:
        """
        获取工作记忆
        
        参数:
            key: 记忆键名
            
        返回:
            Any或None: 记忆值或None（如果未找到）
        """
        try:
            with self.__class__._lock:
                if key in self._working_memory:
                    return self._working_memory[key]
                else:
                    logger.debug(f"未找到工作记忆，键: {key}")
                    return None
        except Exception as e:
            logger.error(f"获取工作记忆失败: {e}")
            return None
    
    def reason(self, premise: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行推理过程
        
        参数:
            premise: 前提条件
            context: 上下文信息
            
        返回:
            Dict: 推理结果
        """
        try:
            with self.__class__._lock:
                # 更新推理次数
                self._status["推理次数"] += 1
                
                # 准备上下文
                if context is None:
                    context = self._working_memory.copy()
                else:
                    # 合并工作记忆到上下文
                    context.update(self._working_memory.copy())
                
                # 应用所有推理规则
                rule_results = {}
                total_weight = 0.0
                weighted_satisfaction = 0.0
                
                for rule_name, rule in self._rules.items():
                    satisfaction, explanation = rule.apply(premise, context)
                    rule_weight = rule.weight
                    
                    rule_results[rule_name] = {
                        "name": rule.name,
                        "description": rule.description,
                        "satisfaction": satisfaction,
                        "explanation": explanation,
                        "weight": rule_weight
                    }
                    
                    total_weight += rule_weight
                    weighted_satisfaction += satisfaction * rule_weight
                
                # 计算总体满足度
                overall_satisfaction = weighted_satisfaction / total_weight if total_weight > 0 else 0.0
                
                # 生成推理结果
                result = {
                    "reasoning_id": f"reasoning_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "premise": premise,
                    "overall_satisfaction": overall_satisfaction,
                    "rule_results": rule_results,
                    "status": "success",
                    "recommendation": "接受推理结论" if overall_satisfaction > 0.7 else "需要进一步验证"
                }
                
                # 将结果添加到工作记忆
                self._working_memory[f"reasoning_{result['reasoning_id']}"] = result
                
                logger.info(f"推理完成，ID: {result['reasoning_id']}, 总体满足度: {overall_satisfaction:.2f}")
                return result
        except Exception as e:
            logger.error(f"推理过程失败: {e}")
            return {
                "reasoning_id": f"reasoning_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "timestamp": datetime.datetime.now().isoformat(),
                "premise": premise,
                "status": "failure",
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取推理引擎状态
        
        返回:
            Dict: 包含引擎状态信息的字典
        """
        with self.__class__._lock:
            # 更新状态
            self._status["runtime"] = (datetime.datetime.now() - 
                                       datetime.datetime.fromisoformat(self._status["start_time"])).total_seconds()
            
            # 添加规则状态
            rule_status = {}
            for rule_name, rule in self._rules.items():
                rule_status[rule_name] = {
                    "name": rule.name,
                    "description": rule.description,
                    "weight": rule.weight
                }
            
            status = {
                **self._status,
                "working_memory_size": len(self._working_memory),
                "rule_status": rule_status
            }
            
            # 返回深拷贝，确保不可修改
            import copy
            return copy.deepcopy(status)

# 创建全局实例
reasoning_engine_instance = None
def get_reasoning_engine() -> ReasoningEngine:
    """
    获取推理引擎实例
    
    返回:
        ReasoningEngine: 推理引擎实例
    """
    global reasoning_engine_instance
    if reasoning_engine_instance is None:
        reasoning_engine_instance = ReasoningEngine()
    return reasoning_engine_instance