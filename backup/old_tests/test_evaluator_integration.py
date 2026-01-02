#!/usr/bin/env python3
# @self-expose: {"id": "test_evaluator_integration", "name": "Test Evaluator Integration", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Evaluator Integration功能"]}}
"""
评估师智能体与统一切片器集成测试
测试基于统一切片原理的写操作评估功能
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

from scheme_evaluator_agent import get_scheme_evaluator

def test_write_operation_evaluation():
    """测试写操作评估功能"""
    print("=== 评估师智能体写操作评估测试 ===")
    
    # 获取评估师智能体实例
    evaluator = get_scheme_evaluator()
    print("✓ 评估师智能体初始化成功")
    
    # 测试文本内容
    test_content = """
    基于统一切片原理的智能评估系统设计。该系统采用信息熵计算和逻辑边界检测技术，
    能够自动识别文本、代码和文档的结构边界，并进行质量评估。系统包含多个评估维度，
    包括技术可行性、成本效益、风险评估等，为架构决策提供数据支持。
    
    系统采用模块化设计，各组件之间通过标准接口进行通信，确保系统的可扩展性和维护性。
    评估结果以量化的形式呈现，便于决策者理解和比较不同方案的优劣。
    """
    
    print(f"测试内容长度: {len(test_content)} 字符")
    
    # 执行写操作评估
    print("\n执行写操作评估...")
    result = evaluator.evaluate_write_operation(test_content, "text_processing")
    
    # 输出评估结果
    print(f"\n评估结果:")
    print(f"- 总体得分: {result.get('overall_score', 0):.1f}")
    print(f"- 评估状态: {result.get('status', 'unknown')}")
    print(f"- 生成分片数: {result.get('total_slices', 0)}")
    print(f"- 平均质量得分: {result.get('avg_quality', 0):.3f}")
    print(f"- 平均信息熵: {result.get('avg_entropy', 0):.3f}")
    print(f"- 语义连贯性: {result.get('semantic_coherence', 0):.3f}")
    
    # 显示分片详情
    slices_details = result.get('slices_details', [])
    if slices_details:
        print(f"\n分片详情:")
        for i, slice_info in enumerate(slices_details, 1):
            print(f"  分片 {i}:")
            print(f"    - 长度: {len(slice_info.get('content', ''))} 字符")
            print(f"    - 质量得分: {slice_info.get('quality_score', 0):.3f}")
            print(f"    - 信息熵: {slice_info.get('entropy', 0):.3f}")
    
    # 验证评估结果
    if result.get('status') == 'passed':
        print("\n✓ 写操作评估测试通过")
        return True
    else:
        print("\n✗ 写操作评估测试失败")
        return False

def test_query_processing():
    """测试查询处理功能"""
    print("\n=== 评估师智能体查询处理测试 ===")
    
    evaluator = get_scheme_evaluator()
    
    # 测试写操作评估查询
    test_query = "评估以下写操作质量：'基于信息熵的分片技术能够有效识别文本结构边界，提高内容处理的准确性和效率。'"
    
    print(f"测试查询: {test_query}")
    
    # 处理查询
    result = evaluator.process_user_query(test_query)
    
    # 输出处理结果
    query_analysis = result.get('query_analysis', {})
    print(f"查询类型: {query_analysis.get('query_type', 'unknown')}")
    print(f"查询描述: {query_analysis.get('description', 'unknown')}")
    
    evaluation_result = result.get('result', {})
    if evaluation_result.get('overall_score') is not None:
        print(f"评估得分: {evaluation_result.get('overall_score', 0):.1f}")
        print(f"评估状态: {evaluation_result.get('status', 'unknown')}")
        print("✓ 查询处理测试通过")
        return True
    else:
        print("✗ 查询处理测试失败")
        return False

def main():
    """主测试函数"""
    print("开始评估师智能体与统一切片器集成测试...\n")
    
    # 执行测试
    test1_passed = test_write_operation_evaluation()
    test2_passed = test_query_processing()
    
    # 总结测试结果
    print("\n=== 测试总结 ===")
    if test1_passed and test2_passed:
        print("✓ 所有测试通过 - 评估师智能体与统一切片器集成成功")
        print("✓ 基于统一切片原理的写操作评估机制已建立")
        return 0
    else:
        print("✗ 部分测试失败 - 需要检查集成问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)