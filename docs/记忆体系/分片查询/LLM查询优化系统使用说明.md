# LLM查询优化记忆数据库系统使用说明

## 系统概述

本系统是一个支持自然语言查询的优化记忆数据库系统，集成了知识图谱构建、索引生成和智能查询功能。系统能够处理174,208条记忆数据，支持多种查询类型和检索策略。

**开发提示词来源**：用户要求重构记忆数据库，让知识图谱文件支持LLM查询

## 系统架构

### 核心组件

1. **LLMQueryOptimizedKnowledgeGraph** - 支持LLM查询的知识图谱格式
2. **LLMIndexGenerator** - LLM优化的索引生成器
3. **LLMQueryProcessor** - LLM查询处理器
4. **KnowledgeGraphQuerySystem** - 知识图谱查询系统

### 文件结构

```
RAG系统/
├── llm_query_optimized_knowledge_graph.py    # 知识图谱格式设计
├── llm_optimized_index_generator.py          # 索引生成器
├── llm_query_integrated_knowledge_graph.py   # 查询接口集成
├── complete_llm_query_system.py               # 完整系统集成
├── test_llm_query_simple.py                   # 简单测试
└── data/
    ├── rag_memory.db                          # 记忆数据库
    └── llm_optimized_indices.json             # 优化索引文件
```

## 快速开始

### 1. 生成索引

```python
from llm_optimized_index_generator import LLMIndexGenerator

# 生成索引
generator = LLMIndexGenerator("data/rag_memory.db")
indices = generator.generate_indices()

# 保存索引
import json
with open("data/llm_optimized_indices.json", 'w', encoding='utf-8') as f:
    json.dump(indices, f, ensure_ascii=False, indent=2)
```

### 2. 执行查询

```python
from llm_query_integrated_knowledge_graph import KnowledgeGraphQuerySystem

# 创建查询系统
query_system = KnowledgeGraphQuerySystem("data/rag_memory.db", "data/llm_optimized_indices.json")

# 执行查询
result = query_system.query("人工智能是什么？")

# 查看结果
for i, res in enumerate(result['results'][:5], 1):
    print(f"{i}. {res['topic']} - {res['content_preview']}")
```

### 3. 完整系统测试

```bash
python complete_llm_query_system.py
```

## 功能特性

### 查询类型支持

系统支持以下查询类型：
- **事实性查询**："什么是人工智能？"
- **分析性查询**："分析深度学习的优势"
- **比较性查询**："比较机器学习和深度学习"
- **探索性查询**："有哪些关于自然语言处理的内容？"

### 检索策略

根据查询类型自动选择最优检索策略：
- **语义索引**：基于关键词匹配
- **时间索引**：按时间维度检索
- **主题索引**：按主题分类检索
- **重要性索引**：基于内容重要性排序
- **关系索引**：利用记忆关联关系

### 性能指标

- **记忆总数**：174,208条
- **索引类型**：5种（语义、时间、主题、重要性、关系）
- **查询响应时间**：< 0.01秒
- **关键词映射**：208,897个关键词

## API参考

### KnowledgeGraphQuerySystem类

#### 方法

**`query(query_text: str) -> Dict`**
- 执行自然语言查询
- 返回包含查询分析、检索策略和结果的字典

**`get_system_stats() -> Dict`**
- 获取系统统计信息
- 返回记忆总数、索引类型等统计信息

#### 示例

```python
# 初始化系统
system = KnowledgeGraphQuerySystem("data/rag_memory.db", "data/llm_optimized_indices.json")

# 执行查询
result = system.query("人工智能的发展历程")

# 获取统计信息
stats = system.get_system_stats()
print(f"记忆总数: {stats['total_memories']}")
```

### LLMQueryProcessor类

#### 方法

**`process_query(query: str) -> Dict`**
- 处理查询并返回分析结果
- 包含查询类型识别、意图分析、关键词提取等功能

#### 示例

```python
from llm_query_integrated_knowledge_graph import LLMQueryProcessor

processor = LLMQueryProcessor("data/llm_optimized_indices.json")
analysis = processor.process_query("比较机器学习和深度学习")

print(f"查询类型: {analysis['query_analysis']['query_type']}")
print(f"查询意图: {analysis['query_analysis']['intent']}")
```

## 高级用法

### 自定义检索策略

```python
# 获取查询分析
query_analysis = processor.process_query("你的查询")

# 自定义检索策略
custom_strategy = {
    'primary_index': 'semantic',
    'secondary_index': 'importance', 
    'ranking_method': 'relevance_first'
}
```

### 扩展查询类型

系统支持扩展新的查询类型识别规则：

```python
def _classify_query_type(self, query: str) -> str:
    # 添加自定义识别规则
    if "你的自定义模式" in query:
        return "custom_type"
    return super()._classify_query_type(query)
```

## 故障排除

### 常见问题

1. **索引文件不存在**
   ```bash
   python llm_optimized_index_generator.py
   ```

2. **数据库连接失败**
   - 检查`data/rag_memory.db`文件是否存在
   - 确认数据库路径正确

3. **查询返回空结果**
   - 检查查询关键词是否在索引中
   - 尝试更具体的查询

### 性能优化

- 定期重新生成索引以包含新记忆
- 使用更具体的关键词提高检索精度
- 根据查询复杂度调整检索策略

## 技术细节

### 索引结构

索引文件采用JSON格式，包含：
- **metadata**：生成时间、记忆总数等元数据
- **semantic_index**：关键词到记忆的映射
- **temporal_index**：时间维度索引
- **topical_index**：主题分类索引
- **importance_index**：重要性分级索引
- **relational_index**：记忆关联关系索引

### 查询处理流程

1. **查询分析**：识别查询类型、意图、关键词
2. **策略选择**：根据查询类型选择最优检索策略
3. **多维度检索**：从不同索引中检索相关记忆
4. **结果排序**：基于相关性、重要性等因素排序
5. **结果丰富**：获取完整记忆内容并返回

## 更新日志

### v1.0 (当前版本)
- 支持自然语言查询处理
- 集成5种索引类型
- 处理174,208条记忆数据
- 查询响应时间<0.01秒

## 联系方式

如有问题或建议，请参考项目文档或联系开发团队。

---

**注意**：本系统专为支持LLM查询的记忆数据库优化设计，持续改进中。