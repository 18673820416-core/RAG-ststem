#!/usr/bin/env python
# @self-expose: {"id": "test_self_expose_protocol", "name": "Test Self Expose Protocol", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Self Expose Protocol功能"]}}
# -*- coding: utf-8 -*-
"""
测试组件自曝光协议和二级报错机制
演示如何通过协议避免接口调用错误
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.self_expose_protocol import get_protocol_manager, register_component, safe_call


def test_self_expose_protocol():
    """测试自曝光协议的完整流程"""
    print("=" * 60)
    print("测试组件自曝光协议和二级报错机制")
    print("=" * 60)
    
    protocol = get_protocol_manager()
    
    # 步骤1: 注册 BaseAgent 的接口
    print("\n步骤1: 注册 BaseAgent 接口")
    print("-" * 60)
    
    base_agent_spec = {
        "id": "base_agent",
        "name": "Base Agent",
        "type": "agent",
        "version": "1.0.0",
        "provides": {
            "capabilities": ["基础智能体能力", "工具调用", "记忆管理"],
            "methods": {
                "respond": {
                    "signature": "(message: str) -> Dict[str, Any]",
                    "description": "处理用户消息并返回响应"
                },
                "call_tool": {
                    "signature": "(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]",
                    "description": "委托工具集成器调用具体工具"
                },
                "create_memory": {
                    "signature": "(content: str, memory_type: str, priority: str, tags: Optional[List[str]]) -> Optional[str]",
                    "description": "创建记忆条目并写入向量数据库"
                }
            }
        }
    }
    
    success = register_component("base_agent", base_agent_spec)
    print(f"✓ BaseAgent 注册{'成功' if success else '失败'}")
    
    # 步骤2: 正确的调用 - 查询已存在的方法
    print("\n步骤2: 正确调用 - 查询已存在的方法")
    print("-" * 60)
    
    method_spec = safe_call(
        caller_id="stable_start_server",
        component_id="base_agent",
        method_name="respond",
        context={"endpoint": "/api/agent-template/message"}
    )
    
    if method_spec:
        print(f"✓ 接口查询成功:")
        print(f"  方法签名: {method_spec['signature']}")
        print(f"  方法描述: {method_spec['description']}")
    else:
        print("✗ 接口查询失败")
    
    # 步骤3: 错误的调用 - 查询不存在的方法（触发二级报错）
    print("\n步骤3: 错误调用 - 查询不存在的方法（触发二级报错）")
    print("-" * 60)
    
    method_spec = safe_call(
        caller_id="stable_start_server",
        component_id="base_agent",
        method_name="process_message",  # 这个方法不存在
        context={
            "endpoint": "/api/agent-template/message",
            "user_message": "测试消息"
        }
    )
    
    if method_spec:
        print("✓ 接口查询成功")
    else:
        print("✗ 接口不存在 - 已触发二级报错机制")
        print("  系统已自动向错误上报服务报告此问题")
        print("  智能体和IDE将收到错误通知")
    
    # 步骤4: 查询未注册的组件（触发二级报错）
    print("\n步骤4: 查询未注册的组件（触发二级报错）")
    print("-" * 60)
    
    method_spec = safe_call(
        caller_id="stable_start_server",
        component_id="unknown_component",  # 这个组件不存在
        method_name="some_method",
        context={"endpoint": "/api/unknown"}
    )
    
    if method_spec:
        print("✓ 接口查询成功")
    else:
        print("✗ 组件未注册 - 已触发二级报错机制")
        print("  系统已自动向错误上报服务报告此问题")
    
    # 步骤5: 生成组件注册报告
    print("\n步骤5: 生成组件注册报告")
    print("-" * 60)
    report = protocol.generate_component_report()
    print(report)
    
    # 步骤6: 验证错误日志
    print("\n步骤6: 验证错误日志")
    print("-" * 60)
    
    from pathlib import Path
    error_log = Path("logs/component_errors.log")
    
    if error_log.exists():
        with open(error_log, 'r', encoding='utf-8') as f:
            errors = f.readlines()
            recent_errors = errors[-3:]  # 获取最近3条错误
            
        print(f"✓ 错误日志已生成: {error_log}")
        print(f"  最近 {len(recent_errors)} 条组件级错误:")
        
        import json
        for i, error_line in enumerate(recent_errors, 1):
            try:
                error = json.loads(error_line)
                print(f"\n  [{i}] {error['type']}")
                print(f"      组件: {error['component']}")
                print(f"      消息: {error['message']}")
                print(f"      时间: {error['timestamp']}")
                if 'suggestion' in error:
                    print(f"      建议: {error['suggestion'][:100]}...")
            except:
                pass
    else:
        print("  错误日志文件尚未生成")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n核心优势:")
    print("✓ 组件在调用前查询接口，发现缺失立即报错")
    print("✓ 无需等到运行时才发现 AttributeError")
    print("✓ 错误信息包含完整上下文和修复建议")
    print("✓ 智能体和IDE自动感知错误")
    print("✓ 支持渐进式引入，可以逐步为组件添加自曝光声明")


if __name__ == "__main__":
    test_self_expose_protocol()
