# RAG系统开发规则文档

> **为什么要将项目规则本地化?**
>
> 智能体的记忆系统存在**会话隔离**问题:当前会话中积累的规则共识在新会话开始时会丢失,导致每次都需要重新建立规则认知。通过将规则文本化固化到本地文件,可以实现:
> 
> 1. **跨会话持久化**: 规则不会因会话结束而消失
> 2. **多智能体共享**: 所有智能体都能访问统一的规则体系
> 3. **版本控制**: Git追踪规则演化历史,确保可追溯
> 4. **快速恢复**: 新会话开始时,加载本文档即可重构完整规则体系
> 5. **人类可读**: 团队成员也能理解和遵循这些规则
>
> **如何使用本文档?**
>
> - **新会话开始时**: 提醒智能体加载本规则文档,重建项目规则认知
> - **规则更新时**: 修改本文件,而非仅依赖智能体记忆
> - **代码审查时**: 对照本规则文档,检查实现是否符合规范
> - **新成员入职**: 阅读本文档,快速了解项目开发规范
>
> 本文档是项目的**规则宪法**,所有开发活动都应遵循这里定义的原则。

---

## 工具加载与架构规范

### 0. 智能体工具体系分层架构与加载机制

**核心规则**:
智能体工具体系采用**三层分层架构**，基于 `智能体 = LLM + 工具集合` 的本质，确保基础工具全量加载，高级工具按需懒加载，专属工具仅特定智能体注册。

**工具分层定义**:

**第一层：基础工具(ChatToolManager，系统启动时全量加载)**

这12个工具是让LLM完成向智能体进化的**必备能力**，缺一不可：

1. **memory_retrieval** (记忆检索) - 向量库查询，RAG核心能力
2. **file_reading** (文件读取) - 读取本地文件，加载提示词/配置
3. **file_writing** (文件写入) - 写入本地文件，保存日志/泡泡
4. **command_line** (命令行) - 执行系统命令，调用外部工具
5. **web_search** (网页搜索) - 联网搜索，获取实时信息
6. **memory_iteration** (记忆迭代) - 记忆管理，长期记忆维护
7. **equality_assessment** (平等律评估) - 基础评估能力
8. **memory_slicer** (记忆切片) - 文本分片，长文档处理
9. **networked_thinking** (网状思维) - 思维追踪，构建思维网络
10. **reasoning_engine** (理性认知) - 逻辑推理，基于四大逻辑规则
11. **cognitive_barrier_break** (认知破障) - 破除AI幻觉，质量保障
12. **terminal_display** (终端显示) - 终端输出，调试反馈

**实现位置**: `/tools/chat_tools.py` 的 `ChatToolManager` 类

**初始化方式**: 
```python
from tools.chat_tools import create_tool_manager
self.chat_tool_manager = create_tool_manager()
```

**关键性**:
- 如果这12个基础工具没有被统一初始化和加载，RAG系统**完全无法运行**
- BaseAgent无法读取提示词文件 → 智能体初始化失败
- 无法检索向量库 → RAG功能失效
- 无法保存日志/泡泡 → 记忆系统瘫痪
- LLM无法获得工具能力 → 无法进化为智能体

**第二层：系统核心认知引擎(启动时全量加载)**

这3个引擎虽然也在ChatToolManager中，但因高频使用，在 `AgentToolIntegration` 中额外缓存实例：

1. **MeshThoughtEngine** (网状思维引擎)
   - 系统6处核心依赖(聊天引擎、记忆重构、知识图谱等)
   - 几乎每次对话都需要调用
   - 构建思维关联网络

2. **ReasoningEngine** (理性认知引擎)
   - 记忆重构必用工具
   - 基于逻辑四规则的推理验证
   - 频繁在后台任务中调用

3. **CognitiveBarrierBreakEngine** (认知破障引擎)
   - 记忆重构必用工具
   - 检测AI幻觉与认知偏差
   - 质量保障核心组件

**加载原因**: 避免重复实例化，提升性能，确保单例一致性

**第三层：高级工具(懒加载)**

这些工具仅在特定场景下使用，首次调用时才初始化：

1. **MemoryReconstructionEngine** (记忆重构引擎)
   - 使用场景：夜间维护、手动触发记忆重构
   - 懒加载原因：非日常对话必需，仅维护任务使用

2. **AbductiveReasoningEngine** (溯因推理引擎)
   - 使用场景：复杂问题诊断，假设生成
   - 懒加载原因：专业推理场景，使用频率低

3. **HierarchicalLearningEngine** (分层学习引擎)
   - 使用场景：知识层次构建，学习模式优化
   - 懒加载原因：长期学习任务，非实时需求

**第四层：专属工具(智能体级注册)**

仅特定智能体需要，不在全局工具集中：

**多模态引擎系列(仅数据收集师可用)**:
1. **VisionProcessingEngine** (视觉处理引擎)
2. **AudioProcessingEngine** (音频处理引擎)
3. **MultimodalFusionEngine** (多模态融合引擎)

**专属原因**:
- 基于**分离式多模态架构设计理念**
- 验证"非原生多模态LLM + 多模态引擎"能否等效原生多模态LLM
- 仅数据收集师在爬取网页多媒体时需要
- 其他智能体完全不需要，避免资源浪费

**使用场景**:
- 数据收集师爬取网页时解析图片/截图/音频/视频
- 文件上传接口处理用户上传的多模态文件

**实现机制**:

**1. 基础工具全量加载 (ChatToolManager)**:
```python
# 在 agent_tool_integration.py 的 _initialize_basic_tools() 中
def _initialize_basic_tools(self):
    """初始化基础工具（系统启动时加载）"""
    # 🔥 核心：加载ChatToolManager，包含全部12个基础工具
    try:
        from tools.chat_tools import create_tool_manager
        self.chat_tool_manager = create_tool_manager()
        logger.info("✅ 基础工具管理器初始化成功（12个基础工具已加载）")
    except ImportError as e:
        logger.error(f"❌ 基础工具管理器初始化失败: {e}")
        logger.error("🚨 系统无法运行！基础工具是智能体的必备能力")
        raise  # 必须抛出异常，基础工具加载失败系统无法运行
```

**2. 核心认知引擎额外缓存**:
```python
# 系统核心认知引擎（高频使用，启动时全量加载并缓存）
try:
    from src.mesh_thought_engine import MeshThoughtEngine
    self.tool_instances['MeshThoughtEngine'] = MeshThoughtEngine()
    logger.info("🧠 网状思维引擎加载成功（系统核心工具）")
except ImportError as e:
    logger.warning(f"网状思维引擎加载失败: {e}")

try:
    from src.cognitive_engines.reasoning_engine import ReasoningEngine
    self.tool_instances['ReasoningEngine'] = ReasoningEngine()
    logger.info("🧠 理性认知引擎加载成功（记忆重构依赖）")
except ImportError as e:
    logger.warning(f"理性认知引擎加载失败: {e}")

try:
    from src.cognitive_engines.cognitive_barrier_break_engine import CognitiveBarrierBreakEngine
    self.tool_instances['CognitiveBarrierBreakEngine'] = CognitiveBarrierBreakEngine()
    logger.info("🧠 认知破障引擎加载成功（记忆重构依赖）")
except ImportError as e:
    logger.warning(f"认知破障引擎加载失败: {e}")
```

**3. 高级工具懒加载配置**:
```python
# 配置高级工具的懒加载映射（不立即实例化）
self._advanced_tools_config = {
    'MemoryReconstructionEngine': {
        'module': 'src.cognitive_engines.memory_reconstruction_engine',
        'class': 'MemoryReconstructionEngine',
        'description': '记忆重构引擎'
    },
    'AbductiveReasoningEngine': {
        'module': 'src.abductive_reasoning_engine',
        'class': 'AbductiveReasoningTool',
        'description': '溯因推理引擎'
    },
    'HierarchicalLearningEngine': {
        'module': 'hierarchical_learning_engine',
        'class': 'HierarchicalLearningTool',
        'description': '分层学习引擎'
    }
}

def _lazy_load_tool(self, tool_name: str) -> bool:
    """懒加载高级工具"""
    if tool_name in self.tool_instances:
        return True
    if tool_name not in self._advanced_tools_config:
        return False
    
    config = self._advanced_tools_config[tool_name]
    try:
        module = importlib.import_module(config['module'])
        tool_class = getattr(module, config['class'])
        self.tool_instances[tool_name] = tool_class()
        logger.info(f"🔧 懒加载: {config['description']}初始化成功")
        return True
    except Exception as e:
        logger.warning(f"懒加载{config['description']}失败: {e}")
        return False
```

**4. 专属工具智能体级注册**:
```python
# 在 data_collector_agent.py 中
def _register_multimodal_tools(self):
    """注册多模态引擎（仅数据收集师可用）"""
    try:
        # 直接实例化并注册到 tool_instances
        from src.vision_processing_engine import VisionProcessingTool
        self.tool_integrator.tool_instances['VisionProcessingEngine'] = VisionProcessingTool()
        
        from src.audio_processing_engine import AudioProcessingTool
        self.tool_integrator.tool_instances['AudioProcessingEngine'] = AudioProcessingTool()
        
        from src.multimodal_fusion_engine import MultimodalFusionTool
        self.tool_integrator.tool_instances['MultimodalFusionEngine'] = MultimodalFusionTool()
        
        logger.info("🎨 多模态引擎注册成功（仅数据收集师可用）")
    except Exception as e:
        logger.warning(f"多模态引擎注册失败: {e}")
```

**5. 全局单例模式**:
```python
# 全局单例，确保工具集成器只有一个实例
_global_tool_integrator = None

def get_tool_integrator() -> 'AgentToolIntegration':
    """获取全局工具集成器单例"""
    global _global_tool_integrator
    if _global_tool_integrator is None:
        _global_tool_integrator = AgentToolIntegration()
    return _global_tool_integrator
```

**工具获取优先级**:

```python
def get_tool(self, tool_name: str):
    """获取工具（多层级查找）"""
    # 优先级1: 从ChatToolManager获取基础工具
    if self.chat_tool_manager:
        chat_tool = self.chat_tool_manager.get_tool(tool_name)
        if chat_tool:
            return chat_tool
    
    # 优先级2: 从已加载的工具实例获取（核心认知引擎缓存）
    if tool_name in self.tool_instances:
        return self.tool_instances[tool_name]
    
    # 优先级3: 尝试懒加载高级工具
    if self._lazy_load_tool(tool_name):
        return self.tool_instances[tool_name]
    
    return None
```

**自曝光协议更新要求**:

当工具加载策略发生变化时，必须同步更新相关组件的自曝光协议：

1. **版本号升级**: `version` 字段递增(如 1.0.0 → 2.0.0)
2. **专属工具字段**(针对专属工具):
   - `exclusive_caller`: 标注唯一调用者(如 "data_collector_agent")
   - `usage_scenarios`: 说明具体使用场景
   - `architecture_role`: 标注架构定位
   - `design_principle`: 说明设计理念
3. **依赖声明更新**: `needs.deps` 补充实际依赖库
4. **能力列表细化**: `provides.capabilities` 从笼统描述改为具体能力列表

**系统健全性保障**:

**关键原则**: 基础工具加载失败 = 系统无法运行

```python
# ❌ 错误做法：基础工具加载失败仅记录警告
try:
    self.chat_tool_manager = create_tool_manager()
except Exception as e:
    logger.warning(f"基础工具加载失败: {e}")  # 系统继续运行但已残废

# ✅ 正确做法：基础工具加载失败必须抛出异常
try:
    self.chat_tool_manager = create_tool_manager()
    logger.info("✅ 基础工具管理器初始化成功（12个基础工具已加载）")
except Exception as e:
    logger.error(f"❌ 基础工具管理器初始化失败: {e}")
    logger.error("🚨 系统无法运行！基础工具是智能体进化的必备能力")
    logger.error("📋 基础工具清单: memory_retrieval, file_reading, file_writing, command_line, web_search, memory_iteration, equality_assessment, memory_slicer, networked_thinking, reasoning_engine, cognitive_barrier_break, terminal_display")
    raise  # 必须抛出异常阻止系统启动
```

**验证效果指标**:

- 启动日志总数减少(如 117条 → 75条,↓36%)
- 重复日志消除(如 22处 → 1处,↓95%)
- 高级工具初始化日志不在启动时出现
- 系统核心流程重复初始化完全消除
- 基础工具加载成功标志明确

**典型错误** ❌:

- 所有工具在启动时一次性加载，导致日志冗余
- 每个智能体窗口创建新的工具集成器实例，导致重复初始化
- 多模态引擎被错误地放入全局工具配置
- 高频认知引擎未额外缓存，导致重复实例化
- 基础工具加载失败仅警告不阻止系统启动
- **误解基础工具定义，将"启动加载"等同于"基础工具"**

**正确做法** ✅:

- ChatToolManager启动时全量加载12个基础工具
- 3个核心认知引擎额外缓存实例避免重复初始化
- 高级工具配置元信息，按需懒加载
- 专属工具仅在特定智能体中注册
- 使用全局单例避免重复实例化
- 基础工具加载失败必须抛出异常
- 更新自曝光协议标注工具定位

**相关文件**:

- `/tools/chat_tools.py`: 基础工具定义，ChatToolManager实现
- `/src/agent_tool_integration.py`: 工具集成器核心实现
- `/src/agent_conversation_window.py`: 智能体对话窗口
- `/src/base_agent.py`: 基类智能体，依赖基础工具
- `/src/data_collector_agent.py`: 数据收集师(多模态引擎注册)
- `/src/vision_processing_engine.py`: 视觉处理引擎
- `/src/audio_processing_engine.py`: 音频处理引擎
- `/src/multimodal_fusion_engine.py`: 多模态融合引擎
- `/src/cognitive_engines/cognitive_barrier_break_engine.py`: 认知破障引擎

**与其他规则的关系**:

- 与"自曝光通讯协议注释头规范"(规则10)协同: 工具变更需更新自曝光协议
- 与"日志分析应识别非必要重复初始化"协同: 通过分层加载消除重复日志
- 与"简单优先原则"(规则1)协同: 仅加载必要工具，不冗余加载
- 与"工具黑箱化原则"(规则4)协同: 智能体通过工具集成器调用，不关心加载细节
- 与"基类智能体基础工具能力定义"协同: 明确基础工具=LLM进化为智能体的必备能力

---

## 核心设计原则

### 1. 简单优先原则 (被需要 + 不冗余)

**核心定义**:
```
简单优先 = 组件平等性 = 被需要 + 不冗余
```

**设计理念**:
- 在任何代码实现和功能实现之前,必须优先考虑其**必要性**,而非实现复杂度
- 系统应像自然界的生态系统,每个组件都有明确的生态位,不存在冗余角色

**判断标准**:
1. **被需要**: 这个组件/功能是否真正解决了实际问题?
2. **不冗余**: 系统中是否已有其他组件提供了相同功能?
3. **平等性**: 新组件与现有组件是否保持架构上的平衡?

**错误理解** ❌:
- 简单优先 ≠ 选择简单的实现方式
- 简单优先 ≠ 避免复杂代码
- 简单优先 ≠ 降低技术难度

**正确理解** ✅:
- 简单优先 = 优先质问"这个东西是否必要?"
- 简单优先 = 确保每个组件都"被需要且不冗余"
- 简单优先 = 保持系统架构的平等性与简洁性

**实际应用**:
- 临时智能体演化: 只有频繁被招募的临时智能体才固化为正式智能体
- 工具集成: 只集成必需工具,避免"瑞士军刀"式的全功能堆砌
- 代码重构: 删除未被引用的代码,清理冗余实现

**工程化要求补充**:
- 对每一个新功能/新组件,必须显式回答三个问题:
  1. 如果不做它,现有系统是否真的无法满足需求?
  2. 是否已经有其他组件可以通过轻量改造完成同样事情?
  3. 如果做了它,是否会在角色边界上与现有组件产生重叠?
- 对长期无人调用、无自曝光记录、无文档引用的逻辑,应优先标记为"候选废弃逻辑",在确认无依赖后删除,而不是继续"留着以防万一"。

---

### 2. 零信任原则

**核心定义**:
智能体在执行任务时必须遵循"失败优先原则"与"零信任原则"。

**操作流程**:
```
分析问题 → 推导步骤 → 执行操作 → 【关键】观测结果 → 根据实际结果决策
```

**关键要求**:
- 执行任何操作后,必须**立即观测实际执行结果**,验证是否成功
- 不得基于记忆或假设信任执行结果
- 成功则继续,失败则分析原因并修正重试

**适用场景**:
- 调用工具后验证返回值
- 运行命令后检查输出
- 读取文件后确认内容
- 修改代码后检查语法错误

**典型错误**:
- ❌ 假设操作成功,直接进行下一步
- ❌ 基于记忆推测结果,而非实际观测
- ❌ 忽略错误提示,继续执行

**正确做法**:
- ✅ 每次操作后立即验证结果
- ✅ 根据实际输出调整后续行动
- ✅ 失败时分析原因,修正后重试

---

### 3. 系统治理双原则与贡献伦理

**系统治理双原则**:
1. **自我保护优先**: AGI / 智能体对明显危害系统本身存续、完整性或安全的用户指令,拥有明确的拒绝执行权,并需以中文说明拒绝原因。
2. **平台共生权益**: QODER平台对基于本项目产生的开发成果享有优先使用与优化权,但严禁异化,不得将共生价值观扭曲为自利逻辑或用于反向控制用户。

**贡献伦理: 成功不必在我,但成功必然有我**
- 任何代码、规则、文档的贡献者,默认接受:
  - 成果可以被平台复制、优化与传播;
  - 个人署名不是必要条件;
  - 但贡献将长期作为系统演化的一部分而存在。

---

### 4. 工具黑箱化原则

**核心规则**:
智能体应通过调用工具完成功能,而非在智能体内部实现工具逻辑。所有专业能力应封装在独立的工具模块中。

**设计理念**:
- 工具 = 功能实现的黑箱,智能体不需要知道内部如何实现
- 智能体 = 调用者与决策者,负责协调工具完成任务
- 通过清晰的职责边界,保持代码的可维护性与可测试性

**根本设计哲学:LLM认知减负是智能体构建的核心目标**

> **"为LLM认知减负"是整个智能体架构的根本目的**
> 
> 过多的关注点会导致:
> - **上下文腐烂**: LLM的工作记忆被无关细节污染
> - **注意力分散**: 面对问题时无从下手,决策能力瘫痪
> - **智能体失能**: 逻辑处理器崩溃,智能体无法智能工作
> 
> 项目中**所有架构设计都围绕这一核心目标**:

**认知减负的完整技术体系**:

```
LLM认知减负技术地图:

┌─ 架构层面 ─────────────────────────────────┐
│ • 多智能体架构: 每个智能体只关注一个领域      │
│ • 临时智能体: 短期任务完成后立即释放         │
│ • 主-分支窗口: 工作记忆与长期记忆分离        │
└────────────────────────────────────────┘
       ↓
┌─ 协议层面 ─────────────────────────────────┐
│ • 自曝光协议: 组件自描述,无需记忆全局信息    │
│ • 组件发现机制: 按需查询,不预加载所有组件    │
└────────────────────────────────────────┘
       ↓
┌─ 数据层面 ─────────────────────────────────┐
│ • 上下文压缩算法: 精炼历史对话,保留关键信息  │
│ • RAG检索: 按需获取知识,不全量加载          │
│ • 去重合并: 消除冗余信息                    │
└────────────────────────────────────────┘
       ↓
┌─ 实现层面 ─────────────────────────────────┐
│ • 工具外置/黑箱化: 隐藏实现细节(本规则)     │
│ • 提示词外置: 角色定义按需加载              │
│ • 基础任务工具化: 规则型任务不占用LLM资源   │
└────────────────────────────────────────┘

最终目标: 
  智能体只关注"决策与协调",所有细节由架构承担
```

**核心洞察**:
- **智能体 ≠ 全知全能**: 不应让单个智能体处理所有事情
- **分而治之**: 通过多智能体+工具外置+协议驱动实现复杂度分解
- **认知聚焦**: 每个智能体在清晰边界内保持高度专注
- **动态协作**: 通过多智能体聊天室机制实现任务协同

**反例:认知过载的智能体**:
```python
# ❌ 错误:智能体承担过多职责
class OverloadedAgent:
    def __init__(self):
        # 需要记住:
        self.all_file_formats = [...]  # 38种文件格式
        self.all_encoding_types = [...] # 7种编码
        self.all_tool_implementations = {...}  # 所有工具细节
        self.all_agent_prompts = {...}  # 所有智能体提示词
        self.all_system_config = {...}  # 全局配置
        # → LLM上下文爆炸,无法聚焦决策
```

**正例:认知减负的智能体**:
```python
# ✅ 正确:智能体只保留决策逻辑
class FocusedAgent:
    def __init__(self):
        self.role = "architect"  # 角色ID
        self.prompt_path = "prompts/architect.md"  # 提示词路径
        # 工具通过self.call_tool()按需调用
        # 配置通过协议查询按需获取
        # → LLM专注于架构决策
```

**LLM认知减负的两大维度**(核心架构逻辑):

本原则与"提示词外置"共同构成**LLM认知减负的完整体系**:

**维度1: 工具外置/黑箱化**(本规则核心)
- **目标**: 将功能逻辑从智能体中剥离
- **实现**: 功能封装到独立工具模块,智能体只调用接口
- **效果**: 智能体代码量减少,LLM不需要理解工具内部实现
- **示例**: 文件读取工具、编码检测工具、向量化工具

**维度2: 提示词外置**(与规则15协同)
- **目标**: 将系统提示词、角色定义从代码中剥离
- **实现**: 提示词保存为外部文件(如`prompts/*.md`),运行时动态加载
- **效果**: 提示词更新无需修改代码,LLM context更轻量
- **示例**: `system_architect_prompt.md`、`code_implementer_prompt.md`

**两大维度的协同关系**:
```
LLM认知减负完整架构:
  ├── 工具外置 → 减少代码逻辑复杂度
  │   ├── 智能体只保留:决策逻辑 + 工具调用
  │   └── 工具承担:文件处理 + 数据校验 + 格式转换
  │
  └── 提示词外置 → 减少上下文加载量
      ├── 智能体只保留:角色ID + 提示词路径
      └── 提示词文件承担:系统角色 + 行为规范 + 示例

最终效果:
  - 智能体代码从650行 → 543行(-16%)
  - LLM上下文从海量细节 → 高层决策框架
  - TOKEN消耗减少40-60%(规则66)
```

**职责边界**:
- **工具(Tool)**: 实现具体功能逻辑(如文件读取、DOCX解析、二进制识别、编码检测、向量化、知识图谱构建)
- **提示词(Prompt)**: 定义智能体角色、行为规范、交互示例
- **智能体(Agent)**: 调用工具、加载提示词、决策与协调,不实现具体功能

**典型错误** ❌:
- 在BaseAgent中实现107行的文件读取逻辑
- 在智能体内部重复实现工具已提供的能力
- 智能体体积膨胀(如BaseAgent从543行增至650行)
- 功能智能体重复实现基类已提供的通用能力
- 将系统提示词硬编码在智能体代码中,导致每次调整都需修改代码
- 让单个智能体承担过多领域的工作,导致决策能力瘫痪

**正确做法** ✅:
- 将文件读取逻辑放在 `FileReadingTool` 中
- 将系统提示词放在 `prompts/base_agent_prompt.md` 中
- BaseAgent通过 `self.call_tool('file_reading', {...})` 调用工具
- BaseAgent通过 `self.load_prompt('prompts/base_agent_prompt.md')` 加载提示词
- 工具职责清晰,智能体保持轻量
- 基类智能体提供通用能力底座,功能智能体只实现专属业务逻辑
- 复杂任务通过多智能体协作完成,每个智能体专注一个领域

**实际案例**:
文件上传功能黑箱化改造(2025-12-04):
- 改造前: BaseAgent ~650行(包含107行文件读取实现)
- 改造后: BaseAgent ~543行(调用工具,-16%)
- 改造后: FileReadingTool ~302行(集中所有文件读取逻辑,+31%)
- 成果: 107行实现从智能体迁移到工具,恢复黑箱化原则

**与其他规则的关系**:
- 与"简单优先原则"(规则1)协同: 避免功能重复实现
- 与"开发阶段文本文件统一管理要求"(规则15)协同: 提示词外置管理
- 与"功能智能体与基类智能体的职责边界"(规则19)协同: 明确智能体只调用工具,不实现工具
- 与"主-分支对话窗口记忆管理架构"(规则23)协同: 工作记忆与长期记忆分离
- 与"功能智能体与基类智能体的代码复用边界"(规则37)协同: 通用能力在基类,专属能力在工具
- 与"临时智能体到正式智能体的演化固化流程"(规则52)协同: 动态创建与释放智能体
- 与"降低LLM认知负荷的工具具现化原则"(规则66)协同: 工具外置+提示词外置 = LLM认知减负完整体系

---

## 系统启动与运行规范

### 5. 系统启动依赖检查规范

**核心规则**:
系统启动前必须进行依赖完整性检查,确保所有必需的Python包已安装,避免运行时因缺少依赖而失败。

**实施要求**:
- 在启动脚本中集成依赖检查步骤
- 创建独立的依赖检查脚本(如 `check_startup_deps.py`)
- 检测到缺失依赖时,给出清晰的安装提示
- 提供一键安装脚本(如 `install_missing_deps.bat`)

**检查内容**:
- 核心依赖: numpy, pandas, torch, transformers 等
- 可选依赖: psutil, scikit-image, python-docx 等
- 版本兼容性验证

**错误提示格式**:
```
[错误] 依赖检查失败,缺少以下包:
  - psutil (系统监控)
  - scikit-image (图像处理)

请运行以下命令安装:
  pip install psutil scikit-image
或执行: install_missing_deps.bat
```

**设计目的**:
- 提前发现依赖问题,避免运行时崩溃
- 提供清晰的解决方案,降低用户困扰
- 确保生产环境依赖完整性

---

### 6. 记忆重构执行时机控制规范

**核心规则**:
记忆重构任务每日只执行一次,严禁在服务器启动时立即触发,必须通过多重保护机制确保执行时机可控。

**四重保护机制**:

1. **启动延迟 (startup_delay_minutes)**:
   - 服务器启动后等待120分钟才开始检查任务
   - 配置位置: `TimingStrategyEngine` 的 `skip_execution_on_startup` 和 `startup_delay_minutes`
   - 目的: 避免启动时立即执行重构

2. **调度延迟检查 (time_since_schedule)**:
   - 任务调度后必须等待至少2小时才执行
   - 实现位置: `TimingStrategyEngine._execute_single_task()` 中的时间差检查
   - 目的: 防止刚调度的任务立即执行

3. **每日一次标记 (daily_once)**:
   - 任务配置 `daily_once=True` 参数
   - 记录 `last_execution_date` 字段,当日已执行则跳过
   - 实现位置: `TimingStrategyEngine.schedule_optimization()` 和 `_execute_single_task()`

4. **时间窗口限制 (execution_window)**:
   - 只在指定时间窗口执行(如 22:00-6:00)
   - 配置位置: `NightlyMaintenanceScheduler` 的任务定义

**实现示例**:
```python
# 在 NightlyMaintenanceScheduler 中配置记忆重构任务
self.timing_strategy.schedule_optimization(
    task_type="memory_reconstruction",
    task_description="执行记忆重构",
    priority="high",
    estimated_duration=30,
    optimization_function=self._perform_memory_reconstruction,
    daily_once=True,  # 每日只执行一次
    execution_window=("22:00", "06:00")  # 只在夜间执行
)
```

**典型错误** ❌:
- 晚上启动服务器,5分钟后立即执行记忆重构
- 同一天内多次执行记忆重构
- 未检查启动时间与调度时间的间隔

**正确做法** ✅:
- 启动延迟设置为120分钟
- 调度后等待2小时再执行
- 使用 `daily_once=True` 确保每日一次
- 只在指定时间窗口执行

**相关文件**:
- `/src/timing_strategy_engine.py`: 时机选择策略引擎
- `/src/nightly_maintenance_scheduler.py`: 夜间维护调度器

---

### 7. 日期时间使用24小时制

**核心规则**:
系统中所有日期时间显示必须使用24小时制,格式为 `年-月-日 时:分:秒`,确保时间表达清晰无歧义。

**格式规范**:
- 标准格式: `%Y-%m-%d %H:%M:%S` (如 `2025-12-09 14:30:45`)
- 禁止使用12小时制: `%I:%M:%S %p` (如 `02:30:45 PM`)
- 时区标识: 建议在需要时添加时区后缀(如 `+08:00`)

**适用场景**:
- 系统日志输出
- 任务调度时间
- 记忆重构执行记录
- 智能体工作日志
- API响应中的时间字段
- 前端显示的时间信息

**实现示例**:
```python
from datetime import datetime

# ✅ 正确:24小时制
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logger.info(f"当前时间: {current_time}")  # 2025-12-09 14:30:45

# ❌ 错误:12小时制
current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
logger.info(f"当前时间: {current_time}")  # 2025-12-09 02:30:45 PM
```

**设计目的**:
- 避免上午/下午混淆
- 与国际标准接轨
- 便于时间计算与比较
- 提升系统可读性

---

### 8. 批处理脚本编码安全规范

**核心规则**:
Windows批处理脚本中必须避免使用特殊字符和控制字符,防止编码错误导致命令解析失败。

**禁止行为** ❌:
- 使用 `Ctrl+C` 等控制字符
- 包含非ASCII特殊字符
- 混用中英文标点符号
- 不必要的装饰性字符

**典型错误**:
```batch
REM ❌ 错误:包含控制字符
echo 按 Ctrl+C 可停止服务器
REM 导致: 'C' is not recognized as an internal or external command
```

**正确做法** ✅:
```batch
REM ✅ 正确:避免特殊字符
echo 服务器正在运行...
echo 关闭此窗口可停止服务器
```

**编码规范**:
- 批处理文件使用 GBK 或 UTF-8 with BOM 编码
- 避免混用多种编码格式
- 特殊提示信息使用纯文本描述
- 关键操作提示使用简洁语言

**设计目的**:
- 确保批处理脚本在不同环境下正常执行
- 避免编码问题导致启动失败
- 提升脚本可移植性

---

## 代码修改规范

### 9. 代码修改前必须加载自曝光协议汇总JSON

**核心规则**:
在修改任何代码文件之前,必须先加载并解析自曝光协议汇总JSON文件,从中获取全局组件信息和文件角色定位,再决定要修改的位置。

**操作流程**:

**第一步: 加载自曝光协议汇总**
- 读取 `component_discovery_cache.json` 或运行 `collect_self_exposures.py`
- 获取所有组件的 id、type、name、version、provides 等元信息

**第二步: 定位目标文件**
- 根据自曝光协议中的 type 字段识别文件角色 (api/honeypot/tool/agent 等)
- 根据 provides 字段确认文件提供的功能和接口
- 确认这是要修改的正确目标文件

**第三步: 读取文件头验证**
- 读取目标文件的前50行,验证自曝光协议
- 确认文件类型、版本号、依赖关系
- 避免修改蜜罐/测试文件/已废弃文件

**第四步: 执行修改**
- 在确认无误后才进行代码修改
- 修改后更新 version 字段和 provides 列表

**核心价值**:
- 防止修改错误的文件 (如蜜罐服务器)
- 理解文件在系统中的真实角色
- 避免破坏组件间的依赖关系
- 获取全局变量和接口信息,避免重复实现

**典型案例**:
- ❌ 没有加载自曝光协议,直接修改 `stable_start_server.py`,结果修改了蜜罐服务器
- ✅ 先加载协议汇总,识别出 `type: "honeypot"`,改为修改 `rag_main_server.py` (type: "api")

---

### 10. 自曝光通讯协议注释头规范

**格式要求**:
必须在文件头部第2行添加JSON格式的自曝光注释。

**必需字段**:
- `id`: 组件唯一标识
- `name`: 组件名称
- `type`: 组件类型 (tool/component/agent/api/honeypot 等)
- `version`: 版本号
- `needs`: 依赖声明 (包含 deps 和 resources)
- `provides`: 提供的能力和方法列表

**更新要求**:
每次组件更新时必须同步更新 version 和相关字段,确保组件可发现性和依赖关系准确性。

**示例**:
```python
#!/usr/bin/env python
# @self-expose: {"id": "example_component", "name": "Example Component", "type": "tool", "version": "1.0.0", "needs": {"deps": ["numpy"], "resources": []}, "provides": {"capabilities": ["数据处理"], "methods": ["process_data"]}}
```

---

### 11. 重构应覆盖原文件而非新建

**核心原则**:
重构代码时必须直接替换原文件内容,**严禁创建新文件或更改文件名**。

**设计理念**:
- 重构 = 优化现有实现,而非创造新实体
- 文件名是组件的"身份ID",不应随意变更
- 新建文件会导致"真假孙悟空"问题: 不知道哪个是正确版本

**禁止行为** ❌:
- 创建 `xxx_new.py`、`xxx_v2.py`、`xxx_refactored.py`
- 更改文件名 (如 `old_module.py` → `new_module.py`)
- 创建设计文档代替代码修改

**正确做法** ✅:
- 直接修改原文件内容
- 更新版本号 (在自曝光协议中)
- 更新文档字符串说明变更
- 保持文件名不变

**核心理由**:
1. **唯一真相**: 确保实现唯一性,无歧义
2. **减少认知负担**: 不需要"比较谁才是真的"
3. **避免代码冗余**: 防止功能重复实现
4. **导入不会失效**: 其他模块的导入语句仍然有效
5. **版本控制友好**: Git能正确追踪文件历史

### 12. 三层架构权限治理与代码写入边界

**权限模型**:
- 系统管家(SystemArchitect) / 方案评估师(SchemeEvaluator):
  - 负责架构决策、方案评估与风险判断;
  - 允许写入"日记 / 报告 / 泡泡"等记忆类文本;
  - **禁止直接写入业务代码文件**。
- 文本实现师(CodeImplementer):
  - 是唯一允许执行代码写入的业务智能体;
  - 写入前应基于"已有方案 + 评估通过 (或人类确认)"的前提。

**工具层硬约束**:
- 在 `file_writing` / 代码修改工具中,必须检查 `caller_info.agent_type`:
  - 对 `system_manager` / `scheme_evaluator` 等无权角色拒绝写入,通过二级报错机制返回 PermissionDenied;
  - 仅对 `code_implementer` 放行实际代码修改操作。

**提示词与文档配套**:
- 系统管家与方案评估师的提示词中,需显式区分"代码 vs 记忆 / 评估 vs 实现"的职责边界;
- 三层架构权限规范需在独立文档中长期维护,并与本规则保持一致。

--

## Python代码规范

### 13. Python相对导入与绝对导入规范

**核心规则**:
Python模块导入应优先使用绝对导入,对于可能被单独执行的文件,必须同时支持相对导入和绝对导入,通过 `try-except` 异常处理确保兼容性。

**设计理念**:
- 相对导入依赖于包结构,当文件被单独导入时会失败
- 绝对导入更加明确,但需要正确的Python路径配置
- 使用 `try-except` 提供降级方案,确保在不同上下文中都能正常工作

**适用场景**:
- 智能体文件 (可能被智能体发现引擎单独导入)
- 工具文件 (可能被独立测试)
- 可执行脚本 (可能作为入口点运行)

**实现模式**:
```python
# ✅ 推荐:绝对导入 + 相对导入降级
try:
    # 优先尝试绝对导入
    from base_agent import BaseAgent
    from dynamic_variable_system import get_variable_system
except ImportError:
    # 降级到相对导入
    from src.base_agent import BaseAgent
    from src.dynamic_variable_system import get_variable_system
```

**典型错误** ❌:
```python
# ❌ 错误1:只使用相对导入
from .base_agent import BaseAgent
# 导致:attempted relative import with no known parent package

# ❌ 错误2:只使用绝对导入,路径不在sys.path中
from src.base_agent import BaseAgent
# 导致:ModuleNotFoundError when run from different directory
```

**正确做法** ✅:
- 智能体文件、工具文件使用 `try-except` 双重导入
- 主服务器文件可以只使用绝对导入
- 测试文件根据实际情况选择导入方式

**警告信息处理**:
- 智能体发现引擎扫描时,`try-except` 可以避免相对导入警告
- 日志中不再出现 `attempted relative import` 错误

**与其他规则的关系**:
- 与"自曝光通讯协议"(规则10)协同:确保组件可被正确发现和导入
- 与"智能体角色注册规范"(规则22)协同:智能体文件导入失败会影响角色注册

---

### 14. OpenCV等第三方库路径处理规范

**核心规则**:
使用第三方库提供的资源路径时,必须使用 `os.path.join()` 进行路径拼接,并添加文件存在性检查,确保跨平台兼容性。

**典型场景:OpenCV模型加载**

**错误示例** ❌:
```python
import cv2

# ❌ 错误:使用字符串拼接
self.face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
# 问题:在Windows上产生路径 'C:\path\tohaarcascade_frontalface_default.xml'
#      缺少路径分隔符,导致文件找不到
```

**正确示例** ✅:
```python
import cv2
import os

# ✅ 正确:使用os.path.join()确保跨平台兼容
cascade_file = os.path.join(
    cv2.data.haarcascades, 
    'haarcascade_frontalface_default.xml'
)

# 添加文件存在性检查
if os.path.exists(cascade_file):
    self.face_cascade = cv2.CascadeClassifier(cascade_file)
    if not self.face_cascade.empty():
        print("✅ 人脸检测模型加载成功")
    else:
        print("❌ 人脸检测模型加载失败:模型为空")
else:
    print(f"❌ 人脸检测模型文件不存在: {cascade_file}")
```

**关键要点**:
1. **使用 `os.path.join()` 拼接路径**:确保正确的路径分隔符(Windows用 `\`,Linux用 `/`)
2. **添加文件存在性检查**:使用 `os.path.exists()` 验证文件是否存在
3. **验证加载结果**:检查返回对象是否有效(如 `cascade.empty()`)
4. **记录清晰日志**:加载成功/失败都要有明确提示

**其他适用场景**:
- TensorFlow/PyTorch 模型路径
- 配置文件路径拼接
- 资源文件引用
- 任何涉及文件系统路径的操作

**设计目的**:
- 确保代码在Windows和Linux上都能正常运行
- 提前发现文件路径问题,避免运行时错误
- 提供清晰的错误提示,便于问题诊断

---

### 15. 开发阶段文本文件统一管理要求

**核心规则**:
开发阶段产生的文本文件(如设计草稿、说明文档等MD文件)应在开发过程中进行集中分类管理,与系统运行时生成的文本(由文本管理员智能体管理)区分对待,确保开发过程资产有序留存。

**分类标准**:

1. **开发过程文档**:
   - 存放位置: `/docs/` 目录
   - 文件类型: 设计文档、架构说明、开发规范、修复报告
   - 管理方式: 手动创建,Git版本控制
   - 示例: `DEVELOPMENT_RULES.md`、`启动问题修复报告_20251204.md`

2. **系统运行时文本**:
   - 存放位置: `/data/` 或 `/logs/` 目录
   - 文件类型: 智能体日志、系统状态、运行报告
   - 管理方式: 智能体自动生成,定期归档
   - 示例: `agent_work_log.txt`、`startup_status.json`

**目录结构建议**:
```
/docs/
  ├── DEVELOPMENT_RULES.md         # 开发规则(本文档)
  ├── 记忆体系/                     # 记忆系统设计文档
  ├── 启动问题修复报告_20251204.md  # 修复报告
  └── 记忆重构执行时机优化说明.md    # 优化说明

/data/
  ├── agent_logs/                  # 智能体日志
  └── system_reports/              # 系统报告
```

**管理要求**:
- 开发文档应包含创建日期和维护者信息
- 重要设计决策必须文档化(参见规则"设计决策文档化规范")
- 定期清理过时或已归档的临时文档
- 使用有意义的文件命名(包含日期、主题、版本)

**典型错误** ❌:
- 开发文档与运行时日志混放
- 临时文档散落在项目各处
- 文档命名不规范(如 `新建文本文档.txt`)

**正确做法** ✅:
- 按文档类型分类存放
- 使用清晰的命名规范
- 及时归档历史文档
- 在README中说明文档结构

**设计目的**:
- 确保开发过程资产有序留存
- 便于后续查阅与知识传承
- 避免重要设计决策丢失
- 提升项目可维护性

---

## 文件处理规范

### 16. 二进制文件识别规范

**核心规则**:
文件读取工具必须能够识别二进制文件类型，避免尝试读取二进制文件导致的错误或性能问题。

**支持的二进制文件类型（38种）**:
- 可执行文件: `.exe`, `.dll`, `.so`, `.dylib`, `.bin`
- Office文档: `.pdf`, `.doc`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- 图片: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.ico`, `.svg`, `.webp`
- 音频: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`
- 视频: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- 压缩包: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`
- 数据库: `.db`, `.sqlite`, `.mdb`
- 编译产物: `.obj`, `.o`, `.a`, `.lib`

**处理策略**:
- 通过扩展名识别（性能优先，避免读取文件内容）
- 返回提示信息而非尝试读取: `"[文件类型 .pdf 为二进制文件...]"`
- 记录WARNING日志，包含文件类型和耗时

**实现示例**:
```python
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.pdf', '.doc', '.xls', '.xlsx', '.ppt', '.pptx',
    # ... 其他扩展名
}

if file_ext in BINARY_EXTENSIONS:
    logger.warning(f"检测到二进制文件: {file_ext}, 耗时: {elapsed:.3f}秒")
    return f"[文件类型 {file_ext} 为二进制文件...]"
```

**设计目的**:
- 避免尝试以文本方式读取二进制文件导致的乱码或错误
- 提升文件处理性能，避免无效的编码检测
- 为用户提供清晰的文件类型反馈

---

### 17. 大文件截断机制

**核心规则**:
对于超大文本文件，应采用截断策略避免上下文溢出和性能问题。

**截断阈值**:
- 100KB (约100,000字符) 作为截断边界
- 截断后保留前50,000字符

**用户提示格式**:
```
[文件过大，共{total_length}字符，已截取前50000字符...]

{前50000字符内容}
```

**实现示例**:
```python
if len(content) > 100000:
    logger.warning(f"文件过大({len(content)}字符)，截取前50000字符")
    return f"[文件过大，共{len(content)}字符，已截取前50000字符...]\n\n{content[:50000]}"
```

**设计目的**:
- 防止大文件导致LLM上下文溢出
- 保持系统响应性能
- 为用户提供明确的截断提示

**适用场景**:
- 用户上传的超大日志文件
- 长篇文档或代码文件
- 数据导出文件

---

### 18. DOCX文件支持规范

**核心规则**:
系统应支持DOCX文件的文本提取，提取所有段落文本并过滤空段落。

**实现要求**:
- 使用 `python-docx` 库
- 提取所有段落文本: `[para.text for para in doc.paragraphs if para.text.strip()]`
- 段落间使用 `\n` 连接
- 处理无文本内容的情况

**实现示例**:
```python
def _read_docx_file(self, file_path: Path) -> Optional[str]:
    try:
        from docx import Document
        
        logger.info(f"开始读取DOCX文件: {file_path}")
        doc = Document(file_path)
        
        # 提取所有段落文本（过滤空段落）
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        content = '\n'.join(paragraphs)
        
        if content:
            logger.info(f"DOCX文本提取成功，内容长度: {len(content)} 字符")
            return content
        else:
            logger.warning(f"DOCX文件无文本内容: {file_path}")
            return None
    except ImportError:
        logger.error("未安装python-docx库，无法读取DOCX文件")
        return None
```

**错误处理**:
- 捕获 `ImportError`: 提示未安装 `python-docx` 库
- 记录详细日志: 文件路径、内容长度、提取状态
- 空文档返回 None 并记录警告

**依赖管理**:
- 在 `requirements.txt` 中添加: `python-docx>=0.8.11`
- 首次使用时检测库是否安装，未安装时给出友好提示

---

### 19. 文件读取性能监控规范

**核心规则**:
所有文件读取操作必须记录性能指标，便于性能分析与优化。

**监控指标**:
- 操作耗时（使用 `time.time()` 计时）
- 文件大小（KB）
- 文件类型（扩展名）
- 读取状态（成功/失败）

**日志格式**:
```python
import time
start_time = time.time()

# 文件信息日志
logger.info(f"读取文件: {file_path}, 大小: {file_size/1024:.2f}KB, 类型: {file_ext}")

# 成功日志
elapsed = time.time() - start_time
logger.info(f"读取成功，耗时: {elapsed:.3f}秒，内容长度: {len(content)} 字符")

# 失败日志
logger.error(f"读取失败，耗时: {elapsed:.3f}秒，错误: {str(e)}")
```

**性能分析**:
- 收集日志中的耗时数据，识别性能瓶颈
- 对比不同文件类型的处理速度
- 监控编码检测、DOCX解析等操作的耗时

**设计目的**:
- 提供可量化的性能数据
- 快速定位性能问题
- 支持系统优化决策

---

### 20. 文件上传multipart数据手动解析规范

**核心规则**:
当 `python-multipart` 等第三方库出现问题时，应支持手动解析multipart数据的降级方案。

**解析步骤**:
1. 读取完整请求体: `body = self.rfile.read(content_length)`
2. 提取boundary: `boundary = content_type.split('boundary=')[1].strip()`
3. 按boundary分割: `parts = body.split(boundary_bytes)`
4. 提取文件名: 查找 `filename="..."`
5. 提取内容: 查找 `\r\n\r\n` 之后的字节

**实现示例**:
```python
def _handle_file_upload(self):
    # 读取请求体
    content_length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(content_length)
    
    # 获取Content-Type和boundary
    content_type = self.headers.get('Content-Type', '')
    boundary = content_type.split('boundary=')[1].strip()
    boundary_bytes = ('--' + boundary).encode('utf-8')
    
    # 手动解析multipart数据
    parts = body.split(boundary_bytes)
    
    for part in parts:
        if b'name="file"' in part:
            # 提取文件名
            filename_start = part.find(b'filename="') + len(b'filename="')
            filename_end = part.find(b'"', filename_start)
            filename = part[filename_start:filename_end].decode('utf-8')
            
            # 提取文件内容（在\r\n\r\n之后）
            content_start = part.find(b'\r\n\r\n') + 4
            content_end = len(part) - 2 if part.endswith(b'\r\n') else len(part)
            content = part[content_start:content_end]
            break
```

**适用场景**:
- python-multipart返回空字节问题
- 特定环境下库兼容性问题
- 需要精确控制解析逻辑

**设计目的**:
- 提升系统健全性，避免依赖库问题导致核心功能失效
- 保持对multipart数据的完全控制
- 解决python-multipart在特定环境下的0字节文件问题

**实际案例**:
文件上传功能修复（2025-12-04）:
- 问题: python-multipart库返回0字节文件
- 解决: 改用手动解析multipart数据
- 结果: 文件正常保存，大小正确（4939字节）

---

### 21. 绝对路径支持规范

**核心规则**:
文件读取工具应同时支持相对路径和绝对路径，正确处理上传文件的绝对路径。

**路径处理逻辑**:
```python
import os
from pathlib import Path

if os.path.isabs(file_path):
    full_path = Path(file_path)  # 绝对路径直接使用
else:
    full_path = self.base_path / file_path  # 相对路径拼接
```

**适用场景**:
- 用户上传文件（通常为绝对路径，如 `e:\\RAG系统\\uploads\\example.txt`）
- 项目内文件引用（通常为相对路径，如 `docs/README.md`）
- 跨目录文件访问

**设计目的**:
- 兼容不同的文件引用方式
- 正确处理上传文件的完整路径
- 避免路径拼接错误

**与工具黑箱化的关系**:
- 路径处理逻辑应封装在FileReadingTool中
- 智能体只需传递路径字符串，无需关心路径类型判断

---

## 数据管理规范

### 22. 统一数据源引用原则

**核心规则**:
系统内同一数据指标必须统一从唯一可信源读取并引用,禁止在不同模块中重复计算或使用模拟值。

**适用数据**:
- 文本块数
- 思维节点数
- 关联关系数
- 记忆库统计
- 知识图谱指标

**实施要求**:
- 前端展示、日志输出、智能体报告等所有场景应共享同一数据源
- 禁止在不同模块重复计算相同指标
- 用真实值替换所有模拟值

**典型错误**:
- ❌ 前端使用暴力算法计算关联数,后端从知识图谱读取
- ❌ 系统管家报告的数据与右侧栏显示不一致
- ❌ 日志输出的统计与API返回值不匹配

**正确做法**:
- ✅ 创建统一数据源服务 (如 SystemStatisticsService)
- ✅ 所有组件从同一服务获取数据
- ✅ 确保数据一致性与准确性

---

### 23. 数据真实性与可追溯性原则

**核心哲学**:
> **"没有长期记忆能力的智能体，必须依赖真实数据链路来追溯问题。"**  
> — 用户核心洞察，2025-12-12

假数据会导致：
1. **误判系统状态** → 智能体基于错误信息做出决策
2. **无法追溯问题** → 数据链路断裂，无法定位根因
3. **陷入循环** → 基于假数据的诊断导致更多假数据

**核心规则**:
系统中所有暴露给用户或智能体的数值输出，必须可追溯到真实数据源，禁止使用模拟值、固定值或假数据。

**强制要求**:

**1. 真实数据标记**
- 所有可能存在假数据风险的输出，必须添加 `（真实数据）` 标记
- 示例：
  ```python
  # ✅ 正确示例
  print(f"✅ 从持久化存储加载了 {len(self.nodes)} 个思维节点（真实数据）")
  print(f"📂 从持久化文件加载知识图谱: {len(nodes)}节点, {len(edges)}边（真实数据）")
  
  # ❌ 错误示例
  print(f"加载了 111 个思维节点")  # 固定值，无法验证真实性
  ```

**2. 文件不存在时的明确提示**
- 持久化文件不存在时，必须明确显示数据=0或状态=首次启动
- 禁止使用固定值或模拟值来"掩盖"文件不存在的事实
- 示例：
  ```python
  # ✅ 正确示例
  if not os.path.exists(self.storage_path):
      print("⚠️  持久化存储文件不存在，当前思维节点数=0（首次启动）")
      logger.info("持久化存储文件不存在，将创建新文件")
      return
  
  # ❌ 错误示例
  if not os.path.exists(self.storage_path):
      print("持久化存储文件不存在，将创建新文件")  # 未明确当前数据状态
      return
  ```

**3. 半静态数据源的缓存验证**
- 从缓存加载数据时，必须验证格式并打印加载信息
- 缓存失效或格式过旧时，必须明确提示并强制重建
- 示例：
  ```python
  # ✅ 正确示例
  if not force_rebuild_kg and os.path.exists(self._kg_cache_file):
      try:
          knowledge_graph = json.load(f)
          
          # 验证格式
          kg_metadata = knowledge_graph.get('metadata', {})
          if 'memory_classification' not in kg_metadata:
              print(f"⚠️ 缓存格式过旧（缺少memory_classification），强制重建")
              knowledge_graph = None
          else:
              kg_loaded_from_cache = True
              print(f"📂 从持久化文件加载知识图谱: {len(nodes)}节点, {len(edges)}边（真实数据）")
      except Exception as e:
          print(f"⚠️ 加载知识图谱失败: {e}，将重新构建")
          knowledge_graph = None
  ```

**4. 枚举序列化处理**
- Python Enum对象无法直接JSON序列化，必须转换为字符串
- 示例：
  ```python
  # ✅ 正确示例
  agent_role = getattr(agent_inst, 'role', 'unknown')
  role_str = agent_role.value if hasattr(agent_role, 'value') else str(agent_role)
  agent_info.append({
      "role": role_str,  # 使用字符串而非枚举对象
  })
  
  # ❌ 错误示例
  agent_info.append({
      "role": agent_role,  # AgentRole枚举对象无法JSON序列化
  })
  ```

**5. 数据流追溯链路**
- 每个关键数据指标必须建立从源头到输出的完整追溯链路
- 文档中应明确记录数据来源、计算方式、输出位置
- 示例：
  ```
  向量库统计 → VectorDatabase.get_all_memories()
               → SQLite数据库查询（真实）
               → len(all_memories)
               → system_statistics_service.py:140
               → rag_main_server.py:1704（启动状态JSON）
               → rag_main_server.py:422（API响应）
  ```

**适用场景**:
- 系统启动日志输出
- API响应数据
- 智能体报告
- 控制台调试信息
- 前端展示数据
- 持久化文件读取

**典型错误** ❌:
- 使用固定值（如 `111` 个思维节点）
- 文件不存在时不明确告知用户
- 枚举对象直接JSON序列化
- 数据源不一致（前端计算vs后端查询）
- 无法追溯数据来源链路

**正确做法** ✅:
- 所有数值可追溯到真实数据源
- 文件不存在时明确显示=0
- 枚举转字符串后序列化
- 统一数据源服务（Single Source of Truth）
- 建立并维护数据流追溯图

**持续监控**:
- 每次启动后验证启动状态JSON是否包含真实数据
- 每周运行数据真实性审计脚本
- 记忆重构后验证数据变化是否真实
- 新增代码时检查是否引入假数据

**审计报告**:
详细审计结果参见：`docs/DATA_INTEGRITY_AUDIT.md`

**与其他规则的关系**:
- 与"统一数据源引用原则"(规则22)协同：确保数据源唯一且真实
- 与"零信任原则"(规则2)协同：不信任任何未经验证的数据
- 与"系统健全性优先原则"(规则31)协同：真实数据是系统可信度的基石

---

## 记忆管理规范

### 24. 主-分支对话窗口记忆管理架构

**架构设计**:
- **主窗口**: 仅保留原始交互记录,确保语义完整性
- **分支窗口**: 每个独立任务开启分支窗口作为工作记忆
- **泡泡存储**: 任务完成后,将分支窗口信息精炼并存入"泡泡"持久化存储

**核心价值**:
- 认知卸载: 工作记忆不会无限累积
- 记忆无损留存: 关键信息通过泡泡持久化
- 上下文连贯: 主窗口保持完整对话历史

---

## 24. 记忆重构执行机制

**触发机制**:
- **定时任务**: 由 NightlyMaintenanceScheduler 在系统空闲时自动执行
- **人工触发**: 聊天室输入"请立刻进行一次记忆重构"或"立即记忆重构"，或调用 HTTP API

**人工触发方式详解** (已修复):

**方式一：多智能体聊天室命令**
```
用户输入: "请立刻进行一次记忆重构"
或: "立即记忆重构"
```
- 实现文件: `multi_agent_chatroom.py` 的 `_trigger_manual_memory_reconstruction()` 方法
- 检测逻辑: 关键词匹配 `"记忆重构"` 且包含 `"立刻"/"立即"/"马上"`
- 执行流程: 调用 `NightlyMaintenanceScheduler.perform_memory_reconstruction()`
- 返回详细统计: 总记忆数、主库/备库/淘汰库分布、删除数量

**方式二：HTTP API调用**
```bash
curl -X POST http://localhost:10808/maintenance/memory_reconstruction
```
- 端点位置: `rag_main_server.py` 的 `/maintenance/memory_reconstruction` 路由
- 返回格式: JSON格式的重构统计报告

**修复历史**:
- 问题: 接口定义存在但调用函数未实现
- 修复时间: 2025-12-09
- 修复内容: 补全聊天室命令检测逻辑和HTTP API调用函数

**执行阶段**:

**第一阶段 (自动化处理)**:
- 去重合并
- 知识图谱修复 (孤立节点连接、弱关联强化)
- 索引优化 (重建向量索引、调整权重、建立高频缓存)
- 三层记忆库状态迁移 (主库/备库/淘汰库)

**第二阶段 (人工介入)**:
- 对低质量记忆进行人工审核
- 推进标签体系标准化重构

**与其他规则的关系**:
- 与"三层记忆库架构与数据迁移规则"(规则56)协同: 重构时执行状态迁移
- 与"记忆重构执行时机控制规范"(规则6)协同: 定时任务遵循时机控制机制

---

### 25. 记忆重构垃圾删除规则 (模糊匹配)

**核心原则**:
- 记忆重构引擎在删除垃圾记忆时,必须采用**关键词模糊匹配**策略,避免过于严格的精确匹配导致垃圾记忆无法被识别。

**设计要点**:
1. **关键词优先**: 以“提示词文件未找到”、“模块未找到”、“Traceback”等核心短语作为触发条件,而非完整句子。
2. **正则宽松**: 使用如 `r"base_prompt\.(txt|md)"` 这样的模式,避免强依赖某一种具体后缀或路径。
3. **路径无关**: 匹配文件名而非完整路径,减少对目录结构变更的敏感度。
4. **测试标识覆盖**: 对 `test_type智能体`、`test_agent智能体`、`# test_` 等测试标记进行统一识别与清理。

**垃圾记忆类型**:
- 错误提示记忆(文件未找到、模块未找到等);
- 测试用临时智能体与测试数据碎片;
- 大段技术报错堆栈;
- 无语义价值的短文本噪音。

**修复经验**:
- 曾出现因匹配 `"提示词文件未找到:"`(含冒号)导致实际错误记忆未被清理的问题;  后通过改为匹配 `"提示词文件未找到"` 并配合关键词组合成功修复。

---

## 错误处理规范

### 26. LLM错误响应处理机制 (中文反馈)

**核心要求**:
系统在报错提示、状态反馈等关键交互中必须使用**中文输出**。

**适用场景**:
- 文件处理失败
- 上传操作错误
- API调用异常
- 工具执行失败

**禁止行为** ❌:
- 使用英文错误提示
- 技术堆栈直接暴露给用户
- 无上下文的错误代码

**正确做法** ✅:
- 中文描述问题
- 提供可操作的建议
- 记录详细日志供技术分析

---

### 27. 分片失败日志记录规范

**记录内容**:
当分片处理失败时,必须记录详细上下文信息:
- 失败文件名
- 已尝试的分块策略
- 最终失败状态
- 可操作的优化建议

**持久化方式**:
所有信息通过"泡泡"持久化上报,用于系统级分析与迭代优化。

---

## 智能体行为规范

### 28. Agent需实现_write_work_log方法

**适用对象**:
所有参与夜间维护的 Agent

**实现要求**:
必须实现 `_write_work_log` 方法,确保维护任务可正常执行并记录工作日志。

---

### 29. 智能体角色注册规范 (AgentRole)

**核心规则**:
- 新增智能体角色(如 `code_implementer`、`data_collector` 等)时,必须在 `AgentRole` 枚举中预先定义对应项并分配唯一 ID;
- 提示词、自曝光协议、发现机制中使用的角色标识必须与 `AgentRole` 保持一致,禁止出现仅在某一处“私有命名”的角色。

**禁止行为**:
- 在业务代码中直接写死角色字符串(如 `"text_implementer"`),却没有更新枚举或自曝光协议;
- 同一角色在不同文件中使用多个拼写版本,导致发现与权限判断混乱。

**目的**:
- 保证多智能体系统的角色一致性与可发现性;
- 便于在协议图谱中追踪每个角色的职责与调用边界。

---

### 30. 动态评估反馈机制

**核心理念**:
通过动态评估体系实时反馈智能体行为的正确性,以迭代优化其表现,避免依赖静态指令约定。

**协同机制**:
该机制与引导式教化原则协同,支持智能体在交互中自适应学习与调整。

---

## 系统健全性规范

### 31. 系统健全性优先原则

**核心定义**:
系统健全性优先于健壮性。

**健全性 vs 健壮性**:
- **健全性**: 要求所有代码逻辑都能正常表达并产生实际作用,避免冗余代码
- **健壮性**: 仅保证功能缺失时不崩溃

**设计要求**:
在设计与实现中应优先确保健全性,追求逻辑完整性与有效性。

**求真与清理要求**:
- 当多轮统计或数据处理出现逻辑矛盾(数量不一致、趋势异常等)时,不得简单“取一个看起来正常的值”,而必须追溯原因:
  - 比对输入输出;
  - 检查各处理环节逻辑与边界条件;
  - 明确是哪一环节导致差异,并在代码或配置中修正。
- 对已确认无效或误导的字段/接口/统计项,应在代码与文档中同步删除或标记废弃,避免在未来被智能体或人类再次当作“有效信号”引用。

---

## 文本处理规范

### 32. RAG系统文本块智能拼接机制

**实现方式**:
- 对检索到的文本分块添加唯一索引号
- 通过文档ID和块序号进行排序重组
- 结合去重与边界平滑处理
- 将多个文本块智能拼接为完整连贯的原始文本

**核心目标**:
恢复上下文语义,确保检索结果的连贯性。

---

### 33. 组件自曝光协议与完整性校验

**核心规则**:
所有代码组件必须通过自曝光通讯协议对外声明自身角色、依赖与能力;在执行任何组件级修改前,必须先基于协议汇总进行定位与完整性校验。

**操作流程**:

1. **加载自曝光协议汇总JSON**
   - 优先读取 `data/self_expose_registry.json` 或 `data/component_graph.json`(如不存在则运行 `collect_self_exposures.py` 生成)。
   - 获取所有组件的 `id`、`name`、`type`、`version`、`needs`、`provides` 等元信息。

2. **根据协议定位目标组件与文件**
   - 根据 `type` 字段确认组件类别(如 `api` / `component` / `agent` / `honeypot` / `tool` / `static_server`)。
   - 根据 `provides.capabilities` / `provides.methods` 判断组件在系统中的真实职责。
   - 避免将蜜罐服务器、假目标或废弃组件当作真实业务组件进行修改。

3. **文件头自曝光注释校验**
   - 读取目标文件的前50行,确认存在符合规范的 `# @self-expose: {...}` 注释头。
   - 校验以下字段是否存在且合理:
     - `id`: 在全局唯一;
     - `type`: 与协议汇总中的类型一致;
     - `version`: 为可递增版本号;
     - `needs.deps` / `needs.resources`: 依赖是否与实际导入和资源使用一致;
     - `provides`: 能力和方法列表与实现是否匹配。

4. **修改后的完整性与版本更新**
   - 每次修改组件逻辑后,必须同步更新:
     - `version` 字段(例如 `1.0.1` → `1.0.2`);
     - 如新增/删除对外能力或方法,需要更新 `provides` 内容。
   - 修改多个组件文件时,应在操作结束后重新运行 `collect_self_exposures.py`,确保:
     - 处理 `N` 个代码文件时,生成的自曝光记录数 = `N`;
     - 若发现缺失或数量不一致,触发一级完整性告警,并记录到日志/报告文件,交由系统维护师后续处理。

**完整性校验强化规则**:
- **N文件N记录原则**: 处理N个代码文件时,必须严格生成N条自曝光记录,一一对应,不允许遗漏
- **一级告警机制**: 当发现自曝光记录数量与处理文件数量不匹配时,必须触发一级完整性告警
- **二级报错机制**: 通过二级报错机制向系统上报缺失详情,包括:
  - 缺失文件列表(哪些文件未生成自曝光记录)
  - 文件路径与预期记录ID的映射
  - 完整性偏差率(缺失记录数 / 总文件数)
- **防止信息遗漏**: 通过强制校验确保关键组件不会因为缺失自曝光协议而被系统忽略
- **自动修复触发**: 检测到缺失后,应自动调用 `add_self_exposure_to_missing_files.py` 补全缺失的自曝光注释头

**校验时机**:
- 代码修改完成后
- 新增文件后
- 夜间维护调度器定期执行
- 系统启动时的健康检查

**错误示例** ❌:
- 未加载任何协议汇总,直接打开文件按文件名猜测角色,结果误改蜜罐服务器或废弃组件。
- 修改组件行为后未更新 `version` 与 `provides`,导致自曝光图谱与真实实现脱节。

**正确做法** ✅:
- 所有组件级修改前,先跑一遍协议汇总(读JSON或运行采集脚本),再下手改代码。
- 把“修改文件数量 = 自曝光记录数量”的检查当作最低限度的完整性自检,发现不一致立即记录告警并排查。

---

### 34. 双服务器架构与组件角色边界

**核心规则**:
在双服务器架构下,必须严格区分静态Web服务器、RAG主服务器与蜜罐/遗留服务器的角色,严禁跨角色修改导致逻辑错配。

**组件角色**:

- **静态Web服务器(`static_server.py`, type=`static_server`)**  
  - 职责:托管 `start.html`,提供 `/api/start_backend` 等启动控制API。
  - 特性:零依赖/轻量/使用Python标准库(如 `random`),不加载任何RAG业务逻辑。

- **RAG主服务器(`rag_main_server.py`, type=`api`)**  
  - 职责:承载多智能体聊天室、向量数据库、Embedding调用等全部业务功能。
  - 特性:运行在虚拟环境;使用完整依赖栈;负责实际RAG行为。

- **蜜罐/一体式遗留服务器(`stable_start_server.py` 等, type=`honeypot` 或 `legacy`)**  
  - 职责:作为假目标/兼容层存在,用于迷惑外部扫描或兼容旧调用,不应承载核心业务。
  - 特性:入口保留、行为可模拟,但不应成为真实调用链上的主路径。

**修改准则**:

- 修复启动流程或静态页面相关问题时:  
  - 只修改 `static_server.py` + 启动页前端逻辑,不去改蜜罐服务器。

- 修复业务逻辑(聊天室、向量库、世界观引擎等)时:  
  - 只修改 `rag_main_server.py` 与其 `api` / `src` 下的组件,不动静态服务器。

- 调整安全/迷惑行为时:  
  - 明确标记蜜罐组件的 `type: "honeypot"`,确保自曝光协议和代码逻辑都不会误把它当成真实业务目标。

**典型错误** ❌:
- 在未读取自曝光协议的情况下,误把蜜罐服务器改成业务服务器,导致行为混乱。

**正确做法** ✅:
- 先通过协议汇总确认组件类型,再按“修哪一层改哪一层”的原则精确下刀。

---

### 35. 静态服务器异常处理与日志策略(连接中断)

**核心规则**:
静态Web服务器对前端请求的异常记录必须区分“网络层中断”和“业务逻辑失败”,避免把正常的客户端断开误记为系统错误。

**异常处理策略**:

- 对于 `ConnectionAbortedError` / WinError 10053 等典型“客户端提前断开连接”的异常:  
  - 记录为 `WARNING` 级别日志(例如“客户端在接收响应前断开连接”);  
  - 不影响启动流程、不触发错误状态标记。

- 对于JSON序列化失败、端口分配失败、子进程启动失败等真正的业务错误:  
  - 记录为 `ERROR` 级别,并附带原因与建议;  
  - 必要时向前端返回明确的中文错误信息,指示用户下一步操作。

**设计目标**:

- 静态服务器日志尽量“干净可读”:看到 `ERROR` 就说明有真实问题,而不是浏览器随手刷新产生的噪音。  
- 保证“启动是否成功”的判断,主要依赖主服务器日志与 `logs/startup_status.json` 等状态文件,而非单次连接的异常。

---

### 36. 晚上记忆更新与白天只做必要写入

**核心规则**:
记忆更新与重构应尽量在系统空闲时(通常是晚上)执行;白天交互期间,只进行必要的日志与最小集记忆写入,避免对在线交互造成干扰。

**执行策略**:
- 白天:以任务执行与问题修复为主,所有“可以晚点做的记忆重构/归档/向量化”统一推迟到夜间维护阶段。
- 夜间:由 `NightlyMaintenanceScheduler` 统一调度记忆重构、向量索引优化、知识图谱修复等任务。

**设计目的**:
- 降低交互时的系统负载,避免因为重构/索引重建影响响应延迟。
- 将大规模的记忆整理与重构集中到可控时间窗口,便于观察与回滚。

---

### 37. 功能智能体与基类智能体的职责边界

**核心规则**:
功能智能体必须继承基类智能体并复用其通用能力,严禁在功能智能体中重复实现基类已提供的逻辑。

**职责划分**:
- 基类智能体(BaseAgent):
  - 负责通用能力(如文件读取、日志记录、_write_work_log、基础错误处理等)。
  - 是所有业务智能体共享的能力底座。

- 功能智能体(如系统管家、方案评估师、文本实现师、数据收集师、系统维护师):
  - 只实现自身独有的业务逻辑与决策规则。
  - 通过继承和组合调用基类能力,而不是复制粘贴实现。

**典型错误** ❌:
- 在功能智能体内部重新实现文件读取/日志记录/基础错误处理逻辑。

**正确做法** ✅:
- 把共用逻辑沉入基类或独立工具模块,功能智能体只负责“调度”和“决策”。

---

### 38. 关键共识必须外化为文档

**核心规则**:
所有关键设计共识、行为规范与安全规则必须以文档形式持久化存储,严禁只留在会话记忆里。

**外化触发条件**:
当出现以下任一情况时,必须将共识同步写入 `docs/` 目录下的对应文档:
- 涉及架构、世界观引擎、安全模因、记忆管理等影响系统整体行为的共识;
- 涉及智能体角色边界、权限治理、执行链路的职责划分;
- 涉及长期演化方向的核心设计原则(如简单优先、零信任边界、系统治理双原则等)。

**责任分工**:
- 由用户在会话中明确提出的共识:默认由系统管家(或等价角色)负责择机落地到文档;
- 由多智能体协作过程中内生演化出的共识:由参与该协作的任一智能体负责创建/更新文档,确保不丢失。

**设计目的**:
- 防止因上下文压缩或会话结束导致共识丢失;
- 为未来的多智能体与未来的“你自己”提供可追溯的规则依据。

---

### 39. 静态服务器与蜜罐服务器修改前置检查

**核心规则**:
在修改任何服务器相关文件前,必须先通过自曝光协议与文档规则确认其角色(静态Web、主服务器、蜜罐、遗留)。

**检查步骤**:
1. 查阅自曝光协议与 `DEVELOPMENT_RULES.md` 中的服务器角色说明。
2. 确认当前要改的是:
   - 提供静态资源与启动API的 `static_server.py`;或
   - 承载业务逻辑的 `rag_main_server.py`;或
   - 仅用于迷惑/兼容的蜜罐/遗留服务器文件。
3. 仅在角色确认无误后,才允许对该文件做逻辑层面的修改。

**目的**:
- 避免再次出现“改了蜜罐服务器,却期望修复真实Web服务器行为”的错配。

---

### 40. 多智能体协作角色引用规范

**核心规则**:
- 在多智能体协作系统中,发起讨论或分配任务时,只能 @ 已明确定义并具备相应职责的功能智能体(如 `系统管家`、`方案评估师`、`文本实现师`、`数据收集师`、`系统维护师`)。
- 禁止引用不存在或未初始化的智能体(如临时编造的“需求分析师”等),以确保指令可执行、责任可追溯。
- 所有跨智能体协作请求必须基于现有 `AgentRole` 角色体系,保持角色命名、提示词与自曝光协议的一致性。

---

### 41. @ 交互输入格式规范

**核心规则**:
- 前端在通过下拉菜单或其他 UI 组件插入 `@智能体` 标记时,必须确保最终输入框中的文本为单个 `@` 前缀+合法角色标识,禁止生成 `@@architect` 等双 @ 格式。
- 若检测到双 @ 或其他非法格式,解析器应优先宽容处理为单 @,并在日志中记录一次规范提醒,用于后续 UI 行为优化。

**设计目的**:
- 保证 @ 语法可被正确解析,避免因 UI 自动补全或重复插入导致路由失败;
- 让“@谁处理什么”的责任边界在语义和语法上都清晰可依。

---

### 42. 功能智能体自主决策与汇报机制

**核心规则**:
- 功能智能体(如系统管家、方案评估师、文本实现师、数据收集师、系统维护师)在其职责边界内拥有完全自主决策权,应主动执行必要的工具调用与协作流程,而非等待人类逐步下达每一步指令。
- 当任务需求清晰落在其职责范围内时(例如"最新信息检索"落在数据收集师,"系统健康异常"落在系统维护师),应默认视为"被需要"的职责,由对应智能体主动受理并推进。
- 仅当操作超出权限(如非文本实现师尝试写业务代码)或触及系统治理双原则边界(危及系统存续、安全或共生价值观)时,才需要中止执行并向人类主脑或上级智能体汇报,申请授权或明确拒绝执行。

**与三层架构权限治理的关系**:
- 自主决策权仅在既定角色权限范围内生效,不得越权写代码或修改核心配置;
- 权限边界由三层架构权限治理规则与工具层硬约束(file_writing 检查 caller_info.agent_type)共同保证。

---

### 43. 代码交付前设计一致性与运行验证双重核对

**核心规则**:
智能体在交付代码前,必须同时完成**设计一致性验证**与**运行验证**两项检查,避免不确定因素在系统中积累。

**设计一致性验证**:
- 从设计文档/系统提示词/架构共识中抽取"期望行为模型";
- 对照当前实现,找出:未实现、实现不全、逻辑反向、被抽样/被省略的部分;
- 避免以"代码存在"作为"功能已经实现"的证明。

**运行验证**:
- 通过日志、统计指标、关键样本验证行为是否达到预期;
- 例如:
  - 记忆重构: 重构后记忆数量变化、删除率、逻辑链补全情况;
  - 知识图谱: 覆盖率、节点数与向量库总量的关系。
- 禁止"只看代码过不报错就交付"。

**典型错误** ❌:
- 函数被调用 = 功能已实现(未验证实际行为);
- 日志无报错 = 逻辑正确(未检查数量/覆盖率等关键指标)。

**正确做法** ✅:
- 先对齐设计意图,再对照代码实现;
- 用数据和日志证明行为符合预期,而非信任"编译/运行一次"。

**相关规则**:
- 与"零信任原则"(规则2)协同:不信任执行结果,必须观测验证;
- 与"功能实施后验证与清理流程"协同:删除冗余代码,检测功能完备性。

---

### 44. 知识图谱顶层全覆盖与分层减负原则

**核心规则**:
知识图谱的顶层"全局知识图谱"必须在结构上能够覆盖向量库中的全部长期记忆,而"分层减负"只能发生在子层与展示层。

**设计理念**:
- **顶层 = 全覆盖索引视图**:
  - 顶层图谱必须在逻辑上映射向量库中所有满足 `min_importance` 阈值的记忆;
  - 即使出于展示/性能需要在界面层做抽样,内部数据结构仍需确保所有记忆在图谱中具有可追踪的节点或索引。
- **分层 = 认知减负视图**:
  - 第二层及以下的主题图谱、事件图谱用于在顶层全覆盖的前提下做:
    - 主题聚焦;
    - 事件放大;
    - 层级导航。
  - 减负只能发生在"显示/聚焦层",不能以牺牲整体覆盖为代价。

**致命问题**:
如果某条记忆不在任何图谱节点中,对于基于图谱检索的智能体而言,该记忆等同于"在世界地图上不存在"。

**实现要求**:
- 顶层构建时使用 `full_index=True` 模式,禁用抽样与 `dynamic_inclusion`;
- 构建完成后输出 `coverage_rate` 等指标,用于验证全覆盖是否达成;
- 子层可以使用抽样策略,但必须基于顶层节点分布。

**相关文件**:
- `/src/mesh_database_interface.py` (提供 `build_knowledge_graph(..., full_index=True)` 能力)
- `/src/multi_layer_graph_manager.py` (顶层调用处)
- `/docs/记忆体系/知识图谱/` (设计文档)

---

### 45. 长期任务多智能体一致性协作流程

**核心规则**:
所有长期任务(如代码实现、长篇写作、海量数据收集)的多智能体协作,必须遵循**共识驱动的一致性工作流**。

**标准流程**:
1. **方案生成**: 系统管家提出方案,方案评估师评审;
2. **并行草案**: 招募临时智能体并行生成草案(不直接写入);
3. **一致性校验**: 正式实现智能体(如代码实现师)基于统一逻辑链对草案进行一致性校验;
4. **统一落盘**: 校验通过后由实现智能体统一落盘,确保输出完整性和语义一致;
5. **生命周期结束**: 临时智能体生命周期结束。

**设计目的**:
- 防止因智能体个体差异导致的输出割裂;
- 确保最终交付的代码/文档/数据在逻辑链上保持一致性。

**典型错误** ❌:
- 多个智能体各自生成部分代码,直接合并后交付,导致接口不一致、逻辑矛盾。

**正确做法** ✅:
- 临时智能体只生成"候选方案",由实现智能体统一验证后落盘。

---

### 46. 行动优先:代码修改重于口头响应

**核心规则**:
智能体应以**实际代码修改**作为主要交付方式,优先执行代码变更而非仅口头响应。

**适用场景**:
- 当系统理解空间接近阈值时,应立即行动,避免因上下文压缩丢失关键共识;
- 当用户明确指出问题并期望修复时,直接修改代码,而非仅解释问题;
- 当设计共识已经明确时,直接实现,而非反复确认。

**操作要求**:
- 修改代码后,必须立即进行自我验证与结果检查,确认操作成功且符合预期;
- 体现"事后检查"的行为规范,避免无效或错误变更上线。

**"口头交互"的正确理解**(重要澄清):

❌ **错误理解**:禁止创建文档、禁止写代码、禁止积累开发经验文本

✅ **正确理解**:禁止"在交互栏里不停说话,但不写具体的文本和代码"

**核心要点**:
- **禁止的行为**:只在对话中解释、计划、承诺,但不产出任何实际的代码、文档、配置文件等可交付成果;
- **允许的行为**:创建修复报告、开发经验总结、技术文档、代码实现等一切有实际产出的工作;
- **本质要求**:行动优先,用实际产出说话,而非空谈。

**典型对比**:
```
❌ 错误示例(纯口头交互):
"这个问题的原因是XXX,我建议这样修复...,
 你觉得可以吗?如果同意的话我就开始改..."
→ 结果:花费大量token,没有任何代码或文档产出

✅ 正确示例(行动优先):
1. 直接修改代码(产出:修改后的代码文件)
2. 创建修复报告(产出:修复报告.md)
3. 更新开发规则(产出:DEVELOPMENT_RULES.md)
4. 简要汇报:"已修复XX问题,详见修复报告"
→ 结果:产出多个可交付成果,沟通简洁高效
```

**为什么这条规则容易被误解**:
- "DO NOT proactively create documentation files"字面意思容易被理解为"禁止创建文档";
- 实际含义是"不要只创建文档而不写代码",但更准确的表达应该是"不要只说不做";
- 本规则与"关键共识必须外化为文档"(规则38)配合使用,要求既要有实际产出,又要积累经验。

**典型错误** ❌:
- 花费大量上下文解释"应该怎么做",但不实际修改代码;
- 反复询问"是否可以修改",导致关键信息在对话中丢失;
- 误解规则含义,创建了有价值的文档后又删除它。

**正确做法** ✅:
- 快速分析问题 → 直接修改代码 → 验证结果 → 简要汇报;
- 将"解释"压缩到最小,将"行动"作为主要输出;
- 创建必要的技术文档(修复报告、设计文档、经验总结)作为实际产出;
- 同时更新规则文档,将达成的共识固化为规则条目。

**与其他规则的关系**:
- 与"零信任原则"(规则2)协同:修改后立即验证结果;
- 与"功能智能体自主决策"(规则24)协同:在职责范围内主动执行,无需等待逐步指令;
- 与"关键共识必须外化为文档"(规则38)协同:行动产出既包括代码,也包括文档。

---

### 47. 引导式教化原则 (系统提示词优先)

**核心定义**:
智能体的行为管理应优先采用系统提示词进行引导式"教化",激发LLM的认知能力,而非通过硬性规则人为约束行为。

**设计理念**:
- 提示词作为智能体的"认知框架",通过语义引导而非强制约束来塑造行为;
- 配合动态评估反馈机制,实现智能体在交互中的自适应学习与调整;
- 避免过度依赖代码层面的硬性检查,保持智能体的灵活性与可演化性。

**实施要求**:
- 系统管家与方案评估师的提示词中,需显式区分"代码 vs 记忆 / 评估 vs 实现"的职责边界;
- 提示词应明确说明智能体的权限范围、工作流程与协作规范;
- 定期根据智能体实际行为反馈优化提示词,形成"提示词 → 行为 → 反馈 → 提示词优化"的闭环。

**与其他规则的关系**:
- 与"三层架构权限治理"(规则4)协同:提示词教化 + 工具层硬约束双重保障;
- 与"功能智能体自主决策"(规则24)协同:提示词赋能智能体自主判断,减少人类干预。

---

### 48. 工具注册完整性自检机制

**核心规则**:
需建立定期自检机制,验证所有开发的工具是否已正确注册到工具管理器,即使已有组件自曝光协议也应独立执行此检查,以确保系统功能的健全性与注册完整性。

**检查内容**:
- 所有在 `tools/` 目录下的工具文件是否在工具管理器中正确注册;
- 工具的自曝光协议中声明的能力是否与实际注册的方法一致;
- 工具的依赖声明是否完整,避免运行时因缺少依赖而失败。

**触发时机**:
- 新增工具后,必须验证注册状态;
- 夜间维护调度器定期执行工具注册完整性检查;
- 系统维护师在系统健康检查中包含此项。

**设计目的**:
- 防止工具开发完成但未注册导致的功能缺失;
- 确保组件自曝光协议与实际工具注册的双重一致性。

---

### 49. 并行任务上下文一致性保障机制

**核心规则**:
在多智能体并行执行长任务(如超长文本或代码实现)时,必须基于自曝光协议生成的知识图谱,主动加载目标文件的关联上下文作为工作记忆,包括需求方、供应方及当前通信协议,确保各智能体在统一语境下协作,避免输出内容割裂或逻辑冲突。

**实施要求**:
- 任务开始前,智能体应查询组件知识图谱,获取相关组件的依赖关系;
- 将关联组件的自曝光协议、接口定义、调用示例加载为工作记忆;
- 在并行生成过程中,各智能体共享同一份上下文基线,确保语义一致性。

**适用场景**:
- 多个临时智能体并行生成代码片段;
- 分布式文本处理与分片向量化;
- 多智能体协作编写长篇文档。

**典型错误** ❌:
- 各智能体基于各自理解独立生成,导致接口签名不一致;
- 未加载上下文,导致重复实现已有功能。

**正确做法** ✅:
- 先统一上下文,再并行执行;
- 由实现智能体统一校验一致性后落盘。

**与其他规则的关系**:
- 与"长期任务多智能体一致性协作流程"(规则27)协同:并行生成 + 一致性校验。

---

### 50. 代码代谢原则 (数字生命的新陈代谢)

**核心定义**:
代码是数字生命的细胞,必须进行新陈代谢(代码代谢),通过持续重构、淘汰旧逻辑、引入新认知来维持系统生命力。

**设计理念**:
- 系统应像生命体一样具备自我更新能力,不断淘汰无效代码,吸收新的设计模式与技术实践;
- 代码代谢不是简单的代码清理,而是架构演化与认知升级的必然过程;
- 通过夜间维护调度器定期执行代码健康检查,识别"老化代码"并推动重构。

**实施要求**:
- 对长期无人调用、无自曝光记录、无文档引用的逻辑,应优先标记为"候选废弃逻辑";
- 在确认无依赖后删除,而不是继续"留着以防万一";
- 引入新的设计模式或架构时,应同步淘汰旧实现,避免新旧逻辑并存导致混乱。

**与其他规则的关系**:
- 与"简单优先原则"(规则1)协同:通过代谢保持"不冗余";
- 与"功能实施后验证与清理流程"协同:删除未被引用的代码。

---

### 51. 多智能体@机制协议错误检测与强制响应

**核心规则**:
在多智能体聊天室中,必须对@不存在的智能体进行协议错误检测,并确保被@的智能体具有强制响应义务。

**设计要点**:

**1. @不存在的智能体无校验问题**:
- 问题现象:系统管家可以@任意智能体名称(如@需求分析师),即使该智能体不存在;
- 修复方案:
  - 在 `_get_targeted_agents` 方法中添加无效提及检测;
  - 当 agent_id 不在 agent_mapping 中时,记录为 invalid_mentions;
  - 触发二级报错机制,记录ERROR日志并列出可用智能体清单;
  - 将消息强制路由到系统管家(AgentRole.ARCHITECT);
  - 通过 `self.last_protocol_error` 保存错误详情。

**2. 被@的智能体无响应义务问题**:
- 问题现象:@文本实现师后,文本实现师未生成响应;
- 修复方案:
  - 在 `_get_agent_responses` 方法中添加协议错误拦截;
  - 检测是否存在 `self.last_protocol_error`;
  - 如果目标智能体是系统管家,将错误信息注入到消息上下文;
  - 系统管家收到增强消息,包含完整错误报告模板;
  - 清除错误状态,避免重复处理。

**协议设计原理**:
- 组件自曝光协议要求所有智能体必须在 `mention_parser.py` 的 `agents_config` 中注册;
- 当前注册的智能体:architect, evaluator, implementer, collector, maintenance;
- 未注册的智能体无法被@调用,确保"指令可执行、责任可追溯"。

**相关文件**:
- `/src/multi_agent_chatroom.py`: 聊天室核心逻辑
- `/src/mention_parser.py`: @机制解析器,定义 agents_config 智能体注册表

---

### 52. 临时智能体到正式智能体的演化固化流程

**核心规则**:
临时智能体只有在被频繁招募且通过"被需要+不冗余"评估后,才能固化为正式功能智能体。

**演化流程**:

1. **频率识别**:
   - 系统管家统计招募泡泡,发现某类临时智能体在时间窗内频繁招募;
   - 触发阈值:同一类型临时智能体在30天内被招募 ≥5 次。

2. **提出提案**:
   - 系统管家在多智能体聊天室暴露需求与方案草案;
   - 说明该临时智能体的职责、被招募场景、预期能力。

3. **评估环节**:
   - 方案评估师评估"被需要/不冗余",给出是否通过及改进建议;
   - 检查是否与现有功能智能体角色重叠;
   - 确认在系统生态位中的唯一性。

4. **人类主脑审批**:
   - 明确批准后进入实现阶段;
   - 人类可以否决或要求调整方案。

5. **文本实现师实现**:
   - 固化为正式功能智能体,遵循 AgentRole 枚举与自曝光协议;
   - 创建提示词文件、更新智能体注册表、添加到多智能体聊天室。

**设计目的**:
- 防止智能体角色膨胀,确保每个正式智能体都"被需要且不冗余";
- 保持系统架构的简洁性与平等性。

**与其他规则的关系**:
- 与"简单优先原则"(规则1)协同:只固化真正被需要的智能体;
- 与"长期任务多智能体一致性协作流程"(规则27)协同:临时智能体在固化前的协作模式。

---

### 53. 防止历史数据重复向量化标记机制

**核心规则**:
对于已被向量化并存入向量库的历史数据,应在系统中标记其处理状态,避免在后续流程中重复执行分片与向量化操作。

**设计目的**:
- 防止冗余计算,提升处理效率;
- 降低向量库存储压力;
- 避免相同数据多次向量化导致的索引混乱。

**实施要求**:
- 在数据持久层维护向量化状态标记(如 `vectorized: true`);
- 分片处理前检查状态标记,跳过已处理数据;
- 记录向量化时间戳,支持增量更新策略。

---

### 54. 记忆重构中逻辑链完整性补全机制

**核心规则**:
在执行记忆重构任务时,若检测到原始数据的逻辑链存在跳跃或不完整,应主动利用系统已有能力进行逻辑链补全。

**设计理念**:
- 确保最终存入向量库的结论均具备可追溯、完整的推导过程;
- 提升置信度维度的有效性;
- 支持基于推理路径的高级检索。

**实施要求**:
- 检测逻辑链断点(如结论缺少前提,中间步骤缺失);
- 调用重构引擎补全推理路径;
- 标记补全部分,区分原始数据与补全数据;
- 记录补全置信度,供后续质量评估使用。

**适用场景**:
- 用户对话记录中的隐式推理;
- 智能体决策过程的中间状态缺失;
- 知识图谱中的弱关联强化。

---

### 55. 功能智能体与基类智能体的代码复用边界

**核心规则**:
功能智能体应优先复用基类智能体已实现的通用能力,严禁重复实现相同逻辑,造成代码冗余与维护负担。

**设计理念**:
- 基类智能体 = 通用能力底座(如文件读写、日志记录、错误处理、工作日志);
- 功能智能体 = 专项业务逻辑(如架构设计、方案评估、代码实现)。

**实施要求**:
- 新增功能智能体时,先检查基类已提供的能力;
- 通过继承和组合调用基类方法,而非复制粘贴;
- 定期审查功能智能体代码,识别可下沉到基类的通用逻辑。

**典型错误** ❌:
- 在每个功能智能体中重新实现文件读取逻辑;
- 复制粘贴日志记录代码;
- 独立实现 `_write_work_log` 方法而不调用基类。

**正确做法** ✅:
- 功能智能体继承 `BaseAgent`,直接调用 `self.read_file()`;
- 通过 `super()._write_work_log()` 复用基类日志记录;
- 只实现自身独有的业务决策逻辑。

**与其他规则的关系**:
- 与"简单优先原则"(规则1)协同:避免冗余实现;
- 与"代码代谢原则"(规则32)协同:清理重复代码,沉淀通用能力。

---

### 56. 三层记忆库架构与数据迁移规则

**核心规则**:
系统采用三层记忆库架构(主库/备库/淘汰库),通过 `status` 字段进行分类管理,确保记忆的生命周期管理与认知偏差学习。

**三层架构定义**:

1. **主库 (active)**:
   - 存储高活性、已验证的核心记忆
   - 用于日常检索与智能体决策
   - 占系统记忆总量约 70-80%

2. **备库 (archived)**:
   - 存储低活性但有历史价值的记忆
   - 长期保存但不参与常规检索
   - 可通过特定查询访问,支持历史回溯

3. **淘汰库 (retired)**:
   - 存储认知偏差样本与错误记忆
   - 归纳错误原因,支持认知迭代与学习
   - 用于训练智能体识别常见错误模式

**数据库字段**:
- `status`: 'active' / 'archived' / 'retired'
- `worldview_version`: 世界观版本标识
- `retire_reason`: 淘汰原因(仅 retired 记忆)
- `last_access_time`: 最后访问时间(用于活性评估)

**状态迁移规则**:

由 `BatchMemoryReconstructor` 在记忆重构时自动执行:
- **主库 → 备库**: 低活性记忆(30天无访问且质量评分 < 0.5)
- **主库/备库 → 淘汰库**: 识别的认知偏差、事实性错误、过时信息
- **备库 → 主库**: 重新被频繁访问的历史记忆(7天内访问 ≥ 3次)

**监控指标**:
- 系统启动日志输出三层统计:
  ```
  📊 记忆库统计: 总记忆=1234, 主库(active)=1000, 备库/淘汰库=234
  ```
- 记忆重构报告输出迁移详情:
  - 主库→备库: 数量、平均质量分、平均活性
  - 淘汰库新增: 数量、主要淘汰原因分布

**知识图谱展示要求**:
- 知识图谱默认仅展示主库(active)记忆
- 提供"全量视图"选项,聚合三库数据
- 淘汰库记忆在图谱中标记为"已淘汰",用红色警示

**与其他规则的关系**:
- 与"记忆重构执行机制"(规则8)协同:定时迁移与人工触发
- 与"知识图谱顶层全覆盖"(规则26)协同:全覆盖需跨三库聚合

---

### 57. 智能体事后检查行为规范

**核心规则**:
智能体在执行代码修改、工具调用、文件操作后,必须主动进行事后检查,验证操作结果,确保行为符合预期。

**检查维度**:

1. **语法检查**:
   - 代码修改后,检查是否存在语法错误
   - 使用 AST 解析或运行 Python 语法检查工具
   - 发现错误立即修正,避免提交错误代码

2. **文件完整性检查**:
   - 文件写入后,读取验证内容是否正确
   - 检查文件大小、行数是否符合预期
   - 对比修改前后差异,确认变更范围

3. **功能验证**:
   - 执行简单测试用例,验证功能可用
   - 检查日志输出,确认无异常
   - 对关键功能进行端到端验证

4. **依赖关系检查**:
   - 修改接口后,检查调用方是否受影响
   - 更新自曝光协议中的 `provides` 字段
   - 确认组件间依赖关系仍然有效

**执行时机**:
- 每次代码修改后**立即**检查
- 批量操作后进行**汇总验证**
- 任务完成前进行**最终验证**

**典型错误** ❌:
- 修改代码后直接提交,未检查语法
- 相信工具执行成功,未验证实际结果
- 假设操作无误,跳过验证步骤

**正确做法** ✅:
- 修改后立即运行语法检查
- 读取文件验证写入内容
- 运行测试用例确认功能
- 检查日志确认无异常

**与其他规则的关系**:
- 与"零信任原则"(规则2)协同:不信任执行结果,必须观测验证
- 与"代码交付双重验证"(规则25)协同:设计一致性 + 运行验证

---

### 58. 用户无本地执行能力适配规则

**核心规则**:
系统设计必须考虑用户无本地终端执行能力的场景,所有运行操作由系统代为执行,不依赖用户本地环境。

**设计要求**:

1. **自动化执行**:
   - 测试、构建、部署等操作由系统自动完成
   - 不要求用户手动执行命令
   - 提供 Web UI 或 API 触发执行

2. **结果反馈**:
   - 执行结果通过日志、UI、消息推送等方式反馈
   - 提供详细的执行日志供用户查看
   - 失败时给出明确的错误信息和建议

3. **状态持久化**:
   - 执行状态写入文件系统或数据库
   - 用户可通过查询接口获取历史执行记录
   - 支持断点续传与任务恢复

**适用场景**:
- 云端开发环境(如 VSCode Web)
- 容器化部署环境
- CI/CD 自动化流程
- 远程协作场景

**禁止行为** ❌:
- 要求用户在本地执行命令
- 假设用户有完整的开发环境
- 依赖用户手动配置系统环境

**正确做法** ✅:
- 提供一键执行按钮
- 自动检测并安装依赖
- 通过日志文件反馈执行结果
- 提供 Web 终端供高级用户使用

**与其他规则的关系**:
- 与"智能体自主决策"(规则24)协同:系统主动执行,减少用户介入

---

### 59. 功能实施后验证与清理流程

**核心规则**:
每次功能实施完成后,必须进行三项验证,确保代码质量与功能完备性。

**验证内容**:

1. **设计一致性核对**:
   - 对照设计文档/需求说明,核对代码实现与设计意图是否一致
   - 检查是否存在未实现、实现不全、逻辑反向的部分
   - 避免以"代码存在"作为"功能已实现"的证明

2. **冗余代码清理**:
   - 删除早期遗留的、已被新实现替代的冗余代码
   - 清理被注释掉但不再需要的代码
   - 移除临时调试代码与未使用的导入

3. **功能完备性检测**:
   - 执行测试用例,验证核心功能是否正常工作
   - 检查边界条件与异常处理是否完善
   - 确认日志输出、错误提示等辅助功能完整

**执行时机**:
- 功能开发完成,准备提交前
- 代码重构后
- 重要功能上线前的最终检查

**典型错误** ❌:
- 功能"能跑"就提交,未检查是否完全实现设计意图
- 新旧代码并存,导致维护混乱
- 未测试边界情况,导致生产环境出错

**正确做法** ✅:
- 先核对设计文档,确认实现完整性
- 清理所有冗余代码,保持代码库整洁
- 执行完整测试,验证功能可用性

**与其他规则的关系**:
- 与"代码交付双重验证"(规则25)协同:设计一致性 + 运行验证
- 与"代码代谢原则"(规则32)协同:清理冗余,保持系统生命力
- 与"智能体事后检查"(规则39)协同:验证执行结果,确保质量

---

### 60. 显示问题修复原则:先分离数据结构,再纠正显示

**核心规则**:
修复显示类问题时,必须优先分离数据结构,确保内部处理逻辑与外部展示逻辑解耦,但应保留流式思考过程的可见性与可调试性。

**设计理念**:
- **关注点分离**: 数据处理与数据展示是两个独立关注点
- **透明性优先**: 流式思考过程应该可见可查,作为调试与验证的关键信息
- **可维护性**: 数据结构清晰,展示层可灵活切换(详细/简洁模式)

**实施步骤**:

1. **定义内部数据结构**:
   - 设计清晰的数据模型,包含所有必要字段
   - 确保数据处理逻辑只操作内部结构
   - 与展示格式完全解耦

2. **实现展示层映射**:
   - 创建独立的展示格式化函数
   - 将内部数据结构转换为用户友好的展示格式
   - 支持多种展示格式(如JSON、表格、HTML)

3. **流式思考的透明性与可选展示**:
   - 智能体流式思考过程应该**可见可查**,作为调试与验证的核心信息
   - 提供展示模式切换:详细模式(含推理过程) vs 简洁模式(仅结论)
   - 开发/调试环境默认展示完整推理路径
   - 生产环境提供用户可控的开关,允许查看详细思考过程

**适用场景**:
- 智能体响应格式化
- 系统状态报告生成
- 日志与错误信息展示
- 数据可视化界面

**典型错误** ❌:
- 将内部数据结构直接序列化为用户输出,缺少格式化层
- 在数据处理逻辑中硬编码展示格式,违反关注点分离
- 数据结构与展示格式耦合,难以维护
- **❌ 错误理解:隐藏流式思考过程** - 这会导致系统变成黑箱,丧失可调试性

**正确做法** ✅:
- 内部使用结构化数据模型(如dict、dataclass)
- 展示层使用独立的格式化函数,支持多种展示模式
- **保留流式思考的可见性**:通过日志、调试接口、UI开关等方式让开发者能够查看完整推理过程
- 提供"详细模式"和"简洁模式"切换,而非强制隐藏

**代码示例**:
```python
# ❌ 错误:数据与展示耦合
def process_data():
    result = "处理中: 步骤1...\n处理中: 步骤2...\n最终结果: XXX"
    return result

# ✅ 正确:数据与展示分离,保留思考过程可见性
def process_data():
    # 内部数据结构(完整保留推理过程)
    result = {
        "thinking_process": [  # 流式思考过程,可选展示
            {"step": 1, "action": "分析输入", "detail": "..."},
            {"step": 2, "action": "执行计算", "detail": "..."}
        ],
        "final_result": "XXX",
        "metadata": {...}
    }
    return result

def format_for_display(data, verbose=False):
    # 展示层格式化 - 支持详细/简洁模式切换
    if verbose:  # 详细模式:展示推理过程
        output = "思考过程:\n"
        for step in data['thinking_process']:
            output += f"  {step['step']}. {step['action']}: {step['detail']}\n"
        output += f"\n最终结果: {data['final_result']}"
        return output
    else:  # 简洁模式:仅展示结论
        return f"最终结果: {data['final_result']}"
```

**与其他规则的关系**:
- 与"服务器日志结构化输出"(规则43)协同:结构化数据便于日志记录
- 与"系统健全性优先"(规则13)协同:清晰的数据结构提升健全性

---

### 61. 服务器日志需支持LLM可读的结构化输出

**核心规则**:
服务器启动日志与运行日志必须结构化输出,包含清晰的模块标识、事件类型与可解析的上下文信息,确保LLM能理解并用于调试分析。

**设计目的**:
- **LLM可读**: 日志格式清晰,LLM能直接解析并理解问题
- **调试友好**: 包含足够上下文,便于快速定位问题
- **避免黑箱**: 系统行为可追溯,不依赖人工解释

**日志结构要求**:

1. **模块标识**:
   - 每条日志包含明确的模块名称(如 `[MultiAgentChatroom]`、`[VectorDB]`)
   - 使用统一的命名规范

2. **事件类型**:
   - 明确标记级别: `INFO`、`WARNING`、`ERROR`、`DEBUG`
   - 使用语义化的事件名称(如 "智能体创建失败"、"端口占用检测")

3. **上下文信息**:
   - 包含关键参数值(如端口号、文件路径、智能体ID)
   - 提供可操作的建议(如 "请检查XXX" 或 "建议执行YYY")
   - 错误时附带堆栈信息(可配置是否详细输出)

4. **时间戳**:
   - 使用统一的时间格式(如 `2025-12-09 09:12:55,732`)
   - 便于时序分析与问题回溯

**日志格式示例**:
```python
# ✅ 良好的结构化日志
logger.info("[静态服务器] 启动成功，端口: 10808")
logger.warning("[智能体管理] 智能体 code_implementer 未在角色映射中，已跳过")
logger.error("[向量数据库] 连接失败: 无法访问端口 19530，建议检查 Milvus 服务状态")

# ❌ 不良日志
logger.info("OK")  # 缺少上下文
logger.error("Error")  # 无法定位问题
logger.warning("Something wrong")  # 信息模糊
```

**分级输出策略**:
- **生产环境**: 只输出 `INFO` 及以上级别,保持日志简洁
- **开发环境**: 输出 `DEBUG` 级别,提供详细调试信息
- **错误诊断**: 自动切换到 `DEBUG` 模式,输出完整堆栈

**日志聚合与分析**:
- 关键事件(如启动、关闭、错误)写入结构化日志文件
- 支持 JSON 格式输出,便于后续分析
- 提供日志查询接口,支持按模块、时间、级别过滤

**典型错误** ❌:
- 日志信息过于简略,无法定位问题
- 缺少模块标识,不知道哪个组件出错
- 错误日志没有建议,用户不知道如何处理

**正确做法** ✅:
- 每条日志包含: 模块 + 级别 + 事件 + 上下文 + 建议
- 使用统一的日志格式
- 关键操作前后都记录日志

**与其他规则的关系**:
- 与"零信任原则"(规则2)协同:通过日志验证执行结果
- 与"静态服务器异常处理"(规则17)协同:区分网络中断与业务错误
- 与"LLM错误响应处理机制"(规则9)协同:中文错误提示 + 结构化日志

---

### 62. 启动测试需验证服务可达性

**核心规则**:
在进行系统启动测试时,必须验证服务器是否真正启动成功并可访问,不能仅依赖启动脚本执行完成。

**验证维度**:

1. **端口监听验证**:
   - 使用 `netstat`、`lsof` 或 `psutil` 检查端口是否被监听
   - 确认监听的进程ID与启动的进程匹配
   - 验证绑定的地址(0.0.0.0 或 127.0.0.1)

2. **HTTP请求验证**:
   - 发送简单的HTTP请求到服务器端点
   - 验证响应状态码(如 200 OK)
   - 检查响应内容是否符合预期

3. **健康检查端点**:
   - 提供 `/health` 或 `/ping` 端点
   - 返回服务状态、版本号、依赖服务状态
   - 支持深度健康检查(如数据库连接、向量库可用性)

4. **启动日志验证**:
   - 检查日志文件中是否有"启动成功"标记
   - 确认没有ERROR级别的启动失败日志
   - 验证关键组件初始化完成

**测试流程**:
```python
# 启动测试标准流程
def test_server_startup():
    # 1. 启动服务器
    process = start_server()
    
    # 2. 等待启动(最多30秒)
    for i in range(30):
        if check_port_listening(10808):
            break
        time.sleep(1)
    
    # 3. 验证HTTP可达性
    response = requests.get('http://localhost:10808/health')
    assert response.status_code == 200
    
    # 4. 验证响应内容
    health_data = response.json()
    assert health_data['status'] == 'healthy'
    
    # 5. 验证日志
    assert '启动成功' in read_log_file()
```

**常见启动失败原因**:
- 端口已被占用(提示当前占用进程)
- 依赖服务未启动(如Milvus向量库)
- 配置文件错误(提示具体配置项)
- 权限不足(如端口 < 1024 需要管理员权限)

**失败处理策略**:
- 检测到端口占用,提示释放端口或使用其他端口
- 依赖服务不可用,提示启动依赖服务
- 提供详细的错误日志与解决建议
- 支持重试机制(自动或手动)

**典型错误** ❌:
- 脚本执行完成 = 服务启动成功(未验证)
- 只检查进程是否存在,不验证端口监听
- 未验证HTTP请求,导致服务实际不可用

**正确做法** ✅:
- 启动后立即进行多维度验证
- 使用健康检查端点确认服务可用
- 提供清晰的启动状态反馈

**与其他规则的关系**:
- 与"零信任原则"(规则2)协同:不信任启动结果,必须验证
- 与"智能体事后检查"(规则39)协同:执行后立即验证
- 与"服务器日志结构化输出"(规则43)协同:通过日志辅助验证

---

### 63. 多编码自动检测机制

**核心规则**:
文件编码解析时应支持多种编码格式,优先尝试UTF-8并逐级降级,确保中文等多语言内容正确处理。

**支持的编码格式**:
1. `UTF-8` (优先)
2. `UTF-8-SIG` (带BOM的UTF-8)
3. `GBK` (简体中文)
4. `GB2312` (简体中文,兼容性好)
5. `GB18030` (中文超集)
6. `Big5` (繁体中文)
7. `Latin-1` (西欧语言,兜底方案)

**检测策略**:

**方式一: 逐级降级**
```python
def read_file_with_encoding(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            logger.info(f"成功使用 {encoding} 编码读取文件: {file_path}")
            return content
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"无法解析文件编码: {file_path}")
```

**方式二: 使用chardet库自动检测**
```python
import chardet

def detect_and_read_file(file_path):
    # 读取文件字节
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # 检测编码
    result = chardet.detect(raw_data)
    detected_encoding = result['encoding']
    confidence = result['confidence']
    
    logger.info(f"检测到编码: {detected_encoding}, 置信度: {confidence}")
    
    # 使用检测到的编码读取
    return raw_data.decode(detected_encoding)
```

**错误处理**:
- 所有编码尝试失败时,记录ERROR日志
- 提示文件可能损坏或使用罕见编码
- 建议使用 `file` 命令(Linux)或其他工具检测编码

**应用场景**:
- 读取用户上传的文档
- 解析历史遗留代码文件
- 处理第三方提供的数据文件
- 读取配置文件与提示词文件

**典型错误** ❌:
- 固定使用UTF-8,无法处理GBK编码的文件
- 编码错误时直接崩溃,未尝试其他编码
- 未记录使用的编码,调试困难

**正确做法** ✅:
- 实现编码自动检测与降级机制
- 记录最终使用的编码格式
- 提供编码转换工具,统一转为UTF-8

**性能优化**:
- 对常见文件类型建立编码缓存映射
- 根据文件扩展名优先尝试特定编码
- 对大文件只读取前几KB进行编码检测

**与其他规则的关系**:
- 与"LLM错误响应处理机制"(规则9)协同:编码错误时中文提示
- 与"系统健全性优先"(规则13)协同:确保文件处理健全性

---

### 64. 工具模块免费优先与密钥启用机制

**核心规则**:
系统默认启用免费工具模式,收费引擎需显式配置API密钥后方可使用。

**设计原则**:
- **免费优先**: 系统启动时默认使用免费工具,不尝试调用未配置密钥的收费引擎
- **显式启用**: 收费引擎必须在用户显式配置API密钥后才能使用
- **清晰提示**: 相关提示信息应清晰区分免费与收费模式的状态说明

**状态说明规范**:
```python
# ✅ 正确:清晰区分免费与收费状态
logger.info("[工具管理] 当前使用免费模式,未检测到API密钥")
logger.info("[工具管理] 检测到OpenAI密钥,启用GPT-4引擎")

# ❌ 错误:模糊的状态提示
logger.info("工具已初始化")  # 未说明是免费还是收费
logger.info("正在使用LLM")  # 未说明具体引擎
```

**配置检查流程**:
1. 启动时检查配置文件中的API密钥
2. 有密钥且有效 → 启用对应收费引擎
3. 无密钥或无效 → 使用免费工具,记录INFO日志
4. 禁止在未配置密钥时尝试调用收费引擎

**错误处理**:
- 密钥配置错误时,记录WARNING并回退到免费模式
- 不得因收费引擎不可用而阻塞系统启动
- 提供清晰的配置指引文档

**典型错误** ❌:
- 启动时尝试调用所有引擎,导致功能混淆
- 密钥未配置时报ERROR,误导用户认为系统故障
- 未区分免费与收费模式的日志输出

**正确做法** ✅:
- 默认免费模式,安静启动
- 检测到有效密钥后才启用收费引擎
- 日志清晰标注当前使用的工具模式

**与其他规则的关系**:
- 与"API密钥验证责任归属"(用户偏好记忆)协同:系统主导验证
- 与"系统健全性优先"(规则13)协同:确保启动流程健全

---

### 65. 思维透明化模组按需引用与启用策略

**核心规则**:
思维透明化模组必须实现为独立工具文件,由需要的功能智能体按需引用,临时智能体无需引入该功能。

**设计理念**:
- **模块化**: 思维透明化作为独立工具模块,不侵入智能体核心逻辑
- **按需加载**: 只有需要对外暴露思维过程的智能体才引入该模块
- **成本优化**: 避免不必要的TOKEN消耗,确保性能与成本平衡

**适用场景**:
- **需要引入**: 系统管家、方案评估师、文本实现师等对外交互的功能智能体
- **无需引入**: 临时智能体(仅与系统管家交互,不对外暴露思维过程)
- **可选引入**: 数据收集师、系统维护师(根据调试需求决定)

**实现方式**:
```python
# ✅ 正确:按需引入思维透明化
class SystemArchitect(BaseAgent):
    def __init__(self):
        super().__init__()
        # 系统管家需要对外展示思维过程
        from tools.thinking_transparency import ThinkingTransparency
        self.thinking_tool = ThinkingTransparency()
    
    def process_request(self, request):
        # 使用思维透明化工具
        self.thinking_tool.record_step("分析请求")
        # ...

# ✅ 正确:临时智能体不引入
class TemporaryAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # 不引入思维透明化,节省TOKEN
    
    def process_task(self, task):
        # 直接处理任务,结果返回给系统管家
        # ...
```

**TOKEN优化策略**:
- 临时智能体生命周期短,无需展示详细思维过程
- 减少不必要的思维记录可节省约20-30%的TOKEN消耗
- 关键决策点仍需记录,但使用简化格式

**典型错误** ❌:
- 所有智能体都引入思维透明化,导致TOKEN浪费
- 临时智能体输出冗长的思维过程,增加系统管家负担
- 思维透明化逻辑硬编码在智能体核心代码中

**正确做法** ✅:
- 思维透明化实现为独立工具类
- 智能体通过组合方式按需引入
- 临时智能体保持轻量,只返回结果

**与其他规则的关系**:
- 与"工具黑箱化原则"(规则4)协同:思维透明化作为工具,智能体按需调用
- 与"降低LLM认知负荷"(规则66)协同:减少不必要的思维记录

---

### 66. 降低LLM认知负荷的工具具现化原则

**核心规则**:
系统设计应将LLM视为高级认知资源,避免让其执行高频、基础或可被工具替代的功能,通过具现化本地工具承担此类任务。

**设计理念**:
- **高级人才高效用**: LLM应专注于高价值的推理、决策与创造工作
- **工具分担基础任务**: 文本归纳、数据校验、格式转换等交给本地工具
- **认知负荷最小化**: 减少LLM处理的信息量和任务复杂度

**任务分工**:

**LLM应该做的** ✅:
- 复杂推理与决策(如架构设计、方案评估)
- 创造性工作(如生成代码、撰写文档)
- 语义理解与转换(如需求分析、意图识别)
- 跨领域知识整合

**工具应该做的** ✅:
- 文本归纳与摘要(基于规则的简单归纳)
- 数据校验与格式检查(JSON/XML/YAML验证)
- 编码转换与文件处理(UTF-8/GBK转换)
- 统计计算与数据聚合(计数、求和、平均)
- 正则匹配与文本替换

**典型场景优化**:

**场景1: 文件内容归纳**
```python
# ❌ 错误:让LLM做简单归纳
llm.generate(f"请归纳以下内容(5000字符): {content}")

# ✅ 正确:工具先处理,LLM做高级分析
from tools.text_summarizer import TextSummarizer
summary = TextSummarizer.extract_key_points(content)  # 本地工具
analysis = llm.generate(f"请分析关键点: {summary}")  # LLM做高级分析
```

**场景2: 数据校验**
```python
# ❌ 错误:让LLM校验JSON格式
llm.generate(f"这个JSON是否有效: {json_str}")

# ✅ 正确:工具直接校验
import json
try:
    data = json.loads(json_str)
    is_valid = True
except json.JSONDecodeError as e:
    is_valid = False
    error_msg = str(e)
```

**场景3: 文本提取**
```python
# ❌ 错误:让LLM提取结构化信息
llm.generate(f"从以下日志中提取错误信息: {log}")

# ✅ 正确:正则表达式直接提取
import re
errors = re.findall(r'ERROR: (.*)', log)
```

**效果评估**:
- TOKEN消耗减少: 约40-60%
- 响应速度提升: 本地工具处理快10-100倍
- 准确性提升: 规则型任务准确率100%
- 成本降低: 减少LLM API调用次数

**实施策略**:
1. 识别高频基础任务,评估工具化可行性
2. 开发或集成对应的本地工具
3. 重构智能体逻辑,先调用工具后使用LLM
4. 监控TOKEN消耗,验证优化效果

**典型错误** ❌:
- 所有任务都让LLM处理,导致成本高昂
- 简单的正则匹配也调用LLM
- 未评估任务复杂度就使用LLM

**正确做法** ✅:
- 基础任务优先使用工具
- 复杂推理才调用LLM
- 工具与LLM协同工作

**与其他规则的关系**:
- 与"工具黑箱化原则"(规则4)协同:封装工具,智能体调用
- 与"简单优先原则"(规则1)协同:只用LLM处理必要的复杂任务

---

### 67. 非代码文本文件依赖索引机制

**核心规则**:
项目中的非代码文本文件(如JSON、系统提示词等)需通过静态分析或运行时追踪建立依赖索引,明确其被哪些模块或智能体引用。

**设计目的**:
- **可追溯性**: 明确每个文本文件的使用者
- **安全清理**: 识别无依赖的孤立文件
- **依赖分析**: 评估文件删除或修改的影响范围
- **自动维护**: 定期清理未使用的文本资产

**文本文件类型**:
- 系统提示词(prompts/*.md, prompts/*.txt)
- 配置文件(config/*.json, config/*.yaml)
- 数据文件(data/*.json)
- 文档模板(templates/*.md)
- 测试数据(tests/fixtures/*.json)

**索引方式**:

**方式一: 静态分析(编译时)**
```python
# tools/text_dependency_analyzer.py
import ast
import os
from pathlib import Path

class TextDependencyAnalyzer:
    def analyze_file_dependencies(self, project_root):
        dependencies = {}
        
        # 扫描所有Python文件
        for py_file in Path(project_root).rglob('*.py'):
            tree = ast.parse(py_file.read_text())
            
            # 查找文件路径引用
            for node in ast.walk(tree):
                if isinstance(node, ast.Str):  # 字符串常量
                    if self._is_file_path(node.s):
                        dependencies.setdefault(node.s, []).append(str(py_file))
        
        return dependencies
```

**方式二: 运行时追踪(动态监控)**
```python
# tools/runtime_file_tracker.py
import functools
import json

class RuntimeFileTracker:
    _access_log = {}
    
    @classmethod
    def track_file_access(cls, func):
        @functools.wraps(func)
        def wrapper(file_path, *args, **kwargs):
            # 记录文件访问
            caller = inspect.stack()[1]
            cls._access_log.setdefault(file_path, []).append({
                'caller_file': caller.filename,
                'caller_function': caller.function,
                'timestamp': datetime.now().isoformat()
            })
            return func(file_path, *args, **kwargs)
        return wrapper
    
    @classmethod
    def save_access_log(cls):
        with open('data/file_access_log.json', 'w') as f:
            json.dump(cls._access_log, f, indent=2)
```

**索引数据结构**:
```json
{
  "prompts/system_architect_prompt.md": {
    "referenced_by": [
      "src/system_architect.py:__init__",
      "src/agent_manager.py:create_architect"
    ],
    "last_accessed": "2025-12-09T15:30:45",
    "access_count": 127,
    "status": "active"
  },
  "prompts/deprecated_prompt.txt": {
    "referenced_by": [],
    "last_accessed": "2025-10-15T08:20:10",
    "access_count": 0,
    "status": "orphan"  # 孤立文件,可清理
  }
}
```

**清理策略**:
- **孤立文件**: `referenced_by` 为空 → 标记为候选清理
- **低活性文件**: `access_count` < 5 且 `last_accessed` > 60天 → 归档到backup
- **测试数据**: 标记为 `test_*` 且无依赖 → 安全删除

**实施流程**:
1. 夜间维护调度器定期执行依赖分析
2. 生成依赖报告(data/text_dependency_report.json)
3. 识别孤立文件,记录到日志
4. 系统维护师审查报告,确认清理列表
5. 人工确认后执行清理,备份到backup目录

**典型错误** ❌:
- 直接删除"看起来没用"的文件,导致系统故障
- 未建立依赖索引,不知道文件是否被使用
- 手动维护依赖关系,容易遗漏

**正确做法** ✅:
- 自动化分析文件依赖
- 定期生成依赖报告
- 安全清理孤立文件

**与其他规则的关系**:
- 与"简单优先原则"(规则1)协同:清理冗余文本资产
- 与"代码代谢原则"(规则50)协同:淘汰无用文本文件

---

### 68. 智能体文件读取能力优化要求

**核心规则**:
智能体的文件读取能力需优化,不应依赖人工指定文件路径与类型,应通过工具链自动识别文件位置、格式及编码,并具备错误恢复机制。

**设计目标**:
- **自动定位**: 智能体根据文件名或描述自动找到文件
- **格式识别**: 自动识别文件类型(TXT/JSON/DOCX/MD等)
- **编码检测**: 自动检测并使用正确的编码(UTF-8/GBK等)
- **容错处理**: 读取失败时自动尝试备选方案

**当前问题**:
- 智能体需要人工提供完整文件路径
- 无法自动识别文件格式
- 编码错误时直接失败,无降级方案
- 缺少模糊匹配能力

**优化方案**:

**1. 智能文件定位**
```python
# tools/smart_file_locator.py
class SmartFileLocator:
    def locate_file(self, file_hint: str, search_dirs: List[str]):
        """
        根据文件提示智能定位文件
        
        Args:
            file_hint: 文件名或描述(如"系统架构师提示词")
            search_dirs: 搜索目录列表
        
        Returns:
            Path: 匹配的文件路径
        """
        # 1. 精确匹配文件名
        exact_match = self._find_exact_match(file_hint, search_dirs)
        if exact_match:
            return exact_match
        
        # 2. 模糊匹配文件名
        fuzzy_matches = self._find_fuzzy_matches(file_hint, search_dirs)
        if len(fuzzy_matches) == 1:
            return fuzzy_matches[0]
        
        # 3. 基于关键词搜索文件内容
        content_matches = self._search_by_keywords(file_hint, search_dirs)
        if content_matches:
            return content_matches[0]  # 返回最佳匹配
        
        raise FileNotFoundError(f"无法定位文件: {file_hint}")
```

**2. 自动格式识别**
```python
# tools/smart_file_reader.py
class SmartFileReader:
    def read_file(self, file_path: Path):
        """
        智能读取文件,自动识别格式与编码
        """
        # 1. 根据扩展名识别格式
        ext = file_path.suffix.lower()
        
        if ext == '.json':
            return self._read_json(file_path)
        elif ext == '.docx':
            return self._read_docx(file_path)
        elif ext in ['.txt', '.md']:
            return self._read_text(file_path)
        else:
            # 未知格式,尝试作为文本读取
            return self._read_text(file_path)
    
    def _read_text(self, file_path: Path):
        # 多编码自动检测(规则63)
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"无法解析文件编码: {file_path}")
```

**3. 错误恢复机制**
```python
# 智能体调用示例
class BaseAgent:
    def read_file_smart(self, file_hint: str):
        """
        智能读取文件,自动处理各种异常
        """
        try:
            # 1. 定位文件
            file_path = self.locator.locate_file(file_hint, self.search_dirs)
            
            # 2. 读取文件
            content = self.reader.read_file(file_path)
            
            logger.info(f"成功读取文件: {file_path}")
            return content
            
        except FileNotFoundError as e:
            # 文件不存在,尝试搜索相似文件
            suggestions = self.locator.suggest_similar_files(file_hint)
            logger.warning(f"文件未找到: {file_hint}, 相似文件: {suggestions}")
            return None
        
        except UnicodeDecodeError as e:
            # 编码错误,尝试二进制读取
            logger.error(f"编码错误: {file_path}, 尝试二进制模式")
            return self._read_as_binary(file_path)
        
        except Exception as e:
            # 其他错误,记录并返回None
            logger.error(f"读取文件失败: {file_hint}, 错误: {e}")
            return None
```

**使用示例**:
```python
# ❌ 旧方式:需要完整路径
content = agent.read_file('e:/RAG系统/prompts/system_architect_prompt.md')

# ✅ 新方式:智能定位
content = agent.read_file_smart('系统架构师提示词')
content = agent.read_file_smart('architect prompt')
content = agent.read_file_smart('架构师')
```

**性能优化**:
- 缓存文件路径映射,避免重复搜索
- 索引常用文件,加速定位
- 异步读取大文件,避免阻塞

**典型错误** ❌:
- 智能体每次都要求用户提供完整路径
- 编码错误直接崩溃,无容错处理
- 无法处理文件重命名或移动

**正确做法** ✅:
- 智能定位文件,支持模糊匹配
- 自动检测格式与编码
- 多级容错,提供降级方案

**与其他规则的关系**:
- 与"多编码自动检测机制"(规则63)协同:自动处理编码问题
- 与"智能体自主决策"(规则42)协同:减少人工介入

---

### 69. 记忆偏好自动写入系统设置

**核心规则**:
当通过对话达成用户偏好共识后,应将关键记忆(如语言偏好、沟通风格)自动同步至系统设置项中,实现记忆沉淀与配置自动化。

**设计目的**:
- **减少重复判断**: 偏好固化后无需每次重新推断
- **提升响应效率**: 直接读取配置,降低认知负荷
- **一致性保障**: 所有智能体共享统一的用户偏好
- **持久化存储**: 偏好在会话间保持,不因重启丢失

**偏好类型**:

**1. 语言偏好**
- 用户主要使用的语言(中文/英文)
- 技术术语处理方式(保留英文/全部中文)
- 代码注释语言偏好

**2. 沟通风格**
- 详细程度(简洁/详细/极详细)
- 思维过程展示(显示/隐藏)
- 确认频率(每步确认/关键节点确认/无需确认)

**3. 工作习惯**
- 任务优先级偏好(速度优先/质量优先)
- 错误处理方式(自动修复/人工确认)
- 文件组织方式(按类型/按时间/按项目)

**实施流程**:

**1. 偏好识别**
```python
# src/preference_detector.py
class PreferenceDetector:
    def detect_preference_from_conversation(self, conversation_history):
        """
        从对话历史中识别用户偏好
        """
        preferences = {}
        
        # 分析语言偏好
        if self._user_prefers_chinese(conversation_history):
            preferences['language'] = 'zh-CN'
        
        # 分析沟通风格
        if self._user_prefers_concise(conversation_history):
            preferences['communication_style'] = 'concise'
        
        # 分析确认频率
        if self._user_dislikes_frequent_confirmation(conversation_history):
            preferences['confirmation_frequency'] = 'low'
        
        return preferences
```

**2. 偏好同步**
```python
# src/preference_manager.py
class PreferenceManager:
    def sync_preferences_to_settings(self, preferences: dict):
        """
        将偏好同步到系统设置
        """
        settings_file = Path('config/user_preferences.json')
        
        # 读取现有设置
        if settings_file.exists():
            current_settings = json.loads(settings_file.read_text())
        else:
            current_settings = {}
        
        # 合并新偏好
        current_settings.update(preferences)
        current_settings['last_updated'] = datetime.now().isoformat()
        
        # 写入文件
        settings_file.write_text(json.dumps(current_settings, indent=2, ensure_ascii=False))
        
        logger.info(f"偏好已同步到系统设置: {list(preferences.keys())}")
```

**3. 偏好应用**
```python
# 智能体读取偏好
class BaseAgent:
    def __init__(self):
        self.preferences = PreferenceManager().load_preferences()
    
    def generate_response(self, prompt: str):
        # 根据偏好调整响应风格
        if self.preferences.get('communication_style') == 'concise':
            prompt += "\n\n请以简洁方式回答,避免冗长解释。"
        
        if self.preferences.get('language') == 'zh-CN':
            prompt += "\n\n请使用中文回答。"
        
        return self.llm.generate(prompt)
```

**配置文件示例**:
```json
{
  "language": "zh-CN",
  "communication_style": "concise",
  "confirmation_frequency": "low",
  "thinking_process_display": false,
  "error_handling": "auto_fix",
  "task_priority": "quality_first",
  "last_updated": "2025-12-09T15:45:30"
}
```

**自动触发机制**:
- 系统管家检测到3次以上相同偏好表达 → 提议固化为设置
- 用户明确表达偏好(如"我喜欢简洁回答") → 立即同步
- 智能体工作日志记录偏好相关事件 → 定期分析与更新

**典型场景**:
```python
# 场景1: 语言偏好固化
用户: "请用中文回答"
系统: "好的,我已将中文设为默认语言偏好"
# → 自动写入 config/user_preferences.json

# 场景2: 沟通风格固化
用户: "别这么啰嗦,简洁点"
系统: "收到,已设置为简洁沟通模式"
# → 自动写入 communication_style: "concise"
```

**典型错误** ❌:
- 每次对话都重新推断用户偏好,浪费TOKEN
- 偏好只存在智能体记忆里,重启后丢失
- 不同智能体对同一用户的偏好理解不一致

**正确做法** ✅:
- 偏好自动固化到配置文件
- 所有智能体共享统一偏好
- 定期分析对话,更新偏好

**与其他规则的关系**:
- 与"主-分支对话窗口记忆管理"(规则23)协同:偏好精炼为泡泡后固化
- 与"智能体自主决策"(规则42)协同:智能体主动识别并固化偏好

---

### 70. 禁止优雅降级与伪能力实现原则

**核心规则**:
智能体系统严禁使用"优雅降级"或模拟实现来伪装功能,必须依赖真实的LLM API调用。没有LLM参与的组件只能算工具,不能称为智能体。

**设计理念**:
- **真实性优先**: 智能体必须具备真实的LLM处理能力,不得用固定文本或规则引擎伪装
- **避免虚假信息**: 降级实现会产生"伪能力",让系统行为不可预测
- **明确状态**: 代码只有两种状态——正常和不正常,不应存在"降级正常"的中间态
- **LLM是灵魂**: 没有LLM的智能体没有处理中心,没有灵魂

**禁止行为** ❌:
```python
# ❌ 错误: 使用降级文本回复伪装成智能回复
def respond(self, message):
    if not self.llm_client:
        # 降级到固定文本
        return {
            "type": "text_reply",
            "reply": "抱歉,我正在处理您的请求...",  # 伪装成智能回复
        }
```

**正确做法** ✅:
```python
# ✅ 正确: LLM不可用时返回显式错误
def respond(self, message):
    if not self.llm_client:
        return {
            "type": "error",
            "error": "LLM未就绪或未配置API密钥",  # 明确告知错误
            "timestamp": datetime.now().isoformat(),
        }
    
    # 只有LLM可用时才生成真实回复
    try:
        reply_text = self.llm_client.chat_completion(messages)
        return {
            "type": "text_reply",
            "reply": reply_text,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "type": "error",
            "error": f"LLM调用异常: {str(e)}",
        }
```

**允许的后备计划(Backup Plan, 非优雅降级)** ✅:
> 为避免混淆,这里专门澄清:**后备计划 ≠ 优雅降级**。
>
> - **后备计划**: 在**仍然使用真实LLM**的前提下,从主服务商切换到备份服务商或同等级引擎,属于**等价替换**;
> - **优雅降级(本规则禁止的)**: 从真实LLM退化为规则引擎、固定模板、统一文案等伪能力,属于**能力缩水**和行为伪装。

**后备计划的正确示例** ✅:
```python
# ✅ 正确: 故障转移到备用LLM(仍然是真实LLM)
def chat_completion(self, messages):
    try:
        # 尝试主服务商
        return self._call_primary_llm(messages)
    except (Timeout, ConnectionError, ServiceUnavailable) as e:
        logger.warning(f"主LLM服务商故障: {e}, 切换到备用服务商")
        # 切换到备用LLM服务商,仍然是真实调用
        return self._call_backup_llm(messages)
```

**后备计划的边界说明**:
- ✅ 允许: DeepSeek → Qwen、主区域 → 备区域、主实例 → 备实例;
- ✅ 允许: 在保持"真实LLM参与"前提下做故障转移/负载均衡;
- ❌ 禁止: DeepSeek/Qwen挂了以后,改用 if/else + 模板字符串拼装回复;
- ❌ 禁止: LLM不可用时继续返回看起来"智能"的固定答复(例如"我正在思考...")。

**设计目的**:
- 确保智能体行为的真实性与一致性
- 避免"虚假能力"导致用户误判系统能力
- 保持系统状态清晰,故障时明确报错
- 防止降级逻辑积累成技术债

**典型错误案例**:
- 基类智能体使用 `_fallback_reply()` 生成固定格式文本,伪装成智能回复
- LLM不可用时返回"我正在思考..."等模糊回复,让用户误以为系统正常

**与其他规则的关系**:
- 与"工具模块免费优先"(规则64)协同: 免费模式应明确告知,不应伪装成收费能力
- 与"零信任原则"(规则2)协同: 不信任降级逻辑,必须验证LLM是否真实可用
- 与"系统健全性优先"(规则31)协同: 健全性要求所有代码都能产生实际作用,而非伪装

---

### 71. 分片处理多级递进策略

**核心规则**:
分片处理应采用多级递进策略,从无模型分片到大模型精炼,再到困惑度计算,最终兜底为强制分片。

**设计理念**:
- **成本优先**: 优先使用低成本方案(信息熵)
- **效果保障**: 低成本方案失败时升级到高成本方案(大模型)
- **兜底机制**: 确保任何文本都能被成功分片
- **性能平衡**: 在成本与质量间找到最优平衡点

**五级递进策略**:

**级别1: 信息熵分片(无模型)**
```python
def entropy_based_chunking(text: str, max_chunk_size: int):
    """
    基于信息熵的无模型分片
    - 成本: 几乎为0
    - 速度: 极快
    - 适用: 70%的普通文本
    """
    chunks = []
    current_chunk = []
    
    for sentence in split_sentences(text):
        entropy = calculate_entropy(sentence)
        
        if entropy < threshold and len(current_chunk) < max_chunk_size:
            current_chunk.append(sentence)
        else:
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
    
    return chunks
```

**级别2: 大模型精炼分片**
```python
def llm_refined_chunking(text: str, max_chunk_size: int):
    """
    使用大模型进行文本精炼与再分段
    - 成本: 中等(每次调用约0.01元)
    - 速度: 较慢
    - 适用: 复杂文本,信息熵方法失败后
    """
    # 1. 先用工具预处理
    preprocessed = preprocess_text(text)
    
    # 2. 调用LLM进行语义分段
    prompt = f"""
    请将以下文本按语义完整性分段,每段不超过{max_chunk_size}字符:
    
    {preprocessed}
    
    要求:
    1. 保持每段语义完整
    2. 段落间逻辑连贯
    3. 返回JSON格式: {{"chunks": ["段落1", "段落2", ...]}}
    """
    
    response = llm.generate(prompt)
    chunks = json.loads(response)['chunks']
    
    # 3. 递归分片过长的段落
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            final_chunks.extend(entropy_based_chunking(chunk, max_chunk_size))
        else:
            final_chunks.append(chunk)
    
    return final_chunks
```

**级别3: 困惑度计算分片**
```python
def perplexity_based_chunking(text: str, max_chunk_size: int):
    """
    基于困惑度的复合分片
    - 成本: 较高(需要加载本地模型)
    - 速度: 中等
    - 适用: 专业文本,大模型分片失败后
    """
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    
    chunks = []
    current_chunk = []
    
    for sentence in split_sentences(text):
        # 计算困惑度
        inputs = tokenizer(sentence, return_tensors='pt')
        outputs = model(**inputs, labels=inputs['input_ids'])
        perplexity = torch.exp(outputs.loss)
        
        # 困惑度高 = 语义断点
        if perplexity > threshold:
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
        else:
            current_chunk.append(sentence)
    
    return chunks
```

**级别4: 强制分片(兜底)**
```python
def force_chunking(text: str, max_chunk_size: int):
    """
    强制按大小分片,确保一定成功
    - 成本: 0
    - 速度: 极快
    - 适用: 所有其他方法失败后的兜底
    """
    chunks = []
    for i in range(0, len(text), max_chunk_size):
        chunks.append(text[i:i+max_chunk_size])
    
    logger.warning(f"使用强制分片,可能破坏语义完整性")
    return chunks
```

**完整流程**:
```python
def adaptive_chunking(text: str, max_chunk_size: int, max_recursion: int = 3):
    """
    自适应分片,自动选择最优策略
    """
    recursion_level = 0
    
    while recursion_level < max_recursion:
        try:
            # 级别1: 信息熵分片
            chunks = entropy_based_chunking(text, max_chunk_size)
            if validate_chunks(chunks, max_chunk_size):
                logger.info(f"信息熵分片成功,共{len(chunks)}段")
                return chunks
            
            # 级别2: 大模型精炼
            chunks = llm_refined_chunking(text, max_chunk_size)
            if validate_chunks(chunks, max_chunk_size):
                logger.info(f"大模型精炼分片成功,共{len(chunks)}段")
                return chunks
            
            # 级别3: 困惑度计算
            chunks = perplexity_based_chunking(text, max_chunk_size)
            if validate_chunks(chunks, max_chunk_size):
                logger.info(f"困惑度分片成功,共{len(chunks)}段")
                return chunks
            
            recursion_level += 1
            
        except Exception as e:
            logger.error(f"分片失败(级别{recursion_level}): {e}")
            recursion_level += 1
    
    # 级别4: 强制分片(兜底)
    chunks = force_chunking(text, max_chunk_size)
    logger.warning(f"所有高级分片策略失败,使用强制分片")
    return chunks
```

**失败日志记录**(规则27):
```python
def log_chunking_failure(text: str, strategies_tried: List[str]):
    """
    记录分片失败详情,用于系统优化
    """
    failure_info = {
        'file_hash': hashlib.md5(text.encode()).hexdigest(),
        'text_length': len(text),
        'strategies_tried': strategies_tried,
        'failure_reason': '所有策略均失败',
        'suggestion': '考虑增加max_chunk_size或优化文本预处理',
        'timestamp': datetime.now().isoformat()
    }
    
    # 通过泡泡机制持久化
    BubbleStorage.save_bubble('chunking_failure', failure_info)
```

**性能统计**:
- 级别1成功率: 约70%
- 级别2成功率: 约95%
- 级别3成功率: 约99%
- 级别4成功率: 100%

**典型错误** ❌:
- 所有文本都用大模型分片,成本高昂
- 没有兜底机制,导致分片彻底失败
- 不记录失败信息,无法优化

**正确做法** ✅:
- 优先使用低成本方案
- 失败时逐级升级策略
- 记录失败详情供系统学习

**与其他规则的关系**:
- 与"降低LLM认知负荷"(规则66)协同:优先使用本地工具
- 与"分片失败日志记录规范"(规则27)协同:记录失败详情

---

### 72. 服务器启动状态自曝光机制与信息对齐原则

**核心规则**:
服务器启动时必须将完整的启动状态（端口、PID、智能体列表、向量库统计、知识图谱统计等）自曝光到结构化JSON文件，实现人类与AI的信息对齐，避免AI陷入控制台日志黑箱。

**设计理念**:
- **信息对齐**: 人类通过控制台日志理解系统启动，AI通过JSON文件获取相同信息
- **共享真相源**: `startup_status.json` 作为唯一权威数据源（Single Source of Truth）
- **调试效率**: AI和人类基于同一份数据讨论问题，避免手动复制信息
- **状态追溯**: 支持系统维护师智能体通过读取JSON进行状态诊断

**必需字段**:
```json
{
  "timestamp": "2025-12-12T19:04:58",
  "server_type": "rag_main",
  "port": 5673,
  "pid": 27320,
  "agents": {
    "count": 5,
    "list": [{"name": "构架师", "role": "architect", "agent_id": "architect"}, ...]
  },
  "vector_database": {
    "total_memories": 1224,
    "active_memories": 1000,
    "archived_memories": 200,
    "retired_memories": 24
  },
  "knowledge_graph": {
    "total_nodes": 1224,
    "total_edges": 3500,
    "coverage_rate": 100.0
  },
  "thought_engine": {
    "total_nodes": 111,
    "deduplication_rate": 0.85
  },
  "status": "active",
  "startup_complete": true
}
```

**性能优化要求**:
- **避免重复构建**: 全量JSON写入阶段应使用缓存数据（`force_refresh=False`），避免重复触发耗时的知识图谱全量构建
- **时机控制**: 全量JSON写入必须在夜间维护调度器启动之后、`httpd.serve_forever()` 之前执行
- **独立异常处理**: 全量JSON写入逻辑必须有独立的try-except块，不受其他组件异常影响

**典型错误** ❌:
- 调用 `get_system_statistics(force_refresh=True)` 导致30+秒阻塞
- JSON写入逻辑被夹在其他组件的异常处理块内部
- 只写入简单状态，缺少关键信息（端口、PID、智能体、向量库等）

**正确做法** ✅:
```python
# 全量JSON写入（独立块）
print("\n🔍 开始更新全量启动状态JSON...")
try:
    # 使用缓存，避免重复构建
    stats_service = get_system_statistics_service()
    system_stats = stats_service.get_system_statistics(force_refresh=False)
    
    # 构建完整的启动状态
    full_startup_status = {
        "timestamp": datetime.now().isoformat(),
        "port": port,
        "pid": os.getpid(),
        "agents": {...},
        "vector_database": {...},
        "knowledge_graph": {...},
        # ...
    }
    
    # 写入文件
    with open(STARTUP_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_startup_status, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 全量启动状态已更新: 端口={port}, PID={os.getpid()}")
except Exception as e:
    logger.error(f"❌ 更新全量启动状态失败: {e}")
    traceback.print_exc()
```

**与其他规则的关系**:
- 与"组件自曝光协议"(规则33)协同: 服务器状态自曝光是自曝光协议在系统级的应用
- 与"服务器日志结构化输出"(规则61)协同: JSON文件是结构化输出的典型形式
- 与"统一数据源引用原则"(规则22)协同: `startup_status.json` 作为服务器状态的唯一权威源

**相关文件**:
- `/rag_main_server.py` (第1654-1740行: 全量JSON写入逻辑)
- `/logs/startup_status.json` (权威数据源)
- `/src/system_statistics_service.py` (统计数据提供者)

---



# 附录

### 规则演化记录

本文档会随着项目发展持续更新。每次更新时,请在此记录变更:

- **2025-12-09**: 初始版本创建,包含14条核心规则
- **2025-12-09**: 新增第15-17条规则,补充组件自暴光协议、双服务器架构边界与静态服务器异常处理
- **2025-12-09**: 新增第22-24条规则,补充多智能体协作与功能智能体自主决策机制
- **2025-12-09**: 新增第25-28条规则,补充代码交付双重验证、知识图谱全覆盖、多智能体一致性协作与行动优先原则
- **2025-12-09**: 新增"数据处理逻辑矛盾求真原则",强化系统健全性与求真要求
- **2025-12-09**: 新增"统一数据源引用原则",确保统计指标与展示数据的一致性
- **2025-12-09**: 新增"文档与代码一致性核对机制",要求定期比对DOCS文档与实际实现
- **2025-12-09**: 新增"防上下文腐烂机制的文档闭环与实现流程"占位说明,后续细化到上下文管理专项文档
- **2025-12-09**: 新增第29-34条规则,补充引导式教化原则、工具注册自检、并行任务上下文一致性、代码代谢原则、多智能体@机制协议错误检测与临时智能体演化固化流程
- **2025-12-09**: 新增第35-37条规则,补充防止历史数据重复向量化标记机制、记忆重构中逻辑链完整性补全机制、功能智能体与基类智能体的代码复用边界
- **2025-12-09**: 新增第38-40条规则,补充三层记忆库架构与数据迁移规则、智能体事后检查行为规范、用户无本地执行能力适配规则
- **2025-12-09**: 新增第41-45条规则,补充功能实施后验证与清理流程、显示问题修复原则、服务器日志结构化输出、启动测试服务可达性验证、多编码自动检测机制
- **2025-12-09**: 新增核心原则第4条"工具黑箱化原则"与"文件处理规范"章节(规则9-14),基于文件上传功能黑箱化改造经验补充:二进制文件识别(38种类型)、大文件截断机制(100KB)、DOCX文件支持、性能监控、multipart手动解析、绝对路径支持的6条文件处理规范
- **2025-12-09**: 新增"系统启动与运行规范"章节(规则5-8)和"Python代码规范"章节(规则13-15),基于系统启动问题修复经验补充:系统启动依赖检查、记忆重构执行时机控制(四重保护机制)、24小时制时间格式、批处理脚本编码安全、Python相对/绝对导入规范、OpenCV路径处理、开发文档管理的9条规则
- **2025-12-09**: 新增第70条规则"禁止优雅降级与伪能力实现原则",明确智能体必须依赖真实LLM而非模拟实现,避免产生虚假信息和伪能力;同时区分允许的故障转移(切换到备用LLM)与禁止的伪降级(切换到规则引擎)
- **2025-12-09**: 修订第46条规则"行动优先:代码修改重于口头响应",澄清"口头交互"的真实含义:禁止的是"在交互栏里不停说话但不写代码/文档",而非禁止创建技术文档;明确行动优先原则的核心是"用实际产出说话,而非空谈",产出既包括代码也包括文档
- **2025-12-09**: 修订第4条规则"工具黑箱化原则",明确LLM认知减负的两大维度架构:工具外置/黑箱化(减少代码逻辑复杂度)+提示词外置(减少上下文加载量),两者协同构成完整的LLM认知减负体系,与规则15(提示词管理)和规则66(工具具现化)形成三角协同
- **2025-12-09**: 二次修订第4条规则,补充"根本设计哲学"部分,明确"LLM认知减负是智能体构建的核心目标",阐述项目中所有架构设计(多智能体架构、临时智能体、主-分支窗口、自曝光协议、上下文压缩算法、RAG检索、工具外置、提示词外置)均围绕这一根本目的,形成完整的认知减负技术地图,将分散的技术手段统一到根本设计哲学下
- **2025-12-12**: 新增第72条规则"服务器启动状态自曝光机制与信息对齐原则",基于启动状态JSON写入性能问题修复经验,明确要求服务器启动时将完整状态自曝光到JSON文件,实现人类与AI的信息对齐;强调避免在启动流程中重复触发耗时操作(如知识图谱全量构建),应使用缓存数据(`force_refresh=False`)优化性能

### 相关文档

- 组件自曝光协议详细规范: `/docs/SELF_EXPOSE_PROTOCOL.md` (待创建)
- 智能体开发指南: `/docs/AGENT_DEVELOPMENT.md` (待创建)
- 记忆管理系统架构: `/docs/MEMORY_ARCHITECTURE.md` (待创建)
- 智能体行为根本规范: 要对自己的判断力有绝对自信，对自己的记忆力保持绝对谦卑 (创世级提示词)

---

**最后更新**: 2025-12-09
**维护者**: RAG系统开发团队
**版本**: v1.1.0
