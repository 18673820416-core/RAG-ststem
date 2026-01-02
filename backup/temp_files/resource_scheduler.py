#!/usr/bin/env python3
# @self-expose: {"id": "resource_scheduler", "name": "Resource Scheduler", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Resource Scheduler功能"]}}
# -*- coding: utf-8 -*-
"""
智能资源调度器 - 双存在态架构的核心组件
实现按需聚合闲置计算资源，服务1亿用户

开发提示词来源：用户关于"合理利用网络闲置资源"的构想
"""

import time
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ResourceType(Enum):
    """资源类型枚举"""
    CPU = "cpu"
    MEMORY = "memory" 
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"

class ResourcePriority(Enum):
    """资源优先级"""
    HIGH = 3    # 用户交互 - 实时响应
    MEDIUM = 2  # 后台计算 - 可延迟
    LOW = 1     # 数据备份 - 网络空闲时

@dataclass
class ResourceNode:
    """资源节点"""
    node_id: str
    node_type: str  # cdn, edge, user_device, browser, cloud
    location: str
    available_resources: Dict[ResourceType, float]  # 可用资源量
    current_usage: Dict[ResourceType, float]  # 当前使用量
    latency: float  # 延迟(ms)
    cost_factor: float  # 成本系数
    
    def get_available_capacity(self, resource_type: ResourceType) -> float:
        """获取可用容量"""
        total = self.available_resources.get(resource_type, 0)
        used = self.current_usage.get(resource_type, 0)
        return max(0, total - used)
    
    def utilization_rate(self, resource_type: ResourceType) -> float:
        """资源利用率"""
        total = self.available_resources.get(resource_type, 1)
        used = self.current_usage.get(resource_type, 0)
        return used / total if total > 0 else 0

class ResourceScheduler:
    """智能资源调度器"""
    
    def __init__(self):
        self.resource_nodes: Dict[str, ResourceNode] = {}
        self.optimization_strategy = "cost_efficiency"  # 成本效率优先
        self.performance_threshold = 0.8  # 性能阈值
        
    def discover_idle_resources(self) -> List[ResourceNode]:
        """发现网络中的闲置资源"""
        print("🔍 扫描网络闲置资源...")
        
        # 模拟发现不同类型的闲置资源节点
        idle_nodes = []
        
        # 1. CDN边缘节点（夜间闲置）
        for i in range(100):  # 模拟100个CDN节点
            node = ResourceNode(
                node_id=f"cdn-edge-{i:03d}",
                node_type="cdn",
                location=f"region-{i%10}",
                available_resources={
                    ResourceType.CPU: 4.0,    # 4核
                    ResourceType.MEMORY: 8.0, # 8GB
                    ResourceType.STORAGE: 50.0, # 50GB
                    ResourceType.NETWORK: 1000.0 # 1Gbps
                },
                current_usage={
                    ResourceType.CPU: random.uniform(0.1, 0.3),    # 10-30%使用率
                    ResourceType.MEMORY: random.uniform(0.2, 0.4), # 20-40%使用率
                    ResourceType.NETWORK: random.uniform(0.05, 0.15) # 5-15%使用率
                },
                latency=random.uniform(10, 50),  # 10-50ms延迟
                cost_factor=0.1  # 低成本
            )
            idle_nodes.append(node)
        
        # 2. 用户设备（计算能力过剩）
        for i in range(1000):  # 模拟1000个用户设备
            node = ResourceNode(
                node_id=f"user-device-{i:04d}",
                node_type="user_device", 
                location=f"user-{i%100}",
                available_resources={
                    ResourceType.CPU: random.uniform(2.0, 8.0),    # 2-8核
                    ResourceType.MEMORY: random.uniform(4.0, 16.0), # 4-16GB
                    ResourceType.STORAGE: random.uniform(50.0, 500.0) # 50-500GB
                },
                current_usage={
                    ResourceType.CPU: random.uniform(0.05, 0.2),    # 5-20%使用率
                    ResourceType.MEMORY: random.uniform(0.1, 0.3)   # 10-30%使用率
                },
                latency=random.uniform(5, 20),  # 5-20ms延迟
                cost_factor=0.05  # 极低成本（利用闲置）
            )
            idle_nodes.append(node)
        
        # 3. 浏览器存储（本地缓存）
        for i in range(500):  # 模拟500个浏览器实例
            node = ResourceNode(
                node_id=f"browser-{i:03d}",
                node_type="browser",
                location=f"browser-{i%50}",
                available_resources={
                    ResourceType.STORAGE: 5.0,  # 5GB本地存储
                    ResourceType.MEMORY: 2.0    # 2GB内存
                },
                current_usage={
                    ResourceType.STORAGE: random.uniform(0.1, 0.5), # 10-50%使用率
                    ResourceType.MEMORY: random.uniform(0.2, 0.6)   # 20-60%使用率
                },
                latency=1.0,  # 1ms延迟（本地）
                cost_factor=0.01  # 几乎零成本
            )
            idle_nodes.append(node)
        
        print(f"✅ 发现 {len(idle_nodes)} 个闲置资源节点")
        
        # 注册发现的节点
        for node in idle_nodes:
            self.resource_nodes[node.node_id] = node
            
        return idle_nodes
    
    def schedule_resources(self, 
                          request: Dict, 
                          priority: ResourcePriority = ResourcePriority.MEDIUM) -> List[Tuple[ResourceNode, Dict]]:
        """智能调度资源"""
        print(f"⚡ 调度资源 (优先级: {priority.name})")
        
        required_resources = request.get('resources', {})
        location_preference = request.get('location', 'nearest')
        
        # 根据优先级调整调度策略
        if priority == ResourcePriority.HIGH:
            strategy = "performance"  # 性能优先
        elif priority == ResourcePriority.LOW:
            strategy = "cost"  # 成本优先
        else:
            strategy = self.optimization_strategy
        
        # 筛选合适的节点
        suitable_nodes = self._filter_suitable_nodes(required_resources, location_preference)
        
        if not suitable_nodes:
            print("❌ 没有找到合适的资源节点")
            return []
        
        # 根据策略排序节点
        if strategy == "performance":
            suitable_nodes.sort(key=lambda x: x.latency)  # 延迟最低优先
        elif strategy == "cost":
            suitable_nodes.sort(key=lambda x: x.cost_factor)  # 成本最低优先
        else:  # cost_efficiency
            suitable_nodes.sort(key=lambda x: x.cost_factor / (x.latency + 1))  # 成本效率比
        
        # 分配资源
        allocations = []
        remaining_resources = required_resources.copy()
        
        for node in suitable_nodes:
            if not remaining_resources:
                break
                
            allocation = {}
            for resource_type, amount in list(remaining_resources.items()):
                available = node.get_available_capacity(resource_type)
                if available > 0:
                    # 分配部分或全部资源
                    alloc_amount = min(amount, available * 0.8)  # 不超过80%可用容量
                    allocation[resource_type] = alloc_amount
                    remaining_resources[resource_type] -= alloc_amount
                    
                    # 更新节点使用量
                    node.current_usage[resource_type] = node.current_usage.get(resource_type, 0) + alloc_amount
                    
                    # 如果该资源需求已满足，从列表中移除
                    if remaining_resources[resource_type] <= 0:
                        del remaining_resources[resource_type]
            
            if allocation:
                allocations.append((node, allocation))
                print(f"   📦 {node.node_id}: {allocation}")
        
        if remaining_resources:
            print(f"⚠️ 资源分配不完全，剩余: {remaining_resources}")
        else:
            print("✅ 资源分配完成")
            
        return allocations
    
    def _filter_suitable_nodes(self, 
                              required_resources: Dict[ResourceType, float], 
                              location: str) -> List[ResourceNode]:
        """筛选合适的资源节点"""
        suitable_nodes = []
        
        for node in self.resource_nodes.values():
            # 检查是否满足所有资源需求
            suitable = True
            for resource_type, amount in required_resources.items():
                if node.get_available_capacity(resource_type) < amount * 0.5:  # 至少50%可用容量
                    suitable = False
                    break
            
            # 检查位置偏好
            if location != "any" and location not in node.location:
                suitable = False
            
            if suitable:
                suitable_nodes.append(node)
        
        return suitable_nodes
    
    def calculate_cost_savings(self, traditional_cost: float) -> Dict:
        """计算成本节省"""
        print("💰 计算双存在态架构的成本节省...")
        
        # 传统架构成本（服务器、带宽、维护）
        traditional_monthly_cost = traditional_cost  # 假设参数
        
        # 双存在态架构成本估算
        quantum_cost_factors = {
            "cdn_usage": 0.1,      # CDN成本是传统服务器的10%
            "user_device": 0.01,   # 用户设备成本几乎为零
            "browser_storage": 0.001,  # 浏览器存储成本极低
            "maintenance": 0.3     # 维护成本降低70%
        }
        
        quantum_monthly_cost = traditional_monthly_cost * sum(quantum_cost_factors.values()) / len(quantum_cost_factors)
        
        # 节省计算
        monthly_savings = traditional_monthly_cost - quantum_monthly_cost
        annual_savings = monthly_savings * 12
        savings_percentage = (monthly_savings / traditional_monthly_cost) * 100
        
        result = {
            "traditional_cost": traditional_monthly_cost,
            "quantum_cost": round(quantum_monthly_cost, 2),
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "savings_percentage": round(savings_percentage, 2)
        }
        
        print(f"✅ 成本节省计算完成")
        print(f"   传统架构月成本: ${result['traditional_cost']:,}")
        print(f"   双存在态月成本: ${result['quantum_cost']:,}")
        print(f"   💰 月节省: ${result['monthly_savings']:,}")
        print(f"   💰 年节省: ${result['annual_savings']:,}")
        print(f"   📊 节省比例: {result['savings_percentage']}%")
        
        return result
    
    def monitor_resource_utilization(self) -> Dict:
        """监控资源利用率"""
        print("📊 监控资源利用率...")
        
        utilization_stats = {
            "total_nodes": len(self.resource_nodes),
            "by_type": {},
            "by_resource": {},
            "overall_utilization": 0
        }
        
        # 按节点类型统计
        node_types = set(node.node_type for node in self.resource_nodes.values())
        for node_type in node_types:
            type_nodes = [n for n in self.resource_nodes.values() if n.node_type == node_type]
            avg_utilization = sum(
                sum(n.utilization_rate(rt) for rt in n.current_usage.keys()) / len(n.current_usage)
                for n in type_nodes
            ) / len(type_nodes) if type_nodes else 0
            
            utilization_stats["by_type"][node_type] = {
                "count": len(type_nodes),
                "avg_utilization": round(avg_utilization, 3)
            }
        
        # 按资源类型统计
        for resource_type in ResourceType:
            total_available = sum(n.available_resources.get(resource_type, 0) for n in self.resource_nodes.values())
            total_used = sum(n.current_usage.get(resource_type, 0) for n in self.resource_nodes.values())
            
            if total_available > 0:
                utilization_rate = total_used / total_available
                utilization_stats["by_resource"][resource_type.value] = round(utilization_rate, 3)
        
        # 总体利用率
        if utilization_stats["by_resource"]:
            utilization_stats["overall_utilization"] = round(
                sum(utilization_stats["by_resource"].values()) / len(utilization_stats["by_resource"]), 3
            )
        
        print(f"✅ 资源利用率监控完成")
        print(f"   总体利用率: {utilization_stats['overall_utilization']:.1%}")
        
        return utilization_stats

def demo_resource_scheduling():
    """演示资源调度"""
    print("🚀 智能资源调度器演示")
    print("=" * 60)
    
    scheduler = ResourceScheduler()
    
    # 1. 发现闲置资源
    print("\n1. 🔍 发现网络闲置资源")
    idle_nodes = scheduler.discover_idle_resources()
    
    # 2. 资源调度演示
    print("\n2. ⚡ 资源调度演示")
    
    # 高优先级请求（用户交互）
    high_priority_request = {
        'resources': {
            ResourceType.CPU: 2.0,
            ResourceType.MEMORY: 4.0,
            ResourceType.NETWORK: 100.0
        },
        'location': 'nearest'
    }
    
    print("   🔴 高优先级调度:")
    high_allocations = scheduler.schedule_resources(high_priority_request, ResourcePriority.HIGH)
    
    # 低优先级请求（数据备份）
    low_priority_request = {
        'resources': {
            ResourceType.STORAGE: 10.0
        },
        'location': 'any'
    }
    
    print("   🟢 低优先级调度:")
    low_allocations = scheduler.schedule_resources(low_priority_request, ResourcePriority.LOW)
    
    # 3. 成本节省计算
    print("\n3. 💰 成本节省分析")
    traditional_monthly_cost = 10000  # 假设传统架构月成本1万美元
    cost_savings = scheduler.calculate_cost_savings(traditional_monthly_cost)
    
    # 4. 资源利用率监控
    print("\n4. 📊 资源利用率监控")
    utilization = scheduler.monitor_resource_utilization()
    
    print("\n🎯 演示完成")
    print(f"   💡 双存在态架构实现'服务1亿用户而不增加额外开销'")
    print(f"   💰 成本节省: {cost_savings['savings_percentage']}%")
    print(f"   📊 资源利用率: {utilization['overall_utilization']:.1%}")

if __name__ == "__main__":
    demo_resource_scheduling()