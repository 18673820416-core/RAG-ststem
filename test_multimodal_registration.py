#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试多模态引擎注册"""

import sys
import logging
from pathlib import Path

# 添加项目路径
rag_system_path = Path("E:\\RAG系统")
sys.path.insert(0, str(rag_system_path))
sys.path.insert(0, str(rag_system_path / "src"))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

print("=" * 60)
print("测试多模态引擎注册")
print("=" * 60)

# 测试1：导入数据收集师
print("\n1. 导入数据收集师智能体...")
try:
    from src.data_collector_agent import get_data_collector
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试2：创建数据收集师实例
print("\n2. 创建数据收集师实例...")
try:
    collector = get_data_collector()
    print(f"✅ 实例创建成功: {collector.agent_id}")
except Exception as e:
    print(f"❌ 实例创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3：检查工具是否注册
print("\n3. 检查多模态引擎是否注册...")
try:
    tool_integrator = collector.tool_integrator
    
    # 检查工具列表
    multimodal_tools = [
        'VisionProcessingEngine',
        'AudioProcessingEngine',
        'MultimodalFusionEngine'
    ]
    
    for tool_name in multimodal_tools:
        tool = tool_integrator.get_tool(tool_name)
        if tool:
            print(f"✅ {tool_name} - 已注册")
        else:
            print(f"❌ {tool_name} - 未注册")
    
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
