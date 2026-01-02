#!/usr/bin/env python
# @self-expose: {"id": "collect_e_drive_data", "name": "E盘数据收集器", "type": "component", "version": "1.0.0", "needs": {"deps": ["data_collector"], "resources": []}, "provides": {"capabilities": ["文件系统数据收集", "智能文本切片", "向量库数据保存"]}}
# -*- coding: utf-8 -*-
"""
收集E盘上的所有文本文件并添加到向量库
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 确保脚本可以从任何目录运行
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# 添加项目根目录到Python路径
sys.path.insert(0, project_root)

# 导入数据收集器类
try:
    from src.data_collector import DataCollector
except ImportError:
    # 如果直接从src目录运行，使用相对导入
    from data_collector import DataCollector

def main():
    """主函数"""
    logger.info("开始收集E盘上的文本文件...")
    
    try:
        # 创建数据收集器实例
        collector = DataCollector()
        logger.info("数据收集器初始化完成")
        
        # 定义要扫描的路径（E盘根目录）
        scan_path = "E:/"
        
        # 第一步：收集数据（使用智能切片）
        logger.info(f"开始收集数据...")
        collected_data = collector.collect_from_file_system(scan_path)
        logger.info(f"从路径 {scan_path} 收集到 {len(collected_data)} 条原始数据")
        
        # 第二步：对收集的数据进行智能切片
        logger.info(f"开始智能切片...")
        all_sliced_data = []
        for item in collected_data:
            content = item.get('content', '')
            if content:
                slices = collector._intelligent_slice_text(content, item.get('file_path', ''))
                all_sliced_data.extend(slices)
        logger.info(f"智能切片后得到 {len(all_sliced_data)} 条数据")
        
        # 第三步：保存收集的数据到向量库
        logger.info(f"开始保存数据到向量库...")
        collector._save_collected_data(all_sliced_data)
        logger.info(f"成功保存 {len(all_sliced_data)} 条数据到向量库")
        
        logger.info("E盘文本文件收集完成！")
        
    except Exception as e:
        logger.error(f"收集过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
