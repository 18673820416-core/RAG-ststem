#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试服务器实例注册表机制
"""

import requests
import json
import os

# 静态服务器地址
STATIC_SERVER = "http://localhost:10808"

def test_query_occupied_ports():
    """测试查询占用端口"""
    print("\n=== 测试1：查询当前占用的端口 ===")
    try:
        response = requests.post(
            f"{STATIC_SERVER}/api/server/occupied-ports",
            json={},
            timeout=5
        )
        result = response.json()
        print(f"✅ 查询成功:")
        print(f"  占用端口: {result.get('occupied_ports', [])}")
        print(f"  推荐空闲端口: {result.get('available_port')}")
        print(f"  所有实例: {json.dumps(result.get('all_instances', {}), ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return None

def test_register_server(port=5001, pid=12345):
    """测试注册服务器实例"""
    print(f"\n=== 测试2：注册服务器实例 (Port={port}, PID={pid}) ===")
    try:
        response = requests.post(
            f"{STATIC_SERVER}/api/server/register",
            json={"port": port, "pid": pid},
            timeout=5
        )
        result = response.json()
        if result.get("success"):
            print(f"✅ {result.get('message')}")
        else:
            print(f"❌ 注册失败: {result.get('error')}")
        return result
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        return None

def test_unregister_server(port=5001):
    """测试注销服务器实例"""
    print(f"\n=== 测试3：注销服务器实例 (Port={port}) ===")
    try:
        response = requests.post(
            f"{STATIC_SERVER}/api/server/unregister",
            json={"port": port},
            timeout=5
        )
        result = response.json()
        if result.get("success"):
            print(f"✅ {result.get('message')}")
        else:
            print(f"❌ 注销失败: {result.get('error')}")
        return result
    except Exception as e:
        print(f"❌ 注销失败: {e}")
        return None

def test_multi_instance_simulation():
    """模拟多实例启动场景"""
    print("\n=== 测试4：模拟多实例启动（智能端口分配） ===")
    
    # 模拟3个实例依次启动
    instances = []
    for i in range(3):
        # 查询可用端口
        query_result = test_query_occupied_ports()
        if query_result and query_result.get("available_port"):
            port = query_result["available_port"]
            pid = 10000 + i
            
            # 注册实例
            register_result = test_register_server(port, pid)
            if register_result and register_result.get("success"):
                instances.append({"port": port, "pid": pid})
                print(f"  ✅ 实例{i+1}成功启动: Port={port}, PID={pid}")
        else:
            print(f"  ❌ 无法获取可用端口，停止模拟")
            break
    
    # 显示当前所有运行中的实例
    print("\n当前运行中的实例:")
    final_status = test_query_occupied_ports()
    
    # 清理：注销所有模拟实例
    print("\n清理模拟实例:")
    for instance in instances:
        test_unregister_server(instance["port"])

if __name__ == "__main__":
    print("=" * 60)
    print("服务器实例注册表机制测试")
    print("=" * 60)
    print("\n⚠️  请确保静态服务器已在 10808 端口运行")
    print("   启动命令: python stable_start_server.py")
    print("=" * 60)
    
    try:
        # 基础功能测试
        test_query_occupied_ports()
        test_register_server(5001, 12345)
        test_query_occupied_ports()
        test_unregister_server(5001)
        test_query_occupied_ports()
        
        # 多实例模拟
        test_multi_instance_simulation()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n测试中断")
