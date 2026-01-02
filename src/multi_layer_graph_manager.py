#!/usr/bin/env python3
# @self-expose: {"id": "multi_layer_graph_manager", "name": "Multi Layer Graph Manager", "type": "component", "version": "1.1.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Multi Layer Graph Manager功能", "knowledge_graph.search_across_layers", "knowledge_graph.get_layer_navigation"]}}
"""
多层图谱管理类
实现图谱管理另一个图谱的多层网状结构
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class GraphLayerConfig:
    """图谱层级配置"""
    layer_id: str
    layer_name: str
    level: int  # 层级深度，1为顶层，数字越大层级越深
    parent_layer_id: Optional[str] = None
    max_nodes: int = 200
    min_importance: float = 0.05
    topic_filter: Optional[str] = None
    dynamic_inclusion: bool = True
    

class MultiLayerGraphManager:
    """多层图谱管理器"""
    
    def __init__(self, mesh_interface):
        self.mesh_interface = mesh_interface
        self.graph_layers: Dict[str, GraphLayerConfig] = {}
        self.layer_graphs: Dict[str, Dict[str, Any]] = {}
        self.layer_hierarchy: Dict[str, List[str]] = {}  # 父层ID -> 子层ID列表
        
    def create_graph_layer(self, layer_name: str, level: int = 1, 
                          parent_layer_id: Optional[str] = None,
                          max_nodes: int = 200, min_importance: float = 0.05,
                          topic_filter: Optional[str] = None) -> str:
        """创建新的图谱层级"""
        
        # 生成唯一层ID
        layer_id = f"layer_{len(self.graph_layers) + 1}"
        
        # 创建层配置
        layer_config = GraphLayerConfig(
            layer_id=layer_id,
            layer_name=layer_name,
            level=level,
            parent_layer_id=parent_layer_id,
            max_nodes=max_nodes,
            min_importance=min_importance,
            topic_filter=topic_filter
        )
        
        # 添加到管理层
        self.graph_layers[layer_id] = layer_config
        
        # 更新层级关系
        if parent_layer_id:
            if parent_layer_id not in self.layer_hierarchy:
                self.layer_hierarchy[parent_layer_id] = []
            self.layer_hierarchy[parent_layer_id].append(layer_id)
        
        print(f"✅ 创建图谱层级: {layer_name} (ID: {layer_id}, 层级: {level})")
        return layer_id
    
    def build_layer_graph(self, layer_id: str) -> Dict[str, Any]:
        """构建指定层级的图谱"""
        
        if layer_id not in self.graph_layers:
            raise ValueError(f"图谱层级 {layer_id} 不存在")
        
        layer_config = self.graph_layers[layer_id]
        
        # 构建该层级的图谱
        graph = self.mesh_interface.build_knowledge_graph(
            topic=layer_config.topic_filter,
            max_nodes=layer_config.max_nodes,
            min_importance=layer_config.min_importance,
            dynamic_inclusion=layer_config.dynamic_inclusion
        )
        
        # 添加层级信息
        graph['layer_info'] = {
            'layer_id': layer_config.layer_id,
            'layer_name': layer_config.layer_name,
            'level': layer_config.level,
            'parent_layer_id': layer_config.parent_layer_id
        }
        
        # 存储图谱
        self.layer_graphs[layer_id] = graph
        
        print(f"✅ 构建层级图谱: {layer_config.layer_name} - 节点数: {len(graph['nodes'])}")
        return graph
    
    def build_multi_layer_graphs(self) -> Dict[str, Any]:
        """构建多层图谱结构"""
        
        print("=== 开始构建多层图谱结构 ===")
        
        # 1. 构建顶层全局图谱（全覆盖索引视图）
        global_layer_id = self.create_graph_layer(
            layer_name="全局知识图谱",
            level=1,
            max_nodes=500,  # 此参数在 full_index=True 时仅用于元数据展示
            min_importance=0.02  # 顶层重要性阈值更低
        )
        
        # 顶层使用 full_index=True，确保覆盖向量库中所有重要记忆
        global_graph = self.mesh_interface.build_knowledge_graph(
            topic=None,
            max_nodes=500,
            min_importance=0.02,
            dynamic_inclusion=False,
            full_index=True
        )
        
        # 2. 分析顶层图谱，自动创建子层
        self._auto_create_sub_layers(global_layer_id, global_graph)
        
        # 3. 构建所有子层图谱
        for layer_id in self.graph_layers:
            if layer_id != global_layer_id:  # 跳过已构建的顶层
                self.build_layer_graph(layer_id)
        
        # 4. 构建层间连接
        self._build_inter_layer_connections()
        
        # 5. 生成多层图谱统计
        stats = self._generate_multi_layer_stats()
        
        print(f"✅ 多层图谱构建完成！")
        print(f"   总层数: {stats['total_layers']}")
        print(f"   总节点数: {stats['total_nodes']}")
        print(f"   总边数: {stats['total_edges']}")
        print(f"   层级深度: {stats['max_depth']}")
        
        return {
            'global_graph': global_graph,
            'layer_graphs': self.layer_graphs,
            'layer_hierarchy': self.layer_hierarchy,
            'statistics': stats
        }
    
    def _auto_create_sub_layers(self, parent_layer_id: str, parent_graph: Dict[str, Any]) -> None:
        """基于父层图谱自动创建子层"""
        
        # 分析父层图谱中的主题分布
        topic_distribution = {}
        for node in parent_graph['nodes']:
            topic = node['topic']
            if topic not in topic_distribution:
                topic_distribution[topic] = 0
            topic_distribution[topic] += 1
        
        # 为主题节点数较多的主题创建子层
        for topic, count in topic_distribution.items():
            if count >= 10:  # 主题节点数达到阈值
                sub_layer_id = self.create_graph_layer(
                    layer_name=f"主题图谱: {topic}",
                    level=2,
                    parent_layer_id=parent_layer_id,
                    topic_filter=topic,
                    max_nodes=200,
                    min_importance=0.05
                )
                
                # 为重要事件创建更深层
                if count >= 30:  # 主题节点数很多，可能需要更深层
                    event_layer_id = self.create_graph_layer(
                        layer_name=f"事件图谱: {topic}",
                        level=3,
                        parent_layer_id=sub_layer_id,
                        topic_filter=topic,
                        max_nodes=100,
                        min_importance=0.1  # 事件层重要性阈值更高
                    )
    
    def _build_inter_layer_connections(self) -> None:
        """构建层间连接关系"""
        
        print("构建层间连接关系...")
        
        for parent_id, child_ids in self.layer_hierarchy.items():
            if parent_id not in self.layer_graphs:
                continue
                
            parent_graph = self.layer_graphs[parent_id]
            
            for child_id in child_ids:
                if child_id not in self.layer_graphs:
                    continue
                    
                child_graph = self.layer_graphs[child_id]
                
                # 构建父层到子层的连接
                self._connect_parent_to_child(parent_graph, child_graph)
    
    def _connect_parent_to_child(self, parent_graph: Dict[str, Any], 
                               child_graph: Dict[str, Any]) -> None:
        """构建父层到子层的连接"""
        
        # 在父层图谱中添加子层连接节点
        connection_node = {
            'id': f"connection_{child_graph['layer_info']['layer_id']}",
            'type': 'layer_connection',
            'content': f"连接到 {child_graph['layer_info']['layer_name']}",
            'topic': '层间连接',
            'importance': 0.5,
            'confidence': 1.0,
            'timestamp': datetime.now().isoformat(),
            'target_layer': child_graph['layer_info']['layer_id']
        }
        
        parent_graph['nodes'].append(connection_node)
        
        # 添加连接边
        connection_edge = {
            'source': connection_node['id'],
            'target': child_graph['nodes'][0]['id'] if child_graph['nodes'] else '',
            'type': 'layer_hierarchy',
            'strength': 0.8,
            'relation': 'parent_child_connection'
        }
        
        parent_graph['edges'].append(connection_edge)
    
    def _generate_multi_layer_stats(self) -> Dict[str, Any]:
        """生成多层图谱统计信息"""
        
        total_nodes = 0
        total_edges = 0
        max_depth = 0
        
        for layer_id, graph in self.layer_graphs.items():
            total_nodes += len(graph['nodes'])
            total_edges += len(graph['edges'])
            max_depth = max(max_depth, graph['layer_info']['level'])
        
        return {
            'total_layers': len(self.layer_graphs),
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'max_depth': max_depth,
            'layer_distribution': {layer_id: len(graph['nodes']) 
                                 for layer_id, graph in self.layer_graphs.items()}
        }
    
    def get_layer_navigation(self, current_layer_id: str) -> Dict[str, Any]:
        """获取层级导航信息"""
        
        if current_layer_id not in self.graph_layers:
            return {'error': '图层不存在'}
        
        current_layer = self.graph_layers[current_layer_id]
        
        navigation = {
            'current_layer': {
                'id': current_layer.layer_id,
                'name': current_layer.layer_name,
                'level': current_layer.level
            },
            'parent_layers': [],
            'child_layers': [],
            'sibling_layers': []
        }
        
        # 获取父层
        if current_layer.parent_layer_id:
            parent_layer = self.graph_layers[current_layer.parent_layer_id]
            navigation['parent_layers'].append({
                'id': parent_layer.layer_id,
                'name': parent_layer.layer_name,
                'level': parent_layer.level
            })
        
        # 获取子层
        if current_layer_id in self.layer_hierarchy:
            for child_id in self.layer_hierarchy[current_layer_id]:
                child_layer = self.graph_layers[child_id]
                navigation['child_layers'].append({
                    'id': child_layer.layer_id,
                    'name': child_layer.layer_name,
                    'level': child_layer.level
                })
        
        # 获取兄弟层（同一父层的其他子层）
        if current_layer.parent_layer_id and current_layer.parent_layer_id in self.layer_hierarchy:
            for sibling_id in self.layer_hierarchy[current_layer.parent_layer_id]:
                if sibling_id != current_layer_id:
                    sibling_layer = self.graph_layers[sibling_id]
                    navigation['sibling_layers'].append({
                        'id': sibling_layer.layer_id,
                        'name': sibling_layer.layer_name,
                        'level': sibling_layer.level
                    })
        
        return navigation
    
    def search_across_layers(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """跨层级搜索"""
        
        results = []
        
        for layer_id, graph in self.layer_graphs.items():
            layer_info = graph['layer_info']
            
            # 在当前层图谱中搜索
            for node in graph['nodes']:
                if query.lower() in node['content'].lower() or query.lower() in node['topic'].lower():
                    results.append({
                        'layer_id': layer_id,
                        'layer_name': layer_info['layer_name'],
                        'layer_level': layer_info['level'],
                        'node': node,
                        'relevance_score': self._calculate_relevance_score(node, query)
                    })
        
        # 按相关性排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'query': query,
            'total_results': len(results),
            'results': results[:max_results],
            'layer_distribution': self._get_results_layer_distribution(results)
        }
    
    def _calculate_relevance_score(self, node: Dict[str, Any], query: str) -> float:
        """计算节点与查询的相关性分数"""
        
        score = 0.0
        
        # 内容匹配
        content_lower = node['content'].lower()
        query_lower = query.lower()
        
        if query_lower in content_lower:
            score += 0.6
        
        # 主题匹配
        topic_lower = node['topic'].lower()
        if query_lower in topic_lower:
            score += 0.8
        
        # 重要性加权
        score += node.get('importance', 0) * 0.2
        
        return min(score, 1.0)
    
    def _get_results_layer_distribution(self, results: List[Dict[str, Any]]) -> Dict[int, int]:
        """获取搜索结果在不同层级的分布"""
        
        distribution = {}
        for result in results:
            level = result['layer_level']
            distribution[level] = distribution.get(level, 0) + 1
        
        return distribution


def test_multi_layer_graph_manager():
    """测试多层图谱管理器"""
    
    print("=== 测试多层图谱管理器 ===")
    
    # 创建网状思维接口实例
    from mesh_database_interface import MeshDatabaseInterface
    interface = MeshDatabaseInterface()
    
    # 创建多层图谱管理器
    manager = MultiLayerGraphManager(interface)
    
    # 构建多层图谱
    multi_layer_result = manager.build_multi_layer_graphs()
    
    # 测试层级导航
    if multi_layer_result['layer_graphs']:
        first_layer_id = list(multi_layer_result['layer_graphs'].keys())[0]
        navigation = manager.get_layer_navigation(first_layer_id)
        print(f"层级导航: {navigation}")
    
    # 测试跨层级搜索
    search_result = manager.search_across_layers("AI", max_results=5)
    print(f"跨层级搜索结果: {len(search_result['results'])} 个结果")
    
    return manager


if __name__ == "__main__":
    test_multi_layer_graph_manager()