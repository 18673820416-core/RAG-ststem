#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试动态智能体窗口功能
"""

# @self-expose: {"id": "simple_test", "name": "Simple Test", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Test功能"]}}

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入功能"""
    print("=== 测试导入功能 ===")
    
    try:
        from multi_agent_chatroom import MultiAgentChatroom
        print("✓ MultiAgentChatroom 导入成功")
        
        from agent_conversation_window import AgentConversationWindow
        print("✓ AgentConversationWindow 导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_chatroom_creation():
    """测试聊天室创建"""
    print("\n=== 测试聊天室创建 ===")
    
    try:
        from multi_agent_chatroom import MultiAgentChatroom
        
        chatroom = MultiAgentChatroom()
        print("✓ 聊天室实例化成功")
        
        # 测试启动
        if chatroom.start_chatroom():
            print("✓ 聊天室启动成功")
            
            # 测试窗口信息获取
            windows_info = chatroom.get_agent_windows_info()
            print(f"✓ 智能体窗口数量: {len(windows_info)}")
            
            # 显示窗口信息
            for window in windows_info:
                print(f"  - {window['role']}: 状态={window['state']}")
            
            # 测试静默广播
            success = chatroom.send_silent_broadcast("测试消息")
            print(f"✓ 静默广播: {'成功' if success else '失败'}")
            
            # 停止聊天室
            chatroom.stop_chatroom()
            print("✓ 聊天室停止成功")
            
            return True
        else:
            print("✗ 聊天室启动失败")
            return False
            
    except Exception as e:
        print(f"✗ 聊天室创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试动态智能体窗口重构功能...")
    
    # 测试导入
    if not test_imports():
        print("\n✗ 导入测试失败")
        return False
    
    # 测试聊天室创建
    if not test_chatroom_creation():
        print("\n✗ 聊天室创建测试失败")
        return False
    
    print("\n=== 所有测试通过 ===")
    print("动态智能体窗口重构功能验证成功！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)