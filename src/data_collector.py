# @self-expose: {"id": "data_collector", "name": "Data Collector", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Data Collector功能"]}}
# 数据收集模块 - 基于逻辑链二次切片技术
# 开发提示词来源：用户要求集成逻辑链二次切片工具替代昂贵的LLM智能切片工具

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

# 导入配置
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.system_config import DATA_SOURCES, DATA_DIR

# 导入统一的记忆切片管理工具
from tools.memory_slicer_tool import MemorySlicerTool

logger = logging.getLogger(__name__)

class DataCollector:
    """数据收集器 - 基于逻辑链二次切片策略"""
    
    def __init__(self, llm_client=None):
        self.collected_data = []
        self.processed_files = set()
        self.llm_client = llm_client  # LLM客户端（未来集成）
        
        # 创建统一的记忆切片管理工具
        self.memory_slicer = MemorySlicerTool()
        
    def collect_from_file_system(self, path: str) -> List[Dict[str, Any]]:
        """从文件系统收集数据（支持文件和文件夹）"""
        path = Path(path)
        
        if not path.exists():
            logger.warning(f"路径不存在: {path}")
            return []
        
        all_data = []
        
        if path.is_file():
            # 处理单个文件
            data = self._process_single_file(path)
            all_data.extend(data)
        elif path.is_dir():
            # 递归遍历文件夹
            logger.info(f"开始遍历文件夹: {path}")
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    data = self._process_single_file(file_path)
                    all_data.extend(data)
            logger.info(f"从文件夹 {path} 收集到 {len(all_data)} 条数据")
        
        return all_data
    
    def _process_single_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """处理单个文件"""
        if file_path in self.processed_files:
            return []
            
        self.processed_files.add(file_path)
        
        try:
            # 根据文件类型处理
            if file_path.suffix.lower() in ['.txt', '.md', '.json']:
                return self._process_text_file(file_path)
            elif file_path.suffix.lower() in ['.log']:
                return self._process_log_file(file_path)
            else:
                logger.debug(f"跳过不支持的文件类型: {file_path}")
                
        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {e}")
            
        return []
    
    def _process_text_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """处理文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 基础文本数据记录
            data_item = {
                "source": "file_system",
                "file_path": str(file_path),
                "content": content,
                "file_type": file_path.suffix,
                "file_size": len(content),
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "collected_at": datetime.now().isoformat()
            }
            
            return [data_item]
            
        except Exception as e:
            logger.error(f"读取文本文件失败 {file_path}: {e}")
            return []
    
    def _process_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """处理日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            log_entries = []
            for line_num, line in enumerate(lines, 1):
                if line.strip():  # 跳过空行
                    log_entry = {
                        "source": "log_file",
                        "file_path": str(file_path),
                        "line_number": line_num,
                        "content": line.strip(),
                        "collected_at": datetime.now().isoformat()
                    }
                    log_entries.append(log_entry)
                    
            return log_entries
            
        except Exception as e:
            logger.error(f"读取日志文件失败 {file_path}: {e}")
            return []
    
    def _intelligent_slice_text(self, text: str, file_path: str, current_depth: int = 0, refinement_attempts: int = 0) -> List[Dict[str, Any]]:
        """使用统一的记忆切片工具进行智能文本切片，添加递归深度限制和错误处理"""
        # 最大递归深度限制
        MAX_RECURSION_DEPTH = 10
        # 最大精炼尝试次数，避免无限循环
        MAX_REFINEMENT_ATTEMPTS = 3
        
        # 构建元数据
        metadata = {
            "source": "memory_slicer_tool",
            "file_path": str(file_path),
            "collected_at": datetime.now().isoformat(),
            "recursion_depth": current_depth
        }
        
        try:
            # 检查递归深度
            if current_depth >= MAX_RECURSION_DEPTH:
                logger.warning(f"达到最大递归深度 {MAX_RECURSION_DEPTH}，当前文本长度: {len(text)}")
                
                # 检查精炼尝试次数
                if refinement_attempts < MAX_REFINEMENT_ATTEMPTS:
                    logger.info(f"进行语义精炼，当前尝试次数: {refinement_attempts + 1}")
                    
                    # 调用记忆重构引擎进行语义精炼
                    refined_text = self._refine_text_semantically(text, file_path)
                    logger.info(f"语义精炼完成，原文本长度: {len(text)}, 精炼后长度: {len(refined_text)}")
                    
                    # 对精炼后的文本进行二次分片（保留当前递归深度，不重置）
                    return self._intelligent_slice_text(refined_text, file_path, current_depth=current_depth, refinement_attempts=refinement_attempts + 1)
                else:
                    logger.info(f"已达到最大精炼尝试次数 {MAX_REFINEMENT_ATTEMPTS}，使用简单分片")
                    # 达到最大尝试次数，使用简单分片
                    return self._simple_slice_text(text, metadata)
            
            # 使用统一的记忆切片工具进行智能切片
            slices = self.memory_slicer.slice_text(text, metadata)
            logger.info(f"记忆切片工具生成 {len(slices)} 个切片，当前递归深度: {current_depth}")
            return slices
            
        except RecursionError as e:
            logger.error(f"递归错误，当前递归深度: {current_depth}, 进行语义精炼: {e}")
            
            # 检查精炼尝试次数
            if refinement_attempts < MAX_REFINEMENT_ATTEMPTS:
                # 调用记忆重构引擎进行语义精炼
                refined_text = self._refine_text_semantically(text, file_path)
                logger.info(f"语义精炼完成，原文本长度: {len(text)}, 精炼后长度: {len(refined_text)}")
                
                # 对精炼后的文本进行二次分片（保留当前递归深度，不重置）
                return self._intelligent_slice_text(refined_text, file_path, current_depth=current_depth, refinement_attempts=refinement_attempts + 1)
            else:
                logger.info(f"已达到最大精炼尝试次数 {MAX_REFINEMENT_ATTEMPTS}，使用简单分片")
                # 达到最大尝试次数，使用简单分片
                return self._simple_slice_text(text, metadata)
            
        except Exception as e:
            logger.error(f"智能切片失败，使用简单分片: {e}")
            
            # 降级处理：使用简单分片
            return self._simple_slice_text(text, metadata)
    
    def _refine_text_semantically(self, text: str, file_path: str) -> str:
        """使用记忆重构引擎进行语义精炼"""
        try:
            # 导入记忆重构引擎
            from cognitive_engines.memory_reconstruction_engine import MemoryReconstructionEngine
            
            # 创建记忆重构引擎实例
            reconstruction_engine = MemoryReconstructionEngine()
            
            # 进行语义精炼
            refined_text = reconstruction_engine.refine_memory(text, {
                "source": "data_collector",
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            })
            
            return refined_text
            
        except Exception as e:
            logger.error(f"语义精炼失败，返回原文本: {e}")
            # 降级处理：返回原文本
            return text
    
    def _simple_slice_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """简单分片算法，作为降级处理"""
        # 简单的按长度分片，确保每个分片不超过1000字
        MAX_SLICE_LENGTH = 1000
        slices = []
        
        start = 0
        slice_id = 0
        
        while start < len(text):
            end = min(start + MAX_SLICE_LENGTH, len(text))
            # 尝试在句子边界处分割
            if end < len(text):
                # 寻找最近的句子结束符
                end = max(text.rfind('.', start, end), text.rfind('。', start, end), 
                         text.rfind('!', start, end), text.rfind('！', start, end),
                         text.rfind('?', start, end), text.rfind('？', start, end))
                if end == -1:  # 没有找到句子结束符，直接按长度分割
                    end = start + MAX_SLICE_LENGTH
                else:
                    end += 1  # 包含句子结束符
            
            slice_content = text[start:end].strip()
            if slice_content:
                slices.append({
                    "content": slice_content,
                    "slice_id": f"simple_{slice_id}",
                    "slice_depth": 0,
                    "parent_id": "",
                    "importance": 0.7,
                    "confidence": 0.8,
                    "source": metadata.get("source", "simple_slice"),
                    "file_path": metadata.get("file_path", "unknown"),
                    "collected_at": metadata.get("collected_at", datetime.now().isoformat()),
                    "is_simple_slice": True
                })
                slice_id += 1
            
            start = end
        
        logger.info(f"简单分片生成 {len(slices)} 个切片")
        return slices
    
    def collect_all_sources(self) -> List[Dict[str, Any]]:
        """收集所有配置的数据源（使用智能切片）"""
        all_data = []
        
        for source_name, config in DATA_SOURCES.items():
            if config.get("enabled", False):
                logger.info(f"开始收集数据源: {source_name}")
                
                paths = config.get("paths", [])
                for path_template in paths:
                    # 简单的路径处理（实际使用时需要更复杂的路径解析）
                    path = path_template.replace("{username}", "current_user")
                    
                    try:
                        raw_data = self.collect_from_file_system(path)
                        
                        # 对收集的数据进行智能切片
                        sliced_data = []
                        for item in raw_data:
                            content = item.get('content', '')
                            if content:
                                slices = self._intelligent_slice_text(content, item.get('file_path', ''))
                                sliced_data.extend(slices)
                        
                        all_data.extend(sliced_data)
                        logger.info(f"从 {path} 收集到 {len(raw_data)} 条原始数据，切片为 {len(sliced_data)} 条")
                        
                    except Exception as e:
                        logger.error(f"收集数据源 {source_name} 路径 {path} 失败: {e}")
        
        # 保存收集的数据
        self._save_collected_data(all_data)
        
        return all_data
    
    def _save_collected_data(self, data: List[Dict[str, Any]]):
        """保存收集的数据到JSON文件和向量库"""
        if not data:
            return
            
        # 保存到JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = DATA_DIR / f"collected_data_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存数据到JSON文件失败: {e}")
        
        # 保存到向量库（使用事件维编码器和网状思维引擎）
        try:
            from src.vector_database import VectorDatabase
            from src.event_dimension_encoder import EventDimensionEncoder
            from src.mesh_thought_engine import MeshThoughtEngine
            
            # 创建向量数据库、事件维编码器和网状思维引擎实例
            vector_db = VectorDatabase()
            event_encoder = EventDimensionEncoder()
            mesh_engine = MeshThoughtEngine()
            
            logger.info(f"开始将 {len(data)} 条切片数据保存到向量库")
            
            # 为每个切片生成向量并保存到向量库
            for slice_data in data:
                content = slice_data.get('content', '')
                if content:
                    # 1. 使用事件维编码器提取事件编码
                    event_codes = event_encoder.extract_event_codes_from_memory(slice_data)
                    
                    # 2. 使用网状思维引擎分析文本关系
                    mesh_engine.add_thought(content, slice_data)
                    
                    # 3. 生成内容向量（简化实现）
                    content_vector = [0.0] * 12  # 12维向量
                    
                    # 4. 构建记忆数据
                    memory_data = {
                        "topic": f"数据收集 - {slice_data.get('source', 'unknown')}",
                        "content": content,
                        "source_type": "collected_data",
                        "slice_id": slice_data.get('slice_id', ''),
                        "slice_depth": slice_data.get('slice_depth', 0),
                        "parent_id": slice_data.get('parent_id', ''),
                        "event_codes": event_codes,
                        "timestamp": slice_data.get('collected_at', datetime.now().isoformat()),
                        "importance": slice_data.get('importance', 0.7),
                        "confidence": slice_data.get('confidence', 0.9),
                        "tags": ["collected", slice_data.get('source', 'unknown')] + event_codes
                    }
                    
                    # 5. 保存到向量库
                    vector_db.add_memory(memory_data, vector=content_vector)
            
            logger.info(f"成功将 {len(data)} 条切片数据保存到向量库")
            
        except Exception as e:
            logger.error(f"保存数据到向量库失败: {e}")

def main():
    """测试数据收集功能"""
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    collector = DataCollector()
    
    # 收集数据
    print("开始收集数据...")
    data = collector.collect_all_sources()
    
    print(f"共收集到 {len(data)} 条数据")
    
    if data:
        # 显示前几条数据作为示例
        for i, item in enumerate(data[:3]):
            print(f"\n示例数据 {i+1}:")
            print(f"来源: {item.get('source', 'N/A')}")
            print(f"路径: {item.get('file_path', 'N/A')}")
            content_preview = item.get('content', '')[:100] + "..." if len(item.get('content', '')) > 100 else item.get('content', '')
            print(f"内容预览: {content_preview}")

if __name__ == "__main__":
    main()