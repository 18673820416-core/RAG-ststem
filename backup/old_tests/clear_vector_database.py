#!/usr/bin/env python3
# @self-expose: {"id": "clear_vector_database", "name": "Clear Vector Database", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Clear Vector Database功能"]}}
# -*- coding: utf-8 -*-
"""
清空向量数据库脚本
用于清空RAG系统中的向量数据库，避免不必要的聊天记录引起误会
"""

import os
import sqlite3
from datetime import datetime

def clear_vector_database():
    """清空向量数据库"""
    
    db_path = "E:\\RAG系统\\data\\rag_memory.db"
    
    if not os.path.exists(db_path):
        print("错误：数据库文件不存在")
        return False
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取数据库中的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 清空所有表的数据
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # 跳过sqlite_sequence表
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"已清空表: {table_name}")
        
        # 重置sqlite_sequence表（用于自增ID重置）
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        # 提交更改
        conn.commit()
        
        # 验证数据库是否已清空
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"表 {table_name} 剩余记录数: {count}")
        
        print("\n✅ 向量数据库已成功清空！")
        print("所有与LLM的聊天记录已被删除")
        print("数据库现在是一个干净的状态")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 清空数据库时出错: {str(e)}")
        return False

def main():
    """主函数"""
    
    print("=" * 60)
    print("           向量数据库清空工具")
    print("=" * 60)
    print("\n⚠️  警告：此操作将永久删除所有向量数据")
    print("包括所有与LLM的聊天记录和记忆数据")
    print("\n操作目的：")
    print("- 避免不必要的聊天记录引起误会")
    print("- 清理过时的记忆数据")
    print("- 为新的项目准备干净的数据库")
    print("=" * 60)
    
    # 确认操作
    confirm = input("\n确认要清空向量数据库吗？(输入 'yes' 确认): ")
    
    if confirm.lower() == 'yes':
        print("\n开始清空数据库...")
        success = clear_vector_database()
        
        if success:
            print("\n🎉 操作完成！")
            print("现在可以专注于新的微信聊天记录提取项目了")
        else:
            print("\n❌ 操作失败，请检查错误信息")
    else:
        print("\n操作已取消")

if __name__ == "__main__":
    main()