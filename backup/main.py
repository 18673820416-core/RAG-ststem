# @self-expose: {"id": "main", "name": "Main", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Main功能"]}}
# RAG系统主程序入口

import argparse
import logging
import re
from pathlib import Path

from src.data_collector import DataCollector
from src.vector_database import VectorDatabase
from src.enhanced_data_crawler import EnhancedDataCrawler

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler()
    ]
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
            
        # 将收集的数据转换为记忆单元格式
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

def crawl_all_interaction_data():
    """爬取所有交互数据（绕过限制）"""
    logger.info("开始爬取所有交互数据...")
    
    crawler = EnhancedDataCrawler()
    all_data = crawler.crawl_all_sources()
    
    logger.info(f"爬取完成！共获得 {len(all_data)} 条交互数据")
    
    # 显示数据统计
    sources = {}
    for item in all_data:
        source = item.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("\n数据来源统计:")
    for source, count in sources.items():
        print(f"  {source}: {count} 条")
    
    return all_data

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

def check_data_quality():
    """检查数据质量"""
    logger.info("开始检查数据质量...")
    
    # 重新爬取数据以进行质量评估
    crawler = EnhancedDataCrawler()
    all_data = crawler.crawl_all_sources()
    
    # 评估数据质量
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
    parser.add_argument('--collect', action='store_true', help='收集数据')
    parser.add_argument('--build', action='store_true', help='构建记忆数据库')
    parser.add_argument('--search', type=str, help='搜索记忆内容')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--crawl', action='store_true', help='爬取所有交互数据（绕过限制）')
    parser.add_argument('--quality', action='store_true', help='检查数据质量')
    parser.add_argument('--limit', type=int, default=10, help='搜索结果数量限制')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG系统 - 基于意识=认知=记忆=意义的循环等式")
    print("=" * 60)
    
    if args.crawl:
        # 爬取所有交互数据
        data = crawl_all_interaction_data()
        # 自动构建记忆数据库
        build_memory_database(data)
    
    if args.collect:
        collect_data()
    
    if args.build:
        # 先收集数据，再构建数据库
        data = collect_data()
        build_memory_database(data)
    
    if args.search:
        search_memories(args.search, args.limit)
    
    if args.stats:
        show_statistics()
    
    if args.quality:
        check_data_quality()
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.collect, args.build, args.search, args.stats, args.crawl, args.quality]):
        print("\n使用方法:")
        print("  python main.py --crawl         # 爬取所有交互数据（绕过限制）")
        print("  python main.py --collect        # 收集数据")
        print("  python main.py --build         # 构建记忆数据库")
        print("  python main.py --search \"关键词\"  # 搜索记忆")
        print("  python main.py --stats         # 显示统计信息")
        print("  python main.py --quality       # 检查数据质量")
        print("\n示例:")
        print("  python main.py --crawl --stats  # 爬取数据并显示统计")
        print("  python main.py --search \"RAG系统\" --limit 5")
        print("  python main.py --quality        # 检查数据质量")

if __name__ == "__main__":
    main()