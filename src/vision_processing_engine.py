#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视觉处理引擎
实现智能体系统的视觉模态处理能力
支持图像识别、特征提取、目标检测等视觉分析功能

注意：人脸识别功能已禁用，以避免OpenCV启动时的FileStorage警告。
如需启用人脸识别，请修改 _initialize_models() 方法。
"""

# @self-expose: {"id": "vision_processing_engine", "name": "视觉处理引擎", "type": "tool", "version": "2.0.0", "needs": {"deps": ["opencv-python", "pillow", "numpy"], "resources": ["模型目录", "OpenCV级联分类器", "图像文件", "Base64图像数据", "配置对象", "结果对象"]}, "provides": {"capabilities": ["初始化视觉模型", "加载图像文件", "从Base64数据加载图像", "调整图像大小", "提取图像特征", "计算图像锐度", "计算颜色直方图", "检测边缘", "分析纹理特征", "检测图像中的对象", "检测人脸", "检测基本形状", "检测颜色区域", "综合分析图像", "生成分析摘要", "支持多种图像格式", "支持图像大小限制", "支持多种操作类型", "支持智能体集成"]}, "exclusive_caller": "data_collector_agent", "usage_scenarios": ["数据收集师爬取网页时解析图片/截图", "文件上传接口处理用户上传的图片"], "architecture_role": "分离式多模态架构组件", "design_principle": "验证'非原生多模态LLM + 多模态引擎'能否等效原生多模态LLM"}

import os
import sys
import json
import base64
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from PIL import Image
import cv2

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

class VisionConfig:
    """视觉处理配置类"""
    
    def __init__(self):
        self.model_path = "models/vision"
        self.max_image_size = (1024, 1024)
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        self.feature_dim = 512
        self.confidence_threshold = 0.5

class VisionResult:
    """视觉处理结果类"""
    
    def __init__(self, success: bool = True, data: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error
        }

class VisionProcessingEngine:
    """视觉处理引擎核心类"""
    
    def __init__(self, config: VisionConfig = None):
        self.config = config or VisionConfig()
        self.models_loaded = False
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化视觉模型"""
        try:
            # 创建模型目录
            model_dir = Path(self.config.model_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # 禁用人脸检测功能（避免OpenCV FileStorage警告）
            self.face_cascade = None
            self.face_detection_available = False
            print("⚠️  人脸识别功能已禁用（避免启动警告）")
            
            # 标记模型已加载
            self.models_loaded = True
            print("视觉处理引擎初始化成功")
            
        except Exception as e:
            print(f"视觉模型初始化失败: {e}")
            self.models_loaded = False
            self.face_cascade = None
            self.face_detection_available = False
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """加载图像文件"""
        try:
            if not os.path.exists(image_path):
                return None
            
            # 检查文件格式
            file_ext = Path(image_path).suffix.lower()
            if file_ext not in self.config.supported_formats:
                return None
            
            # 使用OpenCV加载图像
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 调整图像大小
            image = self._resize_image(image)
            return image
            
        except Exception as e:
            print(f"图像加载失败: {e}")
            return None
    
    def load_image_from_base64(self, base64_data: str) -> Optional[np.ndarray]:
        """从Base64数据加载图像"""
        try:
            # 解码Base64数据
            image_data = base64.b64decode(base64_data)
            
            # 转换为numpy数组
            np_array = np.frombuffer(image_data, np.uint8)
            
            # 解码图像
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            if image is None:
                return None
            
            # 调整图像大小
            image = self._resize_image(image)
            return image
            
        except Exception as e:
            print(f"Base64图像加载失败: {e}")
            return None
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """调整图像大小"""
        height, width = image.shape[:2]
        max_height, max_width = self.config.max_image_size
        
        if height > max_height or width > max_width:
            # 计算缩放比例
            scale = min(max_height / height, max_width / width)
            new_height = int(height * scale)
            new_width = int(width * scale)
            
            # 调整大小
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    def extract_features(self, image: np.ndarray) -> Dict[str, Any]:
        """提取图像特征"""
        try:
            # 转换为灰度图像
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算图像统计特征
            features = {
                'brightness': np.mean(gray),
                'contrast': np.std(gray),
                'sharpness': self._calculate_sharpness(gray),
                'color_histogram': self._calculate_color_histogram(image),
                'edges': self._detect_edges(gray),
                'texture': self._analyze_texture(gray)
            }
            
            return features
            
        except Exception as e:
            print(f"特征提取失败: {e}")
            return {}
    
    def _calculate_sharpness(self, gray_image: np.ndarray) -> float:
        """计算图像锐度"""
        # 使用拉普拉斯算子计算图像锐度
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        return float(laplacian_var)
    
    def _calculate_color_histogram(self, image: np.ndarray) -> Dict[str, List[float]]:
        """计算颜色直方图"""
        # 分离RGB通道
        channels = cv2.split(image)
        
        histograms = {}
        color_names = ['blue', 'green', 'red']
        
        for i, channel in enumerate(channels):
            hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
            histograms[color_names[i]] = hist.flatten().tolist()
        
        return histograms
    
    def _detect_edges(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """检测边缘"""
        # 使用Canny边缘检测
        edges = cv2.Canny(gray_image, 50, 150)
        
        return {
            'edge_count': int(np.sum(edges > 0)),
            'edge_density': float(np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]))
        }
    
    def _analyze_texture(self, gray_image: np.ndarray) -> Dict[str, float]:
        """分析纹理特征"""
        # 计算灰度共生矩阵特征
        try:
            from skimage.feature import graycomatrix, graycoprops
            
            # 归一化灰度值
            gray_normalized = (gray_image / 255.0 * 63).astype(np.uint8)
            
            # 计算灰度共生矩阵
            glcm = graycomatrix(gray_normalized, [1], [0], symmetric=True, normed=True)
            
            # 计算纹理特征
            contrast = graycoprops(glcm, 'contrast')[0, 0]
            dissimilarity = graycoprops(glcm, 'dissimilarity')[0, 0]
            homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
            energy = graycoprops(glcm, 'energy')[0, 0]
            correlation = graycoprops(glcm, 'correlation')[0, 0]
            
            return {
                'contrast': float(contrast),
                'dissimilarity': float(dissimilarity),
                'homogeneity': float(homogeneity),
                'energy': float(energy),
                'correlation': float(correlation)
            }
            
        except ImportError:
            # 如果skimage不可用，返回简单特征
            return {
                'contrast': float(np.std(gray_image)),
                'energy': float(np.mean(gray_image))
            }
    
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测图像中的对象"""
        objects = []
        
        try:
            # 人脸检测
            faces = self._detect_faces(image)
            objects.extend(faces)
            
            # 形状检测
            shapes = self._detect_shapes(image)
            objects.extend(shapes)
            
            # 颜色区域检测
            color_regions = self._detect_color_regions(image)
            objects.extend(color_regions)
            
        except Exception as e:
            print(f"对象检测失败: {e}")
        
        return objects
    
    def _detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测人脸"""
        faces = []
        
        try:
            # 检查人脸检测是否可用
            if not self.face_detection_available or self.face_cascade is None:
                return faces
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用Haar级联分类器检测人脸
            detected_faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            for (x, y, w, h) in detected_faces:
                faces.append({
                    'type': 'face',
                    'confidence': 0.8,  # 简化置信度
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'area': int(w * h)
                })
                
        except Exception as e:
            print(f"人脸检测失败: {e}")
        
        return faces
    
    def _detect_shapes(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测基本形状"""
        shapes = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 二值化处理
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 100:  # 过滤小面积轮廓
                    continue
                
                # 计算轮廓近似
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # 根据顶点数判断形状
                vertices = len(approx)
                shape_type = 'unknown'
                
                if vertices == 3:
                    shape_type = 'triangle'
                elif vertices == 4:
                    shape_type = 'rectangle'
                elif vertices > 4:
                    shape_type = 'circle'
                
                # 计算边界框
                x, y, w, h = cv2.boundingRect(contour)
                
                shapes.append({
                    'type': shape_type,
                    'confidence': 0.7,
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'area': int(area),
                    'vertices': vertices
                })
                
        except Exception as e:
            print(f"形状检测失败: {e}")
        
        return shapes
    
    def _detect_color_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测颜色区域"""
        color_regions = []
        
        try:
            # 转换到HSV颜色空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 定义基本颜色范围
            color_ranges = {
                'red': [(0, 50, 50), (10, 255, 255)],
                'green': [(35, 50, 50), (85, 255, 255)],
                'blue': [(100, 50, 50), (130, 255, 255)],
                'yellow': [(20, 50, 50), (35, 255, 255)]
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                # 创建颜色掩码
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                
                # 查找轮廓
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # 过滤小面积区域
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        color_regions.append({
                            'type': f'{color_name}_region',
                            'confidence': 0.6,
                            'bbox': [int(x), int(y), int(w), int(h)],
                            'area': int(area)
                        })
                        
        except Exception as e:
            print(f"颜色区域检测失败: {e}")
        
        return color_regions
    
    def analyze_image(self, image_path: str = None, base64_data: str = None) -> VisionResult:
        """综合分析图像"""
        try:
            # 加载图像
            if image_path:
                image = self.load_image(image_path)
            elif base64_data:
                image = self.load_image_from_base64(base64_data)
            else:
                return VisionResult(success=False, error="未提供图像数据")
            
            if image is None:
                return VisionResult(success=False, error="图像加载失败")
            
            # 提取特征
            features = self.extract_features(image)
            
            # 检测对象
            objects = self.detect_objects(image)
            
            # 生成分析结果
            result = {
                'image_info': {
                    'dimensions': image.shape[:2],
                    'channels': image.shape[2] if len(image.shape) > 2 else 1
                },
                'features': features,
                'objects': objects,
                'object_count': len(objects),
                'analysis_summary': self._generate_summary(features, objects)
            }
            
            return VisionResult(success=True, data=result)
            
        except Exception as e:
            return VisionResult(success=False, error=f"图像分析失败: {str(e)}")
    
    def _generate_summary(self, features: Dict[str, Any], objects: List[Dict[str, Any]]) -> str:
        """生成分析摘要"""
        summary_parts = []
        
        # 添加特征摘要
        if features.get('brightness'):
            brightness = features['brightness']
            if brightness > 200:
                summary_parts.append("图像亮度较高")
            elif brightness < 50:
                summary_parts.append("图像亮度较低")
        
        # 添加对象摘要
        object_counts = {}
        for obj in objects:
            obj_type = obj['type']
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        
        for obj_type, count in object_counts.items():
            summary_parts.append(f"检测到{count}个{obj_type}")
        
        return "; ".join(summary_parts) if summary_parts else "未检测到显著特征"

class VisionProcessingTool:
    """视觉处理工具类（用于智能体集成）"""
    
    def __init__(self):
        self.engine = VisionProcessingEngine()
        self.tool_name = "VisionProcessingEngine"
        self.tool_description = "视觉处理引擎，支持图像识别、特征提取和对象检测"
        self.tool_usage = "用于分析图像内容，提取视觉特征，检测图像中的对象"
    
    def call(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用视觉处理工具"""
        try:
            if operation == "analyze_image":
                image_path = parameters.get('image_path')
                base64_data = parameters.get('base64_data')
                
                result = self.engine.analyze_image(image_path, base64_data)
                return result.to_dict()
                
            elif operation == "extract_features":
                image_path = parameters.get('image_path')
                base64_data = parameters.get('base64_data')
                
                if image_path:
                    image = self.engine.load_image(image_path)
                elif base64_data:
                    image = self.engine.load_image_from_base64(base64_data)
                else:
                    return {'success': False, 'error': '未提供图像数据'}
                
                if image is None:
                    return {'success': False, 'error': '图像加载失败'}
                
                features = self.engine.extract_features(image)
                return {'success': True, 'data': features}
                
            elif operation == "detect_objects":
                image_path = parameters.get('image_path')
                base64_data = parameters.get('base64_data')
                
                if image_path:
                    image = self.engine.load_image(image_path)
                elif base64_data:
                    image = self.engine.load_image_from_base64(base64_data)
                else:
                    return {'success': False, 'error': '未提供图像数据'}
                
                if image is None:
                    return {'success': False, 'error': '图像加载失败'}
                
                objects = self.engine.detect_objects(image)
                return {'success': True, 'data': objects}
                
            else:
                return {'success': False, 'error': f'未知操作: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': f'工具调用失败: {str(e)}'}

# 测试代码
if __name__ == "__main__":
    # 创建视觉处理引擎实例
    vision_engine = VisionProcessingEngine()
    
    # 测试图像分析
    test_image_path = "test_image.jpg"  # 需要替换为实际测试图像路径
    
    if os.path.exists(test_image_path):
        result = vision_engine.analyze_image(test_image_path)
        print("图像分析结果:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("测试图像不存在，跳过测试")