#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试单例模式修复 + 验证思维引擎是否真实工作
"""

import sys
import os
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mesh_thought_engine_singleton():
    """测试MeshThoughtEngine单例模式"""
    print("\n【测试1】MeshThoughtEngine单例模式")
    print("=" * 60)
    
    from src.mesh_thought_engine import MeshThoughtEngine
    
    # 创建第一个实例
    print("创建第一个实例...")
    engine1 = MeshThoughtEngine()
    print(f"实例1 ID: {id(engine1)}")
    print(f"实例1 节点数: {engine1.get_node_count()}")
    
    # 创建第二个实例
    print("\n创建第二个实例...")
    engine2 = MeshThoughtEngine()
    print(f"实例2 ID: {id(engine2)}")
    print(f"实例2 节点数: {engine2.get_node_count()}")
    
    # 验证是否为同一个实例
    if engine1 is engine2:
        print("\n✅ 单例模式生效：两个实例是同一个对象")
        print("✅ 不会重复加载持久化数据")
    else:
        print("\n❌ 单例模式失败：创建了不同的实例")
    
    return engine1 is engine2

def test_mesh_database_interface_singleton():
    """测试MeshDatabaseInterface单例模式"""
    print("\n【测试2】MeshDatabaseInterface单例模式")
    print("=" * 60)
    
    from src.mesh_database_interface import MeshDatabaseInterface
    
    # 创建第一个实例
    print("创建第一个实例...")
    interface1 = MeshDatabaseInterface()
    print(f"实例1 ID: {id(interface1)}")
    print(f"实例1.thought_engine ID: {id(interface1.thought_engine)}")
    
    # 创建第二个实例
    print("\n创建第二个实例...")
    interface2 = MeshDatabaseInterface()
    print(f"实例2 ID: {id(interface2)}")
    print(f"实例2.thought_engine ID: {id(interface2.thought_engine)}")
    
    # 验证是否为同一个实例
    if interface1 is interface2:
        print("\n✅ 单例模式生效：两个实例是同一个对象")
        print("✅ 不会重复初始化MeshThoughtEngine")
    else:
        print("\n❌ 单例模式失败：创建了不同的实例")
    
    return interface1 is interface2

def test_thought_storage_and_persistence():
    """测试思维节点存储和持久化"""
    print("\n【测试3】思维节点存储和持久化")
    print("=" * 60)
    
    from src.mesh_thought_engine import MeshThoughtEngine
    
    # 获取引擎实例
    engine = MeshThoughtEngine()
    initial_count = engine.get_node_count()
    print(f"初始节点数: {initial_count}")
    
    # 检查持久化文件信息
    storage_path = engine.storage_path
    print(f"\n持久化文件: {storage_path}")
    
    if os.path.exists(storage_path):
        file_time = os.path.getmtime(storage_path)
        file_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_time))
        print(f"文件最后修改时间: {file_time_str}")
        
        # 读取文件内容
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            print(f"文件中记录的节点数: {metadata.get('node_count', 0)}")
            print(f"保存时间戳: {metadata.get('saved_at', 'N/A')}")
            
            if metadata.get('saved_at'):
                saved_time_str = time.strftime('%Y-%m-%d %H:%M:%S', 
                                              time.localtime(metadata['saved_at']))
                print(f"保存日期: {saved_time_str}")
    
    # 尝试添加一个新思维节点
    print("\n尝试添加新思维节点...")
    test_content = f"测试思维节点 - {time.time()}"
    new_node = engine.store_thought(test_content, {
        'test': True,
        'timestamp': time.time()
    })
    print(f"返回节点ID: {new_node.id}")
    
    # 检查节点数是否增加
    new_count = engine.get_node_count()
    print(f"添加后节点数: {new_count}")
    
    if new_count > initial_count:
        print(f"\n✅ 成功添加新节点，节点数从 {initial_count} 增加到 {new_count}")
        print("⚠️  但是注意：服务器启动时总是显示111个节点")
        print("⚠️  可能是因为：")
        print("   1. 单例模式导致内存中的状态不同步到文件")
        print("   2. 服务器重启时重新从文件加载，但文件没有更新")
        print("   3. 查重机制太严格，新内容被识别为重复")
    elif new_count == initial_count:
        print(f"\n⚠️  节点数未增加，仍为 {initial_count}")
        print("可能原因：")
        print("  1. 查重机制认为是重复内容，复用了现有节点")
        print("  2. store_thought返回的是现有节点而非新节点")
    
    return new_count != initial_count

def test_persistence_file_update():
    """测试持久化文件是否真的更新"""
    print("\n【测试4】持久化文件更新验证")
    print("=" * 60)
    
    from src.mesh_thought_engine import MeshThoughtEngine
    
    engine = MeshThoughtEngine()
    storage_path = engine.storage_path
    
    # 记录修改前的时间戳
    if os.path.exists(storage_path):
        before_mtime = os.path.getmtime(storage_path)
        print(f"修改前文件时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(before_mtime))}")
    
    # 添加一个独特的思维节点
    unique_content = f"独特测试内容_{int(time.time() * 1000000)}"
    print(f"\n添加独特内容: {unique_content[:50]}...")
    
    before_count = engine.get_node_count()
    node = engine.store_thought(unique_content)
    after_count = engine.get_node_count()
    
    print(f"添加前节点数: {before_count}")
    print(f"添加后节点数: {after_count}")
    
    # 等待一下确保文件系统更新
    time.sleep(0.1)
    
    # 检查文件是否被修改
    if os.path.exists(storage_path):
        after_mtime = os.path.getmtime(storage_path)
        print(f"\n修改后文件时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(after_mtime))}")
        
        if after_mtime > before_mtime:
            print("✅ 文件已更新")
        else:
            print("❌ 文件未更新！")
            print("⚠️  说明：store_thought可能没有调用_save_to_storage")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("单例模式修复验证 + 思维引擎工作状态检查")
    print("=" * 60)
    
    test1_pass = test_mesh_thought_engine_singleton()
    test2_pass = test_mesh_database_interface_singleton()
    test3_pass = test_thought_storage_and_persistence()
    test_persistence_file_update()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    print("\n单例模式修复:")
    if test1_pass and test2_pass:
        print("✅ 单例模式正常工作，不会重复加载")
    else:
        print("❌ 单例模式存在问题")
    
    print("\n思维引擎工作状态:")
    if test3_pass:
        print("✅ 思维引擎可以正常添加新节点")
    else:
        print("⚠️  思维引擎可能存在问题：")
        print("   - 数据总是111个节点，从未增长")
        print("   - 可能是查重机制过于严格")
        print("   - 或者持久化机制没有正常工作")

if __name__ == "__main__":
    main()
