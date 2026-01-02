"""
分析startup_status.json中的重复日志
按照重复类型分类，定位问题根源
"""
import json

with open('logs/startup_status.json', encoding='utf-8') as f:
    data = json.load(f)

duplicates = data['startup_logs']['duplicates_detected']

print("=" * 80)
print("启动日志重复问题分析")
print("=" * 80)

print(f"\n【总体统计】")
print(f"  总重复数: {len(duplicates)} 处")
print(f"  总日志数: {data['startup_logs']['total_logs']} 条")

# 按类型分类
categories = {
    "高级引擎初始化": [],
    "智能体对话窗口创建": [],
    "系统核心流程": [],
    "配置警告": [],
    "其他": []
}

for dup in duplicates:
    msg = dup['message']
    logger = dup['logger']
    
    if '引擎' in msg or '人脸识别' in msg:
        categories["高级引擎初始化"].append(dup)
    elif '记忆重构引擎初始化成功' in msg:
        categories["智能体对话窗口创建"].append(dup)
    elif 'rag_system' in logger and ('PORT' in msg or '开始执行' in msg or '多智能体' in msg):
        categories["系统核心流程"].append(dup)
    elif '默认服务商' in msg:
        categories["配置警告"].append(dup)
    else:
        categories["其他"].append(dup)

print(f"\n【重复类型分布】")
for cat, items in categories.items():
    if items:
        print(f"  {cat}: {len(items)} 处")

print(f"\n【详细分析】")

print(f"\n1. 高级引擎初始化重复 ({len(categories['高级引擎初始化'])} 处)")
if categories['高级引擎初始化']:
    print("   原因: 每个智能体对话窗口创建时都会初始化一次高级引擎")
    print("   涉及引擎:")
    engine_types = set()
    for dup in categories['高级引擎初始化']:
        if '人脸识别' in dup['message']:
            engine_types.add("人脸识别")
        elif '视觉处理' in dup['message']:
            engine_types.add("视觉处理引擎")
        elif '音频处理' in dup['message']:
            engine_types.add("音频处理引擎")
        elif '多模态融合' in dup['message']:
            engine_types.add("多模态融合引擎")
        elif '溯因推理' in dup['message']:
            engine_types.add("溯因推理引擎")
        elif '分层学习' in dup['message']:
            engine_types.add("分层学习引擎")
    for eng in sorted(engine_types):
        count = sum(1 for d in categories['高级引擎初始化'] if eng.replace('引擎', '') in d['message'])
        print(f"     - {eng}: 重复 {count} 次")

print(f"\n2. 系统核心流程重复 ({len(categories['系统核心流程'])} 处)")
if categories['系统核心流程']:
    print("   这些是真正需要修复的核心问题:")
    for dup in categories['系统核心流程']:
        print(f"     - [{dup['logger']}] {dup['message'][:60]}... (重复{dup['count']}次)")

print(f"\n3. 配置警告重复 ({len(categories['配置警告'])} 处)")
if categories['配置警告']:
    print("   原因: 每个智能体创建时检查配置")
    for dup in categories['配置警告'][:1]:
        print(f"     - {dup['message'][:60]}... (重复{dup['count']}次)")

print(f"\n【问题严重性评估】")
print(f"  ✅ 轻微问题 (可接受): 高级引擎初始化重复")
print(f"     - 每个智能体独立对话窗口需要独立的引擎实例")
print(f"     - 这是架构设计的合理结果，非真正的重复执行")
print(f"  ⚠️  需要关注: 系统核心流程重复")
print(f"     - 这些日志不应该重复")
print(f"     - 可能存在日志记录器配置问题")

print(f"\n【修复建议】")
print(f"  1. 核心流程重复: 检查logger配置，可能存在重复的handler")
print(f"  2. 高级引擎初始化: 正常架构行为，可通过调整日志级别优化显示")
print(f"  3. 配置警告: 可在首次检测时缓存结果，避免重复输出")
