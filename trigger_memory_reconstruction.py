# @self-expose: {"id": "trigger_memory_reconstruction", "name": "Trigger Memory Reconstruction", "type": "tool", "version": "1.0.0", "needs": {"deps": ["memory_reconstruction_engine", "vector_database", "mesh_thought_engine"], "resources": []}, "provides": {"capabilities": ["手动触发记忆重构", "低价值记忆清理"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触发记忆重构任务脚本
功能：
1. 从向量库和网状思维引擎获取所有记忆节点
2. 调用记忆重构引擎批量评估
3. 删除标记为"应删除"的低价值记忆
4. 生成重构报告
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cognitive_engines.memory_reconstruction_engine import BatchMemoryReconstructor
from src.vector_database import VectorDatabase
from src.mesh_thought_engine import MeshThoughtEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MemoryReconstruction")

class MemoryReconstructionTask:
    """记忆重构任务执行器"""
    
    def __init__(self):
        self.reconstructor = BatchMemoryReconstructor()
        self.vector_db = VectorDatabase()
        self.mesh_engine = MeshThoughtEngine()
        
        # 创建报告目录
        self.report_dir = project_root / "logs" / "memory_reconstruction"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("记忆重构任务初始化完成")
    
    def fetch_all_memories(self) -> List[Dict[str, Any]]:
        """从向量库和网状思维引擎获取所有记忆"""
        memories = []
        
        # 1. 从网状思维引擎获取所有节点
        logger.info("从网状思维引擎获取节点...")
        try:
            mesh_nodes = self.mesh_engine.nodes.values()
            for node in mesh_nodes:
                memories.append({
                    'id': node.id,
                    'content': node.content,
                    'source': 'mesh_thought_engine',
                    'metadata': node.metadata
                })
            logger.info(f"从网状思维引擎获取 {len(mesh_nodes)} 个节点")
        except Exception as e:
            logger.error(f"从网状思维引擎获取节点失败: {e}")
        
        # 2. 从向量库获取所有记忆（可选，如果向量库有独立接口）
        # 注意：避免重复，这里暂时只从网状思维引擎获取
        # 如果需要从向量库获取，可以添加类似逻辑
        
        logger.info(f"共获取 {len(memories)} 条记忆待重构")
        return memories
    
    def execute_reconstruction(self) -> Dict[str, Any]:
        """执行记忆重构"""
        logger.info("=" * 60)
        logger.info("开始记忆重构任务")
        logger.info("=" * 60)
        
        # 获取所有记忆
        memories = self.fetch_all_memories()
        
        if not memories:
            logger.warning("未找到任何记忆，跳过重构")
            return {
                'success': False,
                'message': '未找到任何记忆'
            }
        
        # 批量重构
        logger.info(f"开始批量重构 {len(memories)} 条记忆...")
        reconstruction_results = self.reconstructor.reconstruct_batch_memories(memories)
        
        # 执行删除
        deleted_count = self.delete_marked_memories(reconstruction_results['deleted_memory_ids'])
        
        # 生成报告
        report_path = self.generate_report(reconstruction_results, deleted_count)
        
        logger.info("=" * 60)
        logger.info("记忆重构任务完成")
        logger.info(f"总计: {reconstruction_results['total_memories']} 条")
        logger.info(f"应删除: {reconstruction_results['deleted_count']} 条")
        logger.info(f"实际删除: {deleted_count} 条")
        logger.info(f"平均可信度: {reconstruction_results['statistics']['average_confidence']:.2%}")
        logger.info(f"删除率: {reconstruction_results['statistics']['deletion_rate']:.2%}")
        logger.info(f"报告路径: {report_path}")
        logger.info("=" * 60)
        
        return {
            'success': True,
            'total_memories': reconstruction_results['total_memories'],
            'deleted_count': deleted_count,
            'report_path': str(report_path),
            'statistics': reconstruction_results['statistics']
        }
    
    def delete_marked_memories(self, deleted_memory_ids: List[Dict[str, Any]]) -> int:
        """删除标记的记忆"""
        if not deleted_memory_ids:
            logger.info("没有需要删除的记忆")
            return 0
        
        logger.info(f"开始删除 {len(deleted_memory_ids)} 条标记的记忆...")
        deleted_count = 0
        
        for item in deleted_memory_ids:
            memory_id = item['memory_id']
            delete_reason = item['delete_reason']
            
            try:
                # 1. 从网状思维引擎删除节点
                if memory_id in self.mesh_engine.nodes:
                    del self.mesh_engine.nodes[memory_id]
                    logger.info(f"从网状思维引擎删除节点: {memory_id}")
                
                # 2. 从向量库删除记忆（如果向量库有delete方法）
                try:
                    self.vector_db.delete_memory(memory_id)
                    logger.info(f"从向量库删除记忆: {memory_id}")
                except Exception as e:
                    logger.warning(f"从向量库删除记忆 {memory_id} 失败: {e}")
                
                deleted_count += 1
                logger.info(f"成功删除记忆 {memory_id}: {delete_reason}")
                
            except Exception as e:
                logger.error(f"删除记忆 {memory_id} 失败: {e}")
        
        # 持久化网状思维引擎变更
        try:
            self.mesh_engine.save_thoughts()
            logger.info("网状思维引擎变更已持久化")
        except Exception as e:
            logger.error(f"持久化网状思维引擎失败: {e}")
        
        logger.info(f"删除完成: 成功删除 {deleted_count}/{len(deleted_memory_ids)} 条记忆")
        return deleted_count
    
    def generate_report(self, results: Dict[str, Any], actual_deleted: int) -> Path:
        """生成重构报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.report_dir / f"reconstruction_report_{timestamp}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("记忆重构报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("【统计概览】\n")
            f.write(f"  总记忆数: {results['total_memories']}\n")
            f.write(f"  应删除数: {results['deleted_count']}\n")
            f.write(f"  实际删除: {actual_deleted}\n")
            f.write(f"  重构数量: {results['reconstructed_count']}\n")
            f.write(f"  高优先级: {results['high_priority_count']}\n")
            f.write(f"  平均可信度: {results['statistics']['average_confidence']:.2%}\n")
            f.write(f"  重构率: {results['statistics']['reconstruction_rate']:.2%}\n")
            f.write(f"  删除率: {results['statistics']['deletion_rate']:.2%}\n\n")
            
            f.write("【删除记忆详情】\n")
            if results['deleted_memory_ids']:
                for i, item in enumerate(results['deleted_memory_ids'], 1):
                    f.write(f"\n{i}. 记忆ID: {item['memory_id']}\n")
                    f.write(f"   删除原因: {item['delete_reason']}\n")
                    f.write(f"   原始内容: {item['original_content']}\n")
            else:
                f.write("  无\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        logger.info(f"报告已生成: {report_path}")
        return report_path

def main():
    """主函数"""
    try:
        task = MemoryReconstructionTask()
        result = task.execute_reconstruction()
        
        if result['success']:
            print("\n✅ 记忆重构任务执行成功")
            print(f"📊 总记忆数: {result['total_memories']}")
            print(f"🗑️  删除数量: {result['deleted_count']}")
            print(f"📈 平均可信度: {result['statistics']['average_confidence']:.2%}")
            print(f"📄 报告路径: {result['report_path']}")
        else:
            print(f"\n❌ 记忆重构任务失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        logger.error(f"记忆重构任务执行失败: {e}", exc_info=True)
        print(f"\n❌ 记忆重构任务执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

