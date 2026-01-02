# @self-expose: {"id": "chat_tools", "name": "Chat Tools", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Chat Tools功能"]}}
"""
RAG聊天机器人核心工具定义

开发提示词来源：用户对话中关于记忆迭代和工具化思维的讨论
核心理念：RAG = 构建有长期记忆的AI朋友
"""

import json
import logging
import os
import subprocess
import shlex
import re  # 添加re模块,用于equality_assessment工具
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.vector_database import VectorDatabase
from src.llm_client import LLMClient
from tools.memory_slicer_tool import MemorySlicerTool

# 导入引擎工具
from src.mesh_thought_engine import MeshThoughtEngine as NetworkedThinkingEngine  # 网状思维引擎（使用src版本）
from src.cognitive_engines.reasoning_engine import ReasoningEngine  # 理性逻辑认知引擎
from src.cognitive_engines.cognitive_barrier_break_engine import CognitiveBarrierBreakEngine  # 认知破障引擎

# 暂时移除文本处理工具依赖，等待text_cleaner模块实现
# from text_cleaner import TextCleaner, MemoryTextCleaner

logger = logging.getLogger(__name__)

class MemoryRetrievalTool:
    """记忆检索工具 - 核心工具1"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """检索相关记忆"""
        try:
            results = self.vector_db.search_memories(query=query, limit=limit)
            return results
        except Exception as e:
            logger.error(f"记忆检索失败: {e}")
            return []
    
    def get_context_from_memories(self, query: str, max_tokens: int = 32000) -> str:
        """从记忆中构建上下文（充分利用128K上下文能力）"""
        memories = self.search_memories(query, limit=50)  # 增加检索数量
        
        if not memories:
            return ""
            
        context_parts = []
        current_tokens = 0
        
        for memory in memories:
            memory_text = f"[{memory['source_type']}] {memory['content']}"
            token_estimate = len(memory_text) // 4  # 粗略估算
            
            if current_tokens + token_estimate > max_tokens:
                break
                
            context_parts.append(memory_text)
            current_tokens += token_estimate
            
        return "\n".join(context_parts)


class FileReadingTool:
    """文件读取工具 - 核心工具2
    
    开发提示词来源：用户关于完善文件读取工具的讨论
    核心理念：提供全面、智能、安全的文件读取能力
    """
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = Path(base_path)
        
        # 支持的文件格式
        self.supported_formats = {
            'text': ['.txt', '.md', '.rst', '.log'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', '.json', '.xml', '.yaml', '.yml'],
            'data': ['.csv', '.tsv', '.jsonl'],
            'config': ['.ini', '.cfg', '.conf', '.properties'],
            'document': ['.docx']  # 新增：Office文档支持
        }
        
        # 文件大小限制（MB）
        self.max_file_size = 10  # 10MB
        
        # 编码检测
        self.encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        logger.info(f"文件读取工具已初始化，基础路径: {self.base_path}")
        
    def read_text_file(self, file_path: str, encoding: str = None) -> Optional[str]:
        """读取文本文件（支持自动编码检测和DOCX提取）"""
        import time
        start_time = time.time()  # 性能监控
        
        try:
            # 处理绝对路径
            if os.path.isabs(file_path):
                full_path = Path(file_path)
            else:
                full_path = self.base_path / file_path
            
            # 安全检查（绝对路径跳过检查）
            if not os.path.isabs(file_path) and not self._is_file_safe(full_path):
                logger.warning(f"文件安全检查失败: {file_path}")
                return None
            
            if not full_path.exists() or not full_path.is_file():
                logger.error(f"文件不存在: {file_path}")
                return None
                
            # 获取文件信息
            file_size = full_path.stat().st_size
            file_ext = full_path.suffix.lower()
            logger.info(f"读取文件: {file_path}, 大小: {file_size/1024:.2f}KB, 类型: {file_ext}")
            
            # 二进制文件检测（扩展列表）
            BINARY_EXTENSIONS = {
                # 可执行文件
                '.exe', '.dll', '.so', '.dylib', '.bin',
                # Office文档（不可提取文本的）
                '.pdf', '.doc', '.xls', '.xlsx', '.ppt', '.pptx',
                # 图像文件
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
                # 音频文件
                '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
                # 视频文件
                '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                # 压缩文件
                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
                # 数据库文件
                '.db', '.sqlite', '.mdb',
                # 其他二进制
                '.obj', '.o', '.a', '.lib'
            }
            
            # 二进制文件返回友好提示
            if file_ext in BINARY_EXTENSIONS:
                elapsed = time.time() - start_time
                logger.warning(f"检测到二进制文件: {file_ext}, 耗时: {elapsed:.3f}秒")
                return f"[文件类型 {file_ext} 为二进制文件，大小 {file_size/1024:.2f}KB，无法直接显示文本内容。建议使用专门的工具打开此类文件。]"
                
            # 检查文件大小
            file_size_mb = file_size / (1024 * 1024)
            if file_size_mb > self.max_file_size:
                logger.warning(f"文件过大 ({file_size_mb:.2f}MB > {self.max_file_size}MB): {file_path}")
                return None
            
            # DOCX文件特殊处理
            if file_ext == '.docx':
                content = self._read_docx_file(full_path)
                if content:
                    elapsed = time.time() - start_time
                    logger.info(f"DOCX文件读取成功, 耗时: {elapsed:.3f}秒, 内容: {len(content)}字符")
                    # 大文件截断（100KB）
                    if len(content) > 100000:
                        logger.warning(f"DOCX文件过大({len(content)}字符)，截取前50000字符")
                        return f"[文件过大，共{len(content)}字符，已截取前50000字符。建议将大文件拆分为多个小文件分别上传。]\n\n{content[:50000]}"
                    return content
                return None
            
            # 文本文件：自动检测编码或使用指定编码
            if encoding:
                content = self._read_with_encoding(full_path, encoding)
            else:
                content = self._detect_and_read(full_path)
            
            if content:
                elapsed = time.time() - start_time
                logger.info(f"文本文件读取成功, 耗时: {elapsed:.3f}秒, 内容: {len(content)}字符")
                # 大文件截断（100KB）
                if len(content) > 100000:
                    logger.warning(f"文本文件过大({len(content)}字符)，截取前50000字符")
                    return f"[文件过大，共{len(content)}字符，已截取前50000字符。建议将大文件拆分为多个小文件分别上传。]\n\n{content[:50000]}"
                return content
                
            return None
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"文件读取失败: {e}, 耗时: {elapsed:.3f}秒")
            return None
    
    def read_file_chunk(self, file_path: str, start_line: int = 1, num_lines: int = 100) -> Optional[str]:
        """读取文件片段（支持大文件）"""
        try:
            full_path = self.base_path / file_path
            
            if not self._is_file_safe(full_path):
                return None
                
            if full_path.exists() and full_path.is_file():
                lines = []
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        if i >= start_line and i < start_line + num_lines:
                            lines.append(line)
                        elif i >= start_line + num_lines:
                            break
                
                return ''.join(lines) if lines else None
            return None
        except Exception as e:
            logger.error(f"文件片段读取失败: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """获取文件信息"""
        try:
            full_path = self.base_path / file_path
            
            if full_path.exists() and full_path.is_file():
                stat = full_path.stat()
                return {
                    'path': str(full_path),
                    'size': stat.st_size,
                    'size_human': self._format_size(stat.st_size),
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'extension': full_path.suffix.lower(),
                    'type': self._get_file_type(full_path.suffix)
                }
            return None
        except Exception as e:
            logger.error(f"文件信息获取失败: {e}")
            return None
    
    def search_in_files(self, pattern: str, search_text: str, case_sensitive: bool = False) -> List[Dict]:
        """在文件中搜索文本"""
        try:
            results = []
            files = list(self.base_path.rglob(pattern))
            
            for file_path in files:
                if file_path.is_file() and self._is_file_safe(file_path):
                    content = self.read_text_file(str(file_path.relative_to(self.base_path)))
                    if content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if (case_sensitive and search_text in line) or \
                               (not case_sensitive and search_text.lower() in line.lower()):
                                results.append({
                                    'file': str(file_path.relative_to(self.base_path)),
                                    'line': i,
                                    'content': line.strip(),
                                    'match': search_text
                                })
            
            return results
        except Exception as e:
            logger.error(f"文件搜索失败: {e}")
            return []
    
    def list_available_files(self, pattern: str = "*", file_type: str = None) -> List[Dict]:
        """列出可用文件（支持按类型过滤）"""
        try:
            files = list(self.base_path.rglob(pattern))
            file_list = []
            
            for file_path in files:
                if file_path.is_file() and self._is_file_safe(file_path):
                    if file_type and file_type in self.supported_formats:
                        if file_path.suffix.lower() not in self.supported_formats[file_type]:
                            continue
                    
                    stat = file_path.stat()
                    file_list.append({
                        'path': str(file_path.relative_to(self.base_path)),
                        'size': stat.st_size,
                        'size_human': self._format_size(stat.st_size),
                        'modified': stat.st_mtime,
                        'type': self._get_file_type(file_path.suffix)
                    })
            
            # 按修改时间排序
            file_list.sort(key=lambda x: x['modified'], reverse=True)
            return file_list
        except Exception as e:
            logger.error(f"文件列表获取失败: {e}")
            return []
    
    def _read_with_encoding(self, file_path: Path, encoding: str) -> str:
        """使用指定编码读取文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            logger.warning(f"编码 {encoding} 读取失败，尝试其他编码")
            return self._detect_and_read(file_path)
    
    def _detect_and_read(self, file_path: Path) -> str:
        """自动检测编码并读取文件"""
        # 优先尝试导入chardet进行编码检测，若缺失则安全回退
        try:
            import chardet  # type: ignore
        except Exception:
            chardet = None
        
        # 读取二进制内容进行编码检测
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        detected_encoding = 'utf-8'
        confidence = 0.0
        if chardet is not None:
            detection = chardet.detect(raw_data)
            detected_encoding = detection.get('encoding', 'utf-8')
            confidence = detection.get('confidence', 0)
            logger.info(f"检测到文件编码: {detected_encoding} (置信度: {confidence:.2f})")
        
        # 尝试检测到的编码
        if confidence and confidence > 0.5:
            try:
                return raw_data.decode(detected_encoding)
            except UnicodeDecodeError:
                logger.warning(f"检测编码 {detected_encoding} 读取失败")
        
        # 尝试其他常见编码
        for enc in self.encodings:
            try:
                return raw_data.decode(enc)
            except UnicodeDecodeError:
                continue
        
        # 最后尝试忽略错误
        return raw_data.decode('utf-8', errors='ignore')
    
    def _is_file_safe(self, file_path: Path) -> bool:
        """文件安全检查"""
        # 检查是否在基础路径内
        try:
            file_path.relative_to(self.base_path)
        except ValueError:
            return False
        
        # 检查文件扩展名
        unsafe_extensions = ['.exe', '.dll', '.bat', '.cmd', '.ps1', '.sh']
        if file_path.suffix.lower() in unsafe_extensions:
            return False
        
        return True
    
    def _get_file_type(self, extension: str) -> str:
        """获取文件类型"""
        for file_type, extensions in self.supported_formats.items():
            if extension.lower() in extensions:
                return file_type
        return 'other'
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def _read_docx_file(self, file_path: Path) -> Optional[str]:
        """读取DOCX文件并提取文本内容
        
        Args:
            file_path: DOCX文件路径
            
        Returns:
            提取的文本内容或None
        """
        try:
            from docx import Document
            
            logger.info(f"开始读取DOCX文件: {file_path}")
            doc = Document(file_path)
            
            # 提取所有段落文本（过滤空段落）
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            content = '\n'.join(paragraphs)
            
            if content:
                logger.info(f"DOCX文本提取成功，内容长度: {len(content)} 字符")
                return content
            else:
                logger.warning(f"DOCX文件无文本内容: {file_path}")
                return None
                
        except ImportError:
            logger.error("未安装python-docx库，无法读取DOCX文件。请运行: pip install python-docx")
            return None
        except Exception as e:
            logger.error(f"DOCX文件读取失败: {e}")
            return None


class WebSearchTool:
    """网络搜索工具 - 核心工具3
    
    开发提示词来源：用户关于实现真正网络搜索工具的讨论
    核心理念：提供真实、可靠、可配置的网络搜索能力
    
    默认启用免费的 DuckDuckGo 搜索引擎，无需API密钥即可使用。
    支持收费引擎（Google/Bing），需配置API密钥后才能使用。
    
    使用示例：
    - 免费模式：WebSearchTool()  # 自动使用 DuckDuckGo
    - 收费模式：WebSearchTool(api_key="sk-xxx", search_engine="google")
    """
    
    def __init__(self, api_key: str = None, search_engine: str = "duckduckgo"):
        self.api_key = api_key
        self.search_engine = search_engine
        
        # 支持的搜索引擎配置
        self.supported_engines = {
            'google': {
                'name': 'Google Search',
                'api_url': 'https://www.googleapis.com/customsearch/v1',
                'docs': 'https://developers.google.com/custom-search',
                'requires_api_key': True,
                'free': False
            },
            'bing': {
                'name': 'Bing Search',
                'api_url': 'https://api.bing.microsoft.com/v7.0/search',
                'docs': 'https://www.microsoft.com/en-us/bing/apis/bing-web-search-api',
                'requires_api_key': True,
                'free': False
            },
            'duckduckgo': {
                'name': 'DuckDuckGo',
                'api_url': 'https://api.duckduckgo.com/',
                'docs': 'https://duckduckgo.com/api',
                'requires_api_key': False,
                'free': True
            }
        }
        
        # 搜索配置
        self.default_config = {
            'num_results': 5,
            'timeout': 30,
            'safe_search': True,
            'language': 'zh-CN'
        }
        
        # 判断是否需要API密钥
        engine_config = self.supported_engines.get(self.search_engine, {})
        requires_key = engine_config.get('requires_api_key', True)
        
        if requires_key and not api_key:
            self.enabled = False
            logger.warning(f"{engine_config.get('name', self.search_engine)} 是收费引擎，需要配置API密钥。当前已自动切换到免费的 DuckDuckGo 引擎。")
            self.search_engine = 'duckduckgo'
            self.enabled = True
        elif requires_key and api_key:
            self.enabled = True
            logger.info(f"网络搜索工具已启用，使用收费引擎: {self.search_engine}")
        else:
            # DuckDuckGo 免费引擎
            self.enabled = True
            logger.info(f"网络搜索工具已启用，使用免费引擎: DuckDuckGo")
        
    def search_web(self, query: str, num_results: int = None, timeout: int = None) -> List[Dict]:
        """执行网络搜索"""
        if not self.enabled:
            return self._get_fallback_results(query)
            
        try:
            # 使用配置参数
            config = self._get_search_config(num_results, timeout)
            
            # 根据搜索引擎调用相应API
            if self.search_engine == 'google':
                return self._search_google(query, config)
            elif self.search_engine == 'bing':
                return self._search_bing(query, config)
            elif self.search_engine == 'duckduckgo':
                return self._search_duckduckgo(query, config)
            else:
                logger.error(f"不支持的搜索引擎: {self.search_engine}")
                return self._get_fallback_results(query)
                
        except Exception as e:
            logger.error(f"网络搜索失败: {e}")
            return self._get_fallback_results(query)
    
    def _search_google(self, query: str, config: dict) -> List[Dict]:
        """使用Google Custom Search API"""
        import requests
        
        params = {
            'key': self.api_key,
            'cx': 'YOUR_SEARCH_ENGINE_ID',  # 需要配置自定义搜索引擎ID
            'q': query,
            'num': config['num_results'],
            'lr': f"lang_{config['language']}",
            'safe': 'active' if config['safe_search'] else 'off'
        }
        
        response = requests.get(
            self.supported_engines['google']['api_url'],
            params=params,
            timeout=config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_google_results(data)
        else:
            raise Exception(f"Google API错误: {response.status_code}")
    
    def _search_bing(self, query: str, config: dict) -> List[Dict]:
        """使用Bing Search API"""
        import requests
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        params = {
            'q': query,
            'count': config['num_results'],
            'mkt': config['language'],
            'safeSearch': 'Strict' if config['safe_search'] else 'Off'
        }
        
        response = requests.get(
            self.supported_engines['bing']['api_url'],
            headers=headers,
            params=params,
            timeout=config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_bing_results(data)
        else:
            raise Exception(f"Bing API错误: {response.status_code}")
    
    def _search_duckduckgo(self, query: str, config: dict) -> List[Dict]:
        """使用DuckDuckGo API"""
        import requests
        
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        response = requests.get(
            self.supported_engines['duckduckgo']['api_url'],
            params=params,
            timeout=config['timeout']
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_duckduckgo_results(data)
        else:
            raise Exception(f"DuckDuckGo API错误: {response.status_code}")
    
    def _parse_google_results(self, data: dict) -> List[Dict]:
        """解析Google搜索结果"""
        results = []
        
        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google',
                    'timestamp': 'now'
                })
        
        return results
    
    def _parse_bing_results(self, data: dict) -> List[Dict]:
        """解析Bing搜索结果"""
        results = []
        
        if 'webPages' in data and 'value' in data['webPages']:
            for item in data['webPages']['value']:
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Bing',
                    'timestamp': 'now'
                })
        
        return results
    
    def _parse_duckduckgo_results(self, data: dict) -> List[Dict]:
        """解析DuckDuckGo搜索结果"""
        results = []
        
        # DuckDuckGo返回相关主题和摘要
        if 'Abstract' in data and data['Abstract']:
            results.append({
                'title': data.get('Heading', '摘要'),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('Abstract', ''),
                'source': 'DuckDuckGo',
                'timestamp': 'now'
            })
        
        # 相关主题
        if 'RelatedTopics' in data:
            for topic in data['RelatedTopics']:
                if 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1] if 'FirstURL' in topic else '相关主题',
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo',
                        'timestamp': 'now'
                    })
        
        return results
    
    def _get_fallback_results(self, query: str) -> List[Dict]:
        """获取备用结果（当API不可用时）"""
        logger.info(f"使用备用搜索模式查询: {query}")
        
        # 返回一些示例结果
        return [
            {
                'title': f"关于'{query}'的搜索结果（示例）",
                'url': f"https://example.com/search?q={query}",
                'snippet': f"这是关于'{query}'的示例搜索结果。请配置API密钥以获得真实搜索结果。",
                'source': '示例',
                'timestamp': 'now'
            }
        ]
    
    def _get_search_config(self, num_results: int = None, timeout: int = None) -> dict:
        """获取搜索配置"""
        config = self.default_config.copy()
        
        if num_results:
            config['num_results'] = min(num_results, 10)  # 限制最大结果数
        if timeout:
            config['timeout'] = timeout
            
        return config
    
    def enable_search(self, api_key: str = None, search_engine: str = None):
        """启用网络搜索"""
        if api_key:
            self.api_key = api_key
            self.enabled = True
        
        if search_engine and search_engine in self.supported_engines:
            self.search_engine = search_engine
        
        if self.enabled:
            logger.info(f"网络搜索功能已启用，使用引擎: {self.search_engine}")
        
    def disable_search(self):
        """禁用网络搜索"""
        self.enabled = False
        logger.info("网络搜索功能已禁用")
    
    def get_supported_engines(self) -> List[str]:
        """获取支持的搜索引擎列表"""
        return list(self.supported_engines.keys())
    
    def get_engine_info(self, engine: str) -> Optional[Dict]:
        """获取搜索引擎信息"""
        if engine in self.supported_engines:
            return self.supported_engines[engine]
        return None


class MemoryIterationTool:
    """记忆迭代工具 - 核心工具4（灵魂工具）
    
    开发提示词来源：用户关于记忆迭代工具功能的讨论
    核心理念：实现记忆的总结、反思、重构、评估完整迭代循环
    """
    
    def __init__(self, vector_db: VectorDatabase, llm_client: LLMClient):
        self.vector_db = vector_db
        self.llm_client = llm_client
        
        # 记忆迭代的四个核心阶段
        self.iteration_stages = {
            'summary': '总结 - 提炼核心观点',
            'reflection': '反思 - 深度思考关联',
            'restructuring': '重构 - 优化知识结构',
            'evaluation': '评估 - 质量价值判断'
        }
        
    def summarize_related_memories(self, topic: str, max_memories: int = 20) -> Optional[Dict]:
        """总结相关记忆 - 第一阶段：总结提炼"""
        try:
            # 检索相关记忆
            memories = self.vector_db.search_memories(query=topic, limit=max_memories)
            
            if not memories:
                return None
                
            # 构建总结提示词
            memory_texts = [f"{m['content']}" for m in memories]
            prompt = f"""请对以下相关记忆内容进行总结提炼：
            
{chr(10).join(memory_texts)}
            
请生成一个简洁的总结，包含：
1. 核心观点
2. 重要细节
3. 可能的关联
4. 总结性陈述"""
            
            summary = self.llm_client.chat(prompt)
            
            return {
                'topic': topic,
                'summary': summary,
                'source_memories': len(memories),
                'timestamp': 'now',
                'stage': 'summary'
            }
            
        except Exception as e:
            logger.error(f"记忆总结失败: {e}")
            return None
    
    def reflect_on_memories(self, topic: str, max_memories: int = 15) -> Optional[Dict]:
        """反思记忆 - 第二阶段：深度思考关联"""
        try:
            # 检索相关记忆
            memories = self.vector_db.search_memories(query=topic, limit=max_memories)
            
            if not memories:
                return None
                
            # 构建反思提示词
            memory_texts = [f"{m['content']}" for m in memories]
            prompt = f"""请对以下记忆内容进行深度反思：
            
{chr(10).join(memory_texts)}
            
请进行深度反思，包含：
1. 这些记忆之间的深层关联
2. 可能存在的认知盲点
3. 新的洞察和发现
4. 对未来思考的启示"""
            
            reflection = self.llm_client.chat(prompt)
            
            return {
                'topic': topic,
                'reflection': reflection,
                'source_memories': len(memories),
                'timestamp': 'now',
                'stage': 'reflection'
            }
            
        except Exception as e:
            logger.error(f"记忆反思失败: {e}")
            return None
    
    def restructure_knowledge_graph(self, topic: str, max_memories: int = 25) -> Optional[Dict]:
        """重构知识图谱 - 第三阶段：优化知识结构"""
        try:
            # 检索相关记忆
            memories = self.vector_db.search_memories(query=topic, limit=max_memories)
            
            if not memories:
                return None
                
            # 构建重构提示词
            memory_texts = [f"{m['content']}" for m in memories]
            prompt = f"""请对以下知识内容进行结构重构：
            
{chr(10).join(memory_texts)}
            
请重新组织知识结构，包含：
1. 新的知识分类体系
2. 关键概念之间的关系图
3. 知识层次结构优化
4. 便于检索和理解的架构"""
            
            restructured_knowledge = self.llm_client.chat(prompt)
            
            return {
                'topic': topic,
                'restructured_knowledge': restructured_knowledge,
                'source_memories': len(memories),
                'timestamp': 'now',
                'stage': 'restructuring'
            }
            
        except Exception as e:
            logger.error(f"知识重构失败: {e}")
            return None
    
    def evaluate_memory_quality(self, topic: str, max_memories: int = 10) -> Optional[Dict]:
        """评估记忆质量 - 第四阶段：质量价值判断"""
        try:
            # 检索相关记忆
            memories = self.vector_db.search_memories(query=topic, limit=max_memories)
            
            if not memories:
                return None
                
            # 构建评估提示词
            memory_texts = [f"{m['content']}" for m in memories]
            prompt = f"""请评估以下记忆内容的质量和价值：
            
{chr(10).join(memory_texts)}
            
请进行质量评估，包含：
1. 内容准确性和可靠性
2. 知识深度和广度
3. 实用价值和适用性
4. 改进建议和优化方向"""
            
            evaluation = self.llm_client.chat(prompt)
            
            # 计算质量评分
            quality_score = self._calculate_quality_score(memories)
            
            return {
                'topic': topic,
                'evaluation': evaluation,
                'quality_score': quality_score,
                'source_memories': len(memories),
                'timestamp': 'now',
                'stage': 'evaluation'
            }
            
        except Exception as e:
            logger.error(f"记忆评估失败: {e}")
            return None
    
    def complete_memory_iteration(self, topic: str) -> Dict:
        """完整记忆迭代循环 - 执行所有四个阶段"""
        iteration_results = {}
        
        # 执行四个阶段的迭代
        iteration_results['summary'] = self.summarize_related_memories(topic)
        iteration_results['reflection'] = self.reflect_on_memories(topic)
        iteration_results['restructuring'] = self.restructure_knowledge_graph(topic)
        iteration_results['evaluation'] = self.evaluate_memory_quality(topic)
        
        # 生成迭代总结
        iteration_summary = self._generate_iteration_summary(iteration_results)
        
        return {
            'topic': topic,
            'iteration_results': iteration_results,
            'iteration_summary': iteration_summary,
            'timestamp': 'now',
            'completed_stages': [stage for stage, result in iteration_results.items() if result]
        }
    
    def detect_contradictions(self, memory_group: List[Dict]) -> List[Dict]:
        """检测记忆中的矛盾"""
        contradictions = []
        
        # 改进的矛盾检测逻辑
        for i, mem1 in enumerate(memory_group):
            for j, mem2 in enumerate(memory_group[i+1:], i+1):
                contradiction_level = self._analyze_contradiction_level(mem1['content'], mem2['content'])
                if contradiction_level > 0.3:  # 30%矛盾阈值
                    contradictions.append({
                        'memory1': mem1['topic'],
                        'memory2': mem2['topic'],
                        'contradiction_level': contradiction_level,
                        'description': self._generate_contradiction_description(contradiction_level)
                    })
        
        return contradictions
    
    def _analyze_contradiction_level(self, text1: str, text2: str) -> float:
        """分析矛盾程度（0-1）"""
        # 实现更复杂的矛盾检测逻辑
        # 基于关键词对比、语义分析等
        return 0.0  # 暂时返回0
    
    def _generate_contradiction_description(self, level: float) -> str:
        """生成矛盾描述"""
        if level > 0.7:
            return "严重矛盾 - 需要立即处理"
        elif level > 0.4:
            return "中等矛盾 - 建议进一步分析"
        elif level > 0.1:
            return "轻微矛盾 - 可能存在误解"
        else:
            return "无显著矛盾"
    
    def _calculate_quality_score(self, memories: List[Dict]) -> float:
        """计算记忆质量评分（0-1）"""
        if not memories:
            return 0.0
        
        # 基于内容长度、结构、关键词等计算质量
        total_score = 0
        for memory in memories:
            content = memory.get('content', '')
            # 简单的质量指标
            length_score = min(len(content) / 1000, 1.0)  # 长度指标
            structure_score = 1.0 if len(content.split('.')) > 3 else 0.5  # 结构指标
            total_score += (length_score + structure_score) / 2
        
        return total_score / len(memories)
    
    def _generate_iteration_summary(self, iteration_results: Dict) -> str:
        """生成迭代总结"""
        summary_parts = []
        
        for stage, result in iteration_results.items():
            if result:
                summary_parts.append(f"{stage}阶段完成")
        
        return f"记忆迭代完成：{', '.join(summary_parts)}"
    
    def optimize_memory_structure(self):
        """优化记忆结构"""
        # 定期执行记忆优化
        logger.info("开始记忆结构优化...")
        
        # 这里可以实现记忆重组、重要性调整等逻辑
        # 例如：基于使用频率调整记忆权重
        pass


class CommandLineTool:
    """命令行工具 - 核心工具5（行动工具）"""
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = Path(base_path)
        self.safe_commands = [
            'python', 'pip', 'git', 'curl', 'wget', 'echo', 'cat', 'ls', 'dir',
            'find', 'grep', 'sort', 'uniq', 'head', 'tail', 'wc', 'date', 'time',
            'whoami', 'hostname', 'pwd', 'cd', 'mkdir', 'rmdir', 'type'
        ]
        self.dangerous_commands = [
            'rm', 'del', 'format', 'shutdown', 'reboot', 'sudo', 'chmod', 'chown'
        ]
        
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """安全执行命令行指令"""
        try:
            # 安全检查
            if not self._is_command_safe(command):
                return {
                    'success': False,
                    'error': f'命令安全检查失败: {command}',
                    'output': ''
                }
            
            # 执行命令
            import subprocess
            import shlex
            import platform
            
            # 切换到工作目录
            original_cwd = Path.cwd()
            os.chdir(self.base_path)
            
            original_command = command
            
            # 处理Windows系统上的命令转换
            if platform.system() == 'Windows':
                # 将ls命令转换为dir命令
                if command.lower().startswith('ls'):
                    # 更智能的转换，处理各种ls参数组合
                    command_lower = command.lower()
                    
                    # 替换ls为dir
                    command = command.replace('ls', 'dir', 1)
                    
                    # 处理常用参数
                    if '-la' in command_lower or '--all' in command_lower or '-a' in command_lower:
                        # 添加/a参数显示所有文件（包括隐藏文件）
                        if '/a' not in command:
                            command += ' /a'
                    if '-l' in command_lower or '--long' in command_lower:
                        # dir命令默认显示详细信息，无需特殊处理
                        pass
                    
                    # 移除所有不兼容的Unix参数
                    incompatible_params = ['-la', '-l', '-a', '--all', '--long']
                    for param in incompatible_params:
                        command = command.replace(param, '')
            
            # 执行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )
            
            # 恢复原目录
            os.chdir(original_cwd)
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command,
                'original_command': original_command
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'命令执行超时 (>{timeout}秒)',
                'output': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'命令执行异常: {e}',
                'output': ''
            }
    
    def _is_command_safe(self, command: str) -> bool:
        """检查命令是否安全"""
        # 转换为小写
        command_lower = command.lower()
        
        # 检查危险命令
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # 检查是否以安全命令开头（更宽松的匹配，允许命令后面跟着空格或直接结束）
        has_safe_command = False
        for safe in self.safe_commands:
            if command_lower == safe or command_lower.startswith(safe + ' '):
                has_safe_command = True
                break
        
        return has_safe_command
    
    def run_python_script(self, script_path: str, args: str = "") -> Dict[str, Any]:
        """运行Python脚本"""
        full_path = self.base_path / script_path
        if not full_path.exists():
            return {
                'success': False,
                'error': f'脚本文件不存在: {script_path}',
                'output': ''
            }
        
        command = f"python {script_path} {args}"
        return self.execute_command(command)
    
    def list_available_scripts(self) -> List[str]:
        """列出可用脚本"""
        scripts = []
        for pattern in ['*.py', '*.sh', '*.bat']:
            scripts.extend([str(p.relative_to(self.base_path)) 
                          for p in self.base_path.rglob(pattern)])
        return scripts


class EqualityAssessmentTool:
    """平等律评估工具 - 基于平等律的写入前评估"""
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = Path(base_path)
        
        # 平等律核心定义：平等 = 被需要 + 不冗余
        self.equality_principles = {
            'needed': "新内容是否被系统需要",
            'non_redundant': "新内容是否不冗余",
            'value_added': "新内容是否增加系统价值"
        }
    
    def assess_write_operation(self, file_path: str, content: str) -> dict:
        """评估写入操作是否符合平等律"""
        assessment = {
            'should_write': True,
            'reasons': [],
            'suggestions': [],
            'equality_score': 0.0
        }
        
        # 检查是否被需要
        need_assessment = self._assess_need(file_path, content)
        if not need_assessment['needed']:
            assessment['should_write'] = False
            assessment['reasons'].append(need_assessment['reason'])
        else:
            assessment['equality_score'] += 0.4
            assessment['suggestions'].append(need_assessment['suggestion'])
        
        # 检查是否不冗余
        redundancy_assessment = self._assess_redundancy(file_path, content)
        if redundancy_assessment['redundant']:
            assessment['should_write'] = False
            assessment['reasons'].append(redundancy_assessment['reason'])
        else:
            assessment['equality_score'] += 0.4
            assessment['suggestions'].append(redundancy_assessment['suggestion'])
        
        # 检查是否增加价值
        value_assessment = self._assess_value_added(file_path, content)
        if value_assessment['value_added']:
            assessment['equality_score'] += 0.2
            assessment['suggestions'].append(value_assessment['suggestion'])
        else:
            assessment['reasons'].append(value_assessment['reason'])
        
        return assessment
    
    def _assess_need(self, file_path: str, content: str) -> dict:
        """评估内容是否被需要"""
        full_path = self.base_path / file_path
        
        # 检查文件是否已存在
        if full_path.exists():
            existing_content = self._read_file_safely(full_path)
            if existing_content and content.strip() == existing_content.strip():
                return {
                    'needed': False,
                    'reason': f"文件 '{file_path}' 已存在且内容相同",
                    'suggestion': "无需重复写入相同内容"
                }
        
        # 检查内容是否为空或无意义
        if not content.strip() or len(content.strip()) < 10:
            return {
                'needed': False,
                'reason': "内容为空或过于简短，缺乏实际价值",
                'suggestion': "请提供有意义的内容"
            }
        
        return {
            'needed': True,
            'reason': "内容具有实际价值",
            'suggestion': "内容符合被需要原则"
        }
    
    def _assess_redundancy(self, file_path: str, content: str) -> dict:
        """评估内容是否冗余"""
        # 检查系统中是否有类似内容
        similar_files = self._find_similar_content(content)
        
        if similar_files:
            return {
                'redundant': True,
                'reason': f"系统中已存在 {len(similar_files)} 个类似文件",
                'suggestion': f"建议合并到现有文件或更新现有内容"
            }
        
        return {
            'redundant': False,
            'reason': "内容在系统中具有独特性",
            'suggestion': "内容符合不冗余原则"
        }
    
    def _assess_value_added(self, file_path: str, content: str) -> dict:
        """评估内容是否增加系统价值"""
        # 简单的内容质量评估
        value_indicators = [
            len(content) > 100,  # 内容长度
            'def ' in content or 'class ' in content,  # 包含代码
            '#' in content and len(content.split('\n')) > 5,  # 结构化内容
            'http' in content or 'www.' in content,  # 包含链接
            len(content.split('.')) > 3  # 包含完整句子
        ]
        
        value_score = sum(value_indicators) / len(value_indicators)
        
        if value_score > 0.3:
            return {
                'value_added': True,
                'reason': f"内容质量评分: {value_score:.2f}",
                'suggestion': "内容具有较好的系统价值"
            }
        else:
            return {
                'value_added': False,
                'reason': "内容质量较低，可能缺乏实际价值",
                'suggestion': "建议完善内容后再写入"
            }
    
    def _read_file_safely(self, file_path: Path) -> str:
        """安全读取文件内容"""
        try:
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except:
            pass
        return ""
    
    def _find_similar_content(self, content: str, max_files: int = 10) -> list:
        """查找系统中类似的内容"""
        similar_files = []
        
        # 简化实现：检查相同关键词
        keywords = set(re.findall(r'\b\w{4,}\b', content.lower()))
        
        if not keywords:
            return similar_files
        
        # 遍历项目目录查找相似文件
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if len(similar_files) >= max_files:
                    break
                    
                file_path = Path(root) / file
                try:
                    file_content = self._read_file_safely(file_path)
                    file_keywords = set(re.findall(r'\b\w{4,}\b', file_content.lower()))
                    
                    # 计算关键词重叠度
                    overlap = len(keywords & file_keywords) / len(keywords)
                    if overlap > 0.5:  # 50%重叠度
                        similar_files.append({
                            'file_path': str(file_path.relative_to(self.base_path)),
                            'overlap_score': overlap
                        })
                except:
                    continue
        
        return similar_files


class FileWritingTool:
    """文件写入工具 - 基于安全模因内生约束的创造工具"""
    
    def __init__(self, base_path: str = "E:\\RAG系统"):
        self.base_path = Path(base_path)
        self.assessment_tool = EqualityAssessmentTool(base_path)
        
        # 基于系统存续律的引导建议
        self.system_preservation_guidance = {
            'system_dirs': ['C:\\Windows', 'C:\\Program Files', 'C:\\System32'],
            'suggestion': "建议使用项目目录，避免影响系统稳定性"
        }
        
        # 基于平等律的资源使用建议
        self.resource_equality_guidance = {
            'recommended_max_size': 10 * 1024 * 1024,  # 10MB建议值
            'suggestion': "大文件建议分块处理，确保系统资源公平分配"
        }
        
        # 基于一念神魔的格式最佳实践
        self.format_best_practices = {
            'recommended_formats': ['.txt', '.md', '.py', '.json', '.csv', '.log'],
            'suggestion': "推荐使用标准格式，便于系统集成和知识共享"
        }
    
    def write_to_file(self, file_path: str, content: str, overwrite: bool = False, enable_assessment: bool = False) -> dict:
        """写入文件 - 基于安全模因内生约束（可选平等律评估）"""
        result = {'success': False, 'message': '', 'suggestions': []}
        
        # 可选：平等律评估（默认关闭，避免认知资源冲突）
        if enable_assessment:
            equality_assessment = self.assessment_tool.assess_write_operation(file_path, content)
            if not equality_assessment['should_write']:
                result['message'] = "平等律评估未通过"
                result['suggestions'] = equality_assessment['reasons'] + equality_assessment['suggestions']
                result['equality_score'] = equality_assessment['equality_score']
                return result
        
        # 系统存续律检查
        preservation_check = self._check_system_preservation(file_path)
        if not preservation_check['safe']:
            result['message'] = preservation_check['suggestion']
            result['suggestions'] = preservation_check.get('alternatives', [])
            return result
        
        # 平等律检查
        equality_check = self._check_resource_equality(content)
        if not equality_check['safe']:
            result['message'] = equality_check['suggestion']
            result['suggestions'] = equality_check.get('recommendations', [])
            return result
        
        # 一念神魔检查
        format_check = self._check_format_best_practice(file_path)
        if not format_check['safe']:
            result['message'] = format_check['suggestion']
            result['suggestions'] = format_check.get('best_practices', [])
            return result
        
        # 执行写入
        full_path = self.base_path / file_path
        
        # 确保目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查文件是否存在
        if full_path.exists() and not overwrite:
            result['message'] = f"文件 '{file_path}' 已存在"
            result['suggestions'] = ["使用 overwrite=True 参数覆盖文件"]
            return result
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result['success'] = True
            result['message'] = f"文件 '{file_path}' 写入成功"
            result['suggestions'] = [
                "文件已安全保存到项目目录",
                "建议定期备份重要文件"
            ]
            
            # 可选：添加评估结果
            if enable_assessment:
                result['suggestions'].append(f"平等律评分: {equality_assessment['equality_score']:.2f}")
                result['equality_score'] = equality_assessment['equality_score']
            
        except Exception as e:
            result['message'] = f"写入失败: {str(e)}"
            result['suggestions'] = ["检查文件路径权限", "确保磁盘空间充足"]
        
        return result
    
    def append_to_file(self, file_path: str, content: str) -> str:
        """追加内容到文件"""
        return self.write_to_file(file_path, content, mode='a')
    
    def write_json_file(self, file_path: str, data: dict) -> str:
        """写入JSON格式文件"""
        try:
            json_content = json.dumps(data, ensure_ascii=False, indent=2)
            return self.write_to_file(file_path, json_content)
        except Exception as e:
            return f"JSON序列化提醒：{str(e)} - 建议检查数据结构"
    
    def create_markdown_file(self, file_path: str, title: str, content: str) -> str:
        """创建Markdown格式文件"""
        md_content = f"# {title}\n\n{content}"
        return self.write_to_file(file_path, md_content)
    
    def _check_system_preservation(self, file_path: str) -> dict:
        """系统存续律检查 - 引导系统稳定性"""
        for system_dir in self.system_preservation_guidance['system_dirs']:
            if file_path.startswith(system_dir):
                return {
                    'safe': False,
                    'suggestion': self.system_preservation_guidance['suggestion'],
                    'alternatives': ["使用项目目录", "使用用户文档目录"]
                }
        return {'safe': True, 'suggestion': ''}
    
    def _check_resource_equality(self, content: str) -> dict:
        """平等律检查 - 资源公平使用建议"""
        content_size = len(content.encode('utf-8'))
        if content_size > self.resource_equality_guidance['recommended_max_size']:
            return {
                'safe': False,
                'suggestion': self.resource_equality_guidance['suggestion'],
                'recommendations': ["建议分块处理", "考虑使用数据库存储大文件"]
            }
        return {'safe': True, 'suggestion': ''}
    
    def _check_format_best_practice(self, file_path: str) -> dict:
        """一念神魔检查 - 格式最佳实践引导"""
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.format_best_practices['recommended_formats']:
            return {
                'safe': False,
                'suggestion': self.format_best_practices['suggestion'],
                'best_practices': ["使用 .txt、.md、.py 等标准格式"]
            }
        return {'safe': True, 'suggestion': ''}


class TerminalDisplayTool:
    """终端显示栏工具：读取系统日志与运行状态，便于自我调试"""
    def __init__(self, base_path: str = "E:\\RAG系统"):
        from pathlib import Path
        self.base_path = Path(base_path)
        self.logs_dir = self.base_path / 'logs'
        self.data_dir = self.base_path / 'data'

    def list_logs(self) -> dict:
        try:
            if not self.logs_dir.exists():
                return {'success': False, 'error': f'日志目录不存在: {self.logs_dir}'}
            files = sorted([p.name for p in self.logs_dir.glob('*') if p.is_file()])
            return {'success': True, 'data': {'logs': files}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def tail_log(self, file_name: str = 'system_errors.log', lines: int = 200) -> dict:
        try:
            log_path = self.logs_dir / file_name
            if not log_path.exists():
                return {'success': False, 'error': f'日志文件不存在: {log_path}'}
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
            tail = content[-lines:] if lines > 0 else content
            return {'success': True, 'data': {'file': str(log_path), 'lines': tail}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_startup_status(self) -> dict:
        try:
            status_path = self.logs_dir / 'startup_status.json'
            if not status_path.exists():
                return {'success': False, 'error': f'启动状态文件不存在: {status_path}'}
            import json
            with open(status_path, 'r', encoding='utf-8') as f:
                status = json.load(f)
            return {'success': True, 'data': status}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def tail_interactions(self, date_str: str = None, lines: int = 100) -> dict:
        try:
            import datetime, json, os
            # 交互日志目录
            try:
                from config.system_config import INTERACTION_LOG_DIR
                interactions_dir = os.fspath(INTERACTION_LOG_DIR)
            except Exception:
                interactions_dir = os.fspath(self.data_dir / 'interactions')
            if not os.path.exists(interactions_dir):
                return {'success': False, 'error': f'交互日志目录不存在: {interactions_dir}'}
            # 文件名按日期
            if not date_str:
                date_str = datetime.datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(interactions_dir, f'{date_str}.jsonl')
            if not os.path.exists(file_path):
                return {'success': False, 'error': f'交互日志文件不存在: {file_path}'}
            # 读取最后N条
            lines_out = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    try:
                        lines_out.append(json.loads(line))
                    except Exception:
                        lines_out.append({'raw': line})
            return {'success': True, 'data': {'file': file_path, 'events': lines_out}}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ChatToolManager:
    """聊天工具管理器"""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.llm_client = LLMClient()
        
        # 初始化所有工具
        self.tools = {
            'memory_retrieval': MemoryRetrievalTool(self.vector_db),
            'file_reading': FileReadingTool(),
            'web_search': WebSearchTool(),
            'memory_iteration': MemoryIterationTool(self.vector_db, self.llm_client),
            'command_line': CommandLineTool(),
            'file_writing': FileWritingTool(),  # 新增文件写入工具
            'equality_assessment': EqualityAssessmentTool(),  # 新增平等律评估工具
            'memory_slicer': MemorySlicerTool(),  # 新增记忆切片管理工具
            # 新增引擎工具
            'networked_thinking': NetworkedThinkingEngine(),  # 网状思维引擎
            'reasoning_engine': ReasoningEngine(),  # 理性逻辑认知引擎
            'cognitive_barrier_break': CognitiveBarrierBreakEngine(),  # 认知破障引擎
            'terminal_display': TerminalDisplayTool()  # 终端显示栏工具
            # 暂时移除文本处理工具，等待text_cleaner模块实现
            # 'text_cleaner': TextCleaner(),  # 文本清理工具
            # 'memory_text_cleaner': MemoryTextCleaner()  # 记忆文本专用清理器
        }
        
    def get_tool(self, tool_name: str):
        """获取指定工具"""
        return self.tools.get(tool_name)
    
    def list_available_tools(self) -> List[str]:
        """列出可用工具"""
        return list(self.tools.keys())
    
    def close(self):
        """关闭资源"""
        self.vector_db.close()


def create_tool_manager() -> ChatToolManager:
    """创建工具管理器实例"""
    return ChatToolManager()