# @self-expose: {"id": "fix_python_env", "name": "Python环境变量修复脚本", "type": "script", "version": "1.0.0", "needs": {"deps": ["os", "sys", "winreg"], "resources": ["registry_access"]}, "provides": {"capabilities": ["Python环境变量修复", "路径清理", "正确Python路径添加"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python环境变量修复脚本
修复错误的环境变量：C:\Users\liang\AppData\Local\Programs\Python\Python313\%USERPROFILE%\AppData\Local\Microsoft\WindowsApps
"""

import os
import sys
import winreg

def get_user_path():
    """获取用户的Path环境变量"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
        path_value, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)
        return path_value
    except Exception as e:
        print(f"获取环境变量失败: {e}")
        return ""

def set_user_path(new_path):
    """设置用户的Path环境变量"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        print("✅ 环境变量已更新！")
        print("请重新打开命令提示符或PowerShell窗口以生效")
        return True
    except Exception as e:
        print(f"设置环境变量失败: {e}")
        return False

def main():
    print("=== Python环境变量修复脚本 ===")
    
    # 获取当前Path环境变量
    current_path = get_user_path()
    print(f"当前Path环境变量: {current_path}")
    
    # 分割路径
    paths = current_path.split(';')
    print(f"\n当前路径数量: {len(paths)}")
    
    # 显示所有Python相关路径
    print("\n当前Python相关路径:")
    for path in paths:
        if path and ('Python' in path or 'python' in path):
            print(f"  - {path}")
    
    # 修复错误路径
    print("\n=== 开始修复错误路径 ===")
    
    # 定义正确的Python路径
    correct_python_paths = [
        "C:/Users/liang/AppData/Local/Programs/Python/Python313/Scripts",
        "C:/Users/liang/AppData/Local/Programs/Python/Python313"
    ]
    
    # 移除错误路径和重复路径
    new_paths = []
    for path in paths:
        if not path:
            continue
        
        # 跳过包含错误格式的路径
        if "%USERPROFILE%" in path and "Python313" in path:
            print(f"  - 移除错误路径: {path}")
            continue
        
        # 跳过重复的正确路径
        if path in correct_python_paths and path in new_paths:
            print(f"  - 跳过重复路径: {path}")
            continue
        
        new_paths.append(path)
    
    # 添加缺失的正确路径
    for correct_path in correct_python_paths:
        if correct_path not in new_paths:
            new_paths.append(correct_path)
            print(f"  - 添加正确路径: {correct_path}")
    
    # 合并新路径
    new_path = ';'.join(new_paths)
    
    # 显示修复后的路径
    print("\n修复后的Python相关路径:")
    for path in new_path.split(';'):
        if path and ('Python' in path or 'python' in path):
            print(f"  - {path}")
    
    # 确认修复
    print(f"\n修复后的完整Path: {new_path}")
    
    # 更新环境变量
    if set_user_path(new_path):
        print("\n=== 修复完成 ===")
        print("请重新打开命令提示符或PowerShell窗口，然后运行 python --version 验证修复结果")
    else:
        print("\n=== 修复失败 ===")

if __name__ == "__main__":
    main()
