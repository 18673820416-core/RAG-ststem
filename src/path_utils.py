# @self-expose: {"id": "path_utils", "name": "路径处理工具", "type": "component", "version": "1.0.0", "needs": {"deps": ["os", "pathlib"], "resources": []}, "provides": {"capabilities": ["路径解析", "特殊字符处理", "目录访问"]}}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径处理工具模块
解决包含特殊字符（如 #）的目录路径解析问题
"""

import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Path(__file__).parent.parent, 'logs', 'path_utils.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 移除日志中的表情符号，避免GBK编码问题
original_info = logger.info
def safe_info(msg, *args, **kwargs):
    # 移除常见的Unicode表情符号
    safe_msg = msg.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('🔧', '[FIX]').replace('🔄', '[REPLACE]').replace('📝', '[ADD]').replace('🔍', '[SEARCH]').replace('💾', '[SAVE]').replace('🧠', '[LEARN]').replace('📦', '[INSTALL]')
    original_info(safe_msg, *args, **kwargs)

logger.info = safe_info

class PathUtils:
    """路径处理工具类"""
    
    def __init__(self):
        self.problems_dir = None
        self._init_problems_directory()
    
    def _init_problems_directory(self):
        """初始化问题诊断目录"""
        # 尝试使用不带特殊字符的目录名，避免路径解析问题
        base_dir = Path("e:\\RAG系统")
        problems_dir = base_dir / "problems_and_diagnostics"
        
        # 如果目录不存在，创建它
        problems_dir.mkdir(parents=True, exist_ok=True)
        self.problems_dir = problems_dir
        logger.info(f"✅ 问题诊断目录初始化成功: {self.problems_dir}")
    
    def get_problems_directory(self):
        """获取问题诊断目录路径"""
        return self.problems_dir
    
    def safe_path_join(self, *parts):
        """安全的路径拼接，处理特殊字符"""
        try:
            # 使用pathlib进行安全的路径拼接
            path = Path(*parts)
            logger.info(f"✅ 安全路径拼接成功: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"❌ 安全路径拼接失败: {e}")
            # 降级方案：使用os.path.join
            try:
                path = os.path.join(*parts)
                logger.info(f"✅ 降级路径拼接成功: {path}")
                return path
            except Exception as e2:
                logger.error(f"❌ 降级路径拼接失败: {e2}")
                return None
    
    def handle_special_chars(self, path_str):
        """处理路径中的特殊字符"""
        if not path_str:
            return path_str
        
        # 替换可能导致问题的特殊字符
        special_chars = {
            '#': '_sharp_',
            '?': '_question_',
            '*': '_star_',
            '<': '_lt_',
            '>': '_gt_',
            '|': '_pipe_',
            ':': '_colon_',
            '"': '_quote_'
        }
        
        # 如果路径是原始字符串（以 r 开头），先去掉 r
        if path_str.startswith('r"') or path_str.startswith("r'"):
            path_str = path_str[2:-1] if path_str.endswith('"') or path_str.endswith("'") else path_str[2:]
        
        # 替换特殊字符
        for char, replacement in special_chars.items():
            path_str = path_str.replace(char, replacement)
        
        logger.info(f"✅ 处理特殊字符成功: {path_str}")
        return path_str
    
    def safe_path_exists(self, path):
        """安全检查路径是否存在，处理特殊字符"""
        try:
            # 使用Path对象进行安全检查
            path_obj = Path(path)
            exists = path_obj.exists()
            logger.info(f"✅ 安全路径检查: {path} {'存在' if exists else '不存在'}")
            return exists
        except Exception as e:
            logger.error(f"❌ 安全路径检查失败: {e}")
            return False
    
    def safe_list_dir(self, path):
        """安全列出目录内容，处理特殊字符"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                logger.warning(f"❌ 目录不存在: {path}")
                return []
            
            items = [str(item) for item in path_obj.iterdir()]
            logger.info(f"✅ 安全列出目录内容: {path}，共 {len(items)} 个项目")
            return items
        except Exception as e:
            logger.error(f"❌ 安全列出目录内容失败: {e}")
            return []
    
    def get_safe_problems_directory(self):
        """获取安全的问题诊断目录，避免使用特殊字符"""
        # 确保目录存在
        self.problems_dir.mkdir(parents=True, exist_ok=True)
        return self.problems_dir
    
    def fix_path(self, problematic_path):
        """修复包含特殊字符的问题路径"""
        logger.info(f"🔧 修复路径: {problematic_path}")
        
        # 1. 处理特殊字符
        safe_path = self.handle_special_chars(problematic_path)
        
        # 2. 如果是包含 #problems_and_diagnostics 的路径，替换为安全目录
        if "#problems_and_diagnostics" in problematic_path:
            safe_path = str(self.get_safe_problems_directory())
            logger.info(f"🔄 将包含 # 的问题目录替换为安全目录: {safe_path}")
        
        # 3. 确保路径存在
        path_obj = Path(safe_path)
        path_obj.mkdir(parents=True, exist_ok=True)
        
        return safe_path

# 全局实例
path_utils = PathUtils()

def get_path_utils():
    """获取路径处理工具实例"""
    return path_utils

if __name__ == "__main__":
    # 测试路径处理工具
    utils = PathUtils()
    
    # 测试特殊字符处理
    problematic_path = r"e:\AI\qiusuo-framework\#problems_and_diagnostics"
    safe_path = utils.fix_path(problematic_path)
    print(f"原路径: {problematic_path}")
    print(f"修复后: {safe_path}")
    
    # 测试路径存在性检查
    exists = utils.safe_path_exists(safe_path)
    print(f"目录是否存在: {exists}")
    
    # 测试目录列出
    items = utils.safe_list_dir(safe_path)
    print(f"目录内容: {items}")
