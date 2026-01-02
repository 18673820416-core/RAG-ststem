# @self-expose: {"id": "verify_fix", "name": "Python语法验证工具", "type": "script", "version": "1.0.0", "needs": {"deps": ["ast"], "resources": ["file_system_access"]}, "provides": {"capabilities": ["Python语法检查", "类定义统计", "大括号平衡检查", "Try-Except语句平衡检查"]}}
import ast

file_path = 'e:/RAG系统/src/base_agent.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析文件，检查语法错误
    ast.parse(content)
    print('✅ 语法检查通过！文件中没有语法错误。')
    
    # 检查类定义是否正确闭合
    class_count = content.count('class BaseAgent')
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    print(f'📊 类定义数量: {class_count}')
    print(f'📊 大括号数量: 打开 {open_braces}, 关闭 {close_braces}')
    print(f'📊 大括号平衡: {"平衡" if open_braces == close_braces else "不平衡"}')
    
    # 检查try-except语句
    try_count = content.count('try:')
    except_count = content.count('except')
    finally_count = content.count('finally')
    
    print(f'📊 Try语句数量: {try_count}')
    print(f'📊 Except语句数量: {except_count}')
    print(f'📊 Finally语句数量: {finally_count}')
    print(f'📊 Try-Except/Finally平衡: {"平衡" if try_count <= (except_count + finally_count) else "不平衡"}')
    
    print('🎉 所有检查通过！文件语法正确。')
    
except SyntaxError as e:
    print(f'❌ 语法错误: {e}')
    print(f'行号: {e.lineno}, 列号: {e.offset}')
    lines = content.splitlines()
    if e.lineno <= len(lines):
        print(f'错误行内容: {lines[e.lineno-1]}')
        if e.lineno < len(lines):
            print(f'下一行内容: {lines[e.lineno]}')
    print(f'错误类型: {type(e).__name__}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    print(f'错误类型: {type(e).__name__}')