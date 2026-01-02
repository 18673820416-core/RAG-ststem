# @self-expose: {"id": "check_db", "name": "Check Db", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Check Db功能"]}}
import sqlite3
import os

# 连接数据库
conn = sqlite3.connect('data/rag_memory.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'  {table[0]}')

# 检查每个表的记录数
print('\n各表记录数:')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'{table[0]} 表记录数: {count}')

# 检查数据库文件大小
db_size = os.path.getsize('data/rag_memory.db')
print(f'\n数据库文件大小: {db_size:,} 字节 ({db_size/1024/1024:.2f} MB)')

conn.close()