#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动前依赖检查脚本
检查所有必要的依赖是否已正确安装
"""

import sys
import os

def check_dependencies():
    """检查所有必要的依赖"""
    print("=" * 50)
    print("检查系统依赖...")
    print("=" * 50)
    print()
    
    all_ok = True
    
    # 检查核心依赖
    dependencies = [
        ('numpy', 'NumPy'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
        ('psutil', 'psutil'),
        ('skimage', 'scikit-image'),
        ('flask', 'Flask'),
        ('requests', 'Requests'),
        ('sklearn', 'scikit-learn'),
    ]
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {display_name:20s} - 已安装")
        except ImportError:
            print(f"✗ {display_name:20s} - 未安装")
            all_ok = False
    
    print()
    
    # 检查OpenCV数据文件
    try:
        import cv2
        cascade_file = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        if os.path.exists(cascade_file):
            print(f"✓ OpenCV人脸检测模型 - 已找到")
            print(f"  路径: {cascade_file}")
        else:
            print(f"✗ OpenCV人脸检测模型 - 未找到")
            print(f"  预期路径: {cascade_file}")
            all_ok = False
    except Exception as e:
        print(f"✗ OpenCV检查失败: {e}")
        all_ok = False
    
    print()
    print("=" * 50)
    
    if all_ok:
        print("✓ 所有依赖检查通过！")
        print("=" * 50)
        return 0
    else:
        print("✗ 部分依赖缺失，请运行 install_missing_deps.bat")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(check_dependencies())
