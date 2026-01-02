# @self-expose: {"id": "reset_python_path", "name": "Python环境变量重置脚本", "type": "script", "version": "1.0.0", "needs": {"deps": ["os", "sys", "winreg"], "resources": ["registry_access"]}, "provides": {"capabilities": ["Python环境变量重置", "路径清理", "正确Python路径添加"]}}
import os
import sys
import winreg

# 重置Python环境变量脚本
print("=== 重置Python环境变量脚本 ===")

try:
    # 打开注册表
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
    
    # 获取当前Path值
    current_path, _ = winreg.QueryValueEx(key, "Path")
    print(f"当前Path: {current_path}")
    
    # 分割路径
    paths = current_path.split(';')
    
    # 移除所有Python相关路径
    non_python_paths = []
    for path in paths:
        if path and 'Python' not in path and 'python' not in path:
            non_python_paths.append(path)
    
    print(f"\n非Python路径: {non_python_paths}")
    
    # 定义正确的Python路径
    correct_python_paths = [
        "C:\\Users\\liang\\AppData\\Local\\Programs\\Python\\Python313\\Scripts",
        "C:\\Users\\liang\\AppData\\Local\\Programs\\Python\\Python313"
    ]
    
    # 合并新路径：非Python路径 + 正确的Python路径
    new_path = ';'.join(non_python_paths + correct_python_paths)
    
    # 更新注册表
    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
    winreg.CloseKey(key)
    
    print("✅ 环境变量重置完成！")
    print("重置后的Path: {}".format(new_path))
    print("请重新打开命令提示符或PowerShell窗口以生效")
    
    # 验证修复结果
    print("\n=== 验证重置结果 ===")
    # 重新读取注册表以验证
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
    verified_path, _ = winreg.QueryValueEx(key, "Path")
    winreg.CloseKey(key)
    
    print(f"注册表中存储的Path: {verified_path}")
    
    # 检查Python路径是否正确
    verified_paths = verified_path.split(';')
    print("\nPython相关路径验证:")
    for path in verified_paths:
        if path and 'Python' in path:
            print(f"  ✅ {path}")
    
except Exception as e:
    print(f"❌ 重置失败: {e}")
    sys.exit(1)
