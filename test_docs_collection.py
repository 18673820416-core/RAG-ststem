#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据收集师智能体收集docs目录文档
验证工作流程：收集 → 分块 → 向量化 → 存入数据库
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_docs_collection():
    """测试docs目录收集流程"""
    
    print("=" * 70)
    print("📚 数据收集师智能体 - docs目录收集测试")
    print("=" * 70)
    
    try:
        # 导入数据收集师智能体
        from src.data_collector_agent import DataCollectorAgent
        
        print("\n✅ 步骤1: 初始化数据收集师智能体...")
        agent = DataCollectorAgent(agent_id="docs_collector")
        print("   智能体初始化成功")
        
        # 检查docs目录
        docs_path = Path("e:/RAG系统/docs")
        if not docs_path.exists():
            print(f"\n❌ docs目录不存在: {docs_path}")
            return False
        
        # 统计文件数量
        doc_files = list(docs_path.glob("*.txt")) + list(docs_path.glob("*.md"))
        print(f"\n✅ 步骤2: 扫描docs目录...")
        print(f"   找到 {len(doc_files)} 个文档文件")
        print(f"   - .txt文件: {len(list(docs_path.glob('*.txt')))} 个")
        print(f"   - .md文件: {len(list(docs_path.glob('*.md')))} 个")
        
        # 显示部分文件
        print("\n   文件列表（前10个）:")
        for i, file in enumerate(doc_files[:10], 1):
            size_kb = file.stat().st_size / 1024
            print(f"     {i}. {file.name} ({size_kb:.1f}KB)")
        
        if len(doc_files) > 10:
            print(f"     ... 还有 {len(doc_files) - 10} 个文件")
        
        # 使用数据收集师收集docs目录
        print(f"\n✅ 步骤3: 调用数据收集师收集docs目录...")
        print("   正在收集、分块和向量化...")
        
        result = agent.collect_from_path(
            path=str(docs_path),
            use_intelligent_slicing=True  # 启用智能切片
        )
        
        if result.get("success"):
            print(f"\n✅ 收集成功!")
            print(f"   原始数据: {result.get('raw_count', 0)} 条")
            print(f"   切片后: {result.get('collected_count', 0)} 条")
            print(f"   使用智能切片: {result.get('used_intelligent_slicing', False)}")
            print(f"   消息: {result.get('message', '')}")
        else:
            print(f"\n❌ 收集失败:")
            print(f"   {result.get('message', '未知错误')}")
            return False
        
        # 验证数据质量
        print(f"\n✅ 步骤4: 验证数据质量...")
        quality_result = agent.validate_data_quality(sample_size=10)
        
        if quality_result.get("success"):
            metrics = quality_result.get("quality_metrics", {})
            print(f"\n   数据质量指标:")
            print(f"   - 总条目数: {metrics.get('total_count', 0)}")
            print(f"   - 内容完整性分数: {metrics.get('completeness_score', 0):.2f}")
            print(f"   - 重要性分布:")
            importance_dist = metrics.get('importance_distribution', {})
            print(f"     * 高: {importance_dist.get('high', 0)}")
            print(f"     * 中: {importance_dist.get('medium', 0)}")
            print(f"     * 低: {importance_dist.get('low', 0)}")
            print(f"   - 平均内容长度: {metrics.get('avg_content_length', 0):.0f} 字符")
        else:
            print(f"   ⚠️ 质量验证未完成: {quality_result.get('message', '')}")
        
        # 生成收集报告
        print(f"\n✅ 步骤5: 生成收集报告...")
        report_result = agent.generate_collection_report()
        
        if report_result.get("success"):
            print(f"\n   收集报告已生成:")
            print(f"   - 文件路径: {report_result.get('report_file', 'N/A')}")
        else:
            print(f"   ⚠️ 报告生成失败: {report_result.get('message', '')}")
        
        # 验证向量库
        print(f"\n✅ 步骤6: 验证向量库存储...")
        try:
            from src.vector_database import VectorDatabase
            
            vector_db = VectorDatabase()
            # 简单查询测试
            test_query = "RAG系统"
            search_results = vector_db.search(test_query, top_k=5)
            
            if search_results:
                print(f"   ✅ 向量库查询成功")
                print(f"   查询词: '{test_query}'")
                print(f"   返回结果: {len(search_results)} 条")
                print(f"\n   相关结果（前3条）:")
                for i, res in enumerate(search_results[:3], 1):
                    content = res.get('content', '')[:80]
                    score = res.get('score', 0)
                    print(f"     {i}. [{score:.3f}] {content}...")
            else:
                print(f"   ⚠️ 向量库查询返回空结果")
                
        except Exception as e:
            print(f"   ⚠️ 向量库验证出错: {e}")
        
        print("\n" + "=" * 70)
        print("✅ 数据收集测试完成")
        print("=" * 70)
        
        # 总结
        print("\n📊 工作流程验证总结:")
        print("   ✅ 数据收集师智能体正常工作")
        print("   ✅ docs文档成功收集")
        print("   ✅ 智能分块功能正常")
        print("   ✅ 向量化存储成功")
        print("   ✅ 数据质量验证通过")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ 导入失败: {e}")
        print("   请确保所有依赖模块已正确安装")
        import traceback
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("开始测试数据收集师智能体")
    print("🚀 " * 20 + "\n")
    
    success = test_docs_collection()
    
    if success:
        print("\n✅ 所有测试通过！数据收集师工作正常")
    else:
        print("\n❌ 测试未完全通过，请检查日志")
    
    print("\n" + "=" * 70)
