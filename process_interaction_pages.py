#!/usr/bin/env python
# @self-expose: {"id": "process_interaction_pages", "name": "Process Interaction Pages", "type": "component", "version": "1.0.0", "needs": {"deps": ["mesh_thought_engine", "vector_database"], "resources": []}, "provides": {"capabilities": "处理交互页面文件并存入向量库"}}
# -*- coding: utf-8 -*-
"""
处理交互页面文件，经过二次分片和网状思维引擎处理后存入12维向量库

功能：
1. 读取交互页面文件内容
2. 使用二次分片工具对内容进行分片
3. 使用网状思维引擎对每个分片生成向量
4. 将分片和向量存入12维向量库

使用方法：
python process_interaction_pages.py
"""

import os
import re
import json
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from src.mesh_thought_engine import MeshThoughtEngine, VectorStore
from src.vector_database import VectorDatabase
from src.agent_conversation_window import AgentConversationWindow

class InteractionPageProcessor:
    """交互页面处理器"""
    
    def __init__(self):
        """初始化处理器"""
        # 创建网状思维引擎实例
        self.mesh_engine = MeshThoughtEngine(vector_dimension=12)  # 使用12维向量
        # 创建向量数据库实例
        self.vector_db = VectorDatabase()
        # 创建会话窗口实例（用于二次分片）
        self.conversation_window = AgentConversationWindow("processor", "页面处理器", None)
        
        # 配置
        self.vector_store = VectorStore(dimension=12)  # 12维向量存储
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return ""
    
    def clean_html_content(self, html_content: str) -> str:
        """清理HTML内容，提取文本"""
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # 移除多余空白字符
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def slice_content(self, content: str) -> List[str]:
        """二次分片处理"""
        # 首先使用逻辑链分片
        slices = self.conversation_window._slice_logic_chain(content)
        
        # 进一步优化分片，确保每个分片大小合适
        optimized_slices = []
        for slice in slices:
            if len(slice) > 200:  # 如果分片太长，进一步分割
                # 按句子分割
                sentences = re.split(r'[。！？!?]', slice)
                current_slice = ""
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_slice) + len(sentence) < 200:
                        current_slice += sentence + "。"
                    else:
                        if current_slice:
                            optimized_slices.append(current_slice)
                        current_slice = sentence + "。"
                if current_slice:
                    optimized_slices.append(current_slice)
            elif len(slice) > 50:  # 合适大小的分片
                optimized_slices.append(slice)
        
        return optimized_slices
    
    def process_page(self, file_path: str, page_type: str):
        """处理单个页面文件"""
        print(f"\n=== 处理页面文件: {file_path} ===")
        
        # 1. 读取文件内容
        html_content = self.read_file_content(file_path)
        if not html_content:
            return
        
        # 2. 清理HTML内容
        clean_text = self.clean_html_content(html_content)
        print(f"清理后文本长度: {len(clean_text)} 字符")
        
        # 3. 二次分片处理
        slices = self.slice_content(clean_text)
        print(f"二次分片结果: {len(slices)} 个分片")
        
        # 4. 处理每个分片
        for i, slice_content in enumerate(slices):
            if len(slice_content) < 50:  # 跳过太短的分片
                continue
            
            print(f"\n处理分片 {i+1}/{len(slices)}")
            print(f"分片内容: {slice_content[:100]}...")
            
            # 5. 使用网状思维引擎处理
            thought_node = self.mesh_engine.store_thought(slice_content, {
                'source': page_type,
                'file_path': file_path,
                'slice_index': i
            })
            
            # 6. 生成12维向量
            vector = self.vector_store.embed(slice_content)
            
            # 7. 存入12维向量库
            memory_data = {
                'topic': f"{page_type}交互页面",
                'content': slice_content,
                'source_type': page_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'importance': thought_node.importance,
                'confidence': 0.9,
                'tags': [page_type, '交互页面', '向量库']
            }
            
            memory_id = self.vector_db.add_memory(memory_data, vector)
            print(f"存入向量库成功，ID: {memory_id}")
    
    def process_all_pages(self):
        """处理所有交互页面"""
        # 定义要处理的页面文件
        pages = [
            (r"e:\RAG系统\simple_chat.html", "simple_chat"),
            (r"e:\RAG系统\templates\agent_chatbot.html", "agent_chatbot")
        ]
        
        for file_path, page_type in pages:
            if os.path.exists(file_path):
                self.process_page(file_path, page_type)
            else:
                print(f"文件不存在: {file_path}")
    
    def get_statistics(self):
        """获取处理统计信息"""
        print(f"\n=== 处理统计信息 ===")
        print(f"网状思维引擎节点数: {self.mesh_engine.get_node_count()}")
        print(f"向量库记忆单元数: {self.vector_db.get_memory_count()}")
        
        # 打印向量库时间线统计
        timeline_stats = self.vector_db.get_timeline_statistics()
        print(f"向量库最早时间: {timeline_stats.get('earliest_time')}")
        print(f"向量库最晚时间: {timeline_stats.get('latest_time')}")
        print(f"每日统计: {timeline_stats.get('daily_statistics')}")
    
    def close(self):
        """关闭资源"""
        self.vector_db.close()

if __name__ == "__main__":
    # 创建处理器实例
    processor = InteractionPageProcessor()
    
    try:
        # 处理所有交互页面
        processor.process_all_pages()
        
        # 获取统计信息
        processor.get_statistics()
        
        print("\n=== 处理完成 ===")
    finally:
        # 关闭资源
        processor.close()