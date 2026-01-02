#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试自曝光协议解析器"""

import sys
sys.path.insert(0, 'src')

from agent_discovery_engine import AgentDiscoveryEngine
import json

def test_file(file_path):
    """测试单个文件的协议解析"""
    print(f"\n{'='*60}")
    print(f"测试文件: {file_path}")
    print('='*60)
    
    engine = AgentDiscoveryEngine()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        protocols = engine._extract_self_expose_protocol(content)
        print(f"✅ 提取到 {len(protocols)} 个协议")
        
        if protocols:
            for i, protocol_str in enumerate(protocols, 1):
                print(f"\n协议 #{i}:")
                print(f"  原始长度: {len(protocol_str)} 字符")
                
                try:
                    data = json.loads(protocol_str)
                    print(f"  ✅ JSON解析成功")
                    print(f"  ID: {data.get('id')}")
                    print(f"  Name: {data.get('name')}")
                    print(f"  Type: {data.get('type')}")
                    print(f"  Version: {data.get('version')}")
                except json.JSONDecodeError as je:
                    print(f"  ❌ JSON解析失败: {je}")
                    print(f"  错误位置: 第 {je.lineno} 行, 第 {je.colno} 列")
                    # 显示错误附近的内容
                    error_pos = je.pos
                    start = max(0, error_pos - 30)
                    end = min(len(protocol_str), error_pos + 30)
                    print(f"  错误附近内容: ...{protocol_str[start:end]}...")
        else:
            print("⚠️  未找到协议")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

# 测试文件列表
test_files = [
    'src/abductive_reasoning_engine.py',
    'src/agent_behavior_evaluator.py',
    'src/agent_discovery_engine.py',
]

print("="*60)
print("自曝光协议解析器测试")
print("="*60)

for file_path in test_files:
    test_file(file_path)

print("\n" + "="*60)
print("测试完成")
print("="*60)
