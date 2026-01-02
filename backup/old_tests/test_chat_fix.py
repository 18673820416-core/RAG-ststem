#!/usr/bin/env python3
# @self-expose: {"id": "test_chat_fix", "name": "Test Chat Fix", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Chat Fix功能"]}}
# -*- coding: utf-8 -*-
"""
测试修复后的聊天功能
"""

import requests
import json

def test_chat_function():
    """测试聊天功能"""
    url = "http://localhost:10808/api/chatroom/message"
    
    # 测试消息
    test_messages = [
        "你好，你是谁？",
        "你知道AGI是什么吗？",
        "介绍一下你的功能",
        "测试一下对话功能"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n=== 测试 {i}: {message} ===")
        
        try:
            # 发送请求
            response = requests.post(
                url,
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("响应数据:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                # 检查关键字段
                if "response" in data:
                    print(f"✅ 成功获取回复: {data['response'][:100]}...")
                elif "agent_responses" in data and data["agent_responses"]:
                    print(f"✅ 成功获取智能体回复: {data['agent_responses'][0]['content'][:100]}...")
                else:
                    print("❌ 响应格式异常")
                    
            else:
                print(f"❌ 请求失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试修复后的聊天功能...")
    test_chat_function()
    print("\n🎯 测试完成！")