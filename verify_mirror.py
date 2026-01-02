"""
终端输出与JSON文件完整镜像验证
对比终端显示的每一行与JSON中的日志记录
"""
import json

# 终端输出（用户提供的完整输出）
terminal_output = """导入多智能体聊天室模块成功
导入时机选择策略引擎成功
导入记忆重构引擎成功
✅ 从持久化存储加载了 111 个思维节点（真实数据）
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
导入夜间维护调度器成功
开始启动RAG系统服务器... 端口: 6666, PID: 14188
2025-12-12 22:39:50,694 - rag_system - INFO - 程序开始执行，端口: 6666, PID: 14188
2025-12-12 22:39:54,819 - rag_system - WARNING - 向静态服务器注册失败（静态服务器可能未运行）: HTTPConnectionPool(host='localhost', port=10808): Max retries exceeded with url: /api/server/register (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x00000213850CE270>: Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。'))
2025-12-12 22:39:54,819 - rag_system - INFO - 全局PORT已设置为: 6666
2025-12-12 22:39:54,820 - rag_system - INFO - 进入start_server函数
初始化聊天室...
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
2025-12-12 22:39:54,850 - MultiAgentChatroom - INFO - 通过发现机制创建智能体: system_architect_agent ->  系统管家
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
2025-12-12 22:39:54,852 - MultiAgentChatroom - INFO - 通过发现机制创建智能体: scheme_evaluator_agent ->  方案评估师
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
2025-12-12 22:39:54,853 - MultiAgentChatroom - INFO - 通过发现机制创建智能体: code_implementer_agent ->  文本实现师
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
2025-12-12 22:39:54,854 - MultiAgentChatroom - INFO - 通过发现机制创建智能体: data_collector_agent -> 数据收集师
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
⚠️ 默认服务商 qianwen 未配置，切换到 deepseek
2025-12-12 22:39:54,861 - MultiAgentChatroom - INFO - 通过发现机制创建智能体: system_maintenance_agent -> 系统维护师
2025-12-12 22:39:54,861 - MultiAgentChatroom - INFO - 通过智能体发现机制成功初始化 5 个智能体
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
2025-12-12 22:39:54,863 - AgentWindow_系统管家_window - INFO - 记忆重构引擎初始化成功
2025-12-12 22:39:54,863 - AgentWindow_系统管家_window - INFO - 智能体独立对话窗口初始化完成: 系统管家 (43b6a797-fc29-42a1-b63c-339d4ff0acb1)
2025-12-12 22:39:54,863 - AgentWindow_系统管家_window - INFO - 上下文管理配置: 最大长度=128000, 压缩阈值=0.8
2025-12-12 22:39:54,863 - MultiAgentChatroom - INFO - 创建智能体对话窗口: 系统管家
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
2025-12-12 22:39:54,865 - AgentWindow_方案评估师_window - INFO - 记忆重构引擎初始化成功
2025-12-12 22:39:54,865 - AgentWindow_方案评估师_window - INFO - 智能体独立对话窗口初始化完成: 方案评估师 (e41fd4e2-0544-4235-b160-2da20b3162c5)
2025-12-12 22:39:54,865 - AgentWindow_方案评估师_window - INFO - 上下文管理配置: 最大长度=128000, 压缩阈值=0.8
2025-12-12 22:39:54,865 - MultiAgentChatroom - INFO - 创建智能体对话窗口: 方案评估师
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
2025-12-12 22:39:54,867 - AgentWindow_文本实现师_window - INFO - 记忆重构引擎初始化成功
2025-12-12 22:39:54,867 - AgentWindow_文本实现师_window - INFO - 智能体独立对话窗口初始化完成: 文本实现师 (da1a0814-0a5c-4a9f-a993-01f834218d30)
2025-12-12 22:39:54,867 - AgentWindow_文本实现师_window - INFO - 上下文管理配置: 最大长度=128000, 压缩阈值=0.8
2025-12-12 22:39:54,867 - MultiAgentChatroom - INFO - 创建智能体对话窗口: 文本实现师
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
2025-12-12 22:39:54,868 - AgentWindow_数据收集师_window - INFO - 记忆重构引擎初始化成功
2025-12-12 22:39:54,869 - AgentWindow_数据收集师_window - INFO - 智能体独立对话窗口初始化完成: 数据收集师 (5d32ca12-099d-4196-8993-ea8cd84f5c9f)
2025-12-12 22:39:54,869 - AgentWindow_数据收集师_window - INFO - 上下文管理配置: 最大长度=128000, 压缩阈值=0.8
2025-12-12 22:39:54,869 - MultiAgentChatroom - INFO - 创建智能体对话窗口: 数据收集师
⚠️  人脸识别功能已禁用（避免启动警告）
视觉处理引擎初始化成功
音频处理引擎初始化成功
多模态融合引擎初始化成功
溯因推理引擎知识库初始化成功
分层学习引擎知识库初始化成功
2025-12-12 22:39:54,870 - AgentWindow_系统维护师_window - INFO - 记忆重构引擎初始化成功
2025-12-12 22:39:54,871 - AgentWindow_系统维护师_window - INFO - 智能体独立对话窗口初始化完成: 系统维护师 (f89836da-447f-4cab-bc80-14f018e54723)
2025-12-12 22:39:54,871 - AgentWindow_系统维护师_window - INFO - 上下文管理配置: 最大长度=128000, 压缩阈值=0.8
2025-12-12 22:39:54,871 - MultiAgentChatroom - INFO - 创建智能体对话窗口: 系统维护师
2025-12-12 22:39:54,871 - MultiAgentChatroom - INFO - 成功创建 5 个智能体对话窗口
2025-12-12 22:39:54,873 - MultiAgentChatroom - INFO - 从交互日志恢复 10 条历史消息
2025-12-12 22:39:54,873 - rag_system - INFO - 多智能体聊天室初始化成功
2025-12-12 22:39:54,874 - rag_system - INFO - 多智能体聊天室初始化成功（main server）
初始化时机选择策略引擎...
2025-12-12 22:39:54,875 - rag_system - INFO - 时机选择策略引擎初始化成功并启动监控
调度记忆重构任务...
2025-12-12 22:39:54,875 - rag_system - INFO - 记忆重构任务已调度
设置服务器...
2025-12-12 22:39:54,875 - rag_system - INFO - 创建TCPServer实例，监听 0.0.0.0:6666
2025-12-12 22:39:54,876 - rag_system - INFO - TCPServer实例创建成功
2025-12-12 22:39:54,876 - rag_system - INFO - 后端服务状态已设置为active
2025-12-12 22:39:54,876 - rag_system - INFO - RAG系统稳定版启动服务器，端口: 6666

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RAG系统稳定版已启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  重要提示:
1. 端口号是您的系统安全密钥，请妥善保管
2. 如需查看端口号，请查看日志文件: logs/startup_status.json
3. 打开浏览器访问启动页面即可使用系统


🌙 正在启动夜间维护调度器...
2025-12-12 22:39:54,877 - rag_system - INFO - 正在启动夜间维护调度器
🌙 夜间维护调度已启动 - 将在系统空闲时自动执行
🌙 注：每个任务每天只执行一次，通常在晚上22:00-6:00之间
✅ 夜间维护调度器已启动
   - 智能体将在系统空闲时（晚上22:00-6:00）自动写日记
   - 自动执行记忆重构和向量库更新
   - 明天可查看维护报告

2025-12-12 22:39:54,878 - rag_system - INFO - 夜间维护调度器启动成功

🔍 开始更新全量启动状态JSON...
2025-12-12 22:39:54,878 - rag_system - INFO - 🔍 开始更新全量启动状态JSON...
2025-12-12 22:39:54,891 - rag_system - INFO - ✅ 全量启动状态已更新: 端口=6666, PID=14188, 智能体=5, 向量库=1224条, 日志=132条, 重复日志=22处
✅ 系统初始化完成: 智能体=5, 向量库=1224条
⚠️  检测到 22 处日志重复问题（详见startup_status.json）
🚀 知识图谱异步初始化已启动（后台线程）
✅ 知识图谱持久化文件已存在，跳过重复构建
2025-12-12 22:39:54,893 - rag_system - INFO - 知识图谱持久化文件已存在，跳过重复构建""".strip().split('\n')

# 读取JSON文件
with open('logs/startup_status.json', encoding='utf-8') as f:
    data = json.load(f)

logs = data['startup_logs']['logs']

# 构建JSON日志的消息列表
json_messages = [log['message'] for log in logs]

print("=" * 80)
print("终端输出与JSON文件完整镜像验证")
print("=" * 80)

print(f"\n【统计信息】")
print(f"  终端输出行数: {len(terminal_output)}")
print(f"  JSON日志条数: {len(logs)}")

# 逐行对比
missing_in_json = []
extra_in_json = []

print(f"\n【逐行核对】")
for i, terminal_line in enumerate(terminal_output, 1):
    terminal_msg = terminal_line.strip()
    
    # 跳过空行
    if not terminal_msg:
        continue
    
    # 检查是否在JSON中
    if terminal_msg in json_messages:
        print(f"  ✅ 第{i}行 - 已匹配")
    else:
        # 尝试部分匹配（logging格式的日志）
        found = False
        for log in logs:
            if terminal_msg in f"{log['timestamp']} - {log['logger']} - {log['level']} - {log['message']}":
                print(f"  ✅ 第{i}行 - 已匹配（logging格式）")
                found = True
                break
        
        if not found:
            missing_in_json.append((i, terminal_msg))
            print(f"  ❌ 第{i}行 - JSON中缺失")

print(f"\n【缺失分析】")
if missing_in_json:
    print(f"  ⚠️  发现 {len(missing_in_json)} 条终端日志未被JSON捕获:")
    for line_no, msg in missing_in_json[:10]:  # 只显示前10条
        print(f"    {line_no}. {msg[:80]}")
else:
    print(f"  ✅ 所有终端日志均已被JSON捕获")

print(f"\n【完整性验证】")
print(f"  终端显示总行数: {len(terminal_output)}")
print(f"  JSON记录日志数: {len(logs)}")
print(f"  匹配成功率: {(len(terminal_output) - len(missing_in_json)) / len(terminal_output) * 100:.1f}%")

# 检查关键日志
print(f"\n【关键日志验证】")
key_logs = [
    "导入多智能体聊天室模块成功",
    "导入时机选择策略引擎成功",
    "导入记忆重构引擎成功",
    "导入夜间维护调度器成功",
    "开始启动RAG系统服务器... 端口: 6666, PID: 14188",
    "✅ 系统初始化完成: 智能体=5, 向量库=1224条",
    "⚠️  检测到 22 处日志重复问题（详见startup_status.json）"
]

for key_log in key_logs:
    if key_log in json_messages:
        print(f"  ✅ {key_log[:60]}")
    else:
        print(f"  ❌ {key_log[:60]}")
