#!/usr/bin/env python3
# @self-expose: {"id": "test_auto_refresh", "name": "Test Auto Refresh", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Auto Refresh功能"]}}
"""
测试自动刷新功能
这个脚本模拟用户发送消息并检查前端是否能自动刷新
"""

import requests
import json
import time

def test_auto_refresh():
    """测试自动刷新功能"""
    base_url = "http://localhost:10808"
    
    print("=== 测试自动刷新功能 ===")
    
    # 1. 先获取当前聊天历史
    print("1. 获取当前聊天历史...")
    try:
        response = requests.get(f"{base_url}/api/chatroom/history")
        if response.status_code == 200:
            history = response.json()
            initial_count = history.get('count', 0)
            print(f"   初始消息数量: {initial_count}")
        else:
            print(f"   获取历史失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   获取历史异常: {e}")
        return
    
    # 2. 发送测试消息
    print("2. 发送测试消息...")
    test_message = "测试自动刷新功能，请回复我"
    try:
        response = requests.post(
            f"{base_url}/api/chatroom/message",
            json={"message": test_message, "session_id": "default_session"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   消息发送成功")
            print(f"   响应内容: {result.get('response', '无内容')[:100]}...")
        else:
            print(f"   发送消息失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   发送消息异常: {e}")
        return
    
    # 3. 等待后端处理（模拟用户等待）
    print("3. 等待后端处理（5秒）...")
    time.sleep(5)
    
    # 4. 再次获取聊天历史，检查是否有新消息
    print("4. 检查是否有新消息...")
    try:
        response = requests.get(f"{base_url}/api/chatroom/history")
        if response.status_code == 200:
            history = response.json()
            final_count = history.get('count', 0)
            print(f"   最终消息数量: {final_count}")
            
            if final_count > initial_count:
                print("✅ 测试通过：检测到新消息，自动刷新功能正常")
                print(f"   新增消息数量: {final_count - initial_count}")
                
                # 显示新增的消息内容
                if history.get('history'):
                    new_messages = history['history'][initial_count:]
                    for i, msg in enumerate(new_messages):
                        print(f"   新增消息 {i+1}: {msg.get('role', 'unknown')} - {msg.get('content', '无内容')[:50]}...")
            else:
                print("❌ 测试失败：未检测到新消息")
                print("   可能原因：")
                print("   - 后端处理时间较长")
                print("   - 消息未正确保存到历史")
                print("   - 前端轮询机制需要调整")
                
        else:
            print(f"   获取历史失败: {response.status_code}")
    except Exception as e:
        print(f"   检查消息异常: {e}")
    
    print("\n=== 测试完成 ===")
    print("说明：")
    print("1. 前端现在每3秒会检查一次聊天历史")
    print("2. 如果检测到新消息，会自动刷新页面内容")
    print("3. 用户不再需要手动刷新页面")

def test_frontend_api():
    """测试前端实际使用的API路径"""
    base_url = "http://localhost:10808"
    
    print("\n=== 测试前端API路径 ===")
    
    # 测试聊天历史API
    print("1. 测试聊天历史API...")
    try:
        response = requests.get(f"{base_url}/api/chatroom/history")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
        else:
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试发送消息API
    print("\n2. 测试发送消息API...")
    try:
        response = requests.post(
            f"{base_url}/api/chatroom/message",
            json={"message": "测试消息", "session_id": "default_session"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
        else:
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"   异常: {e}")

if __name__ == "__main__":
    test_frontend_api()
    test_auto_refresh()