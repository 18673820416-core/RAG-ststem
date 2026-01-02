# RAG系统稳定配方记录

## 📋 核心配方
**Python 3.13.7 + NumPy 2.2.6 + OpenCV-Python 4.12.0.88 (稳定构建版本)**

### 配方来源
- **发现时间**: 2025年11月25日
- **最新更新**: 2025年11月30日
- **问题根源**: Python 3.14与NumPy存在兼容性问题；旧版本OpenCV-Python与NumPy 2.x不兼容
- **解决方案**: 使用Python 3.13.7 + NumPy 2.2.6 + OpenCV-Python 4.12.0.88的稳定组合
- **验证状态**: ✅ 完全兼容，所有核心功能正常

### 新增发现 (2025年11月30日更新)
- **新问题**: 旧版本OpenCV-Python (4.8.1.78)与NumPy 2.x不兼容，导致"AttributeError: _ARRAY_API not found"错误
- **解决方案**: 升级OpenCV-Python到4.12.0.88，该版本兼容NumPy 2.x
- **验证结果**: OpenCV-Python 4.12.0.88 + NumPy 2.2.6组合稳定运行

### 配方验证
```bash
# Python版本验证
Python 3.13.7 (稳定版本)

# NumPy版本验证  
NumPy 2.2.6 (完全兼容)

# OpenCV-Python版本验证
OpenCV-Python 4.12.0.88 (完全兼容)

# 核心功能验证
✅ 网状思维引擎 (可用)
✅ 视觉处理引擎 (可用)
✅ 多模态融合引擎 (可用)
✅ 向量数据库 (可用)
✅ 命令行工具 (可用)
```

## 🚫 不兼容组合
- Python 3.14.x + 任何NumPy版本 (存在兼容性问题)
- 任何Python版本 + NumPy实验版本 (系统警告"CRASHES ARE TO BE EXPECTED")
- NumPy MINGW-W64实验性构建 (Windows平台稳定性风险)

### NumPy构建问题详细说明
**问题现象**:
- NumPy启动时显示"Numpy built with MINGW-W64 on Windows 64 bits is experimental"
- 出现多个RuntimeWarning: invalid value encountered in exp2/nextafter/log10
- 明确提示"CRASHES ARE TO BE EXPECTED"

**影响范围**:
- 系统稳定性存在风险
- 可能导致服务器意外崩溃
- 数值计算可能产生错误结果

**解决方案**:
1. 重新安装稳定的NumPy版本: `pip uninstall numpy && pip install numpy==2.3.3`
2. 使用官方推荐的NumPy构建版本
3. 避免使用实验性构建

## 📁 当前系统文件
- `stable_start_server.py` - 稳定版服务器 (符合Python 3.13.7 + NumPy 2.3.3配方)

## 🗑️ 历史文件清理记录

### 清理原因
**核心原则**: 系统应该保持精简和高效，避免版本混乱和文件冗余。

### 已清理文件说明
- `start_server.py` - 使用Python 3.14.0的实验版本，存在兼容性问题
- `enhanced_start_server.py` - 增强版服务器 (历史版本，功能已整合到稳定版)
- `python313_start_server.py` - Python 3.13.7专用服务器 (历史版本)
- `test_start_server.py` - 测试版本，功能与稳定版本重复
- `experimental_start_server.py` - 实验性版本，存在稳定性风险

### 当前系统状态
- **单一服务器架构**: 所有功能集成在 `stable_start_server.py` 中
- **文件精简**: 从多个重复启动文件精简为1个核心启动文件
- **版本统一**: 使用Python 3.13.7 + NumPy 2.2.6 + OpenCV-Python 4.12.0.88稳定配方
- **维护简化**: 减少版本管理复杂度，提高系统稳定性

## 🔧 配置验证机制
所有启动文件必须包含配方验证代码：
```python
# 配方验证
import sys
import numpy
import cv2

assert sys.version_info[:2] == (3, 13), "必须使用Python 3.13.x版本"
assert numpy.__version__ == "2.2.6", "必须使用NumPy 2.2.6版本"
assert cv2.__version__ == "4.12.0", "必须使用OpenCV-Python 4.12.0版本"
```

## � 代码索引与文档管理

### 现有代码索引文档
基于项目中的文档索引系统，已建立完整的代码文件说明：

#### 核心索引文档
- **文件结构说明.md** - 完整的系统文件结构说明，包含所有核心模块功能描述
- **项目文档集中管理方案.md** - 文档集中管理机制，避免逻辑不一致问题

#### 索引来源
- **发现时间**: 2025年11月25日
- **索引状态**: ✅ 已建立完整的代码文件索引系统
- **维护机制**: 新功能必须更新对应文档索引

### 核心模块索引

#### 主程序文件
- `main.py` - 系统主入口，支持命令行参数运行

#### 配置模块  
- `config/api_keys.py` - API密钥管理
- `config/system_config.py` - 系统运行参数配置

#### 核心功能模块
- `src/data_collector.py` - 数据收集器
- `src/vector_database.py` - 向量数据库管理
- `src/enhanced_data_crawler.py` - 增强数据爬取器
- `src/folder_crawler.py` - 文件夹爬取器（支持DOCX）
- `src/logic_chain_slicer.py` - 逻辑链一级切片器
- `src/event_slicer.py` - 事件二次切片器
- `src/llm_client.py` - LLM客户端基础版
- `src/llm_client_enhanced.py` - 增强LLM客户端

### 索引维护规范
1. **新功能必须更新索引**: 新增模块必须在文件结构说明中记录
2. **文档引用规范**: 技术决策必须基于已有共识文档
3. **版本控制**: 重要文档使用版本号管理变更记录

## �� 未来升级策略
1. **测试先行**: 任何版本升级前必须进行完整测试
2. **回滚机制**: 保持稳定版本的备份
3. **渐进升级**: 逐步验证新版本的兼容性
4. **索引同步**: 系统变更必须同步更新代码索引文档

---
*最后更新: 2025-11-30*
*关联文档: 文件结构说明.md, 项目文档集中管理方案.md*