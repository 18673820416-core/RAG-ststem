# @self-expose: {"id": "generate_file_list", "name": "Python文件列表生成器", "type": "script", "version": "1.0.0", "needs": {"deps": ["os"], "resources": ["file_system_access"]}, "provides": {"capabilities": ["Python文件列表生成", "目录过滤", "文件过滤"]}}
import os

def generate_file_list():
    """生成过滤后的Python文件列表"""
    all_files = []
    # 使用os.walk遍历所有Python文件
    for root, dirs, files in os.walk('.'):
        # 过滤掉不需要的目录
        dirs[:] = [d for d in dirs if d not in ['myenv', 'myenv_stable', '.venv', '__pycache__', 'backup', 'tests', 'test', 'old_tests', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                # 过滤掉测试文件
                if not file.startswith('test_') and not file.startswith('check_'):
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
    
    # 将文件列表写入文件
    with open('python_files_list.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_files))
    
    print(f"生成了 {len(all_files)} 个文件的列表")

if __name__ == "__main__":
    generate_file_list()
