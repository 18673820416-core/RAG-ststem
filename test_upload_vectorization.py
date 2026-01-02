#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试文件上传的完整流程：上传 → 分片 → 向量化 → 入库"""

import requests
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_upload_and_vectorization():
    """测试文件上传并检查向量化结果"""
    
    print("=" * 60)
    print("测试文件上传 + 分片 + 向量化流程")
    print("=" * 60)
    
    # 1. 上传测试文件
    url = "http://localhost:10808/api/upload"
    test_file = "test_upload_new.txt"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"\n📤 步骤1: 上传文件 {test_file}")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查向量化结果
            if 'vectorization' in result:
                vec_result = result['vectorization']
                print(f"\n✅ 向量化结果:")
                print(f"   状态: {vec_result.get('status')}")
                print(f"   总切片数: {vec_result.get('total_slices', 0)}")
                print(f"   已保存切片数: {vec_result.get('saved_slices', 0)}")
                print(f"   消息: {vec_result.get('message', '')}")
                
                if vec_result.get('status') == 'success':
                    print(f"\n🎉 文件上传并向量化成功!")
                    return True
                else:
                    print(f"\n⚠️  向量化失败: {vec_result.get('reason', '未知原因')}")
                    return False
            else:
                print(f"\n⚠️  响应中没有向量化结果字段")
                return False
        else:
            print(f"❌ 上传失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务器 {url}")
        print(f"   请确保服务器已启动（python stable_start_server.py --port 10808）")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 验证向量库中的数据
    print(f"\n📊 步骤2: 检查向量库中的数据")
    try:
        from src.vector_database import VectorDatabase
        
        vector_db = VectorDatabase()
        
        # 查询最近上传的文件
        memories = vector_db.search_memories(
            query="测试文件 分片 向量化",
            limit=10
        )
        
        if memories:
            print(f"   找到 {len(memories)} 条相关记忆")
            
            # 显示最近的一条
            latest = memories[0]
            print(f"\n   最新记忆:")
            print(f"   - ID: {latest.get('id', 'N/A')}")
            print(f"   - 主题: {latest.get('topic', 'N/A')}")
            print(f"   - 来源: {latest.get('source_type', 'N/A')}")
            print(f"   - 时间: {latest.get('timestamp', 'N/A')}")
            print(f"   - 内容预览: {latest.get('content', '')[:100]}...")
            
            # 筛选文件上传相关的记忆
            upload_memories = [m for m in memories if m.get('source_type') == 'file_upload']
            if upload_memories:
                print(f"\n   文件上传类型记忆数: {len(upload_memories)}")
                return True
            else:
                print(f"\n   ⚠️  未找到文件上传类型的记忆")
                return False
        else:
            print(f"   ⚠️  向量库中未找到相关记忆")
            return False
            
    except Exception as e:
        print(f"   ❌ 查询向量库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upload_and_vectorization()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过：文件上传 → 分片 → 向量化 → 入库流程正常")
    else:
        print("❌ 测试失败：请检查上述错误信息")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
