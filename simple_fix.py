# @self-expose: {"id": "simple_fix", "name": "Python环境变量简单修复脚本", "type": "script", "version": "1.0.0", "needs": {"deps": ["os", "sys", "winreg"], "resources": ["registry_access"]}, "provides": {"capabilities": ["Python环境变量修复", "错误路径移除"]}}
import os
import sys
import winreg

# 简单的Python环境变量修复脚本
print("=== Python环境变量修复脚本 ===")

try:
    # 打开注册表
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    
    # 获取当前Path值
    current_path, _ = winreg.QueryValueEx(key, "Path")
    print(f"当前Path: {current_path}")
    
    # 分割路径
    paths = current_path.split(';')
    
    # 定义要移除的错误路径
    error_path = "C:\\Users\\liang\\AppData\\Local\\Programs\\Python\\Python313\\%USERPROFILE%\\AppData\\Local\\Microsoft\\WindowsApps"
    
    # 移除错误路径
    new_paths = []
    for path in paths:
        if path != error_path and path:
            new_paths.append(path)
    
    # 添加正确的Python路径（如果缺失）
    correct_paths = [
        "C:\\Users\\liang\\AppData\\Local\\Programs\\Python\\Python313\\Scripts",
        "C:\\Users\\liang\\AppData\\Local\\Programs\\Python\\Python313"
    ]
    
    for correct_path in correct_paths:
        if correct_path not in new_paths:
            new_paths.append(correct_path)
    
    # 合并新路径
    new_path = ';'.join(new_paths)
    
    # 更新注册表
    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
    winreg.CloseKey(key)
    
    print("✅ 环境变量修复完成！")
    print("修复后的Path: {}".format(new_path))
    print("请重新打开命令提示符或PowerShell窗口以生效")
    
except Exception as e:
    print(f"❌ 修复失败: {e}")
    sys.exit(1)
