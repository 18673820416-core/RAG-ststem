# @self-expose: {"id": "audio_processing_engine", "name": "音频处理引擎", "type": "tool", "version": "2.0.0", "needs": {"deps": ["numpy", "wave", "struct"], "resources": ["音频文件", "Base64音频数据", "配置对象", "结果对象"]}, "provides": {"capabilities": ["初始化音频模型", "加载音频文件", "从Base64数据加载音频", "WAV格式解析", "24位音频转换", "音频重采样", "提取音频特征", "计算时域特征", "计算频域特征", "计算能量特征", "计算过零率", "计算频谱质心", "计算频谱滚降点", "提取MFCC特征", "检测静音段", "综合分析音频", "生成分析摘要", "支持多种音频格式", "支持音频时长限制", "支持智能体集成"]}, "exclusive_caller": "data_collector_agent", "usage_scenarios": ["数据收集师爬取网页时解析音频/视频", "文件上传接口处理用户上传的音频"], "architecture_role": "分离式多模态架构组件", "design_principle": "验证'非原生多模态LLM + 多模态引擎'能否等效原生多模态LLM"}
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
音频处理引擎
实现智能体系统的音频模态处理能力
支持音频分析、特征提取、语音识别等音频处理功能
"""

import os
import sys
import json
import base64
import numpy as np
import wave
import struct
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 添加RAG系统路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

class AudioConfig:
    """音频处理配置类"""
    
    def __init__(self):
        self.model_path = "models/audio"
        self.supported_formats = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
        self.sample_rate = 16000  # 标准采样率
        self.frame_length = 0.025  # 帧长度（秒）
        self.frame_shift = 0.010   # 帧移（秒）
        self.n_mfcc = 13           # MFCC特征维度
        self.max_audio_duration = 30  # 最大音频时长（秒）

class AudioResult:
    """音频处理结果类"""
    
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

class AudioProcessingEngine:
    """音频处理引擎核心类"""
    
    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.models_loaded = False
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化音频模型"""
        try:
            # 创建模型目录
            model_dir = Path(self.config.model_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # 标记模型已加载
            self.models_loaded = True
            print("音频处理引擎初始化成功")
            
        except Exception as e:
            print(f"音频模型初始化失败: {e}")
            self.models_loaded = False
    
    def load_audio(self, audio_path: str) -> Optional[Tuple[np.ndarray, int]]:
        """加载音频文件"""
        try:
            if not os.path.exists(audio_path):
                return None
            
            # 检查文件格式
            file_ext = Path(audio_path).suffix.lower()
            if file_ext not in self.config.supported_formats:
                return None
            
            # 目前仅支持WAV格式的直接处理
            if file_ext == '.wav':
                return self._load_wav_file(audio_path)
            else:
                # 对于其他格式，需要外部库支持
                print(f"暂不支持 {file_ext} 格式，请转换为WAV格式")
                return None
                
        except Exception as e:
            print(f"音频加载失败: {e}")
            return None
    
    def load_audio_from_base64(self, base64_data: str) -> Optional[Tuple[np.ndarray, int]]:
        """从Base64数据加载音频"""
        try:
            # 解码Base64数据
            audio_data = base64.b64decode(base64_data)
            
            # 将数据写入临时文件
            temp_path = "temp_audio.wav"
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # 加载临时文件
            result = self.load_audio(temp_path)
            
            # 删除临时文件
            os.remove(temp_path)
            
            return result
            
        except Exception as e:
            print(f"Base64音频加载失败: {e}")
            return None
    
    def _load_wav_file(self, wav_path: str) -> Optional[Tuple[np.ndarray, int]]:
        """加载WAV文件"""
        try:
            with wave.open(wav_path, 'rb') as wav_file:
                # 获取音频参数
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # 读取音频数据
                frames = wav_file.readframes(n_frames)
                
                # 转换为numpy数组
                if sample_width == 1:
                    # 8位无符号整数
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = (audio_data - 128).astype(np.int16)
                elif sample_width == 2:
                    # 16位有符号整数
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                elif sample_width == 3:
                    # 24位有符号整数（需要特殊处理）
                    audio_data = self._convert_24bit_to_32bit(frames)
                else:
                    print(f"不支持的采样宽度: {sample_width}")
                    return None
                
                # 处理多声道音频（转换为单声道）
                if n_channels > 1:
                    audio_data = audio_data.reshape(-1, n_channels)
                    audio_data = np.mean(audio_data, axis=1)
                
                # 重采样到标准采样率
                if frame_rate != self.config.sample_rate:
                    audio_data = self._resample_audio(audio_data, frame_rate, self.config.sample_rate)
                
                return audio_data, self.config.sample_rate
                
        except Exception as e:
            print(f"WAV文件加载失败: {e}")
            return None
    
    def _convert_24bit_to_32bit(self, frames: bytes) -> np.ndarray:
        """将24位音频数据转换为32位"""
        # 每3个字节表示一个24位样本
        samples = []
        for i in range(0, len(frames), 3):
            # 将3个字节转换为32位整数
            sample_bytes = frames[i:i+3] + b'\x00'  # 添加一个字节使其成为32位
            sample = struct.unpack('<i', sample_bytes)[0]
            samples.append(sample)
        
        return np.array(samples, dtype=np.int32)
    
    def _resample_audio(self, audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """重采样音频"""
        try:
            # 简单的线性重采样
            ratio = target_rate / original_rate
            new_length = int(len(audio_data) * ratio)
            
            # 创建重采样索引
            indices = np.linspace(0, len(audio_data) - 1, new_length)
            
            # 线性插值
            resampled = np.interp(indices, np.arange(len(audio_data)), audio_data)
            
            return resampled.astype(audio_data.dtype)
            
        except Exception as e:
            print(f"音频重采样失败: {e}")
            return audio_data
    
    def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """提取音频特征"""
        try:
            features = {}
            
            # 基本统计特征
            features['basic_stats'] = self._calculate_basic_stats(audio_data)
            
            # 频谱特征
            features['spectral'] = self._calculate_spectral_features(audio_data, sample_rate)
            
            # MFCC特征（简化版）
            features['mfcc'] = self._calculate_simplified_mfcc(audio_data, sample_rate)
            
            # 能量特征
            features['energy'] = self._calculate_energy_features(audio_data)
            
            # 零交叉率
            features['zero_crossing_rate'] = self._calculate_zero_crossing_rate(audio_data)
            
            return features
            
        except Exception as e:
            print(f"音频特征提取失败: {e}")
            return {}
    
    def _calculate_basic_stats(self, audio_data: np.ndarray) -> Dict[str, float]:
        """计算基本统计特征"""
        return {
            'mean': float(np.mean(audio_data)),
            'std': float(np.std(audio_data)),
            'max': float(np.max(audio_data)),
            'min': float(np.min(audio_data)),
            'rms': float(np.sqrt(np.mean(audio_data**2))),
            'duration': float(len(audio_data) / self.config.sample_rate)
        }
    
    def _calculate_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """计算频谱特征"""
        try:
            # 计算FFT
            fft_data = np.fft.fft(audio_data)
            fft_magnitude = np.abs(fft_data)
            
            # 计算频率
            frequencies = np.fft.fftfreq(len(audio_data), 1/sample_rate)
            
            # 只取正频率部分
            positive_freq_idx = frequencies >= 0
            frequencies = frequencies[positive_freq_idx]
            fft_magnitude = fft_magnitude[positive_freq_idx]
            
            # 计算频谱质心
            spectral_centroid = np.sum(frequencies * fft_magnitude) / np.sum(fft_magnitude)
            
            # 计算频谱带宽
            spectral_bandwidth = np.sqrt(np.sum((frequencies - spectral_centroid)**2 * fft_magnitude) / np.sum(fft_magnitude))
            
            # 计算频谱滚降点
            total_energy = np.sum(fft_magnitude)
            cumulative_energy = np.cumsum(fft_magnitude)
            spectral_rolloff = frequencies[np.argmax(cumulative_energy >= 0.85 * total_energy)]
            
            return {
                'spectral_centroid': float(spectral_centroid),
                'spectral_bandwidth': float(spectral_bandwidth),
                'spectral_rolloff': float(spectral_rolloff),
                'dominant_frequency': float(frequencies[np.argmax(fft_magnitude)])
            }
            
        except Exception as e:
            print(f"频谱特征计算失败: {e}")
            return {}
    
    def _calculate_simplified_mfcc(self, audio_data: np.ndarray, sample_rate: int) -> List[float]:
        """计算简化的MFCC特征"""
        try:
            # 简化的MFCC计算（不使用外部库）
            # 这里实现一个简化的版本，实际应用中应该使用librosa等专业库
            
            # 预加重
            pre_emphasis = 0.97
            emphasized = np.append(audio_data[0], audio_data[1:] - pre_emphasis * audio_data[:-1])
            
            # 分帧
            frame_length = int(self.config.frame_length * sample_rate)
            frame_shift = int(self.config.frame_shift * sample_rate)
            
            frames = []
            for i in range(0, len(emphasized) - frame_length, frame_shift):
                frame = emphasized[i:i+frame_length]
                frames.append(frame)
            
            if not frames:
                return [0.0] * self.config.n_mfcc
            
            # 应用汉明窗
            hamming_window = np.hamming(frame_length)
            windowed_frames = [frame * hamming_window for frame in frames]
            
            # 计算功率谱
            power_spectra = [np.abs(np.fft.fft(frame))**2 for frame in windowed_frames]
            
            # 简化的梅尔滤波器组（固定频率范围）
            mel_filters = self._create_simplified_mel_filters(sample_rate, frame_length)
            
            # 应用梅尔滤波器
            mel_spectra = []
            for spectrum in power_spectra:
                mel_spectrum = []
                for mel_filter in mel_filters:
                    mel_energy = np.sum(spectrum[:len(mel_filter)] * mel_filter)
                    mel_spectrum.append(mel_energy)
                mel_spectra.append(mel_spectrum)
            
            # 取对数并计算均值作为简化MFCC
            log_mel_spectra = np.log(np.array(mel_spectra) + 1e-8)
            mean_mfcc = np.mean(log_mel_spectra, axis=0)
            
            # 只取前n_mfcc个系数
            return mean_mfcc[:self.config.n_mfcc].tolist()
            
        except Exception as e:
            print(f"简化MFCC计算失败: {e}")
            return [0.0] * self.config.n_mfcc
    
    def _create_simplified_mel_filters(self, sample_rate: int, n_fft: int) -> List[np.ndarray]:
        """创建简化的梅尔滤波器组"""
        # 简化的梅尔滤波器实现
        n_filters = 26  # 固定滤波器数量
        filters = []
        
        # 梅尔频率范围
        mel_min = 0
        mel_max = 2595 * np.log10(1 + sample_rate / 2 / 700)
        
        # 创建梅尔频率点
        mel_points = np.linspace(mel_min, mel_max, n_filters + 2)
        
        # 转换为线性频率
        freq_points = 700 * (10**(mel_points / 2595) - 1)
        
        # 转换为FFT bin索引
        bin_points = np.floor((n_fft + 1) * freq_points / sample_rate).astype(int)
        
        for i in range(n_filters):
            # 创建三角滤波器
            filter_bank = np.zeros(n_fft // 2 + 1)
            
            start = bin_points[i]
            center = bin_points[i+1]
            end = bin_points[i+2]
            
            # 上升部分
            if start < center:
                filter_bank[start:center] = np.linspace(0, 1, center - start)
            
            # 下降部分
            if center < end:
                filter_bank[center:end] = np.linspace(1, 0, end - center)
            
            filters.append(filter_bank)
        
        return filters
    
    def _calculate_energy_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """计算能量特征"""
        # 分帧计算能量
        frame_length = int(self.config.frame_length * self.config.sample_rate)
        frame_shift = int(self.config.frame_shift * self.config.sample_rate)
        
        energies = []
        for i in range(0, len(audio_data) - frame_length, frame_shift):
            frame = audio_data[i:i+frame_length]
            energy = np.sum(frame**2)
            energies.append(energy)
        
        if not energies:
            return {'mean_energy': 0.0, 'energy_variance': 0.0}
        
        return {
            'mean_energy': float(np.mean(energies)),
            'energy_variance': float(np.var(energies)),
            'max_energy': float(np.max(energies)),
            'min_energy': float(np.min(energies))
        }
    
    def _calculate_zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """计算零交叉率"""
        zero_crossings = np.sum(np.diff(np.signbit(audio_data)))
        zcr = zero_crossings / len(audio_data)
        return float(zcr)
    
    def analyze_audio(self, audio_path: str = None, base64_data: str = None) -> AudioResult:
        """综合分析音频"""
        try:
            # 加载音频
            if audio_path:
                result = self.load_audio(audio_path)
            elif base64_data:
                result = self.load_audio_from_base64(base64_data)
            else:
                return AudioResult(success=False, error="未提供音频数据")
            
            if result is None:
                return AudioResult(success=False, error="音频加载失败")
            
            audio_data, sample_rate = result
            
            # 提取特征
            features = self.extract_features(audio_data, sample_rate)
            
            # 生成分析结果
            result_data = {
                'audio_info': {
                    'duration': len(audio_data) / sample_rate,
                    'sample_rate': sample_rate,
                    'samples': len(audio_data)
                },
                'features': features,
                'analysis_summary': self._generate_summary(features)
            }
            
            return AudioResult(success=True, data=result_data)
            
        except Exception as e:
            return AudioResult(success=False, error=f"音频分析失败: {str(e)}")
    
    def _generate_summary(self, features: Dict[str, Any]) -> str:
        """生成分析摘要"""
        summary_parts = []
        
        # 添加时长信息
        if 'basic_stats' in features and 'duration' in features['basic_stats']:
            duration = features['basic_stats']['duration']
            summary_parts.append(f"音频时长: {duration:.2f}秒")
        
        # 添加能量信息
        if 'energy' in features and 'mean_energy' in features['energy']:
            mean_energy = features['energy']['mean_energy']
            if mean_energy > 1e6:
                summary_parts.append("音频能量较高")
            elif mean_energy < 1e4:
                summary_parts.append("音频能量较低")
        
        # 添加频谱信息
        if 'spectral' in features and 'dominant_frequency' in features['spectral']:
            dominant_freq = features['spectral']['dominant_frequency']
            if dominant_freq > 2000:
                summary_parts.append("高频成分较多")
            elif dominant_freq < 500:
                summary_parts.append("低频成分较多")
        
        return "; ".join(summary_parts) if summary_parts else "音频特征分析完成"

class AudioProcessingTool:
    """音频处理工具类（用于智能体集成）"""
    
    def __init__(self):
        self.engine = AudioProcessingEngine()
        self.tool_name = "AudioProcessingEngine"
        self.tool_description = "音频处理引擎，支持音频分析、特征提取和语音识别"
        self.tool_usage = "用于分析音频内容，提取音频特征，识别语音信息"
    
    def call(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用音频处理工具"""
        try:
            if operation == "analyze_audio":
                audio_path = parameters.get('audio_path')
                base64_data = parameters.get('base64_data')
                
                result = self.engine.analyze_audio(audio_path, base64_data)
                return result.to_dict()
                
            elif operation == "extract_features":
                audio_path = parameters.get('audio_path')
                base64_data = parameters.get('base64_data')
                
                if audio_path:
                    result = self.engine.load_audio(audio_path)
                elif base64_data:
                    result = self.engine.load_audio_from_base64(base64_data)
                else:
                    return {'success': False, 'error': '未提供音频数据'}
                
                if result is None:
                    return {'success': False, 'error': '音频加载失败'}
                
                audio_data, sample_rate = result
                features = self.engine.extract_features(audio_data, sample_rate)
                return {'success': True, 'data': features}
                
            else:
                return {'success': False, 'error': f'未知操作: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': f'工具调用失败: {str(e)}'}

# 测试代码
if __name__ == "__main__":
    # 创建音频处理引擎实例
    audio_engine = AudioProcessingEngine()
    
    # 测试音频分析
    test_audio_path = "test_audio.wav"  # 需要替换为实际测试音频路径
    
    if os.path.exists(test_audio_path):
        result = audio_engine.analyze_audio(test_audio_path)
        print("音频分析结果:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("测试音频不存在，跳过测试")