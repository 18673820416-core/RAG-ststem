# @self-expose: {"id": "test_unified_memory", "name": "Test Unified Memory", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Unified Memory功能"]}}
"""
统一记忆系统集成测试
开发提示词来源：用户要求完善记忆统一性
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from base_agent import BaseAgent

def test_unified_memory_integration():
    """测试统一记忆系统集成"""
    print("=== 统一记忆系统集成测试 ===")
    
    try:
        # 创建测试智能体
        print("1. 创建测试智能体...")
        test_agent = BaseAgent(
            agent_id="test_agent_001",
            agent_type="tester",
            prompt_file="test_prompt.txt"
        )
        print("✓ 智能体创建成功")
        
        # 测试记忆创建
        print("\n2. 测试记忆创建功能...")
        memory_id = test_agent.create_memory(
            content="这是一个测试记忆条目，用于验证统一记忆系统的功能",
            memory_type="knowledge",
            priority="high",
            tags=["test", "integration"]
        )
        print(f"✓ 记忆创建成功，ID: {memory_id}")
        
        # 测试记忆检索
        print("\n3. 测试记忆检索功能...")
        memories = test_agent.search_memories(
            memory_type="knowledge",
            tags=["test"],
            limit=5
        )
        print(f"✓ 记忆检索成功，找到 {len(memories)} 条相关记忆")
        
        # 测试记忆获取
        print("\n4. 测试记忆获取功能...")
        memory = test_agent.get_memory(memory_id)
        if memory:
            print(f"✓ 记忆获取成功，内容: {memory.get('content', '')[:50]}...")
        else:
            print("✗ 记忆获取失败")
        
        # 测试记忆统计
        print("\n5. 测试记忆统计功能...")
        stats = test_agent.get_memory_statistics()
        print(f"✓ 记忆统计成功，总记忆数: {stats.get('total_memories', 0)}")
        
        # 测试记忆迁移
        print("\n6. 测试旧记忆迁移功能...")
        migration_result = test_agent.migrate_old_memories()
        print(f"✓ 记忆迁移完成，迁移了 {migration_result['migrated_entries']} 条记录")
        
        # 测试智能体响应（集成记忆）
        print("\n7. 测试智能体响应（集成记忆）...")
        response = test_agent.respond("你好，请介绍一下记忆系统的功能", use_memory=True)
        print(f"✓ 智能体响应成功，响应长度: {len(response)} 字符")
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_sharing():
    """测试记忆共享功能"""
    print("\n=== 记忆共享功能测试 ===")
    
    try:
        # 创建两个测试智能体
        print("1. 创建两个测试智能体...")
        agent1 = BaseAgent(
            agent_id="agent_001",
            agent_type="tester",
            prompt_file="test_prompt.txt"
        )
        
        agent2 = BaseAgent(
            agent_id="agent_002", 
            agent_type="tester",
            prompt_file="test_prompt.txt"
        )
        print("✓ 智能体创建成功")
        
        # 智能体1创建记忆
        print("\n2. 智能体1创建记忆...")
        memory_id = agent1.create_memory(
            content="这是智能体1创建的共享记忆",
            memory_type="knowledge",
            priority="medium",
            tags=["shared", "test"]
        )
        print(f"✓ 记忆创建成功，ID: {memory_id}")
        
        # 智能体1共享记忆给智能体2
        print("\n3. 智能体1共享记忆给智能体2...")
        success = agent1.share_memory(
            memory_id=memory_id,
            target_agent_id="agent_002",
            permission_level="read"
        )
        print(f"✓ 记忆共享{'成功' if success else '失败'}")
        
        # 智能体2尝试获取共享记忆
        print("\n4. 智能体2尝试获取共享记忆...")
        shared_memory = agent2.get_memory(memory_id)
        if shared_memory:
            print(f"✓ 共享记忆获取成功，内容: {shared_memory.get('content', '')[:50]}...")
        else:
            print("✗ 共享记忆获取失败")
        
        print("\n=== 记忆共享测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 记忆共享测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行集成测试
    success1 = test_unified_memory_integration()
    
    # 运行记忆共享测试
    success2 = test_memory_sharing()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！统一记忆系统集成成功！")
    else:
        print("\n❌ 部分测试失败，请检查系统配置")