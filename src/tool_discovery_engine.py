#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具发现引擎 - 为数据收集师智能体提供全网工具发现能力
开发提示词来源：用户要求解决数据收集师智能体的外部工具发现和集成问题
"""

# @self-expose: {"id": "tool_discovery_engine", "name": "Tool Discovery Engine", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Tool Discovery Engine功能"]}}

import os
import sys
import json
import requests
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ToolDiscoveryEngine:
    """工具发现引擎 - 智能发现和评估外部数据收集工具"""
    
    def __init__(self, cache_dir: str = "data/tool_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
        # 工具分类和关键词
        self.tool_categories = {
            "web_crawler": ["爬虫", "crawler", "scraper", "spider"],
            "data_extractor": ["数据提取", "extractor", "parser", "scraping"],
            "file_processor": ["文件处理", "processor", "converter", "parser"],
            "api_client": ["API", "client", "wrapper", "SDK"],
            "database_tool": ["数据库", "database", "db", "SQL"],
            "nlp_processor": ["NLP", "自然语言处理", "text", "analysis"]
        }
    
    def search_github_tools(self, keywords: List[str], category: str = None) -> List[Dict]:
        """在GitHub搜索相关数据收集工具"""
        
        # 构建搜索查询
        query_parts = []
        if category and category in self.tool_categories:
            query_parts.extend(self.tool_categories[category])
        query_parts.extend(keywords)
        
        query = " OR ".join(query_parts)
        query += " language:python"  # 限制为Python项目
        
        # GitHub API搜索
        url = "https://api.github.com/search/repositories"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 20
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                results = response.json()["items"]
                
                # 分析工具质量
                analyzed_results = []
                for repo in results:
                    tool_info = self._analyze_github_repo(repo)
                    if tool_info["quality_score"] >= 0.6:  # 质量阈值
                        analyzed_results.append(tool_info)
                
                # 缓存结果
                self._cache_results(analyzed_results, f"github_{category or 'general'}")
                
                return analyzed_results
            else:
                logger.error(f"GitHub API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"GitHub搜索失败: {e}")
            return []
    
    def _analyze_github_repo(self, repo: Dict) -> Dict[str, Any]:
        """分析GitHub仓库的工具质量"""
        
        # 基础信息
        repo_info = {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "updated_at": repo["updated_at"],
            "language": repo["language"]
        }
        
        # 质量评分（0-1）
        quality_score = 0
        
        # 流行度评分（40%）
        popularity_score = min(repo["stargazers_count"] / 1000, 1) * 0.4
        
        # 活跃度评分（30%）
        from datetime import datetime
        last_update = datetime.fromisoformat(repo["updated_at"].replace('Z', '+00:00'))
        days_since_update = (datetime.now() - last_update).days
        activity_score = max(0, 1 - days_since_update / 365) * 0.3
        
        # 文档完整性评分（30%）
        doc_score = self._assess_documentation(repo["html_url"]) * 0.3
        
        quality_score = popularity_score + activity_score + doc_score
        
        repo_info["quality_score"] = round(quality_score, 2)
        repo_info["quality_level"] = self._get_quality_level(quality_score)
        
        return repo_info
    
    def _assess_documentation(self, repo_url: str) -> float:
        """评估文档完整性"""
        # 简化的文档评估（实际实现需要更复杂的逻辑）
        # 检查README、文档链接、示例代码等
        return 0.7  # 默认值
    
    def _get_quality_level(self, score: float) -> str:
        """根据评分获取质量等级"""
        if score >= 0.8:
            return "优秀"
        elif score >= 0.6:
            return "良好"
        elif score >= 0.4:
            return "一般"
        else:
            return "较差"
    
    def generate_tool_wrapper(self, tool_info: Dict) -> Optional[str]:
        """为外部工具生成Python包装器"""
        
        tool_name = tool_info["name"]
        repo_url = tool_info["url"]
        
        # 分析工具安装方式
        installation_method = self._analyze_installation_method(repo_url)
        
        # 生成包装器代码模板
        wrapper_code = f'''
# {tool_name} 包装器
# 来源: {repo_url}

import subprocess
import sys
from typing import Dict, Any

class {tool_name.title().replace('-', '').replace('_', '')}Wrapper:
    """{tool_info.get('description', '外部数据收集工具')}"""
    
    def __init__(self):
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查并安装依赖"""
        try:
            # 尝试导入工具
            # 如果失败，自动安装
            pass
        except ImportError:
            self._install_tool()
    
    def _install_tool(self):
        """安装工具"""
        # 根据installation_method选择安装方式
        if "{installation_method}" == "pip":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "{tool_name}"])
        elif "{installation_method}" == "git":
            subprocess.check_call(["git", "clone", "{repo_url}"])
            # 添加路径到sys.path
            sys.path.insert(0, "{tool_name}")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        # 需要根据具体工具API实现
        return {{"success": True, "data": "工具执行结果"}}
'''
        
        return wrapper_code
    
    def _analyze_installation_method(self, repo_url: str) -> str:
        """分析工具的安装方式"""
        # 简化的分析逻辑
        # 实际实现需要检查requirements.txt、setup.py等文件
        return "pip"  # 默认使用pip安装
    
    def _cache_results(self, results: List[Dict], cache_key: str):
        """缓存搜索结果"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def get_cached_tools(self, category: str = None) -> List[Dict]:
        """获取缓存的工具信息"""
        cache_file = self.cache_dir / f"github_{category or 'general'}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


def create_tool_discovery_engine() -> ToolDiscoveryEngine:
    """创建工具发现引擎实例"""
    return ToolDiscoveryEngine()