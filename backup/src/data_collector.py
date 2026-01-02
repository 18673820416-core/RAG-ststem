# @self-expose: {"id": "data_collector", "name": "Data Collector", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Data Collector功能"]}}
# 数据收集模块 - 基于LLM智能切片

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

from config.system_config import DATA_SOURCES, DATA_DIR

# 导入统一切片模块
from tools.memory_slicer_tool import MemorySlicerTool

logger = logging.getLogger(__name__)

class DataCollector:
    """数据收集器 - 基于LLM智能切片策略"""
    
    def __init__(self, llm_client=None):
        self.collected_data = []
        self.processed_files = set()
        self.llm_client = llm_client  # LLM客户端（未来集成）
        
        # 创建统一切片器
        self.slicer = MemorySlicerTool()
        
    def collect_from_file_system(self, file_path: str) -> List[Dict[str, Any]]:
        """从文件系统收集数据"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return []
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"文件内容为空: {file_path}")
                return []
            
            # 构建元数据
            metadata = {
                "source": "file_system",
                "file_path": str(file_path),
                "file_size": len(content),
                "collected_at": datetime.now().isoformat()
            }
            
            # 进行智能切片
            slices = self._intelligent_slice_text(content, str(file_path))
            
            logger.info(f"从文件 {file_path} 收集到 {len(slices)} 个切片")
            return slices
            
        except Exception as e:
            logger.error(f"收集文件数据失败 {file_path}: {e}")
            return []
    
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
    
    def _intelligent_slice_text(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """基于语义边界的智能文本切片"""
        # 构建元数据
        metadata = {
            "source": "intelligent_slice",
            "file_path": str(file_path),
            "collected_at": datetime.now().isoformat()
        }
        
        # 使用LLM切片器进行智能切片
        return self.slicer.slice_text(text, metadata)
    
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
        """保存收集的数据"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = DATA_DIR / f"collected_data_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")

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