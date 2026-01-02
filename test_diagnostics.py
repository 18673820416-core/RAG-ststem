#!/usr/bin/env python3
# @self-expose: {"id": "test_diagnostics", "name": "Test Diagnostics", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Diagnostics功能"]}}
# -*- coding: utf-8 -*-
"""
测试问题诊断模块的功能
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.problem_diagnostics import ProblemDiagnostics
from src.path_utils import get_path_utils
from src.error_knowledge_base import ErrorKnowledgeBase
from src.agent_error_handler import AgentErrorHandler

def test_problem_diagnostics():
    """测试问题诊断模块的基本功能"""
    print("=== 测试问题诊断模块 ===")
    
    # 初始化诊断模块
    diagnostics = ProblemDiagnostics()
    
    # 运行完整诊断
    results = diagnostics.run_full_diagnostics()
    
    # 验证诊断结果
    assert results is not None, "诊断结果不能为空"
    assert 'status' in results, "诊断结果必须包含status字段"
    assert 'problems' in results, "诊断结果必须包含problems字段"
    assert 'system_info' in results, "诊断结果必须包含system_info字段"
    assert 'component_status' in results, "诊断结果必须包含component_status字段"
    
    print(f"✅ 诊断完成，状态: {results['status']}")
    print(f"✅ 检测到 {len(results['problems'])} 个问题")
    
    # 测试报告生成
    text_report = diagnostics.generate_report(format='text')
    assert isinstance(text_report, str), "文本报告必须是字符串"
    assert len(text_report) > 0, "文本报告不能为空"
    print("✅ 文本报告生成成功")
    
    json_report = diagnostics.generate_report(format='json')
    assert isinstance(json_report, dict), "JSON报告必须是字典"
    print("✅ JSON报告生成成功")
    
    # 测试报告保存
    report_path = diagnostics.save_report()
    assert os.path.exists(report_path), "报告文件必须保存成功"
    print(f"✅ 报告保存成功: {report_path}")
    
    # 清理测试文件
    if os.path.exists(report_path):
        os.remove(report_path)
    
    return True

def test_path_utils():
    """测试路径处理工具"""
    print("\n=== 测试路径处理工具 ===")
    
    path_utils = get_path_utils()
    
    # 测试特殊字符处理
    problematic_path = "e:\\AI\\qiusuo-framework\\#problems_and_diagnostics"
    safe_path = path_utils.fix_path(problematic_path)
    
    assert safe_path is not None, "修复后的路径不能为空"
    assert "#" not in safe_path, "修复后的路径不应包含#字符"
    print(f"✅ 路径特殊字符处理成功: {safe_path}")
    
    # 测试问题目录获取
    problems_dir = path_utils.get_problems_directory()
    assert os.path.exists(problems_dir), "问题目录必须存在"
    print(f"✅ 问题目录获取成功: {problems_dir}")
    
    return True

def test_error_knowledge_base():
    """测试错误知识库"""
    print("\n=== 测试错误知识库 ===")
    
    kb = ErrorKnowledgeBase()
    
    # 测试添加解决方案
    error_pattern = "Connection refused"
    solution = {
        "solution": "检查服务是否正在运行",
        "actions": ["检查相关服务进程", "尝试重启服务"]
    }
    kb.add_solution(error_pattern, solution)
    
    # 测试获取解决方案
    retrieved_solution = kb.get_solution("Connection refused")
    assert retrieved_solution is not None, "应该能获取到解决方案"
    print("✅ 错误知识库功能正常")
    
    # 测试统计信息
    stats = kb.get_statistics()
    assert isinstance(stats, dict), "统计信息必须是字典"
    print(f"✅ 知识库统计信息: {stats}")
    
    return True

def test_agent_error_handler():
    """测试智能体错误处理模块"""
    print("\n=== 测试智能体错误处理模块 ===")
    
    error_handler = AgentErrorHandler()
    
    # 测试错误分析
    test_error = {
        "type": "ConnectionError",
        "message": "Connection refused",
        "timestamp": datetime.now().isoformat()
    }
    
    analysis = error_handler.analyze_error(test_error)
    assert isinstance(analysis, dict), "错误分析结果必须是字典"
    print("✅ 智能体错误处理模块功能正常")
    
    return True

def test_diagnostics_api():
    """测试诊断API端点"""
    print("\n=== 测试诊断API端点 ===")
    
    import requests
    
    try:
        response = requests.get("http://localhost:10808/api/diagnostics", timeout=5)
        assert response.status_code == 200, f"API请求失败，状态码: {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "API响应必须包含success: true"
        assert "diagnostics" in data, "API响应必须包含diagnostics字段"
        
        print("✅ 诊断API端点功能正常")
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API测试失败: {e}")
        return False
    except AssertionError as e:
        print(f"⚠️ API响应验证失败: {e}")
        return False

if __name__ == "__main__":
    """运行所有测试"""
    print("开始测试问题诊断相关功能...\n")
    
    test_results = {
        "problem_diagnostics": test_problem_diagnostics(),
        "path_utils": test_path_utils(),
        "error_knowledge_base": test_error_knowledge_base(),
        "agent_error_handler": test_agent_error_handler(),
        "diagnostics_api": test_diagnostics_api()
    }
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总测试数: {total}, 通过: {passed}, 失败: {total - passed}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败！")
        sys.exit(1)
