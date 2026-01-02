# @self-expose: {"id": "main", "name": "Main", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Main功能"]}}
# RAG系统主程序入口

import argparse
import json
import logging
import re
from pathlib import Path

from src.data_collector import DataCollector
from src.vector_database import VectorDatabase
from src.enhanced_data_crawler import EnhancedDataCrawler
from src.mesh_database_interface import MeshDatabaseInterface

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def collect_data():
    """数据收集功能"""
    logger.info("开始数据收集...")
    
    collector = DataCollector()
    data = collector.collect_all_sources()
    
    logger.info(f"数据收集完成，共收集到 {len(data)} 条数据")
    return data

def build_memory_database(data: list):
    """构建记忆数据库 - 添加数据质量过滤"""
    logger.info("开始构建记忆数据库...")
    
    db = VectorDatabase()
    
    memory_count = 0
    filtered_count = 0
    
    for item in data:
        content = item.get('content', '')
        
        # 数据质量过滤 - 删除空内容和短内容
        if not content.strip():
            logger.debug(f"过滤掉空内容: {item.get('source', 'unknown')}")
            filtered_count += 1
            continue
            
        if len(content.strip()) < 20:
            logger.debug(f"过滤掉过短内容 (<20字符): {item.get('source', 'unknown')}")
            filtered_count += 1
            continue
            
        # 检查是否只包含特殊字符或数字
        if re.match(r'^[\s\d\W]+$', content.strip()):
            logger.debug(f"过滤掉无效内容 (仅特殊字符或数字): {item.get('source', 'unknown')}")
            filtered_count += 1
            continue
            
        # 处理数据收集器生成的数据格式
        if 'metadata' in item and 'file_path' in item['metadata']:
            # 这是数据收集器生成的数据格式
            file_path = item['metadata']['file_path']
            source_type = 'collected_data'
            
            # 根据文件路径确定主题
            if 'docs' in file_path.lower():
                topic = 'DOCS聊天记录'
            elif 'logs' in file_path.lower():
                topic = '系统日志'
            else:
                topic = '其他数据'
                
            # 使用语义质量作为重要性指标
            importance = item.get('semantic_quality', 0.5)
            
            memory_data = {
                'topic': topic,
                'content': content,
                'source_type': source_type,
                'timestamp': item['metadata'].get('collected_at', ''),
                'importance': importance,
                'confidence': 0.8,
                'tags': ['collected', 'sliced']
            }
        else:
            # 这是传统的数据格式
            memory_data = {
                'topic': item.get('source', '未分类'),
                'content': content,
                'source_type': item.get('source', 'unknown'),
                'timestamp': item.get('collected_at', item.get('last_modified', '')),
                'importance': 0.5,  # 默认重要性
                'confidence': 0.8,  # 默认置信度
                'tags': [item.get('file_type', 'unknown')]
            }
        
        # 添加记忆单元（暂时不处理向量）
        db.add_memory(memory_data)
        memory_count += 1
    
    logger.info(f"记忆数据库构建完成，添加了 {memory_count} 条记忆，过滤掉了 {filtered_count} 条低质量数据")
    print(f"✅ 记忆数据库构建完成")
    print(f"   添加记忆: {memory_count} 条")
    print(f"   过滤数据: {filtered_count} 条")
    db.close()

def search_memories(query: str, limit: int = 10):
    """搜索记忆"""
    logger.info(f"搜索记忆: {query}")
    
    db = VectorDatabase()
    results = db.search_memories(query=query, limit=limit)
    
    print(f"\n搜索 '{query}' 的结果 ({len(results)} 条):")
    print("=" * 50)
    
    for i, memory in enumerate(results, 1):
        print(f"\n{i}. [{memory['source_type']}] {memory['topic']}")
        print(f"   重要性: {memory['importance']} | 置信度: {memory['confidence']}")
        print(f"   时间: {memory['timestamp']}")
        print(f"   内容: {memory['content'][:100]}...")
        if memory.get('tags'):
            print(f"   标签: {', '.join(memory['tags'])}")
    
    db.close()

def load_existing_data():
    """加载已爬取的数据"""
    data_file = Path("data/crawled_data.json")
    
    if not data_file.exists():
        logger.warning("未发现已爬取的数据文件")
        print("❌ 未发现已爬取的数据")
        print("   请先运行数据爬取工具: python tools/data_crawler.py --crawl")
        return []
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"加载现有数据成功，共 {len(data)} 条记录")
        return data
        
    except Exception as e:
        logger.error(f"加载现有数据失败: {e}")
        print(f"❌ 加载数据失败: {e}")
        return []

def load_collected_data():
    """加载数据收集器生成的数据"""
    # 查找最新的收集数据文件
    data_dir = Path("data")
    collected_files = list(data_dir.glob("collected_data_*.json"))
    
    if not collected_files:
        logger.warning("未发现数据收集器生成的数据文件")
        print("❌ 未发现数据收集器生成的数据")
        print("   请先运行数据收集器: python src/data_collector.py")
        return []
    
    # 按时间戳排序，取最新的文件
    collected_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = collected_files[0]
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"加载收集数据成功，共 {len(data)} 条记录")
        print(f"✅ 加载收集数据成功: {latest_file.name}")
        print(f"   记录数量: {len(data)} 条")
        return data
        
    except Exception as e:
        logger.error(f"加载收集数据失败: {e}")
        print(f"❌ 加载收集数据失败: {e}")
        return []

def show_statistics():
    """显示系统统计信息"""
    db = VectorDatabase()
    
    memory_count = db.get_memory_count()
    topics = db.get_topics()
    
    print("\nRAG系统统计信息:")
    print("=" * 30)
    print(f"记忆单元总数: {memory_count}")
    print(f"主题分类数: {len(topics)}")
    print(f"主题列表: {', '.join(topics[:10])}{'...' if len(topics) > 10 else ''}")
    
    db.close()

def show_mesh_statistics():
    """显示网状思维引擎统计信息"""
    try:
        mesh_interface = MeshDatabaseInterface()
        
        print("\n网状思维引擎统计信息:")
        print("=" * 40)
        
        # 思维节点统计
        node_count = mesh_interface.thought_engine.get_node_count()
        print(f"思维节点总数: {node_count}")
        
        if node_count > 0:
            # 隐藏关系发现
            hidden_relations = mesh_interface.thought_engine.discover_hidden_relations(similarity_threshold=0.3)
            print(f"隐藏关系数量: {len(hidden_relations)}")
            
            # 动态关系更新
            mesh_interface.thought_engine.update_relation_strengths()
            print("动态关系强度已更新")
            
            # 显示最重要的节点
            important_nodes = mesh_interface.thought_engine.get_most_important_nodes(limit=3)
            print(f"\n最重要的思维节点 (前3个):")
            for i, node in enumerate(important_nodes, 1):
                print(f"  {i}. {node.id} - 重要性: {node.importance:.3f}")
                print(f"     内容: {node.content[:80]}..." if len(node.content) > 80 else f"     内容: {node.content}")
        
        # 记忆数据库统计
        db_stats = mesh_interface.get_mesh_statistics()
        print(f"\n记忆数据库统计:")
        print(f"  记忆总数: {db_stats['vector_database']['total_memories']}")
        print(f"  主题数: {len(db_stats['vector_database']['topics'])}")
        
        # 集成指标
        print(f"\n集成指标:")
        print(f"  网状增强记忆数: {db_stats['integration_metrics']['memories_with_mesh']}")
        print(f"  平均重要性: {db_stats['integration_metrics']['average_importance']:.3f}")
        
        # 关联网络统计
        if node_count > 0:
            total_connections = sum(len(node.connections) for node in mesh_interface.thought_engine.nodes.values())
            avg_connections = total_connections / node_count if node_count > 0 else 0
            print(f"  平均关联数: {avg_connections:.2f}")
        
        mesh_interface.vector_db.close()
        
    except Exception as e:
        print(f"获取网状思维引擎统计信息失败: {e}")

def search_memories_with_mesh(query: str, limit: int = 10):
    """使用网状思维引擎增强搜索记忆"""
    logger.info(f"网状增强搜索: {query}")
    
    interface = MeshDatabaseInterface()
    results = interface.search_memories_with_mesh(query=query, limit=limit)
    
    memories = results['memories']
    mesh_info = results['mesh_enhancement']
    
    print(f"\n网状增强搜索 '{query}' 的结果:")
    print("=" * 60)
    
    if mesh_info.get('enabled', True):
        print(f"连续性水平: {mesh_info.get('continuity_level', 0):.3f}")
        print(f"激活思维节点: {mesh_info.get('thoughts_activated', 0)}个")
        print(f"增强查询: {mesh_info.get('enhanced_query', query)}")
    
    print(f"找到记忆: {len(memories)} 条")
    
    for i, memory in enumerate(memories, 1):
        print(f"\n{i}. [{memory['source_type']}] {memory['topic']}")
        print(f"   重要性: {memory['importance']:.3f} | 置信度: {memory['confidence']:.3f}")
        if memory.get('mesh_importance'):
            print(f"   网状重要性: {memory['mesh_importance']:.3f}")
        print(f"   时间: {memory['timestamp']}")
        print(f"   内容: {memory['content'][:120]}...")
        if memory.get('tags'):
            print(f"   标签: {', '.join(memory['tags'])}")
    
    interface.vector_db.close()

def build_knowledge_graph(topic: str = None):
    """构建知识图谱（优先使用接口构建，回退至先进重建器）"""
    logger.info(f"构建知识图谱: {topic or '全局'}")
    try:
        from src.mesh_database_interface import MeshDatabaseInterface
        from src.multi_layer_graph_manager import MultiLayerGraphManager
        interface = MeshDatabaseInterface()
        graph = interface.build_knowledge_graph(topic=topic)
        edges = graph.get('edges', [])
        time_edges = [e for e in edges if e.get('type') == 'time_sequence']
        causal_edges = [e for e in edges if e.get('type') == 'causal']
        meta = graph.get('metadata', {})
        print("\n知识图谱统计:")
        print("=" * 60)
        print(f"主题: {meta.get('topic', topic or '全局')}")
        print(f"构建时间: {meta.get('build_time')}")
        print(f"节点数: {len(graph.get('nodes', []))}")
        print(f"边数: {len(edges)}")
        print(f"覆盖率: {meta.get('coverage_rate', 0):.2f}%")
        print(f"时间序列边: {len(time_edges)}")
        print(f"因果关系边: {len(causal_edges)}")
        # 构建多层图谱并输出分布
        manager = MultiLayerGraphManager(interface)
        result = manager.build_multi_layer_graphs()
        search_res = manager.search_across_layers(str(topic or ''), max_results=10)
        dist = search_res.get('layer_distribution') or search_res.get('distribution', {})
        print("\n层级分布(检索结果):")
        for level, count in sorted(dist.items()):
            print(f"  层级{level}: {count}个")
        # 缓存保存
        import os, json
        cache_dir = os.path.join('data', 'graph_cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"graph_{(topic or 'global')}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'graph': graph, 'layer_stats': result.get('statistics', {})}, f, ensure_ascii=False, indent=2)
        print("\n✅ 知识图谱构建完成并已缓存")
        
        return graph
    except Exception as e:
        print(f"⚠️ 接口构建失败，回退至先进重建器: {e}")
    
    print("⚠️  使用记忆锚点先进逻辑：网状思维引擎+主题维度树形结构")
    
    # 导入先进重建器
    from rebuild_knowledge_graph import AdvancedKnowledgeGraphRebuilder
    
    rebuilder = AdvancedKnowledgeGraphRebuilder()
    
    # 使用先进重建方法
    hierarchical_graph = rebuilder.rebuild_advanced()
    
    if not hierarchical_graph:
        print("❌ 知识图谱构建失败")
        return None
    
    print(f"\n先进知识图谱 - {topic or '全局'}:")
    print("=" * 60)
    
    global_layer = hierarchical_graph['global_layer']
    topic_layer = hierarchical_graph['topic_layer']
    event_layer = hierarchical_graph['event_layer']
    
    metadata = global_layer['metadata']
    print(f"架构: {metadata['architecture']}")
    print(f"构建时间: {metadata['build_time']}")
    print(f"节点总数: {len(global_layer['nodes'])}")
    print(f"边总数: {len(global_layer['edges'])}")
    print(f"主题数量: {topic_layer['metadata']['total_topics']}")
    print(f"逻辑链数量: {event_layer['metadata']['total_logic_chains']}")
    print(f"时间关系数量: {event_layer['metadata']['total_temporal_relations']}")
    print(f"因果关系数量: {event_layer['metadata']['total_causal_relations']}")
    print(f"先进特性: {', '.join(metadata['advanced_features'])}")
    
    # 显示部分节点
    print(f"\n节点示例 (前5个):")
    for i, node in enumerate(global_layer['nodes'][:5]):
        print(f"  {i+1}. {node['content']}")
        print(f"     主题: {node['topic']}, 重要性: {node['importance']:.3f}")
        print(f"     网状连接数: {node['mesh_connections']}")
    
    # 显示边信息
    if global_layer['edges']:
        print(f"\n边示例 (前5个):")
        for i, edge in enumerate(global_layer['edges'][:5]):
            source_node = next((n for n in global_layer['nodes'] if n['id'] == edge['source']), None)
            target_node = next((n for n in global_layer['nodes'] if n['id'] == edge['target']), None)
            
            if source_node and target_node:
                print(f"  {i+1}. {source_node['content'][:30]}... -> {target_node['content'][:30]}...")
                print(f"     关系类型: {edge['type']}, 权重: {edge['weight']:.3f}")
                print(f"     关系描述: {edge['relation']}")
    
    # 显示主题层次结构
    print(f"\n主题层次结构:")
    global_topic = topic_layer['hierarchy']['global']
    print(f"  全局主题: {global_topic['name']}")
    for i, subtopic in enumerate(global_topic['children'][:3]):
        print(f"    {i+1}. {subtopic['name']} ({subtopic['coverage']}个记忆)")
    
    print(f"\n✅ 先进知识图谱构建完成！")
    
    return hierarchical_graph

def check_data_quality():
    """检查数据质量"""
    logger.info("开始检查数据质量...")
    
    # 加载现有数据
    all_data = load_existing_data()
    if not all_data:
        return None
    
    # 评估数据质量
    crawler = EnhancedDataCrawler()
    quality_report = crawler.evaluate_data_quality(all_data)
    
    print("\n数据质量评估报告:")
    print("=" * 50)
    print(f"总记录数: {quality_report['total_records']}")
    print(f"平均质量分数: {quality_report['average_quality_score']}")
    
    print("\n质量分布:")
    for level, count in quality_report['quality_distribution'].items():
        percentage = (count / quality_report['total_records']) * 100
        print(f"  {level}: {count} 条 ({percentage:.1f}%)")
    
    print("\n按来源质量统计:")
    for source, stats in quality_report['source_quality'].items():
        avg_score = stats['total_score'] / stats['count']
        print(f"  {source}: {stats['count']} 条，平均质量: {avg_score:.3f}")
    
    if quality_report['issues_found']:
        print(f"\n发现的问题 ({len(quality_report['issues_found'])} 个):")
        for issue in quality_report['issues_found'][:10]:  # 只显示前10个问题
            print(f"  - {issue}")
        if len(quality_report['issues_found']) > 10:
            print(f"  ... 还有 {len(quality_report['issues_found']) - 10} 个问题")
    else:
        print("\n未发现明显数据问题")
    
    # 质量建议
    print("\n质量改进建议:")
    if quality_report['average_quality_score'] < 0.5:
        print("  ⚠️  数据质量较低，建议检查数据源和爬取配置")
    elif quality_report['average_quality_score'] < 0.7:
        print("  ℹ️  数据质量一般，可考虑优化数据预处理")
    else:
        print("  ✅ 数据质量良好")
    
    return quality_report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='RAG系统 - 记忆系统化管理')
    parser.add_argument('--build', action='store_true', help='构建记忆数据库（使用现有数据）')
    parser.add_argument('--build-collected', action='store_true', help='构建包含收集数据的记忆数据库')
    parser.add_argument('--search', type=str, help='搜索记忆内容')
    parser.add_argument('--mesh-search', type=str, help='使用网状思维引擎增强搜索')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--mesh-stats', action='store_true', help='显示网状思维引擎统计信息')
    parser.add_argument('--knowledge-graph', type=str, nargs='?', const='', help='构建知识图谱（可指定主题）')
    parser.add_argument('--quality', action='store_true', help='检查数据质量')
    parser.add_argument('--limit', type=int, default=10, help='搜索结果数量限制')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG系统 - 基于意识=认知=记忆=意义的循环等式")
    print("=" * 60)
    
    if args.build:
        # 使用现有数据构建数据库
        data = load_existing_data()
        if data:
            build_memory_database(data)
    
    if args.build_collected:
        # 使用收集数据构建数据库
        data = load_collected_data()
        if data:
            build_memory_database(data)
    
    if args.search:
        search_memories(args.search, args.limit)
    
    if args.mesh_search:
        search_memories_with_mesh(args.mesh_search, args.limit)
    
    if args.stats:
        show_statistics()
    
    if args.mesh_stats:
        show_mesh_statistics()
    
    if args.knowledge_graph is not None:
        topic = args.knowledge_graph if args.knowledge_graph != '' else None
        build_knowledge_graph(topic)
    
    if args.quality:
        check_data_quality()
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.build, args.build_collected, args.search, args.mesh_search, 
                args.stats, args.mesh_stats, args.knowledge_graph is not None,
                args.quality]):
        print("\n使用方法:")
        print("  python main.py --build                 # 使用现有数据构建记忆数据库")
        print("  python main.py --build-collected       # 使用收集数据构建记忆数据库")
        print("  python main.py --search \"关键词\"       # 搜索记忆")
        print("  python main.py --mesh-search \"关键词\"  # 使用网状思维引擎增强搜索")
        print("  python main.py --stats                 # 显示统计信息")
        print("  python main.py --mesh-stats            # 显示网状思维引擎统计信息")
        print("  python main.py --knowledge-graph       # 构建全局知识图谱")
        print("  python main.py --knowledge-graph \"主题\" # 构建指定主题知识图谱")
        print("  python main.py --quality               # 检查数据质量")
        print("  --limit N                             # 搜索结果数量限制（默认10）")
        print("\n数据爬取工具:")
        print("  python tools/data_crawler.py --crawl        # 全量爬取数据")
        print("  python tools/data_crawler.py --incremental  # 增量爬取数据")
        print("  python tools/data_crawler.py --status      # 显示爬取状态")
        print("\n示例:")
        print("  python tools/data_crawler.py --crawl       # 先爬取数据")
        print("  python main.py --build --stats              # 构建数据库并显示统计")
        print("  python main.py --build-collected --stats    # 构建收集数据库并显示统计")
        print("  python main.py --mesh-search \"AI技术\" --limit 5")
        print("  python main.py --mesh-stats                 # 显示网状思维统计")
        print("  python main.py --knowledge-graph \"AI技术\" # 构建AI技术知识图谱")

if __name__ == "__main__":
    main()