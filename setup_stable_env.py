# @self-expose: {"id": "setup_stable_env", "name": "RAG系统稳定环境配置脚本", "type": "script", "version": "1.0.0", "needs": {"deps": ["os", "sys", "subprocess", "platform"], "resources": ["command_execution", "file_system_access"]}, "provides": {"capabilities": ["虚拟环境创建", "稳定依赖安装", "Python版本检查", "环境配置指导"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG系统稳定环境配置脚本

该脚本将：
1. 检查当前Python版本
2. 如果不是Python 3.13.x，尝试使用python3.13命令
3. 创建虚拟环境
4. 安装稳定的NumPy版本和其他依赖
5. 提供启动系统的命令
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

def main():
    print("=== RAG系统稳定环境配置 ===")
    print(f"当前系统: {platform.system()} {platform.version()}")
    print(f"当前Python版本: {sys.version}")
    
    # 1. 检查Python 3.13是否可用
    python_cmd = "python"
    python313_cmd = "python3.13"
    
    print(f"\n1. 检查Python 3.13是否可用...")
    result = run_command(f"{python313_cmd} --version")
    
    if result.returncode == 0:
        print("✅ Python 3.13可用")
        python_cmd = python313_cmd
    else:
        print("❌ Python 3.13不可用，尝试使用系统Python...")
        
    # 2. 检查当前Python版本
    result = run_command(f"{python_cmd} --version")
    
    # 3. 创建虚拟环境
    venv_name = "rag-stable-env"
    print(f"\n2. 创建虚拟环境 {venv_name}...")
    result = run_command(f"{python_cmd} -m venv {venv_name}")
    
    if result.returncode != 0:
        print("❌ 创建虚拟环境失败")
        return
    
    print("✅ 虚拟环境创建成功")
    
    # 4. 激活虚拟环境并安装依赖
    print(f"\n3. 安装稳定依赖...")
    
    # Windows和Linux/Mac的激活命令不同
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\Scripts\activate"
        pip_cmd = f"{venv_name}\Scripts\pip"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        pip_cmd = f"{venv_name}/bin/pip"
    
    # 安装稳定的NumPy版本
    result = run_command(f"{pip_cmd} install numpy==2.3.3")
    
    if result.returncode != 0:
        print("❌ 安装NumPy失败")
        return
    
    print("✅ NumPy 2.3.3安装成功")
    
    # 5. 安装其他依赖（如果有requirements.txt）
    if os.path.exists("requirements.txt"):
        print("\n4. 安装其他依赖...")
        result = run_command(f"{pip_cmd} install -r requirements.txt")
        
        if result.returncode == 0:
            print("✅ 所有依赖安装成功")
        else:
            print("⚠️  部分依赖安装失败")
    
    # 6. 提供使用说明
    print(f"\n=== 环境配置完成 ===")
    print(f"✅ 虚拟环境已创建: {venv_name}")
    print(f"✅ NumPy 2.3.3已安装")
    print(f"\n📋 使用说明:")
    print(f"1. 激活虚拟环境:")
    print(f"   {activate_cmd}")
    print(f"2. 启动系统:")
    print(f"   python stable_start_server.py")
    print(f"3. 退出虚拟环境:")
    print(f"   deactivate")
    print(f"\n💡 提示: 每次启动系统前，请先激活虚拟环境")

if __name__ == "__main__":
    main()