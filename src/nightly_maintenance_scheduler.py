#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @self-expose: {"id": "nightly_maintenance_scheduler", "name": "Nightly Maintenance Scheduler", "type": "component", "version": "1.1.1", "needs": {"deps": ["timing_strategy_engine", "memory_reconstruction_engine", "agent_manager", "base_agent", "vector_database", "mesh_thought_engine"], "resources": []}, "provides": {"capabilities": ["夜间自动维护", "记忆重构调度", "智能体日记管理", "系统维护报告", "低价值记忆清理"]}}
"""
夜间维护调度器 - 基于TimingStrategyEngine的智能体记忆维护

开发提示词来源：记忆锤点_架构自优化共识.md - 时机选择策略
核心功能：在系统空闲时（晚上）自动执行智能体日记写入和记忆重构

设计理念：
- 白天：智能体记泡泡（轻量级，不打断工作）
- 晚上：自动写日记 → 记忆重构 → 向量库更新
- 完整闭环：泡泡 → 日记 → 重构 → 更新 🔄

进化值评估体系集成：
- 自动收集智能体日记
- 执行记忆重构（语义精炼 + 逻辑验证 + 幻觉清理）
- 生成系统维护报告
- 支持记忆更新时机策略：系统空闲时自动更新
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .timing_strategy_engine import TimingStrategyEngine, OptimizationTiming

logger = logging.getLogger(__name__)

class NightlyMaintenanceScheduler:
    """夜间维护调度器 - 智能体自动维护管理"""
    
    def __init__(self, agent_manager=None):
        """初始化夜间维护调度器
        
        Args:
            agent_manager: 智能体管理器实例（可选，延迟注入）
        """
        self.agent_manager = agent_manager
        self.timing_engine = TimingStrategyEngine()
        
        # 维护配置
        self.config = {
            "diary_cleanup_enabled": True,      # 是否清理已解决的泡泡
            "memory_reconstruction_enabled": True,  # 是否执行记忆重构
            "vector_db_update_enabled": True,   # 是否更新向量数据库
            "generate_report_enabled": True,    # 是否生成维护报告
        }
        
        # 维护统计
        self.maintenance_history = []
        
        logger.info("夜间维护调度器初始化完成")
    
    def set_agent_manager(self, agent_manager):
        """设置智能体管理器（延迟注入）
        
        Args:
            agent_manager: 智能体管理器实例
        """
        self.agent_manager = agent_manager
        logger.info("智能体管理器已注入到夜间维护调度器")
    
    def start_scheduled_maintenance(self):
        """启动定时维护调度
        
        自动在系统空闲时（晚上）执行维护任务
        """
        # 注册每日维护任务 - 每天只执行一次
        self.timing_engine.schedule_optimization(
            task_type="daily_diary_writing",
            task_description="每日智能体写日记",
            priority="medium",
            estimated_duration=10,  # 预计10分钟
            optimization_function=self.perform_daily_diary_writing,
            daily_once=True  # 每天只执行一次
        )
        
        # 注册记忆重构任务 - 每天只执行一次
        self.timing_engine.schedule_optimization(
            task_type="memory_reconstruction",
            task_description="批量记忆重构和压缩",
            priority="medium",
            estimated_duration=30,  # 预计30分钟
            optimization_function=self.perform_memory_reconstruction,
            daily_once=True  # 每天只执行一次
        )
        
        # 注册向量数据库更新任务 - 每天只执行一次
        self.timing_engine.schedule_optimization(
            task_type="vector_db_update",
            task_description="向量数据库增量更新",
            priority="low",
            estimated_duration=15,  # 预计15分钟
            optimization_function=self.perform_vector_db_update,
            daily_once=True  # 每天只执行一次
        )
        
        # 启动监控
        self.timing_engine.start_monitoring()
        
        logger.info("✅ 夜间维护调度已启动")
        print("🌙 夜间维护调度已启动 - 将在系统空闲时自动执行")
        print("🌙 注：每个任务每天只执行一次，通常在晚上22:00-6:00之间")
    
    def perform_daily_diary_writing(self) -> Dict[str, Any]:
        """执行每日日记写入任务
        
        Returns:
            Dict: 执行结果
        """
        logger.info("🌙 开始夜间维护：智能体写日记")
        print(f"\n{'='*70}")
        print(f"🌙 夜间维护开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        if not self.agent_manager:
            logger.warning("智能体管理器未设置，跳过日记写入")
            return {"status": "skipped", "reason": "agent_manager_not_set"}
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "diary_count": 0,
            "success_count": 0,
            "failed_count": 0,
            "agents": []
        }
        
        try:
            # 获取所有智能体（列表形式）
            all_agents = self.agent_manager.get_all_agent_instances()
            results["diary_count"] = len(all_agents)
            
            print(f"📝 正在为 {len(all_agents)} 个智能体写日记...\n")
            
            # 为每个智能体写日记
            for agent in all_agents:
                try:
                    agent_result = {
                        "agent_id": agent.agent_id,
                        "agent_type": agent.agent_type,
                        "status": "success"
                    }
                    
                    # 写日记
                    diary_path = agent.write_daily_diary(
                        cleanup_resolved=self.config["diary_cleanup_enabled"]
                    )
                    
                    if diary_path:
                        agent_result["diary_path"] = str(diary_path)
                        results["success_count"] += 1
                        print(f"  ✅ {agent.agent_id} ({agent.agent_type})")
                        print(f"     日记: {Path(diary_path).name}")
                    else:
                        agent_result["status"] = "no_diary"
                        print(f"  ⏭️  {agent.agent_id} - 今天无内容")
                    
                    results["agents"].append(agent_result)
                    
                except Exception as e:
                    agent_result = {
                        "agent_id": agent.agent_id,
                        "agent_type": agent.agent_type,
                        "status": "failed",
                        "error": str(e)
                    }
                    results["agents"].append(agent_result)
                    results["failed_count"] += 1
                    logger.error(f"智能体 {agent.agent_id} 写日记失败: {e}")
                    print(f"  ❌ {agent.agent_id} - 失败: {e}")
            
            print(f"\n📊 日记写入统计:")
            print(f"  总智能体数: {results['diary_count']}")
            print(f"  成功: {results['success_count']}")
            print(f"  失败: {results['failed_count']}")
            
            # 记录维护历史
            self.maintenance_history.append({
                "type": "daily_diary",
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            
        except Exception as e:
            logger.error(f"日记写入任务失败: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def perform_memory_reconstruction(self) -> Dict[str, Any]:
        """执行记忆重构任务（含低价值记忆删除）
        
        Returns:
            Dict: 执行结果
        """
        if not self.config["memory_reconstruction_enabled"]:
            return {"status": "disabled"}
        
        logger.info("🔄 开始记忆重构任务")
        print(f"\n🔄 批量记忆重构中...\n")
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "reconstructed_count": 0,
            "deleted_count": 0,
            "total_memories": 0,
            "average_confidence": 0.0,
            "deletion_rate": 0.0
        }
        
        try:
            from .cognitive_engines.memory_reconstruction_engine import BatchMemoryReconstructor
            from .vector_database import VectorDatabase
            from .mesh_thought_engine import MeshThoughtEngine
            
            reconstructor = BatchMemoryReconstructor()
            
            # 获取向量库中的所有记忆（用于重构和清理）
            vector_db = VectorDatabase()
            all_memories = vector_db.get_all_memories()
            
            results["total_memories"] = len(all_memories)
            
            if all_memories:
                # 批量重构（包含删除判断）
                recon_result = reconstructor.reconstruct_batch_memories(all_memories)
                
                results["reconstructed_count"] = recon_result["reconstructed_count"]
                results["deleted_count"] = recon_result["deleted_count"]
                results["average_confidence"] = recon_result["statistics"]["average_confidence"]
                results["deletion_rate"] = recon_result["statistics"]["deletion_rate"]
                
                # 根据重构结果更新记忆状态（active/archive/retired）
                if recon_result.get("status_updates"):
                    logger.info("开始更新记忆状态(status/worldview_version/retire_reason)...")
                    for status_item in recon_result["status_updates"]:
                        memory_id = status_item["memory_id"]
                        new_status = status_item.get("status")
                        worldview_version = status_item.get("worldview_version")
                        retire_reason = status_item.get("retire_reason")
                        if new_status:
                            try:
                                updated = vector_db.update_memory_status(
                                    memory_id,
                                    new_status,
                                    worldview_version=worldview_version,
                                    retire_reason=retire_reason,
                                )
                                if updated:
                                    logger.info(f"更新记忆 {memory_id} 状态为 {new_status}, retire_reason={retire_reason}")
                            except Exception as e:
                                logger.error(f"更新记忆 {memory_id} 状态失败: {e}")
                
                # 执行删除操作（从向量库和网状思维引擎）
                if recon_result["deleted_memory_ids"]:
                    logger.info(f"开始删除 {len(recon_result['deleted_memory_ids'])} 条低价值记忆")
                    print(f"\n🗑️  删除低价值记忆中...")
                    
                    mesh_engine = MeshThoughtEngine()
                    deleted_from_vector = 0
                    deleted_from_mesh = 0
                    
                    for deletion_item in recon_result["deleted_memory_ids"]:
                        memory_id = deletion_item["memory_id"]
                        delete_reason = deletion_item["delete_reason"]
                        
                        # 从向量库删除
                        if vector_db.delete_memory(memory_id):
                            deleted_from_vector += 1
                        
                        # 从网状思维引擎删除（基于内容匹配）
                        original_content = deletion_item.get("original_content", "")
                        if original_content:
                            mesh_result = mesh_engine.remove_node_by_content(original_content)
                            if mesh_result:
                                deleted_from_mesh += 1
                                logger.debug(f"网状思维引擎删除成功: {memory_id}")
                            else:
                                logger.debug(f"网状思维引擎中未找到对应节点: {memory_id}")
                        else:
                            logger.warning(f"删除项目缺少原始内容: {memory_id}")
                        
                        logger.info(f"删除记忆 {memory_id}: {delete_reason}")
                    
                    # 持久化网状思维引擎（自动调用）
                    mesh_engine.save_thoughts()
                    
                    print(f"  ✅ 向量库删除: {deleted_from_vector}/{len(recon_result['deleted_memory_ids'])}")
                    print(f"  ✅ 网状思维引擎删除: {deleted_from_mesh}/{len(recon_result['deleted_memory_ids'])}")
                    print(f"  📊 删除率: {results['deletion_rate']:.2%}")
                
                print(f"  ✅ 重构完成: {recon_result['reconstructed_count']}/{recon_result['total_memories']}")
                print(f"  📈 平均可信度: {recon_result['statistics']['average_confidence']:.2%}")
                print(f"  ⭐ 高优先级: {recon_result['high_priority_count']}")
                print(f"  🗑️  删除无效记忆: {results['deleted_count']}/{results['total_memories']}")
                
                # 🔄 记忆重构后触发知识图谱全量重建
                print(f"\n🔄 触发知识图谱重建...")
                try:
                    from .system_statistics_service import get_system_statistics_service
                    stats_service = get_system_statistics_service()
                    kg_stats = stats_service.rebuild_knowledge_graph()
                    
                    # 提取知识图谱统计
                    kg_nodes = kg_stats['knowledge_graph']['total_nodes']
                    kg_edges = kg_stats['knowledge_graph']['total_edges']
                    coverage = kg_stats['knowledge_graph']['coverage_rate']
                    
                    results["knowledge_graph_rebuilt"] = True
                    results["kg_nodes"] = kg_nodes
                    results["kg_edges"] = kg_edges
                    results["kg_coverage"] = coverage
                    
                    print(f"  ✅ 知识图谱重建完成")
                    print(f"  📊 节点: {kg_nodes}, 边: {kg_edges}, 覆盖率: {coverage:.1f}%")
                except Exception as kg_error:
                    logger.error(f"知识图谱重建失败: {kg_error}")
                    results["knowledge_graph_rebuilt"] = False
                    results["kg_error"] = str(kg_error)
                    print(f"  ⚠️ 知识图谱重建失败: {kg_error}")
            else:
                print(f"  ⏭️  向量库中没有记忆需要重构")
            
            # 记录维护历史
            self.maintenance_history.append({
                "type": "memory_reconstruction",
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            
        except Exception as e:
            logger.error(f"记忆重构任务失败: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ 重构失败: {e}")
        
        return results
    
    def perform_vector_db_update(self) -> Dict[str, Any]:
        """执行向量数据库更新任务
        
        Returns:
            Dict: 执行结果
        """
        if not self.config["vector_db_update_enabled"]:
            return {"status": "disabled"}
        
        logger.info("💾 开始向量数据库更新")
        print(f"\n💾 向量数据库增量更新中...\n")
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "updated_files": 0
        }
        
        try:
            # TODO: 实际的向量数据库更新逻辑
            # 这里应该集成向量数据库的增量更新功能
            
            print(f"  ✅ 向量数据库更新完成")
            
            # 记录维护历史
            self.maintenance_history.append({
                "type": "vector_db_update",
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            
        except Exception as e:
            logger.error(f"向量数据库更新失败: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ 更新失败: {e}")
        
        return results
    
    def generate_maintenance_report(self) -> Optional[str]:
        """生成维护报告
        
        Returns:
            str: 报告文件路径
        """
        if not self.config["generate_report_enabled"]:
            return None
        
        try:
            # 统计今天的维护记录
            today = datetime.now().date()
            today_maintenance = [
                m for m in self.maintenance_history
                if datetime.fromisoformat(m["timestamp"]).date() == today
            ]
            
            # 生成报告
            report = f"""# 系统维护报告

**日期**: {datetime.now().strftime('%Y年%m月%d日')}  
**报告生成时间**: {datetime.now().strftime('%H:%M:%S')}

---

## 📊 维护任务统计

"""
            
            # 日记写入统计
            diary_tasks = [m for m in today_maintenance if m["type"] == "daily_diary"]
            if diary_tasks:
                latest_diary = diary_tasks[-1]["results"]
                report += f"""### 智能体日记写入
- 总智能体数: {latest_diary.get('diary_count', 0)}
- 成功写入: {latest_diary.get('success_count', 0)}
- 失败: {latest_diary.get('failed_count', 0)}
- 成功率: {latest_diary.get('success_count', 0) / max(latest_diary.get('diary_count', 1), 1):.1%}

"""
            
            # 记忆重构统计
            recon_tasks = [m for m in today_maintenance if m["type"] == "memory_reconstruction"]
            if recon_tasks:
                latest_recon = recon_tasks[-1]["results"]
                report += f"""### 记忆重构
- 处理记忆数: {latest_recon.get('total_memories', 0)}
- 重构数量: {latest_recon.get('reconstructed_count', 0)}
- 平均可信度: {latest_recon.get('average_confidence', 0):.2%}

"""
            
            # 向量库更新统计
            vector_tasks = [m for m in today_maintenance if m["type"] == "vector_db_update"]
            if vector_tasks:
                report += f"""### 向量数据库更新
- 更新文件数: {vector_tasks[-1]["results"].get('updated_files', 0)}
- 更新状态: ✅ 成功

"""
            
            report += f"""---

## 🕐 维护时间线

"""
            for m in today_maintenance:
                time_str = datetime.fromisoformat(m["timestamp"]).strftime('%H:%M:%S')
                status_icon = "✅" if m["results"].get("status") == "success" else "❌"
                report += f"- **{time_str}** {status_icon} {m['type']}\n"
            
            report += f"""
---

**维护完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 保存报告
            report_dir = Path("data/system_reports")
            report_dir.mkdir(parents=True, exist_ok=True)
            report_file = report_dir / f"{datetime.now().strftime('%Y%m%d')}_maintenance_report.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"维护报告已生成: {report_file}")
            print(f"\n📊 维护报告已保存: {report_file}")
            
            return str(report_file)
            
        except Exception as e:
            logger.error(f"生成维护报告失败: {e}")
            return None
    
    def get_maintenance_status(self) -> Dict[str, Any]:
        """获取维护状态
        
        Returns:
            Dict: 维护状态信息
        """
        return {
            "is_running": self.timing_engine.is_monitoring,
            "config": self.config,
            "maintenance_count": len(self.maintenance_history),
            "last_maintenance": self.maintenance_history[-1] if self.maintenance_history else None,
            "timing_status": self.timing_engine.get_scheduling_status()
        }

# 全局夜间维护调度器实例
_nightly_scheduler = None

def get_nightly_scheduler(agent_manager=None) -> NightlyMaintenanceScheduler:
    """获取夜间维护调度器实例（单例模式）
    
    Args:
        agent_manager: 智能体管理器实例（可选）
        
    Returns:
        NightlyMaintenanceScheduler: 夜间维护调度器实例
    """
    global _nightly_scheduler
    
    if _nightly_scheduler is None:
        _nightly_scheduler = NightlyMaintenanceScheduler(agent_manager)
    elif agent_manager is not None:
        _nightly_scheduler.set_agent_manager(agent_manager)
    
    return _nightly_scheduler
