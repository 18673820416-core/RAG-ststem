# @self-expose: {"id": "database_manager", "name": "Database Manager", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Database Manager功能"]}}
"""
线程安全的数据库连接管理器

开发提示词来源：用户反馈的多线程SQLite连接问题
核心理念：每个线程使用独立的数据库连接，避免跨线程连接错误
"""

import sqlite3
import threading
from typing import Optional
from pathlib import Path

from config.system_config import DATABASE_PATH

class DatabaseManager:
    """线程安全的数据库连接管理器"""
    
    _local = threading.local()  # 线程本地存储
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """获取当前线程的数据库连接"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            # 创建新的数据库连接
            self._local.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,  # 允许不同线程使用
                timeout=30.0  # 设置超时时间
            )
            # 启用外键约束
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # 设置WAL模式提高并发性能
            self._local.connection.execute("PRAGMA journal_mode = WAL")
            
        return self._local.connection
    
    def close_connection(self):
        """关闭当前线程的数据库连接"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def execute_query(self, sql: str, params: tuple = ()):
        """执行查询并返回结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def execute_update(self, sql: str, params: tuple = ()):
        """执行更新操作并提交"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def close_all_connections():
    """关闭所有数据库连接（主要用于清理）"""
    global _db_manager
    if _db_manager:
        # 注意：这只能关闭当前线程的连接
        _db_manager.close_connection()
        _db_manager = None