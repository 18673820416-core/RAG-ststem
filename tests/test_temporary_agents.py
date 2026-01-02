#!/usr/bin/env python
# @self-expose: {"id": "test_temporary_agents", "name": "Test Temporary Agents", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Temporary Agents功能"]}}
# -*- coding: utf-8 -*-
"""
测试智能体动态扩展功能 - 验证临时智能体的创建和管理
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_temporary_agent_creation():
    """测试临时智能体创建功能"""
    print("=== 测试智能体动态扩展功能 ===")
    
    try:
        # 导入智能体管理器
        from src.agent_manager import get_agent_manager
        
        # 获取智能体管理器实例
        agent_manager = get_agent_manager()
        
        # 获取当前智能体列表
        original_agents = agent_manager.get_all_agents()
        print(f"初始智能体数量: {len(original_agents)}")
        print(f"初始智能体列表: {list(original_agents.keys())}")
        
        # 测试1: 创建临时智能体
        print("\n1. 测试创建临时智能体...")
        temp_agent_id = agent_manager.create_temporary_agent("system_architect")
        if temp_agent_id:
            print(f"✓ 成功创建临时智能体: {temp_agent_id}")
        else:
            print("✗ 创建临时智能体失败")
            return False
        
        # 测试2: 检查临时智能体是否被正确添加
        print("\n2. 测试临时智能体是否被正确添加...")
        all_agents = agent_manager.get_all_agents()
        print(f"当前智能体数量: {len(all_agents)}")
        print(f"当前智能体列表: {list(all_agents.keys())}")
        
        if temp_agent_id in all_agents:
            print(f"✓ 临时智能体 {temp_agent_id} 已被正确添加")
        else:
            print(f"✗ 临时智能体 {temp_agent_id} 未被添加")
            return False
        
        # 测试3: 获取临时智能体列表
        print("\n3. 测试获取临时智能体列表...")
        temp_agents = agent_manager.get_temporary_agents()
        print(f"临时智能体数量: {len(temp_agents)}")
        print(f"临时智能体列表: {list(temp_agents.keys())}")
        
        if temp_agent_id in temp_agents:
            print(f"✓ 临时智能体 {temp_agent_id} 已被正确识别为临时智能体")
        else:
            print(f"✗ 临时智能体 {temp_agent_id} 未被识别为临时智能体")
            return False
        
        # 测试4: 移除临时智能体
        print("\n4. 测试移除临时智能体...")
        remove_result = agent_manager.remove_temporary_agent(temp_agent_id)
        if remove_result:
            print(f"✓ 成功移除临时智能体: {temp_agent_id}")
        else:
            print(f"✗ 移除临时智能体 {temp_agent_id} 失败")
            return False
        
        # 测试5: 检查临时智能体是否被正确移除
        print("\n5. 测试临时智能体是否被正确移除...")
        all_agents = agent_manager.get_all_agents()
        temp_agents = agent_manager.get_temporary_agents()
        
        if temp_agent_id not in all_agents and temp_agent_id not in temp_agents:
            print(f"✓ 临时智能体 {temp_agent_id} 已被正确移除")
        else:
            print(f"✗ 临时智能体 {temp_agent_id} 未被完全移除")
            return False
        
        # 测试6: 批量创建临时智能体
        print("\n6. 测试批量创建临时智能体...")
        temp_agent_ids = []
        for i in range(3):
            temp_id = agent_manager.create_temporary_agent("code_implementer")
            if temp_id:
                temp_agent_ids.append(temp_id)
                print(f"✓ 成功创建临时智能体 {i+1}: {temp_id}")
            else:
                print(f"✗ 创建临时智能体 {i+1} 失败")
                return False
        
        # 测试7: 清理所有临时智能体
        print("\n7. 测试清理所有临时智能体...")
        clear_result = agent_manager.clear_all_temporary_agents()
        print(f"清理结果: {clear_result}")
        
        if clear_result["removed_agents"] == clear_result["temporary_agents"]:
            print(f"✓ 成功清理所有 {clear_result['removed_agents']} 个临时智能体")
        else:
            print(f"✗ 清理临时智能体不完全，预期清理 {clear_result['temporary_agents']} 个，实际清理 {clear_result['removed_agents']} 个")
            return False
        
        # 最终检查
        print("\n8. 最终检查智能体列表...")
        final_agents = agent_manager.get_all_agents()
        final_temp_agents = agent_manager.get_temporary_agents()
        
        print(f"最终智能体数量: {len(final_agents)}")
        print(f"最终临时智能体数量: {len(final_temp_agents)}")
        
        if len(final_temp_agents) == 0:
            print("✓ 所有临时智能体已被成功清理")
        else:
            print(f"✗ 仍有 {len(final_temp_agents)} 个临时智能体未被清理")
            return False
        
        print("\n=== 所有测试通过！智能体动态扩展功能正常工作 ===")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_temporary_agent_creation()
