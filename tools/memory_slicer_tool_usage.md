# 记忆切片管理工具使用指南

## 工具概述

记忆切片管理工具（MemorySlicerTool）是一个统一的记忆切片管理工具，整合了逻辑链切片器和事件切片器，提供完整的记忆切片管理功能。

**开发提示词来源**：用户对话中关于统一管理逻辑切片和主题二次切片的建议

## 核心功能

### 1. 文本智能切片
```python
from tools.memory_slicer_tool import MemorySlicerTool

# 创建切片工具实例
slicer = MemorySlicerTool()

# 配置切片参数
config = {
    "enable_event_slicing": True,  # 启用事件二次切片
    "max_slice_size": 500,        # 最大切片大小
    "min_slice_size": 100,        # 最小切片大小
    "quality_threshold": 0.8      # 质量阈值
}

# 构建元数据
metadata = {
    "source": "user_input",
    "file_path": "example.txt",
    "collected_at": "2024-01-01T10:00:00"
}

# 执行文本切片
slices = slicer.slice_text("这是一段需要切分的文本内容...", metadata, config)
```

### 2. 文件切片
```python
# 对单个文件进行切片
slices = slicer.slice_file("path/to/document.txt", config)

# 批量文件切片
batch_slices = slicer.batch_slice_files("data/*.txt", config)
```

### 3. 层级检索功能
```python
# 基于层级编码的智能检索
query = "搜索关键词"
results = slicer.hierarchical_retrieval(query, slices, top_k=10)

# 解析层级结构
hierarchy = slicer.get_slice_hierarchy(slices)
```

## 在工具箱中的使用

### 通过工具箱管理器调用
```python
from tools.chat_tools import ChatToolManager

# 创建工具管理器
tool_manager = ChatToolManager()

# 获取记忆切片工具
slicer_tool = tool_manager.get_tool('memory_slicer')

# 使用切片工具
slices = slicer_tool.slice_text("文本内容...", metadata)
```

### 在数据收集器中的集成
```python
from src.data_collector import DataCollector

# 创建数据收集器（自动使用统一切片工具）
collector = DataCollector()

# 收集数据并自动切片
collected_data = collector.collect_all_sources()
```

## 配置参数详解

### 切片配置选项
```python
config = {
    # 基础配置
    "enable_event_slicing": True,      # 是否启用事件二次切片
    "max_slice_size": 500,            # 最大切片字符数
    "min_slice_size": 100,            # 最小切片字符数
    
    # 质量配置
    "quality_threshold": 0.8,         # 切片质量阈值
    "enable_quality_assessment": True, # 是否启用质量评估
    
    # 事件切片配置
    "event_extraction_method": "tfidf", # 事件提取方法
    "min_event_words": 3,             # 最小事件词数量
    "event_similarity_threshold": 0.7, # 事件相似度阈值
    
    # 逻辑链切片配置
    "logical_boundary_detection": True, # 逻辑边界检测
    "min_logical_unit_size": 200,     # 最小逻辑单元大小
}
```

## 使用场景示例

### 场景1：用户上传文件处理
```python
def process_uploaded_file(file_path):
    """处理用户上传的文件"""
    from tools.chat_tools import ChatToolManager
    
    tool_manager = ChatToolManager()
    slicer = tool_manager.get_tool('memory_slicer')
    
    # 配置适合文档的切片参数
    config = {
        "enable_theme_slicing": True,
        "max_slice_size": 800,
        "min_slice_size": 200
    }
    
    # 对上传文件进行切片
    slices = slicer.slice_file(file_path, config)
    
    # 分析切片质量
    quality = slicer.analyze_slice_quality(slices)
    
    return slices, quality
```

### 场景2：网络知识爬取
```python
def process_web_content(content, url):
    """处理网络爬取的内容"""
    from tools.memory_slicer_tool import MemorySlicerTool
    
    slicer = MemorySlicerTool()
    
    metadata = {
        "source": "web_crawler",
        "url": url,
        "collected_at": "2024-01-01T10:00:00"
    }
    
    config = {
        "enable_theme_slicing": True,
        "max_slice_size": 400,
        "quality_threshold": 0.75
    }
    
    slices = slicer.slice_text(content, metadata, config)
    return slices
```

### 场景3：记忆整理智能体
```python
class MemoryOrganizerAgent:
    """记忆整理智能体"""
    
    def __init__(self):
        from tools.chat_tools import ChatToolManager
        self.tool_manager = ChatToolManager()
        self.slicer = self.tool_manager.get_tool('memory_slicer')
    
    def reorganize_memories(self, memories):
        """重新组织记忆切片"""
        # 合并相关记忆内容
        combined_content = "\n".join([m['content'] for m in memories])
        
        # 使用更精细的切片配置重新切片
        config = {
            "enable_theme_slicing": True,
            "max_slice_size": 300,
            "min_slice_size": 100,
            "quality_threshold": 0.85
        }
        
        metadata = {
            "source": "memory_reorganization",
            "original_memories": len(memories)
        }
        
        new_slices = self.slicer.slice_text(combined_content, metadata, config)
        return new_slices
```

## 错误处理与调试

### 常见错误处理
```python
try:
    slices = slicer.slice_text(content, metadata, config)
except Exception as e:
    print(f"切片失败: {e}")
    # 使用默认配置重试
    slices = slicer.slice_text(content, metadata)
```

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 执行切片操作
slices = slicer.slice_text(content, metadata, config)
```

## 性能优化建议

1. **批量处理**：对于大量文件，使用`batch_slice_files`方法
2. **配置调优**：根据内容类型调整切片参数
3. **缓存机制**：对重复内容启用切片结果缓存
4. **并行处理**：对于大型文档，考虑并行切片处理

## 版本历史

- v1.0: 初始版本，整合逻辑链切片和事件二次切片
- 集成到RAG系统工具箱
- 支持多种使用场景和配置选项