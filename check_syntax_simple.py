# @self-expose: {"id": "check_syntax_simple", "name": "Check Syntax Simple", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Syntax Simple功能"]}}
import ast

file_path = 'e:/RAG系统/src/base_agent.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ast.parse(content)
    print('语法正确')
except SyntaxError as e:
    print(f'语法错误: {e}')
    print(f'行号: {e.lineno}, 列号: {e.offset}')
    lines = content.splitlines()
    if e.lineno <= len(lines):
        print(f'错误行内容: {lines[e.lineno-1]}')
        if e.lineno < len(lines):
            print(f'下一行内容: {lines[e.lineno]}')
    print(f'错误类型: {type(e).__name__}')
except Exception as e:
    print(f'其他错误: {e}')
    print(f'错误类型: {type(e).__name__}')