# @self-expose: {"id": "check_file", "name": "Check File", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check File功能"]}}
with open('e:/RAG系统/src/base_agent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f'总行数: {len(lines)}')
    
    # 查看报错的行
    error_lines = [1296, 1303, 1361, 1372, 1374, 1375]
    for line_num in error_lines:
        if line_num <= len(lines):
            print(f'第{line_num}行内容: {repr(lines[line_num-1].rstrip())}')
        else:
            print(f'第{line_num}行不存在')