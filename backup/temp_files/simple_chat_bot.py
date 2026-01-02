#!/usr/bin/env python
# @self-expose: {"id": "simple_chat_bot", "name": "Simple Chat Bot", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Simple Chat Bot功能"]}}
# -*- coding: utf-8 -*-
"""
简易聊天机器人启动脚本
开发提示词来源：用户要求启动真正的简易聊天机器人进行交互
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """启动简易聊天机器人"""
    print("=== 简易聊天机器人启动 ===")
    print("正在初始化聊天引擎...")
    
    try:
        # 导入聊天引擎
        from src.chat_engine import create_chat_engine
        
        # 创建聊天引擎实例
        engine = create_chat_engine()
        print("聊天引擎初始化成功！")
        print("输入 '退出' 或 'quit' 结束对话")
        print("-" * 50)
        
        # 开始对话循环
        while True:
            try:
                user_input = input("\n你: ").strip()
                
                if user_input.lower() in ['退出', 'quit', 'exit']:
                    print("对话结束，再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户输入
                print("机器人: 正在思考...")
                response = engine.chat(user_input)
                
                # 显示响应
                print(f"机器人: {response.get('response', '抱歉，我暂时无法回答这个问题。')}")
                
                # 显示使用的策略
                strategy = response.get('strategy', '未知')
                print(f"[策略: {strategy}]")
                
            except KeyboardInterrupt:
                print("\n\n对话被中断，再见！")
                break
            except Exception as e:
                print(f"\n机器人: 抱歉，处理时出现了错误: {e}")
                
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请检查依赖模块是否正确安装")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()