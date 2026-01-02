#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版测试：直接调用数据收集器收集docs目录
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置基本日志
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def simple_test():
    """简化版测试"""
    print("=" * 60)
    print("📚 简化测试：docs目录数据收集")
    print("=" * 60)
    
    # 步骤1：检查docs目录
    docs_path = Path("e:/RAG系统/docs")
    print(f"\n✅ 检查docs目录: {docs_path}")
    
    if not docs_path.exists():
        print(f"❌ 目录不存在")
        return
    
    # 统计文件
    txt_files = list(docs_path.glob("*.txt"))
    md_files = list(docs_path.glob("*.md"))
    print(f"   找到 {len(txt_files)} 个.txt文件")
    print(f"   找到 {len(md_files)} 个.md文件")
    print(f"   总计: {len(txt_files) + len(md_files)} 个文档")
    
    # 步骤2：创建数据收集器
    print(f"\n✅ 初始化数据收集器...")
    try:
        from src.data_collector import DataCollector
        collector = DataCollector()
        print("   数据收集器初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 步骤3：收集数据
    print(f"\n✅ 开始收集docs目录数据...")
    print(f"   这将执行：收集 → 智能分块 → 向量化 → 存储")
    
    try:
        raw_data = collector.collect_from_file_system(str(docs_path))
        print(f"\n   收集到 {len(raw_data)} 个原始文档")
        
        if raw_data:
            # 显示第一个文档的信息
            first_doc = raw_data[0]
            print(f"\n   示例文档信息:")
            print(f"   - 文件: {Path(first_doc.get('file_path', '')).name}")
            print(f"   - 大小: {first_doc.get('file_size', 0)} 字符")
            print(f"   - 类型: {first_doc.get('file_type', 'N/A')}")
            
            # 步骤4：智能分块
            print(f"\n✅ 开始智能分块...")
            all_slices = []
            for doc in raw_data[:5]:  # 先测试前5个文档
                content = doc.get('content', '')
                if content:
                    slices = collector._intelligent_slice_text(
                        content, 
                        doc.get('file_path', '')
                    )
                    all_slices.extend(slices)
                    print(f"   {Path(doc.get('file_path', '')).name}: {len(slices)} 个切片")
            
            print(f"\n   总切片数: {len(all_slices)}")
            
            # 步骤5：保存数据（含向量化）
            print(f"\n✅ 保存数据到向量库...")
            collector._save_collected_data(all_slices)
            print(f"   保存完成！")
            
            # 步骤6：验证向量库
            print(f"\n✅ 验证向量库...")
            try:
                from src.vector_database import VectorDatabase
                vdb = VectorDatabase()
                
                test_results = vdb.search("RAG系统", top_k=3)
                if test_results:
                    print(f"   查询成功，返回 {len(test_results)} 条结果")
                    print(f"\n   示例结果:")
                    for i, res in enumerate(test_results[:2], 1):
                        print(f"   {i}. {res.get('content', '')[:60]}...")
                else:
                    print(f"   查询返回空结果")
                    
            except Exception as e:
                print(f"   向量库验证出错: {e}")
            
            print("\n" + "=" * 60)
            print("✅ 测试完成！")
            print("=" * 60)
            print(f"\n📊 工作流程摘要:")
            print(f"   ✅ 收集了 {len(raw_data)} 个文档")
            print(f"   ✅ 生成了 {len(all_slices)} 个智能切片")
            print(f"   ✅ 数据已存入向量库")
            
        else:
            print(f"❌ 未收集到任何数据")
            
    except Exception as e:
        print(f"❌ 收集过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
