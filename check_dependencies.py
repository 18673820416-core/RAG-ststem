#!/usr/bin/env python3
# @self-expose: {"id": "check_dependencies", "name": "Check Dependencies", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Dependencies功能"]}}
# -*- coding: utf-8 -*-
"""
RAG系统依赖版本检测脚本

该脚本将：
1. 检测Python版本
2. 检测NumPy版本
3. 检测其他关键依赖的版本
4. 提供详细的报告
5. 给出修复建议
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result

def check_python_version():
    """检测Python版本"""
    print("=== 检测Python版本 ===")
    print(f"当前Python版本: {sys.version}")
    print(f"Python解释器路径: {sys.executable}")
    
    # 检查是否为3.13.x版本
    is_stable = sys.version_info[:2] == (3, 13)
    print(f"是否为稳定版本: {'✅ 是' if is_stable else '❌ 否'}")
    
    return {
        "version": sys.version,
        "executable": sys.executable,
        "is_stable": is_stable,
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro
    }

def check_numpy_version():
    """检测NumPy版本"""
    print("\n=== 检测NumPy版本 ===")
    
    try:
        import numpy
        version = numpy.__version__
        print(f"当前NumPy版本: {version}")
        
        # 检查是否为2.3.3版本
        is_stable = version == "2.3.3"
        print(f"是否为稳定版本: {'✅ 是' if is_stable else '❌ 否'}")
        
        # 检查是否为实验性构建
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import numpy
            has_warnings = len(w) > 0
            print(f"是否有警告: {'❌ 是' if has_warnings else '✅ 否'}")
            if has_warnings:
                for warning in w:
                    print(f"  警告: {warning.message}")
        
        return {
            "version": version,
            "is_stable": is_stable,
            "has_warnings": has_warnings,
            "warnings": [str(warning.message) for warning in w] if has_warnings else []
        }
    except ImportError as e:
        print(f"❌ 无法导入NumPy: {e}")
        return {
            "version": None,
            "is_stable": False,
            "has_warnings": False,
            "warnings": []
        }

def check_other_dependencies():
    """检测其他关键依赖"""
    print("\n=== 检测其他关键依赖 ===")
    
    dependencies = [
        "requests",
        "transformers",
        "torch",
        "faiss-cpu",
        "sentence-transformers"
    ]
    
    results = []
    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, "__version__", "未知版本")
            print(f"✅ {dep}: {version}")
            results.append({
                "name": dep,
                "version": version,
                "is_installed": True
            })
        except ImportError:
            print(f"❌ {dep}: 未安装")
            results.append({
                "name": dep,
                "version": None,
                "is_installed": False
            })
    
    return results

def check_pip_version():
    """检测pip版本"""
    print("\n=== 检测pip版本 ===")
    
    result = run_command("pip --version")
    if result.returncode == 0:
        print(f"✅ pip: {result.stdout.strip()}")
        return {
            "version": result.stdout.strip(),
            "is_installed": True
        }
    else:
        # 尝试使用python -m pip
        result = run_command("python -m pip --version")
        if result.returncode == 0:
            print(f"✅ python -m pip: {result.stdout.strip()}")
            return {
                "version": result.stdout.strip(),
                "is_installed": True,
                "using_python_m_pip": True
            }
        else:
            print(f"❌ pip: 未安装")
            return {
                "version": None,
                "is_installed": False
            }

def main():
    print("=== RAG系统依赖版本检测报告 ===")
    print(f"检测时间: {platform.system()} {platform.version()}")
    print(f"检测路径: {os.getcwd()}")
    
    # 检测各依赖
    python_info = check_python_version()
    numpy_info = check_numpy_version()
    pip_info = check_pip_version()
    other_deps = check_other_dependencies()
    
    # 生成修复建议
    print("\n=== 修复建议 ===")
    
    # Python版本建议
    if not python_info["is_stable"]:
        print(f"1. Python版本建议: 建议使用Python 3.13.x版本，当前版本: {python_info['version'].split()[0]}")
        print(f"   下载地址: https://www.python.org/downloads/release/python-3137/")
    else:
        print("1. Python版本: ✅ 已使用稳定版本")
    
    # NumPy版本建议
    if not numpy_info["is_stable"] or numpy_info["has_warnings"]:
        print(f"2. NumPy版本建议: 建议使用NumPy 2.3.3稳定版本，当前版本: {numpy_info['version']}")
        print("   修复命令:")
        print("   pip uninstall -y numpy")
        print("   pip install numpy==2.3.3")
        if numpy_info["has_warnings"]:
            print(f"   当前警告: {'; '.join(numpy_info['warnings'])}")
    else:
        print("2. NumPy版本: ✅ 已使用稳定版本")
    
    # 其他依赖建议
    missing_deps = [dep for dep in other_deps if not dep["is_installed"]]
    if missing_deps:
        print(f"3. 缺失依赖: {', '.join([dep['name'] for dep in missing_deps])}")
        print("   安装命令:")
        print(f"   pip install {' '.join([dep['name'] for dep in missing_deps])}")
    else:
        print("3. 其他依赖: ✅ 所有关键依赖已安装")
    
    # 启动系统建议
    print("\n=== 启动系统建议 ===")
    if python_info["is_stable"] and numpy_info["is_stable"] and not numpy_info["has_warnings"]:
        print("✅ 系统已准备就绪，可以启动")
        print("   启动命令: python stable_start_server.py")
    else:
        print("❌ 系统环境尚未稳定，建议先修复依赖问题")
    
    print("\n=== 检测完成 ===")

if __name__ == "__main__":
    main()