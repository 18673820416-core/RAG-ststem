#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本生成器
根据错误信息自动生成测试脚本
"""
# @self-expose: {"id": "test_script_generator", "name": "Test Script Generator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Script Generator功能"]}}

import os
import json
import subprocess
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Path(__file__).parent.parent, 'logs', 'test_script_generator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestScriptGenerator:
    """测试脚本生成器"""
    
    def __init__(self, rag_system_path="E:\RAG系统"):
        self.rag_system_path = Path(rag_system_path)
    
    def generate_test_script(self, error_data):
        """根据错误信息生成测试脚本"""
        error_type = error_data.get('type', 'unknown')
        error_message = error_data.get('message', '')
        
        logger.info(f"📝 生成测试脚本: {error_type} - {error_message}")
        
        # 根据错误类型生成不同的测试脚本
        if "Connection refused" in error_message:
            return self._generate_connection_test_script(error_data)
        elif "ModuleNotFoundError" in error_message:
            return self._generate_import_test_script(error_data)
        elif "FileNotFoundError" in error_message:
            return self._generate_file_test_script(error_data)
        elif "PermissionError" in error_message:
            return self._generate_permission_test_script(error_data)
        elif "JSONDecodeError" in error_message:
            return self._generate_json_test_script(error_data)
        
        logger.warning(f"❌ 无法生成测试脚本: 未知错误类型")
        return None
    
    def _generate_connection_test_script(self, error_data):
        """生成连接测试脚本"""
        return f"""#!/usr/bin/env python3
# 自动生成的连接测试脚本

import socket

try:
    # 测试连接
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('localhost', 10808))
    print("✅ 连接测试成功")
    s.close()
except Exception as e:
    print(f"❌ 连接测试失败: {e}")
    import sys
    sys.exit(1)
"""
    
    def _generate_import_test_script(self, error_data):
        """生成导入测试脚本"""
        error_message = error_data.get('message', '')
        module_name = None
        
        # 尝试从错误信息中提取模块名
        if "No module named" in error_message:
            module_name = error_message.split("'" or '"')[1] if "'" in error_message or '"' in error_message else None
        elif "ModuleNotFoundError" in error_message:
            parts = error_message.split(":")
            if len(parts) > 1:
                module_name = parts[1].strip().replace("'", "").replace('"', '')
        
        if module_name:
            return f"""#!/usr/bin/env python3
# 自动生成的导入测试脚本

try:
    # 测试导入缺失的模块
    import {module_name}
    print(f"✅ 成功导入模块: {module_name}")
except Exception as e:
    print(f"❌ 导入模块失败: {e}")
    import sys
    sys.exit(1)
"""
    
    def _generate_file_test_script(self, error_data):
        """生成文件测试脚本"""
        error_message = error_data.get('message', '')
        file_path = None
        
        # 尝试从错误信息中提取文件路径
        if "No such file or directory" in error_message:
            file_path = error_message.split("'" or '"')[1] if "'" in error_message or '"' in error_message else None
        elif "FileNotFoundError" in error_message:
            parts = error_message.split(":")
            if len(parts) > 1:
                file_path = parts[1].strip().replace("'", "").replace('"', '')
        
        if file_path:
            return f"""#!/usr/bin/env python3
# 自动生成的文件测试脚本

import os

# 测试文件是否存在
file_path = '{file_path}'
if os.path.exists(file_path):
    print(f"✅ 文件存在: {file_path}")
    if os.path.isfile(file_path):
        print(f"✅ 是文件")
    elif os.path.isdir(file_path):
        print(f"✅ 是目录")
else:
    print(f"❌ 文件不存在: {file_path}")
    import sys
    sys.exit(1)
"""
    
    def _generate_permission_test_script(self, error_data):
        """生成权限测试脚本"""
        error_message = error_data.get('message', '')
        file_path = None
        
        # 尝试从错误信息中提取文件路径
        if "Permission denied" in error_message:
            file_path = error_message.split("'" or '"')[1] if "'" in error_message or '"' in error_message else None
        elif "PermissionError" in error_message:
            parts = error_message.split(":")
            if len(parts) > 1:
                file_path = parts[1].strip().replace("'", "").replace('"', '')
        
        if file_path:
            return f"""#!/usr/bin/env python3
# 自动生成的权限测试脚本

import os
import stat

# 测试文件权限
file_path = '{file_path}'
if os.path.exists(file_path):
    # 检查文件权限
    st = os.stat(file_path)
    permissions = stat.filemode(st.st_mode)
    print(f"✅ 文件存在，权限: {permissions}")
    
    # 尝试读取文件
    try:
        with open(file_path, 'r') as f:
            print(f"✅ 成功读取文件")
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")
        import sys
        sys.exit(1)
else:
    print(f"❌ 文件不存在: {file_path}")
    import sys
    sys.exit(1)
"""
    
    def _generate_json_test_script(self, error_data):
        """生成JSON测试脚本"""
        error_message = error_data.get('message', '')
        file_path = None
        
        # 尝试从错误信息中提取文件路径
        if "JSONDecodeError" in error_message:
            parts = error_message.split(":")
            if len(parts) > 1:
                # 尝试从错误信息中提取文件路径
                # 这可能需要更复杂的解析
                pass
        
        if file_path:
            return f"""#!/usr/bin/env python3
# 自动生成的JSON测试脚本

import json

# 测试JSON文件
file_path = '{file_path}'
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"✅ 成功解析JSON文件")
    print(f"📊 JSON数据类型: {type(data).__name__}")
except json.JSONDecodeError as e:
    print(f"❌ JSON解析失败: {e}")
    import sys
    sys.exit(1)
except Exception as e:
    print(f"❌ 读取文件失败: {e}")
    import sys
    sys.exit(1)
"""
    
    def execute_test_script(self, test_script, output_file=None):
        """执行测试脚本"""
        import tempfile
        
        logger.info("▶️ 执行测试脚本")
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_file_path = f.name
        
        try:
            # 执行测试脚本
            result = subprocess.run(['python', temp_file_path], capture_output=True, text=True)
            
            # 输出结果
            logger.info(f"测试结果:")
            logger.info(f"stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"stderr: {result.stderr}")
            
            # 保存结果到文件
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"stdout: {result.stdout}\nstderr: {result.stderr}\nreturncode: {result.returncode}")
            
            return result.returncode == 0
        finally:
            # 删除临时文件
            os.unlink(temp_file_path)

if __name__ == "__main__":
    # 测试脚本生成器
    generator = TestScriptGenerator()
    
    # 测试连接测试脚本生成
    test_error = {
        "type": "ConnectionError",
        "message": "Connection refused",
        "timestamp": "2025-11-28T09:45:30"
    }
    
    script = generator.generate_test_script(test_error)
    if script:
        print("生成的测试脚本:")
        print(script)
        
        # 执行测试脚本
        success = generator.execute_test_script(script)
        print(f"\n测试脚本执行结果: {'成功' if success else '失败'}")
