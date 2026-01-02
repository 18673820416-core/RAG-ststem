# @self-expose: {"id": "enhanced_data_crawler", "name": "Enhanced Data Crawler", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Enhanced Data Crawler功能"]}}
# 增强型数据爬取器 - 绕过限制，爬取所有交互数据

import os
import json
import logging
import sqlite3
import shutil
import tempfile
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from config.system_config import DATA_DIR

logger = logging.getLogger(__name__)

class EnhancedDataCrawler:
    """增强型数据爬取器 - 绕过限制，爬取所有交互数据"""
    
    def __init__(self):
        self.crawled_data = []
        self.processed_sources = set()
        
    def crawl_browser_data(self) -> List[Dict[str, Any]]:
        """爬取浏览器交互数据 - 专门针对Edge浏览器DeepSeek聊天优化"""
        browser_data = []
        
        # 获取当前用户名
        username = os.getenv('USERNAME') or 'liang'  # 默认使用liang用户
        logger.info(f"当前用户名: {username}")
        
        # 常见浏览器数据路径
        browser_paths = [
            # Edge (优先处理，因为用户使用Edge)
            f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default",
            # Chrome
            f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default",
            # Firefox
            f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles",
        ]
        
        for path in browser_paths:
            try:
                if os.path.exists(path):
                    logger.info(f"发现浏览器数据路径: {path}")
                    
                    # 如果是Edge浏览器，进行深度爬取
                    if "Microsoft\\Edge" in path:
                        edge_deepseek_data = self._crawl_edge_deepseek_deep(path)
                        browser_data.extend(edge_deepseek_data)
                    
                    # 爬取浏览器历史数据库
                    history_data = self._crawl_browser_history(path)
                    browser_data.extend(history_data)
                    
                    # 爬取浏览器缓存
                    cache_data = self._crawl_browser_cache(path)
                    browser_data.extend(cache_data)
                    
                else:
                    logger.warning(f"浏览器数据路径不存在: {path}")
                    
            except Exception as e:
                logger.warning(f"爬取浏览器数据失败 {path}: {e}")
        
        logger.info(f"爬取到 {len(browser_data)} 条浏览器交互数据")
        return browser_data
    
    def _crawl_edge_deepseek_deep(self, edge_path: str) -> List[Dict[str, Any]]:
        """深度爬取Edge浏览器中的DeepSeek聊天数据"""
        deepseek_data = []
        
        try:
            # Edge浏览器中DeepSeek聊天的关键存储位置（更精确的路径）
            key_locations = [
                # Local Storage 文件
                os.path.join(edge_path, "Local Storage", "leveldb"),
                os.path.join(edge_path, "Local Storage\\leveldb"),
                # Session Storage 文件
                os.path.join(edge_path, "Session Storage", "leveldb"),
                os.path.join(edge_path, "Session Storage\\leveldb"),
                # IndexedDB 数据库
                os.path.join(edge_path, "IndexedDB"),
                os.path.join(edge_path, "IndexedDB\\*.leveldb"),
                # Web Storage
                os.path.join(edge_path, "WebStorage"),
                # 缓存目录
                os.path.join(edge_path, "Cache"),
                os.path.join(edge_path, "Cache\\Cache_Data"),
                # 其他可能的存储位置
                os.path.join(edge_path, "Storage"),
                os.path.join(edge_path, "databases"),
            ]
            
            # 首先检查这些路径是否存在
            existing_locations = []
            for location in key_locations:
                if os.path.exists(location):
                    existing_locations.append(location)
                    logger.info(f"发现Edge浏览器存储位置: {location}")
            
            # 如果没有找到任何存储位置，尝试列出edge_path下的所有子目录
            if not existing_locations:
                logger.info(f"未找到标准存储位置，列出{edge_path}下的所有子目录:")
                try:
                    for item in os.listdir(edge_path):
                        item_path = os.path.join(edge_path, item)
                        if os.path.isdir(item_path):
                            logger.info(f"  - {item}")
                            existing_locations.append(item_path)
                except Exception as e:
                    logger.warning(f"列出{edge_path}子目录失败: {e}")
            
            for location in existing_locations:
                try:
                    logger.info(f"深度搜索DeepSeek相关文件: {location}")
                    
                    # 深度搜索DeepSeek相关文件
                    deepseek_files = self._find_deepseek_files(location)
                    
                    if deepseek_files:
                        logger.info(f"在{location}中找到{len(deepseek_files)}个DeepSeek相关文件")
                    
                    for file_path in deepseek_files:
                        try:
                            # 检查文件大小
                            file_size = os.path.getsize(file_path)
                            if file_size > 10 * 1024 * 1024:  # 跳过大于10MB的文件
                                logger.debug(f"跳过大文件: {file_path} ({file_size} bytes)")
                                continue
                            
                            # 读取文件内容
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # 提取聊天内容
                            chat_content = self._extract_deepseek_chat_content(file_path, content)
                            
                            if chat_content and len(chat_content.strip()) > 50:  # 过滤掉太短的内容
                                deepseek_data.append({
                                    "source": "edge_deepseek_deep",
                                    "file_path": str(file_path),
                                    "content": chat_content,
                                    "crawled_at": datetime.now().isoformat(),
                                    "session_id": self._extract_session_id(content),
                                    "file_size": file_size
                                })
                                logger.info(f"成功提取DeepSeek聊天内容: {file_path}")
                        
                        except Exception as e:
                            logger.debug(f"读取DeepSeek文件失败 {file_path}: {e}")
                
                except Exception as e:
                    logger.warning(f"处理存储位置失败 {location}: {e}")
        
        except Exception as e:
            logger.warning(f"深度爬取Edge浏览器DeepSeek数据失败: {e}")
        
        logger.info(f"深度爬取获得 {len(deepseek_data)} 条DeepSeek聊天数据")
        return deepseek_data
    
    def _find_deepseek_files(self, directory: str) -> List[str]:
        """查找包含DeepSeek聊天数据的文件"""
        deepseek_files = []
        
        try:
            # DeepSeek相关的文件模式（更精确的匹配）
            patterns = [
                "*deepseek*",
                "*chat.deepseek.com*",
                "*platform.deepseek.com*",
                "*indexeddb*",
                "*localstorage*",
                "*sessionstorage*",
                "*webstorage*",
                "*conversation*",
                "*message*",
                "*dialog*",
                "*chat*"
            ]
            
            for pattern in patterns:
                for file_path in Path(directory).rglob(pattern):
                    if file_path.is_file():
                        # 检查文件大小，避免处理太大的文件
                        file_size = file_path.stat().st_size
                        if file_size < 10 * 1024 * 1024:  # 10MB限制
                            deepseek_files.append(str(file_path))
                        else:
                            logger.debug(f"跳过大文件: {file_path} ({file_size} bytes)")
            
            # 如果没有找到文件，尝试直接检查IndexedDB目录
            if not deepseek_files and "IndexedDB" in directory:
                indexeddb_path = Path(directory)
                if indexeddb_path.exists():
                    for item in indexeddb_path.iterdir():
                        if item.is_dir() and "deepseek" in item.name.lower():
                            # 检查leveldb目录中的文件
                            leveldb_files = list(item.rglob("*.ldb")) + list(item.rglob("*.log"))
                            for leveldb_file in leveldb_files:
                                if leveldb_file.is_file():
                                    file_size = leveldb_file.stat().st_size
                                    if file_size < 5 * 1024 * 1024:  # 5MB限制
                                        deepseek_files.append(str(leveldb_file))
        
        except Exception as e:
            logger.debug(f"查找DeepSeek文件失败: {e}")
        
        return deepseek_files
    
    def _extract_deepseek_chat_content(self, file_path: str, content: str) -> str:
        """从文件内容中提取DeepSeek聊天内容"""
        try:
            # 如果是数据库文件，尝试读取数据库
            if file_path.endswith(('.db', '.sqlite', '.localstorage', '.sessionstorage')):
                return self._extract_from_database(file_path)
            
            # 尝试解析JSON格式
            if content.strip().startswith('{') or content.strip().startswith('['):
                try:
                    json_data = json.loads(content)
                    return self._parse_deepseek_chat_json(json_data)
                except:
                    pass
            
            # 尝试提取对话内容
            chat_patterns = [
                r'"content"\s*:\s*"([^"]+)"',
                r'"text"\s*:\s*"([^"]+)"',
                r'"message"\s*:\s*"([^"]+)"',
                r'"body"\s*:\s*"([^"]+)"',
                r'user:\s*([^\n]+)',
                r'assistant:\s*([^\n]+)',
                r'User:\s*([^\n]+)',
                r'Assistant:\s*([^\n]+)',
                r'用户:\s*([^\n]+)',
                r'助手:\s*([^\n]+)'
            ]
            
            extracted = []
            for pattern in chat_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 20:  # 过滤掉太短的内容
                        extracted.append(match.strip())
            
            if extracted:
                return " | ".join(extracted)
            
            # 如果包含DeepSeek相关关键词，返回部分内容
            if 'deepseek' in content.lower() or 'chat' in content.lower():
                return content[:1000]
            
            return ""
        
        except Exception as e:
            logger.debug(f"提取DeepSeek聊天内容失败: {e}")
            return ""
    
    def _extract_from_database(self, db_path: str) -> str:
        """从数据库文件中提取聊天内容 - 专门处理LevelDB格式"""
        try:
            # 如果是LevelDB数据库文件
            if db_path.endswith(('.ldb', '.log')) and 'leveldb' in db_path.lower():
                return self._extract_from_leveldb(db_path)
            
            # 如果是SQLite数据库文件
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
                shutil.copy2(db_path, temp_file.name)
                temp_db_path = temp_file.name
            
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # 尝试读取所有表的数据
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            all_content = []
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 50")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        row_text = str(row)
                        if 'deepseek' in row_text.lower() or 'chat' in row_text.lower():
                            all_content.append(row_text)
                except:
                    pass
            
            conn.close()
            os.unlink(temp_db_path)
            
            return " | ".join(all_content) if all_content else ""
        
        except Exception as e:
            logger.debug(f"从数据库提取内容失败 {db_path}: {e}")
            return ""
    
    def _extract_from_leveldb(self, leveldb_path: str) -> str:
        """从LevelDB数据库文件中提取聊天内容"""
        try:
            # 对于LevelDB文件，我们尝试读取二进制内容并解析
            with open(leveldb_path, 'rb') as f:
                content = f.read()
            
            # 多种编码尝试
            decoded_content = None
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    decoded_content = content.decode(encoding, errors='ignore')
                    # 检查是否包含可读内容
                    if len(decoded_content.strip()) > 10:
                        break
                except:
                    continue
            
            if decoded_content is None:
                # 如果所有编码都失败，尝试直接处理二进制
                decoded_content = str(content)
            
            # 更精确的聊天内容提取模式
            chat_patterns = [
                # JSON格式的内容提取
                r'"content"\s*:\s*"([^"]+)"',
                r'"text"\s*:\s*"([^"]+)"',
                r'"message"\s*:\s*"([^"]+)"',
                r'"prompt"\s*:\s*"([^"]+)"',
                r'"response"\s*:\s*"([^"]+)"',
                # 单引号格式
                r"'content'\s*:\s*'([^']+)'",
                r"'text'\s*:\s*'([^']+)'",
                r"'message'\s*:\s*'([^']+)'",
                # 无引号格式
                r'content\s*[:=]\s*([^,\s}]+)',
                r'text\s*[:=]\s*([^,\s}]+)',
                r'message\s*[:=]\s*([^,\s}]+)',
                # 对话模式
                r'(用户|User|human)["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
                r'(助手|AI|assistant)["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
                # 直接提取较长的文本块
                r'([\u4e00-\u9fff\w\s]{30,})'
            ]
            
            extracted_content = []
            for pattern in chat_patterns:
                matches = re.findall(pattern, decoded_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # 处理分组匹配
                        text = match[1] if len(match) > 1 else match[0]
                    else:
                        text = match
                    
                    # 过滤条件
                    if (len(text) > 20 and 
                        not text.startswith('http') and 
                        not text.isdigit() and
                        not all(c in '{}[](),.:;\'\"' for c in text.strip())):
                        extracted_content.append(text.strip())
            
            # 去重并合并
            unique_content = list(set(extracted_content))
            
            # 检查DeepSeek相关关键词
            deepseek_keywords = ['deepseek', 'chat', '对话', '问题', '回答', 'AI', '助手', '用户', '你好', '谢谢']
            has_deepseek_content = any(keyword in decoded_content.lower() for keyword in deepseek_keywords)
            
            if unique_content:
                return ' | '.join(unique_content[:5])  # 限制返回内容数量
            elif has_deepseek_content and len(decoded_content.strip()) > 50:
                # 返回包含关键词的段落
                lines = decoded_content.split('\n')
                relevant_lines = [line for line in lines if any(keyword in line.lower() for keyword in deepseek_keywords)]
                if relevant_lines:
                    return ' | '.join(relevant_lines[:3])
                else:
                    return decoded_content[:300]  # 返回前300个字符
            else:
                return ""
        
        except Exception as e:
            logger.debug(f"从LevelDB提取内容失败 {leveldb_path}: {e}")
            return ""
    
    def _parse_deepseek_chat_json(self, json_data: Any) -> str:
        """解析DeepSeek聊天JSON数据"""
        try:
            if isinstance(json_data, dict):
                # DeepSeek聊天数据的常见字段
                chat_fields = ['content', 'text', 'message', 'body', 'value', 'data', 'result']
                
                for field in chat_fields:
                    if field in json_data:
                        field_value = json_data[field]
                        if isinstance(field_value, str) and len(field_value.strip()) > 20:
                            return field_value
                        elif isinstance(field_value, (dict, list)):
                            nested = self._parse_deepseek_chat_json(field_value)
                            if nested:
                                return nested
                
                # 递归处理所有值
                for key, value in json_data.items():
                    if isinstance(value, (dict, list)):
                        nested = self._parse_deepseek_chat_json(value)
                        if nested:
                            return nested
            
            elif isinstance(json_data, list):
                contents = []
                for item in json_data:
                    if isinstance(item, (dict, list)):
                        item_content = self._parse_deepseek_chat_json(item)
                        if item_content:
                            contents.append(item_content)
                
                if contents:
                    return " | ".join(contents)
            
            return ""
        
        except Exception as e:
            logger.debug(f"解析DeepSeek聊天JSON失败: {e}")
            return ""
    
    def _crawl_browser_history(self, browser_path: str) -> List[Dict[str, Any]]:
        """爬取浏览器历史记录 - 专门针对DeepSeek聊天页面优化"""
        history_data = []
        
        # 浏览器历史数据库文件
        history_files = [
            "History",
            "Web Data",
            "Login Data"
        ]
        
        for history_file in history_files:
            db_path = os.path.join(browser_path, history_file)
            
            if os.path.exists(db_path):
                try:
                    # 复制数据库文件到临时位置（避免锁定）
                    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
                        shutil.copy2(db_path, temp_file.name)
                        temp_db_path = temp_file.name
                    
                    # 读取数据库
                    conn = sqlite3.connect(temp_db_path)
                    cursor = conn.cursor()
                    
                    # 查询历史记录
                    if history_file == "History":
                        # 专门查询DeepSeek相关的历史记录
                        cursor.execute("""
                            SELECT url, title, visit_count, last_visit_time 
                            FROM urls 
                            WHERE url LIKE '%deepseek%' OR title LIKE '%deepseek%' OR url LIKE '%chat/deepseek%'
                        """)
                        
                        deepseek_rows = cursor.fetchall()
                        for row in deepseek_rows:
                            # 提取聊天内容信息
                            chat_content = self._extract_chat_from_url(row[0], row[1])
                            
                            history_data.append({
                                "source": "browser_history",
                                "url": row[0],
                                "title": row[1],
                                "visit_count": row[2],
                                "last_visit": row[3],
                                "crawled_at": datetime.now().isoformat(),
                                "chat_content": chat_content,
                                "session_id": self._extract_session_id_from_url(row[0])
                            })
                        
                        # 查询其他历史记录（限制数量）
                        cursor.execute("""
                            SELECT url, title, visit_count, last_visit_time 
                            FROM urls 
                            WHERE url NOT LIKE '%deepseek%' AND title NOT LIKE '%deepseek%'
                            ORDER BY last_visit_time DESC 
                            LIMIT 100
                        """)
                        
                        other_rows = cursor.fetchall()
                        for row in other_rows:
                            history_data.append({
                                "source": "browser_history",
                                "url": row[0],
                                "title": row[1],
                                "visit_count": row[2],
                                "last_visit": row[3],
                                "crawled_at": datetime.now().isoformat()
                            })
                    
                    conn.close()
                    os.unlink(temp_db_path)  # 删除临时文件
                    
                except Exception as e:
                    logger.warning(f"读取浏览器历史数据库失败 {db_path}: {e}")
        
        return history_data
    
    def _extract_chat_from_url(self, url: str, title: str) -> str:
        """从URL和标题中提取聊天内容信息"""
        chat_info = []
        
        # 从标题中提取信息
        if title and title.strip():
            chat_info.append(f"标题: {title}")
        
        # 从URL中提取会话ID等信息
        if 'deepseek' in url.lower():
            # 提取会话ID
            session_id = self._extract_session_id_from_url(url)
            if session_id != "unknown":
                chat_info.append(f"会话ID: {session_id}")
            
            # 标记为DeepSeek聊天
            chat_info.append("类型: DeepSeek AI聊天")
        
        return " | ".join(chat_info) if chat_info else "无聊天内容信息"
    
    def _extract_session_id_from_url(self, url: str) -> str:
        """从URL中提取会话ID"""
        # 匹配DeepSeek聊天会话ID格式
        session_pattern = r'https://chat\.deepseek\.com/a/chat/s/([a-f0-9-]+)'
        match = re.search(session_pattern, url)
        
        if match:
            return match.group(1)
        
        return "unknown"
    
    def _crawl_browser_cache(self, browser_path: str) -> List[Dict[str, Any]]:
        """爬取浏览器缓存数据 - 专门针对DeepSeek聊天页面优化"""
        cache_data = []
        
        cache_dirs = [
            "Cache",
            "Local Storage", 
            "Session Storage"
        ]
        
        for cache_dir in cache_dirs:
            cache_path = os.path.join(browser_path, cache_dir)
            
            if os.path.exists(cache_path):
                try:
                    # 专门处理DeepSeek聊天页面的缓存
                    deepseek_cache_data = self._crawl_deepseek_specific_cache(cache_path)
                    cache_data.extend(deepseek_cache_data)
                    
                    # 通用缓存爬取
                    for root, dirs, files in os.walk(cache_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            
                            # 处理所有可能的缓存文件
                            if file.endswith(('.txt', '.log', '.json', '.dat', '.localstorage', '.sessionstorage')):
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                    
                                    # 检查是否包含DeepSeek相关内容
                                    if 'deepseek' in content.lower() or 'chat' in content.lower():
                                        cache_data.append({
                                            "source": "browser_cache",
                                            "file_path": file_path,
                                            "content": content[:5000],  # 增加长度限制
                                            "crawled_at": datetime.now().isoformat()
                                        })
                                except:
                                    pass  # 跳过无法读取的文件
                    
                except Exception as e:
                    logger.warning(f"爬取浏览器缓存失败 {cache_path}: {e}")
        
        return cache_data
    
    def _crawl_deepseek_specific_cache(self, cache_path: str) -> List[Dict[str, Any]]:
        """专门爬取DeepSeek聊天页面的缓存数据"""
        deepseek_data = []
        
        try:
            # 查找包含聊天会话ID的文件
            deepseek_patterns = [
                "*deepseek*",
                "*chat*",
                "*session*",
                "*conversation*",
                "*message*",
                "*localstorage*",
                "*sessionstorage*"
            ]
            
            for pattern in deepseek_patterns:
                for file_path in Path(cache_path).rglob(pattern):
                    if file_path.is_file():
                        try:
                            # 读取文件内容
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # 检查是否包含DeepSeek聊天会话ID
                            if self._contains_deepseek_session(content):
                                # 提取聊天内容
                                chat_content = self._extract_chat_content(content)
                                
                                if chat_content and len(chat_content.strip()) > 20:  # 过滤掉太短的内容
                                    deepseek_data.append({
                                        "source": "deepseek_chat",
                                        "file_path": str(file_path),
                                        "content": chat_content,
                                        "crawled_at": datetime.now().isoformat(),
                                        "session_id": self._extract_session_id(content)
                                    })
                        
                        except Exception as e:
                            logger.debug(f"读取DeepSeek缓存文件失败 {file_path}: {e}")
            
            # 专门检查Edge浏览器的Local Storage和Session Storage
            if "Local Storage" in cache_path or "Session Storage" in cache_path:
                edge_chat_data = self._crawl_edge_deepseek_storage(cache_path)
                deepseek_data.extend(edge_chat_data)
        
        except Exception as e:
            logger.warning(f"爬取DeepSeek特定缓存失败: {e}")
        
        return deepseek_data
    
    def _crawl_edge_deepseek_storage(self, storage_path: str) -> List[Dict[str, Any]]:
        """专门爬取Edge浏览器的DeepSeek聊天存储数据"""
        edge_data = []
        
        try:
            # Edge浏览器存储文件的常见位置和格式
            storage_files = [
                "https_chat.deepseek.com_0.localstorage",
                "https_chat.deepseek.com_0.localstorage-journal",
                "https_chat.deepseek.com_0.sessionstorage",
                "https_chat.deepseek.com_0.sessionstorage-journal"
            ]
            
            for storage_file in storage_files:
                file_path = os.path.join(storage_path, storage_file)
                
                if os.path.exists(file_path):
                    try:
                        # 尝试读取SQLite数据库格式的存储文件
                        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
                            shutil.copy2(file_path, temp_file.name)
                            temp_db_path = temp_file.name
                        
                        conn = sqlite3.connect(temp_db_path)
                        cursor = conn.cursor()
                        
                        # 查询存储数据
                        try:
                            cursor.execute("SELECT key, value FROM ItemTable")
                            for key, value in cursor.fetchall():
                                if value and isinstance(value, (str, bytes)):
                                    # 尝试解析存储的值
                                    parsed_content = self._parse_storage_value(value)
                                    if parsed_content and 'deepseek' in parsed_content.lower():
                                        edge_data.append({
                                            "source": "edge_deepseek_storage",
                                            "file_path": file_path,
                                            "content": parsed_content[:2000],
                                            "crawled_at": datetime.now().isoformat(),
                                            "storage_key": key
                                        })
                        except:
                            # 如果不是标准格式，尝试直接读取
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            if 'deepseek' in content.lower():
                                edge_data.append({
                                    "source": "edge_deepseek_storage",
                                    "file_path": file_path,
                                    "content": content[:2000],
                                    "crawled_at": datetime.now().isoformat()
                                })
                        
                        conn.close()
                        os.unlink(temp_db_path)
                        
                    except Exception as e:
                        logger.debug(f"读取Edge存储文件失败 {file_path}: {e}")
        
        except Exception as e:
            logger.warning(f"爬取Edge浏览器DeepSeek存储失败: {e}")
        
        return edge_data
    
    def _parse_storage_value(self, value: Any) -> str:
        """解析浏览器存储的值"""
        try:
            if isinstance(value, bytes):
                # 尝试解码字节数据
                try:
                    return value.decode('utf-8')
                except:
                    try:
                        return value.decode('latin-1')
                    except:
                        return str(value)
            
            elif isinstance(value, str):
                # 尝试解析JSON格式
                if value.strip().startswith('{') or value.strip().startswith('['):
                    try:
                        json_data = json.loads(value)
                        return self._parse_chat_json(json_data)
                    except:
                        pass
                
                return value
            
            else:
                return str(value)
        
        except Exception as e:
            logger.debug(f"解析存储值失败: {e}")
            return str(value)
    
    def _contains_deepseek_session(self, content: str) -> bool:
        """检查内容是否包含DeepSeek聊天会话"""
        # 检查是否包含DeepSeek聊天URL模式
        deepseek_url_patterns = [
            r'https://chat\.deepseek\.com/a/chat/s/[a-f0-9-]+',
            r'deepseek',
            r'chat/s/[a-f0-9-]+'
        ]
        
        for pattern in deepseek_url_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_session_id(self, content: str) -> str:
        """从内容中提取会话ID"""
        # 匹配DeepSeek聊天会话ID格式
        session_pattern = r'https://chat\.deepseek\.com/a/chat/s/([a-f0-9-]+)'
        match = re.search(session_pattern, content)
        
        if match:
            return match.group(1)
        
        return "unknown"
    
    def _extract_chat_content(self, content: str) -> str:
        """从缓存内容中提取聊天内容"""
        try:
            # 尝试解析JSON格式的聊天数据
            if content.strip().startswith('{') or content.strip().startswith('['):
                try:
                    json_data = json.loads(content)
                    return self._parse_chat_json(json_data)
                except:
                    pass
            
            # 尝试提取对话文本
            chat_patterns = [
                r'"content"\s*:\s*"([^"]+)"',  # JSON格式的内容
                r'"text"\s*:\s*"([^"]+)"',     # JSON格式的文本
                r'"message"\s*:\s*"([^"]+)"',  # JSON格式的消息
                r'user:\s*([^\n]+)',              # 用户消息
                r'assistant:\s*([^\n]+)',         # 助手回复
            ]
            
            extracted_content = []
            for pattern in chat_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 10:  # 过滤掉太短的内容
                        extracted_content.append(match.strip())
            
            if extracted_content:
                return " | ".join(extracted_content)
            
            # 如果无法提取特定内容，返回前1000个字符
            return content[:1000]
        
        except Exception as e:
            logger.debug(f"提取聊天内容失败: {e}")
            return content[:1000]
    
    def _parse_chat_json(self, json_data: Any) -> str:
        """解析JSON格式的聊天数据"""
        try:
            if isinstance(json_data, dict):
                # 尝试提取常见字段
                content_fields = ['content', 'text', 'message', 'body', 'value']
                
                for field in content_fields:
                    if field in json_data and json_data[field]:
                        return str(json_data[field])
                
                # 递归处理嵌套结构
                for key, value in json_data.items():
                    if isinstance(value, (dict, list)):
                        nested_content = self._parse_chat_json(value)
                        if nested_content:
                            return nested_content
            
            elif isinstance(json_data, list):
                # 处理数组
                contents = []
                for item in json_data:
                    if isinstance(item, (dict, list)):
                        item_content = self._parse_chat_json(item)
                        if item_content:
                            contents.append(item_content)
                
                if contents:
                    return " | ".join(contents)
            
            return str(json_data)[:1000]
        
        except Exception as e:
            logger.debug(f"解析聊天JSON失败: {e}")
            return str(json_data)[:1000]
    
    def crawl_ide_data(self) -> List[Dict[str, Any]]:
        """爬取IDE交互数据"""
        ide_data = []
        
        # IDE数据路径
        ide_paths = [
            "E:\\AI\\qiusuo-framework\\logs",
            "E:\\灵境\\VCPChat\\logs",
            "E:\\QiuSuo\\logs",
            "E:\\RAG系统\\logs",
        ]
        
        for ide_path in ide_paths:
            if os.path.exists(ide_path):
                try:
                    # 遍历IDE日志目录
                    for root, dirs, files in os.walk(ide_path):
                        for file in files:
                            if file.endswith(('.log', '.txt', '.json')):
                                file_path = os.path.join(root, file)
                                
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                    
                                    ide_data.append({
                                        "source": "ide_logs",
                                        "file_path": file_path,
                                        "content": content,
                                        "crawled_at": datetime.now().isoformat()
                                    })
                                except Exception as e:
                                    logger.warning(f"读取IDE日志文件失败 {file_path}: {e}")
                    
                except Exception as e:
                    logger.warning(f"爬取IDE数据失败 {ide_path}: {e}")
        
        logger.info(f"爬取到 {len(ide_data)} 条IDE交互数据")
        return ide_data
    
    def crawl_doubao_client_data(self) -> List[Dict[str, Any]]:
        """爬取豆包客户端交互数据"""
        doubao_data = []
        
        # 豆包客户端数据路径
        doubao_paths = [
            "C:\\Users\\{username}\\AppData\\Local\\Doubao\\Application",
            "C:\\Users\\{username}\\AppData\\Local\\ByteDance\\Doubao",
            "C:\\Users\\{username}\\AppData\\Roaming\\ByteDance\\Doubao",
            "C:\\Program Files\\ByteDance\\Doubao",
            "C:\\Program Files (x86)\\ByteDance\\Doubao",
        ]
        
        username = os.getenv('USERNAME') or 'current_user'
        
        for path_template in doubao_paths:
            path = path_template.replace("{username}", username)
            
            if os.path.exists(path):
                try:
                    logger.info(f"发现豆包客户端路径: {path}")
                    
                    # 查找豆包客户端的对话历史文件
                    doubao_patterns = [
                        "*conversation*",
                        "*chat*",
                        "*dialog*", 
                        "*history*",
                        "*log*",
                        "*session*",
                        "*message*",
                        "*data*",
                        "*storage*",
                    ]
                    
                    for pattern in doubao_patterns:
                        for file_path in Path(path).rglob(pattern):
                            if file_path.is_file() and file_path.suffix in ['.txt', '.log', '.json', '.db', '.sqlite', '.dat']:
                                try:
                                    # 处理数据库文件
                                    if file_path.suffix in ['.db', '.sqlite']:
                                        db_data = self._crawl_doubao_database(file_path)
                                        doubao_data.extend(db_data)
                                    else:
                                        # 处理文本文件
                                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read()
                                        
                                        if content.strip():
                                            doubao_data.append({
                                                "source": "doubao_client",
                                                "file_path": str(file_path),
                                                "content": content[:5000],  # 限制长度
                                                "crawled_at": datetime.now().isoformat()
                                            })
                                except Exception as e:
                                    logger.warning(f"读取豆包文件失败 {file_path}: {e}")
                    
                except Exception as e:
                    logger.warning(f"爬取豆包客户端数据失败 {path}: {e}")
        
        logger.info(f"爬取到 {len(doubao_data)} 条豆包客户端交互数据")
        return doubao_data
    
    def _crawl_doubao_database(self, db_path: Path) -> List[Dict[str, Any]]:
        """爬取豆包客户端数据库"""
        db_data = []
        
        try:
            # 复制数据库文件到临时位置（避免锁定）
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
                shutil.copy2(db_path, temp_file.name)
                temp_db_path = temp_file.name
            
            # 读取数据库
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # 尝试查询常见的表结构
            tables_to_check = [
                'conversations', 'messages', 'chats', 'dialogs',
                'history', 'sessions', 'user_data', 'chat_history'
            ]
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            for table in all_tables:
                try:
                    # 尝试读取表数据
                    cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        # 将行数据转换为可读文本
                        row_text = f"表{table}: {str(row)}"
                        
                        db_data.append({
                            "source": "doubao_database",
                            "file_path": str(db_path),
                            "table_name": table,
                            "content": row_text,
                            "crawled_at": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.debug(f"读取表 {table} 失败: {e}")
            
            conn.close()
            os.unlink(temp_db_path)  # 删除临时文件
            
        except Exception as e:
            logger.warning(f"读取豆包数据库失败 {db_path}: {e}")
        
        return db_data
    
    def crawl_local_client_data(self) -> List[Dict[str, Any]]:
        """爬取本地客户端交互数据"""
        client_data = []
        
        # 本地客户端数据路径
        client_paths = [
            "E:\\AI",
            "E:\\灵境",
            "E:\\QiuSuo",
            "E:\\RAG系统",
        ]
        
        for client_path in client_paths:
            if os.path.exists(client_path):
                try:
                    # 查找对话历史文件
                    conversation_patterns = [
                        "*conversation*",
                        "*chat*",
                        "*dialog*",
                        "*history*",
                        "*log*",
                    ]
                    
                    for pattern in conversation_patterns:
                        for file_path in Path(client_path).rglob(pattern):
                            if file_path.is_file() and file_path.suffix in ['.txt', '.log', '.json', '.md']:
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                    
                                    client_data.append({
                                        "source": "local_client",
                                        "file_path": str(file_path),
                                        "content": content,
                                        "crawled_at": datetime.now().isoformat()
                                    })
                                except Exception as e:
                                    logger.warning(f"读取客户端文件失败 {file_path}: {e}")
                    
                except Exception as e:
                    logger.warning(f"爬取本地客户端数据失败 {client_path}: {e}")
        
        logger.info(f"爬取到 {len(client_data)} 条本地客户端交互数据")
        return client_data
    
    def crawl_all_sources(self) -> List[Dict[str, Any]]:
        """爬取所有数据源"""
        all_data = []
        
        logger.info("开始爬取浏览器交互数据...")
        browser_data = self.crawl_browser_data()
        all_data.extend(browser_data)
        
        logger.info("开始爬取IDE交互数据...")
        ide_data = self.crawl_ide_data()
        all_data.extend(ide_data)
        
        logger.info("开始爬取豆包客户端交互数据...")
        doubao_data = self.crawl_doubao_client_data()
        all_data.extend(doubao_data)
        
        logger.info("开始爬取本地客户端交互数据...")
        client_data = self.crawl_local_client_data()
        all_data.extend(client_data)
        
        # 保存爬取的数据
        self._save_crawled_data(all_data)
        
        logger.info(f"总共爬取到 {len(all_data)} 条交互数据")
        
        # 评估数据质量
        quality_report = self.evaluate_data_quality(all_data)
        logger.info(f"数据质量评估完成: {quality_report}")
        
        return all_data
    
    def evaluate_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估数据质量"""
        quality_report = {
            "total_records": len(data),
            "quality_scores": [],
            "quality_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0},
            "source_quality": {},
            "issues_found": []
        }
        
        for record in data:
            score = self._calculate_quality_score(record)
            quality_report["quality_scores"].append(score)
            
            # 分类质量等级
            if score >= 0.8:
                quality_report["quality_distribution"]["excellent"] += 1
            elif score >= 0.6:
                quality_report["quality_distribution"]["good"] += 1
            elif score >= 0.4:
                quality_report["quality_distribution"]["fair"] += 1
            else:
                quality_report["quality_distribution"]["poor"] += 1
            
            # 按来源统计质量
            source = record.get("source", "unknown")
            if source not in quality_report["source_quality"]:
                quality_report["source_quality"][source] = {"count": 0, "total_score": 0}
            quality_report["source_quality"][source]["count"] += 1
            quality_report["source_quality"][source]["total_score"] += score
            
            # 检查问题
            issues = self._check_data_issues(record)
            if issues:
                quality_report["issues_found"].extend(issues)
        
        # 计算平均质量分数
        if quality_report["quality_scores"]:
            avg_score = sum(quality_report["quality_scores"]) / len(quality_report["quality_scores"])
            quality_report["average_quality_score"] = round(avg_score, 3)
        else:
            quality_report["average_quality_score"] = 0
        
        return quality_report
    
    def _calculate_quality_score(self, record: Dict[str, Any]) -> float:
        """计算单个记录的质量分数（0-1）"""
        score = 0.0
        content = record.get("content", "")
        
        # 1. 内容长度评分（20%）
        length_score = min(len(content) / 1000, 1.0) * 0.2
        score += length_score
        
        # 2. 文本可读性评分（30%）
        readability_score = self._assess_readability(content) * 0.3
        score += readability_score
        
        # 3. 信息密度评分（25%）
        information_density = self._assess_information_density(content) * 0.25
        score += information_density
        
        # 4. 结构完整性评分（25%）
        structure_score = self._assess_structure(content) * 0.25
        score += structure_score
        
        return round(score, 3)
    
    def _assess_readability(self, text: str) -> float:
        """评估文本可读性"""
        if not text.strip():
            return 0.0
        
        # 计算句子数量
        sentences = re.split(r'[.!?。！？]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # 计算单词数量
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        if sentence_count == 0 or word_count == 0:
            return 0.0
        
        # 平均句子长度
        avg_sentence_length = word_count / sentence_count
        
        # 可读性评分（基于句子长度和词汇多样性）
        if avg_sentence_length < 5:
            return 0.3  # 太短
        elif avg_sentence_length < 15:
            return 0.8  # 理想长度
        elif avg_sentence_length < 25:
            return 0.6  # 稍长
        else:
            return 0.4  # 过长
    
    def _assess_information_density(self, text: str) -> float:
        """评估信息密度"""
        if not text.strip():
            return 0.0
        
        # 计算关键词密度
        keywords = ['的', '是', '在', '有', '和', '与', '或', '但', '因为', '所以', '如果', '那么']
        keyword_count = sum(1 for word in text if word in keywords)
        
        # 计算名词短语密度
        noun_phrases = re.findall(r'[\u4e00-\u9fff]+的[\u4e00-\u9fff]+', text)
        noun_phrase_density = len(noun_phrases) / max(len(text.split()), 1)
        
        # 计算实体密度
        entities = re.findall(r'[A-Za-z]+|[\u4e00-\u9fff]{2,}', text)
        entity_density = len(entities) / max(len(text.split()), 1)
        
        # 综合信息密度评分
        density_score = (noun_phrase_density + entity_density) / 2
        return min(density_score * 2, 1.0)  # 归一化到0-1
    
    def _assess_structure(self, text: str) -> float:
        """评估结构完整性"""
        if not text.strip():
            return 0.0
        
        score = 0.0
        
        # 检查段落结构
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.3
        
        # 检查标点符号使用
        punctuation_count = len(re.findall(r'[.!?。！？]', text))
        if punctuation_count > len(text) / 100:
            score += 0.3
        
        # 检查连接词使用
        connectors = ['首先', '其次', '然后', '最后', '因此', '所以', '但是', '然而']
        connector_count = sum(1 for connector in connectors if connector in text)
        if connector_count > 0:
            score += 0.2
        
        # 检查标题结构
        if re.search(r'^#+\s+.+', text, re.MULTILINE):
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_data_issues(self, record: Dict[str, Any]) -> List[str]:
        """检查数据问题"""
        issues = []
        content = record.get("content", "")
        
        # 检查空内容
        if not content.strip():
            issues.append(f"空内容: {record.get('file_path', 'unknown')}")
        
        # 检查过短内容
        if len(content.strip()) < 10:
            issues.append(f"内容过短: {record.get('file_path', 'unknown')}")
        
        # 检查编码问题
        if '\ufffd' in content:
            issues.append(f"编码问题: {record.get('file_path', 'unknown')}")
        
        # 检查重复内容
        if len(content) > 100 and len(set(content)) / len(content) < 0.1:
            issues.append(f"可能重复: {record.get('file_path', 'unknown')}")
        
        return issues
    
    def _save_crawled_data(self, data: List[Dict[str, Any]]):
        """保存爬取的数据"""
        if not data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(__file__).parent.parent / "data" / f"crawled_data_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"爬取数据已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存爬取数据失败: {e}")

def main():
    """测试增强型数据爬取器"""
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    crawler = EnhancedDataCrawler()
    
    print("开始爬取所有交互数据...")
    all_data = crawler.crawl_all_sources()
    
    print(f"爬取完成！共获得 {len(all_data)} 条交互数据")
    
    # 显示数据统计
    sources = {}
    for item in all_data:
        source = item.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("\n数据来源统计:")
    for source, count in sources.items():
        print(f"  {source}: {count} 条")

if __name__ == "__main__":
    main()