#!/usr/bin/env python
# @self-expose: {"id": "test_vision_engine", "name": "Test Vision Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Vision Engine功能"]}}
# -*- coding: utf-8 -*-
"""
测试视觉处理引擎
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.vision_processing_engine import VisionProcessingEngine

# 创建视觉处理引擎实例
print("=== 测试视觉处理引擎 ===")
vision_engine = VisionProcessingEngine()

# 测试图像加载和分析功能
print("\n1. 测试基本功能...")
print(f"视觉引擎初始化状态: {'成功' if vision_engine.models_loaded else '失败'}")
print(f"人脸检测可用: {'是' if vision_engine.face_detection_available else '否'}")

# 测试特征提取功能
print("\n2. 测试特征提取...")
# 创建一个简单的测试图像
import numpy as np
import cv2

# 创建一个300x300的彩色图像
test_image = np.zeros((300, 300, 3), dtype=np.uint8)
# 在图像中心绘制一个红色矩形
cv2.rectangle(test_image, (100, 100), (200, 200), (0, 0, 255), -1)
# 在图像左上角绘制一个绿色圆形
cv2.circle(test_image, (50, 50), 30, (0, 255, 0), -1)

# 提取特征
features = vision_engine.extract_features(test_image)
print(f"特征提取成功: {len(features) > 0}")
if features:
    print(f"亮度: {features.get('brightness'):.2f}")
    print(f"对比度: {features.get('contrast'):.2f}")
    print(f"锐度: {features.get('sharpness'):.2f}")
    print(f"边缘数量: {features.get('edges', {}).get('edge_count', 0)}")

# 测试对象检测功能
print("\n3. 测试对象检测...")
objects = vision_engine.detect_objects(test_image)
print(f"对象检测成功: {len(objects) > 0}")
if objects:
    print(f"检测到对象数量: {len(objects)}")
    for obj in objects:
        print(f"  - {obj['type']}: 置信度 {obj['confidence']:.2f}, 位置 {obj['bbox']}")

# 测试综合分析功能
print("\n4. 测试综合分析...")
result = vision_engine.analyze_image(image_path=None, base64_data=None)
print(f"综合分析API: {'可用' if not result.success else '返回结果'}")

print("\n=== 测试完成 ===")
