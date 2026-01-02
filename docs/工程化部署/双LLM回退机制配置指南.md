# 双LLM回退机制配置指南

## 📋 问题诊断

你遇到的"LLM未返回结果"问题根因：

1. **只配置了一个LLM服务商**（千问），当它失效时没有备选方案
2. **缺少自动回退逻辑**，之前代码中LLM调用失败后直接返回None
3. **错误信息不够详细**，无法快速定位是超时、限流还是API key失效

---

## ✅ 已完成的修复

### 1. **增强LLMClientEnhanced**（`src/llm_client_enhanced.py`）

#### 新增功能：
- ✅ **自动回退机制**：当主LLM失败时自动切换到备用LLM
- ✅ **多服务商支持**：初始化时可检测所有已配置的服务商
- ✅ **详细错误日志**：区分超时、连接错误、限流等不同场景
- ✅ **智能重试**：失败后短暂等待再重试（避免立即重试触发限流）

#### 关键改动：
```python
# 新参数：enable_fallback（默认True）
client = LLMClientEnhanced(enable_fallback=True)

# 调用流程：
# 1. 尝试主provider（如qianwen）
# 2. 失败后自动遍历其他可用provider（如deepseek）
# 3. 找到可用的后自动切换并记录
```

---

### 2. **增强chat_api错误处理**（`api/chat_api.py`）

#### 新增功能：
- ✅ **详细初始化日志**：记录LLM客户端启动过程
- ✅ **区分配置错误和运行时错误**：密钥未配置vs API调用失败
- ✅ **友好的错误提示**：告诉用户具体检查什么（API key/网络/限流）
- ✅ **显示当前使用的provider**：用户可以看到是哪个LLM在响应

#### 日志示例：
```
🛠️ 正在初始化LLM客户端...
✅ LLM客户端初始化成功，使用provider: qianwen
🤖 开始调用LLM生成响应...
⚠️ qianwen 调用失败，切换到 deepseek...
✅ deepseek 调用成功
✅ LLM响应成功，使用provider: deepseek，响应长度: 234
```

---

## 🔧 配置多个LLM服务商

### 方法1：手动编辑配置文件

编辑 `config/api_keys.json`，添加至少两个LLM：

```json
{
  "qianwen": {
    "key": "sk-ca5cbb1572724063ae886b8012aa0541",
    "description": "字节跳动千问API密钥（主LLM）",
    "added_time": "2025-12-03"
  },
  "deepseek": {
    "key": "你的DeepSeek API密钥",
    "description": "DeepSeek API密钥（备用LLM）",
    "added_time": "2025-12-03"
  }
}
```

### 方法2：使用API密钥管理工具

运行以下命令添加密钥：

```bash
python tools/api_key_tool.py add deepseek
```

---

## 📊 支持的LLM服务商

当前系统支持以下服务商（按推荐优先级）：

| 服务商 | API端点 | 推荐场景 | 获取密钥 |
|--------|---------|---------|----------|
| **qianwen** | 字节跳动千问 | 中文对话，低成本 | [豆包官网](https://console.volcengine.com/) |
| **deepseek** | DeepSeek AI | 代码生成，推理能力 | [DeepSeek官网](https://platform.deepseek.com/) |
| **openai** | OpenAI GPT | 通用能力，英文优势 | [OpenAI官网](https://platform.openai.com/) |
| **anthropic** | Claude | 长文本，安全性 | [Anthropic官网](https://console.anthropic.com/) |
| **google** | Gemini | 多模态 | [Google AI Studio](https://ai.google.dev/) |

---

## 🧪 测试回退机制

### 运行诊断脚本

```bash
python test_llm_fallback.py
```

### 预期输出

```
============================================================
1. 测试API密钥配置
============================================================

已配置的API密钥: ['qianwen', 'deepseek']

支持的LLM端点: ['deepseek', 'openai', 'anthropic', 'google', 'qianwen']

密钥状态检查:
  deepseek: ✅ 已配置
  openai: ❌ 未配置
  anthropic: ❌ 未配置
  google: ❌ 未配置
  qianwen: ✅ 已配置

============================================================
2. 测试单个LLM调用
============================================================

默认服务商: qianwen

正在创建 qianwen 客户端...
✅ 客户端创建成功

发起测试请求...
✅ LLM调用成功
响应内容: 在线

============================================================
3. 测试可用服务商检测
============================================================

可用的LLM服务商: ['qianwen', 'deepseek']

✅ 成功：有 2 个服务商可用，可以实现回退机制
```

---

## 🚨 常见问题排查

### Q1：为什么千问突然"未返回结果"？

**可能原因：**
1. **内容审核**：你提到的"二元对立衍生第三态，和"可能触发敏感词检测
2. **限流**：短时间内请求过多
3. **服务器故障**：千问API服务端临时故障
4. **网络超时**：网络波动导致60秒内未响应

**验证方法：**
查看后端日志（如果有），应该看到类似：
```
⏱️ qianwen 请求超时 (尝试 1/5)
⏱️ qianwen 请求超时 (尝试 2/5)
...
⚠️ qianwen 调用失败，切换到 deepseek...
```

---

### Q2：为什么两个LLM都"未返回结果"？

如果你确实配置了两个LLM但都失败，检查：

1. **API密钥是否有效**
   ```bash
   # 测试千问
   curl -X POST https://api.volcengine.com/v3/chat/completions \
     -H "Authorization: Bearer 你的千问key" \
     -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"hi"}]}'
   
   # 测试DeepSeek
   curl -X POST https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer 你的deepseek_key" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
   ```

2. **网络连接是否正常**
   ```bash
   ping api.volcengine.com
   ping api.deepseek.com
   ```

3. **查看详细错误日志**
   修改后端代码中的日志级别为DEBUG，重启服务器：
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

---

### Q3：如何手动测试LLM调用？

创建测试脚本：

```python
from src.llm_client_enhanced import LLMClientEnhanced

# 测试自动回退
client = LLMClientEnhanced(enable_fallback=True)
response = client.chat_completion([
    {"role": "user", "content": "你好"}
])

print(f"使用的provider: {client.provider}")
print(f"响应: {response}")
```

---

## 📈 性能与成本优化

### 回退优先级配置

修改 `config/system_config.py` 中的默认服务商顺序：

```python
LLM_CONFIG = {
    "default_provider": "qianwen",  # 主LLM（成本低）
    "fallback_order": ["deepseek", "openai"],  # 备用顺序
    "timeout": 60,
    "max_retries": 5,
}
```

### 成本对比（参考价格）

| 服务商 | 输入成本 | 输出成本 | 适合场景 |
|--------|---------|---------|---------|
| 千问 | ¥0.001/1K tokens | ¥0.002/1K tokens | 日常对话 |
| DeepSeek | ¥0.001/1K tokens | ¥0.002/1K tokens | 代码生成 |
| OpenAI GPT-3.5 | $0.0015/1K tokens | $0.002/1K tokens | 英文任务 |

---

## 🔒 安全建议

1. **不要提交API密钥到Git**
   ```bash
   # 确认 .gitignore 包含
   config/api_keys.json
   ```

2. **定期轮换密钥**
   ```bash
   python tools/api_key_tool.py remove qianwen
   python tools/api_key_tool.py add qianwen
   ```

3. **设置使用额度限制**
   在各服务商控制台设置每日/每月最大消费

---

## ✨ 后续优化方向

- [ ] 根据响应速度动态调整provider优先级
- [ ] 统计各provider的成功率，自动淘汰不可用的
- [ ] 支持本地LLM（Ollama/LM Studio）作为终极备选
- [ ] 实现负载均衡（多provider并行调用取最快）

---

**最后提醒：**  
现在你已经有了完整的回退机制，但务必**至少配置2个LLM服务商的API密钥**，否则回退机制无法工作！

建议配置：**千问（主） + DeepSeek（备）**，两者都有免费额度且在中文场景表现良好。
