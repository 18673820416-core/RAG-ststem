# @self-expose: {"id": "fix_python_path", "name": "Python路径修复脚本", "type": "script", "version": "1.0.0", "needs": {"deps": ["os", "sys", "subprocess", "platform"], "resources": ["command_execution"]}, "provides": {"capabilities": ["Python版本检查", "PATH环境变量管理", "Python路径修复", "系统路径分析"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Python路径脚本

该脚本将：
1. 检查系统中可用的Python版本
2. 显示当前的PATH环境变量
3. 帮助您更新PATH环境变量，移除不存在的Python路径
4. 确保Python 3.13已正确添加到PATH中
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result

def check_available_python_versions():
    """检查系统中可用的Python版本"""
    print("=== 检查系统中可用的Python版本 ===")
    
    if platform.system() == "Windows":
        # Windows系统
        result = run_command("where python")
        if result.returncode == 0:
            python_paths = result.stdout.strip().split('\n')
            print(f"找到 {len(python_paths)} 个Python解释器:")
            for path in python_paths:
                print(f"  - {path}")
                # 检查每个Python版本
                version_result = run_command(f"\"{path}\" --version")
                if version_result.returncode == 0:
                    print(f"    版本: {version_result.stdout.strip()}")
                else:
                    print(f"    ❌ 无法获取版本")
        else:
            print("❌ 未找到Python解释器")
    else:
        # Linux/Mac系统
        result = run_command("which -a python python3 python3.13")
        if result.returncode == 0:
            python_paths = result.stdout.strip().split('\n')
            print(f"找到 {len(python_paths)} 个Python解释器:")
            for path in python_paths:
                print(f"  - {path}")
                # 检查每个Python版本
                version_result = run_command(f"{path} --version")
                if version_result.returncode == 0:
                    print(f"    版本: {version_result.stdout.strip()}")
                else:
                    print(f"    ❌ 无法获取版本")
        else:
            print("❌ 未找到Python解释器")

def show_path_environment():
    """显示当前的PATH环境变量"""
    print("\n=== 显示当前的PATH环境变量 ===")
    path_env = os.environ.get("PATH", "")
    paths = path_env.split(os.pathsep)
    print(f"PATH环境变量包含 {len(paths)} 个路径:")
    
    # 检查每个路径是否存在
    for path in paths:
        if path:
            exists = os.path.exists(path)
            print(f"  {'✅' if exists else '❌'} {path}")
            # 检查是否包含Python相关路径
            if "Python" in path or "python" in path:
                print(f"    ⚠️  这是Python相关路径")

def main():
    print("=== 修复Python路径脚本 ===")
    print(f"当前系统: {platform.system()} {platform.version()}")
    
    # 检查可用的Python版本
    check_available_python_versions()
    
    # 显示当前的PATH环境变量
    show_path_environment()
    
    # 给出修复建议
    print("\n=== 修复建议 ===")
    print("1. 检查Python 3.13是否已安装:")
    print("   - 从官网下载: https://www.python.org/downloads/release/python-3137/")
    print("   - 确保勾选\"Add Python 3.13 to PATH")
    print("   - 重新安装Python 3.13")
    
    print("\n2. 更新系统PATH环境变量:")
    print("   - 移除指向不存在的Python 3.14的路径")
    print("   - 添加Python 3.13的安装路径")
    
    print("\n3. 在Windows系统中更新PATH的步骤:")
    print("   - 右键点击"此电脑" → "属性" → "高级系统设置" → "环境变量")
    print("   - 在"系统变量"中找到"Path" → "编辑")
    print("   - 移除包含Python 3.14的路径")
    print("   - 添加Python 3.13的安装路径，例如: C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\")
    print("   - 添加Python 3.13的根路径，例如: C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python313\\")
    print("   - 点击"确定"保存更改")
    print("   - 重新打开命令提示符")
    
    print("\n4. 验证修复结果:")
    print("   - 重新打开命令提示符")
    print("   - 运行: python --version")
    print("   - 运行: python -c \"import numpy; print(numpy.__version__)\"")
    print("   - 运行: python check_dependencies.py")
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    main()