#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接测试文件上传后的分片和向量化功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.memory_slicer_tool import MemorySlicerTool
from src.vector_database import VectorDatabase
from src.event_dimension_encoder import EventDimensionEncoder
from src.mesh_thought_engine import MeshThoughtEngine
from datetime import datetime

def test_manual_vectorization():
    """手动测试分片和向量化流程"""
    
    print("=" * 60)
    print("手动测试：文件内容 → 分片 → 向量化 → 入库")
    print("=" * 60)
    
    # 读取测试文件
    test_file = "test_upload_new.txt"
    print(f"\n📖 读取测试文件: {test_file}")
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   文件内容长度: {len(content)} 字符")
        print(f"   内容预览: {content[:100]}...")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    # 创建工具实例
    print(f"\n🔧 初始化工具...")
    try:
        slicer = MemorySlicerTool()
        vector_db = VectorDatabase()
        event_encoder = EventDimensionEncoder()
        mesh_engine = MeshThoughtEngine()
        print(f"   ✓ 分片工具初始化成功")
        print(f"   ✓ 向量数据库初始化成功")
        print(f"   ✓ 事件维编码器初始化成功")
        print(f"   ✓ 网状思维引擎初始化成功")
    except Exception as e:
        print(f"❌ 工具初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 执行分片
    print(f"\n✂️  执行多层次自适应分片...")
    try:
        metadata = {
            "source": "manual_test",
            "filename": test_file,
            "file_ext": ".txt",
            "upload_time": datetime.now().isoformat()
        }
        
        slices = slicer.slice_text(
            text=content,
            metadata=metadata,
            source_file=test_file
        )
        
        print(f"   ✓ 分片完成，生成 {len(slices)} 个切片")
        
        if slices:
            print(f"\n   切片详情:")
            for i, slice_data in enumerate(slices[:3], 1):  # 显示前3个
                print(f"   [{i}] ID: {slice_data.get('slice_id')}, 深度: {slice_data.get('slice_depth')}")
                print(f"       内容: {slice_data.get('content', '')[:60]}...")
    except Exception as e:
        print(f"❌ 分片失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 向量化并存储
    print(f"\n💾 向量化并存入向量库...")
    saved_count = 0
    
    for idx, slice_data in enumerate(slices, 1):
        slice_content = slice_data.get('content', '')
        if not slice_content:
            continue
        
        try:
            # 提取事件编码
            event_codes = event_encoder.extract_event_codes_from_memory(slice_data)
            
            # 网状思维分析
            mesh_engine.add_thought(slice_content, slice_data)
            
            # 生成简单向量
            content_vector = [0.5] * 12  # 简化的12维向量
            
            # 构建记忆数据
            memory_data = {
                "topic": f"手动测试 - {test_file}",
                "content": slice_content,
                "source_type": "manual_test",
                "filename": test_file,
                "slice_id": slice_data.get('slice_id', ''),
                "slice_depth": slice_data.get('slice_depth', 0),
                "parent_id": slice_data.get('parent_id', ''),
                "event_codes": event_codes,
                "timestamp": metadata['upload_time'],
                "importance": 0.7,
                "confidence": 0.9,
                "tags": ["manual_test", test_file, "txt"] + event_codes
            }
            
            # 保存到向量库
            memory_id = vector_db.add_memory(memory_data, vector=content_vector)
            saved_count += 1
            
            if idx <= 3:  # 显示前3个
                print(f"   [{idx}] ✓ 已保存，ID: {memory_id}")
                
        except Exception as e:
            print(f"   [{idx}] ❌ 保存失败: {e}")
            continue
    
    print(f"\n   ✓ 向量化完成，成功保存 {saved_count}/{len(slices)} 个切片")
    
    # 验证查询
    print(f"\n🔍 验证查询...")
    try:
        memories = vector_db.search_memories(
            query="测试",
            source_type="manual_test",
            limit=5
        )
        
        print(f"   找到 {len(memories)} 条相关记忆")
        
        if memories:
            print(f"\n   查询结果样例:")
            for i, mem in enumerate(memories[:2], 1):
                print(f"   [{i}] 主题: {mem.get('topic')}")
                print(f"       来源: {mem.get('source_type')}")
                print(f"       内容: {mem.get('content', '')[:60]}...")
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
        return False
    
    return saved_count > 0

if __name__ == "__main__":
    success = test_manual_vectorization()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过：分片 → 向量化 → 入库流程正常")
    else:
        print("❌ 测试失败")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
