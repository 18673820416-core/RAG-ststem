#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @self-expose: {"id": "self_expose_protocol", "name": "Self-Expose Protocol Manager", "type": "system", "version": "1.0.0", "needs": {"deps": ["error_reporting"], "resources": []}, "provides": {"capabilities": ["组件接口查询", "接口验证", "主动报错"], "methods": {"register_component": {"signature": "(component_id: str, interface_spec: Dict) -> bool", "description": "注册组件接口"}, "query_interface": {"signature": "(component_id: str, method_name: str) -> Optional[Dict]", "description": "查询组件接口"}, "validate_interface": {"signature": "(component_id: str, required_methods: List[str]) -> Tuple[bool, List[str]]", "description": "验证组件接口完整性"}, "report_interface_missing": {"signature": "(caller_id: str, component_id: str, method_name: str, context: Dict) -> None", "description": "报告接口缺失错误"}}}}
"""
组件自曝光协议管理器
实现组件接口的自曝光、查询、验证和主动报错机制

开发提示词来源：组件自曝光内部通讯协议 + 二级报错机制优化方案
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from src.error_reporting import get_error_reporting_service

logger = logging.getLogger(__name__)


class SelfExposeProtocol:
    """组件自曝光协议管理器"""
    
    def __init__(self, registry_path: str = "data/self_expose_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 组件接口注册表
        self.component_registry: Dict[str, Dict] = {}
        
        # 错误上报服务
        self.error_service = get_error_reporting_service()
        
        # 加载已注册的组件
        self._load_registry()
        
        # ✅ 降噪：将初始化完成日志降级为DEBUG
        logger.debug("组件自曝光协议管理器初始化完成")
    
    def _load_registry(self):
        """从文件加载组件注册表"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    self.component_registry = json.load(f)
                # ✅ 降噪：将组件加载日志降级为DEBUG，避免启动时日志混乱
                logger.debug(f"已加载 {len(self.component_registry)} 个组件注册信息")
            except Exception as e:
                logger.error(f"加载组件注册表失败: {e}")
                self.component_registry = {}
    
    def _save_registry(self):
        """保存组件注册表到文件"""
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.component_registry, f, ensure_ascii=False, indent=2)
            logger.debug("组件注册表已保存")
        except Exception as e:
            logger.error(f"保存组件注册表失败: {e}")
    
    def register_component(self, component_id: str, interface_spec: Dict) -> bool:
        """
        注册组件接口
        
        Args:
            component_id: 组件唯一标识
            interface_spec: 接口规范，包含methods字段定义所有公开方法
            
        Returns:
            是否注册成功
        """
        try:
            # 验证接口规范格式
            if "provides" not in interface_spec:
                raise ValueError("接口规范缺少 'provides' 字段")
            
            if "methods" not in interface_spec["provides"]:
                raise ValueError("接口规范缺少 'provides.methods' 字段")
            
            # 注册组件
            self.component_registry[component_id] = {
                "interface_spec": interface_spec,
                "registered_at": datetime.now().isoformat(),
                "last_queried": None
            }
            
            # 保存到文件
            self._save_registry()
            
            logger.info(f"组件 {component_id} 注册成功，提供 {len(interface_spec['provides']['methods'])} 个方法")
            return True
            
        except Exception as e:
            logger.error(f"注册组件 {component_id} 失败: {e}")
            return False
    
    def query_interface(self, component_id: str, method_name: Optional[str] = None) -> Optional[Dict]:
        """
        查询组件接口
        
        Args:
            component_id: 组件唯一标识
            method_name: 可选，指定查询的方法名，不指定则返回所有方法
            
        Returns:
            方法规范字典，未找到返回None
        """
        if component_id not in self.component_registry:
            logger.warning(f"组件 {component_id} 未注册")
            return None
        
        # 更新最后查询时间
        self.component_registry[component_id]["last_queried"] = datetime.now().isoformat()
        
        component_info = self.component_registry[component_id]
        methods = component_info["interface_spec"]["provides"]["methods"]
        
        if method_name:
            # 查询特定方法
            if method_name in methods:
                return methods[method_name]
            else:
                logger.warning(f"组件 {component_id} 不提供方法 {method_name}")
                return None
        else:
            # 返回所有方法
            return methods
    
    def validate_interface(self, component_id: str, required_methods: List[str]) -> Tuple[bool, List[str]]:
        """
        验证组件接口完整性
        
        Args:
            component_id: 组件唯一标识
            required_methods: 需要的方法列表
            
        Returns:
            (是否完整, 缺失的方法列表)
        """
        if component_id not in self.component_registry:
            # 组件未注册，所有方法都缺失
            return (False, required_methods)
        
        component_methods = self.component_registry[component_id]["interface_spec"]["provides"]["methods"]
        missing_methods = [method for method in required_methods if method not in component_methods]
        
        is_complete = len(missing_methods) == 0
        return (is_complete, missing_methods)
    
    def report_interface_missing(
        self, 
        caller_id: str, 
        component_id: str, 
        method_name: str, 
        context: Optional[Dict] = None
    ):
        """
        报告接口缺失错误（二级报错机制）
        
        这是自曝光协议的核心功能：组件在查询发现接口缺失时，主动向系统报错
        
        Args:
            caller_id: 调用方组件ID
            component_id: 被调用组件ID
            method_name: 缺失的方法名
            context: 上下文信息
        """
        # 生成组件级错误
        component_error = {
            "error_id": self.error_service.generate_error_id(caller_id, "interface_missing"),
            "level": "component",
            "type": "InterfaceMissingError",
            "message": f"组件 {caller_id} 尝试调用 {component_id}.{method_name}，但该方法不存在",
            "timestamp": datetime.now().isoformat(),
            "component": caller_id,
            "function": "interface_query",
            "file_path": "runtime",
            "line_number": 0,
            "stack_trace": "接口查询层",
            "context": {
                "caller_id": caller_id,
                "target_component": component_id,
                "missing_method": method_name,
                "registered_components": list(self.component_registry.keys()),
                "available_methods": list(self.component_registry.get(component_id, {}).get("interface_spec", {}).get("provides", {}).get("methods", {}).keys()) if component_id in self.component_registry else [],
                "user_context": context or {}
            },
            "severity": "error",
            "suggestion": self._generate_fix_suggestion(caller_id, component_id, method_name)
        }
        
        # 上报到二级报错系统
        self.error_service.report_component_error(component_error)
        
        logger.error(
            f"接口缺失报错: {caller_id} -> {component_id}.{method_name}\n"
            f"建议: {component_error['suggestion']}"
        )
    
    def _generate_fix_suggestion(self, caller_id: str, component_id: str, method_name: str) -> str:
        """生成修复建议"""
        if component_id not in self.component_registry:
            return (
                f"1. 检查组件 {component_id} 是否已正确注册\n"
                f"2. 确认组件ID拼写是否正确\n"
                f"3. 查看组件注册表：{self.registry_path}"
            )
        else:
            available_methods = self.component_registry[component_id]["interface_spec"]["provides"]["methods"]
            return (
                f"1. 组件 {component_id} 已注册，但不提供方法 {method_name}\n"
                f"2. 可用方法列表: {', '.join(available_methods.keys())}\n"
                f"3. 请在 {component_id} 中实现方法 {method_name}\n"
                f"4. 或者修改 {caller_id} 调用已有的方法"
            )
    
    def safe_call(self, caller_id: str, component_id: str, method_name: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        安全调用：查询接口前先验证，缺失则主动报错
        
        这是推荐的调用方式，确保在运行时发现接口缺失时立即报错
        
        Args:
            caller_id: 调用方组件ID
            component_id: 被调用组件ID
            method_name: 方法名
            context: 上下文信息
            
        Returns:
            方法规范，如果不存在则报错并返回None
        """
        # 查询接口
        method_spec = self.query_interface(component_id, method_name)
        
        if method_spec is None:
            # 接口缺失，主动报错
            self.report_interface_missing(caller_id, component_id, method_name, context)
            return None
        
        # 接口存在，返回方法规范
        logger.debug(f"接口查询成功: {component_id}.{method_name}")
        return method_spec
    
    def get_all_components(self) -> List[str]:
        """获取所有已注册的组件ID列表"""
        return list(self.component_registry.keys())
    
    def get_component_info(self, component_id: str) -> Optional[Dict]:
        """获取组件完整信息"""
        return self.component_registry.get(component_id)
    
    def generate_component_report(self) -> str:
        """生成组件注册报告"""
        report_lines = [
            "=" * 60,
            "组件自曝光注册表报告",
            "=" * 60,
            f"总组件数: {len(self.component_registry)}",
            ""
        ]
        
        for component_id, info in self.component_registry.items():
            methods = info["interface_spec"]["provides"]["methods"]
            report_lines.extend([
                f"组件: {component_id}",
                f"  注册时间: {info['registered_at']}",
                f"  最后查询: {info['last_queried'] or '从未'}",
                f"  提供方法: {len(methods)}",
                ""
            ])
            
            for method_name, method_spec in methods.items():
                report_lines.append(f"    - {method_name}: {method_spec.get('signature', 'N/A')}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


# 全局协议管理器实例
_protocol_manager = None


def get_protocol_manager() -> SelfExposeProtocol:
    """获取全局协议管理器实例"""
    global _protocol_manager
    if _protocol_manager is None:
        _protocol_manager = SelfExposeProtocol()
    return _protocol_manager


def register_component(component_id: str, interface_spec: Dict) -> bool:
    """便捷函数：注册组件"""
    return get_protocol_manager().register_component(component_id, interface_spec)


def safe_call(caller_id: str, component_id: str, method_name: str, context: Optional[Dict] = None) -> Optional[Dict]:
    """便捷函数：安全调用（自动报错）"""
    return get_protocol_manager().safe_call(caller_id, component_id, method_name, context)


def query_interface(component_id: str, method_name: Optional[str] = None) -> Optional[Dict]:
    """便捷函数：查询接口"""
    return get_protocol_manager().query_interface(component_id, method_name)
