#!/usr/bin/env python3
# @self-expose: {"id": "data_crawler", "name": "Data Crawler", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Data Crawler功能"]}}
# -*- coding: utf-8 -*-
"""
独立数据爬取工具
- 通过命令激活才启动爬取
- 支持增量更新和全量爬取模式
- 爬取完成后数据持久化存储
- 避免主程序启动时重复爬取
"""

import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.enhanced_data_crawler import EnhancedDataCrawler
from src.data_collector import DataCollector
from config.system_config import DATA_DIR

logger = logging.getLogger(__name__)

class DataCrawlerTool:
    """独立数据爬取工具"""
    
    def __init__(self):
        self.crawler = EnhancedDataCrawler()
        self.collector = DataCollector()
        self.data_file = DATA_DIR / "crawled_data.json"
        self.metadata_file = DATA_DIR / "crawl_metadata.json"
    
    def check_existing_data(self) -> bool:
        """检查是否存在已爬取的数据"""
        return self.data_file.exists() and self.metadata_file.exists()
    
    def load_existing_data(self) -> Dict[str, Any]:
        """加载已爬取的数据"""
        if not self.check_existing_data():
            return {"data": [], "metadata": {}}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {"data": data, "metadata": metadata}
        except Exception as e:
            logger.error(f"加载现有数据失败: {e}")
            return {"data": [], "metadata": {}}
    
    def save_data(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """保存爬取的数据和元数据"""
        try:
            # 确保数据目录存在
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            # 保存数据
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存元数据
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {self.data_file}")
            logger.info(f"元数据已保存到: {self.metadata_file}")
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def crawl_full(self) -> List[Dict[str, Any]]:
        """全量爬取所有数据"""
        logger.info("开始全量数据爬取...")
        
        # 爬取所有交互数据
        all_data = self.crawler.crawl_all_sources()
        
        # 构建元数据
        metadata = {
            "crawl_type": "full",
            "crawl_time": datetime.now().isoformat(),
            "total_records": len(all_data),
            "sources": {}
        }
        
        # 统计来源信息
        for item in all_data:
            source = item.get('source', 'unknown')
            metadata['sources'][source] = metadata['sources'].get(source, 0) + 1
        
        # 保存数据
        self.save_data(all_data, metadata)
        
        logger.info(f"全量爬取完成！共获得 {len(all_data)} 条数据")
        return all_data
    
    def crawl_incremental(self) -> List[Dict[str, Any]]:
        """增量爬取新数据"""
        logger.info("开始增量数据爬取...")
        
        # 加载现有数据
        existing_data = self.load_existing_data()
        old_data = existing_data.get("data", [])
        old_metadata = existing_data.get("metadata", {})
        
        # 获取上次爬取时间
        last_crawl_time = old_metadata.get("crawl_time")
        
        # 增量爬取逻辑（简化版，实际需要更复杂的增量检测）
        # 这里暂时使用全量爬取，实际应该实现增量检测
        new_data = self.crawl_full()
        
        # 合并数据（去重）
        combined_data = self._merge_data(old_data, new_data)
        
        # 更新元数据
        metadata = {
            "crawl_type": "incremental",
            "crawl_time": datetime.now().isoformat(),
            "previous_crawl": last_crawl_time,
            "total_records": len(combined_data),
            "new_records": len(new_data) - len(old_data),
            "sources": {}
        }
        
        # 统计来源信息
        for item in combined_data:
            source = item.get('source', 'unknown')
            metadata['sources'][source] = metadata['sources'].get(source, 0) + 1
        
        # 保存数据
        self.save_data(combined_data, metadata)
        
        logger.info(f"增量爬取完成！新增 {metadata['new_records']} 条数据，总计 {len(combined_data)} 条")
        return combined_data
    
    def _merge_data(self, old_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
        """合并新旧数据（简单去重）"""
        # 基于内容哈希去重（简化版）
        seen = set()
        merged = []
        
        for item in old_data + new_data:
            # 生成简单的哈希标识
            content_hash = hash(item.get('content', '') + item.get('source', ''))
            
            if content_hash not in seen:
                seen.add(content_hash)
                merged.append(item)
        
        return merged
    
    def show_status(self):
        """显示数据爬取状态"""
        if not self.check_existing_data():
            print("❌ 未发现已爬取的数据")
            print("   请先运行爬取命令: python tools/data_crawler.py --crawl")
            return
        
        # 加载元数据
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print("📊 数据爬取状态:")
        print("=" * 50)
        print(f"爬取类型: {metadata.get('crawl_type', 'unknown')}")
        print(f"爬取时间: {metadata.get('crawl_time', 'unknown')}")
        print(f"数据总量: {metadata.get('total_records', 0)} 条")
        
        if 'sources' in metadata:
            print("\n数据来源统计:")
            for source, count in metadata['sources'].items():
                print(f"  {source}: {count} 条")
        
        if metadata.get('crawl_type') == 'incremental':
            print(f"新增数据: {metadata.get('new_records', 0)} 条")
            print(f"上次爬取: {metadata.get('previous_crawl', 'unknown')}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='独立数据爬取工具')
    parser.add_argument('--crawl', action='store_true', help='全量爬取所有数据')
    parser.add_argument('--incremental', action='store_true', help='增量爬取新数据')
    parser.add_argument('--status', action='store_true', help='显示爬取状态')
    parser.add_argument('--force', action='store_true', help='强制重新爬取（忽略现有数据）')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tool = DataCrawlerTool()
    
    if args.status:
        tool.show_status()
    
    elif args.crawl:
        if tool.check_existing_data() and not args.force:
            print("⚠️  已存在爬取数据，使用 --force 参数强制重新爬取")
            print("   或使用 --incremental 进行增量爬取")
            return
        
        tool.crawl_full()
    
    elif args.incremental:
        if not tool.check_existing_data():
            print("ℹ️  未发现现有数据，将进行全量爬取")
            tool.crawl_full()
        else:
            tool.crawl_incremental()
    
    else:
        print("独立数据爬取工具")
        print("=" * 30)
        print("使用方法:")
        print("  python tools/data_crawler.py --crawl        # 全量爬取")
        print("  python tools/data_crawler.py --incremental  # 增量爬取")
        print("  python tools/data_crawler.py --status      # 显示状态")
        print("  python tools/data_crawler.py --crawl --force # 强制重新爬取")

if __name__ == "__main__":
    main()