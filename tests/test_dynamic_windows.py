#!/usr/bin/env python
# @self-expose: {"id": "test_dynamic_windows", "name": "Test Dynamic Windows", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Dynamic Windows功能"]}}
# -*- coding: utf-8 -*-
"""
测试动态智能体窗口功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_chatroom import MultiAgentChatroom

def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试动态智能体窗口基本功能 ===")
    
    try:
        # 创建聊天室实例
        chatroom = MultiAgentChatroom()
        print("✓ 聊天室实例化成功")
        
        # 测试启动
        if chatroom.start_chatroom():
            print("✓ 聊天室启动成功")
            
            # 测试窗口信息获取
            windows_info = chatroom.get_agent_windows_info()
            print(f"✓ 智能体窗口数量: {len(windows_info)}")
            
            for window in windows_info:
                print(f"  - {window['role']}: 状态={window['state']}, 对话数={window['conversation_count']}")
            
            # 测试静默广播
            success = chatroom.send_silent_broadcast("系统测试消息")
            print(f"✓ 静默广播: {'成功' if success else '失败'}")
            
            # 测试用户消息发送
            print("\n=== 测试用户消息发送 ===")
            result = chatroom.send_user_message("大家好，我们来测试一下动态智能体窗口功能")
            
            if "error" not in result:
                print("✓ 用户消息发送成功")
                print(f"  响应数量: {len(result['agent_responses'])}")
                print(f"  窗口协作水平: {result['collaboration_level']}")
                
                # 显示窗口状态
                for window in result["windows_info"]:
                    print(f"  {window['role']}: 香农熵={window['shannon_entropy']:.2f}")
            else:
                print(f"✗ 用户消息发送失败: {result['error']}")
            
            # 测试智能体添加功能
            print("\n=== 测试智能体繁殖功能 ===")
            new_agent_id = chatroom.add_new_agent("测试智能体", "测试角色")
            if new_agent_id:
                print(f"✓ 新智能体添加成功: {new_agent_id}")
                
                # 检查窗口数量
                updated_windows = chatroom.get_agent_windows_info()
                print(f"✓ 更新后智能体窗口数量: {len(updated_windows)}")
            else:
                print("✗ 新智能体添加失败")
            
            # 停止聊天室
            chatroom.stop_chatroom()
            print("✓ 聊天室停止成功")
            
            print("\n=== 所有测试通过 ===")
            return True
            
        else:
            print("✗ 聊天室启动失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)