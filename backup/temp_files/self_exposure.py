# @self-expose: {"id": "self_exposure_parser", "name": "自我声明解析器", "type": "service", "version": "1.0.0", "needs": {"deps": ["os", "re", "json"], "resources": ["文件系统"]}, "provides": {"capabilities": ["自我声明解析", "多文件扫描", "声明统一管理", "JSON格式输出", "命令行工具支持"]}}
import os
import re
import json

class SelfExposureParser:
    def __init__(self):
        # 简化的正则表达式，匹配单行注释中的声明
        self.pattern = re.compile(r'#\s*@self-expose:\s*(\{.*?\})\s*$')
    
    def parse_file(self, file_path, max_lines=10):
        """
        解析单个文件的自我申明注释
        
        Args:
            file_path: 文件路径
            max_lines: 读取的最大行数
            
        Returns:
            dict: 解析后的自我申明数据，None表示未找到
        """
        try:
            # 尝试使用UTF-8编码打开文件，如果失败则跳过
            with open(file_path, 'r', encoding='utf-8') as f:
                for i in range(max_lines):
                    line = f.readline()
                    if not line:
                        break
                    
                    match = self.pattern.match(line.strip())
                    if match:
                        try:
                            return json.loads(match.group(1))
                        except json.JSONDecodeError:
                            return None
        except UnicodeDecodeError:
            # 忽略无法解码的文件
            return None
        except Exception as e:
            # 只打印非编码错误的其他异常
            print(f"解析文件 {file_path} 时出错: {e}")
        return None
    
    def collect_self_exposures(self, root_dir, output_file="self_exposures.json", max_lines=10):
        """
        收集所有文件的自我申明注释，集中存储到一个JSON文件中
        
        Args:
            root_dir: 要扫描的根目录
            output_file: 输出的JSON文件名
            max_lines: 每个文件读取的最大行数
            
        Returns:
            list: 收集到的所有自我申明数据
        """
        exposures = []
        
        # 遍历所有Python文件
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    exposure = self.parse_file(file_path, max_lines)
                    if exposure:
                        # 添加来源信息
                        exposure['source'] = {
                            'file': file_path.replace(root_dir, ''),
                            'full_path': file_path
                        }
                        exposures.append(exposure)
        
        # 保存到统一文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exposures, f, ensure_ascii=False, indent=2)
        
        print(f"成功收集 {len(exposures)} 个自我申明，保存到 {output_file}")
        return exposures

# 命令行工具支持
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python self_exposure.py collect <root_dir> [output_file]")
        print("  python self_exposure.py parse <file_path>")
        sys.exit(1)
    
    parser = SelfExposureParser()
    
    if sys.argv[1] == "collect":
        root_dir = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "self_exposures.json"
        parser.collect_self_exposures(root_dir, output_file)
    elif sys.argv[1] == "parse":
        file_path = sys.argv[2]
        exposure = parser.parse_file(file_path)
        if exposure:
            print(json.dumps(exposure, ensure_ascii=False, indent=2))
        else:
            print(f"未在文件 {file_path} 中找到自我申明")
    else:
        print(f"未知命令: {sys.argv[1]}")
        sys.exit(1)