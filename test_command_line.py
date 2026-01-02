# @self-expose: {"id": "test_command_line", "name": "Test Command Line", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Command Line功能"]}}
import requests
import json

# 测试命令行工具的Python脚本
url = "http://localhost:10808/api/chatroom/message"
headers = {
    "Content-Type": "application/json"
}

# 测试消息：直接请求执行命令行工具
# 这里我们使用一个简单的命令，查看当前目录下的文件
data = {
    "message": "请执行命令 'ls -la' 查看当前目录下的文件",
    "agent_id": "base_agent"
}

print("发送请求...")
response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"响应状态码: {response.status_code}")
print(f"响应内容: {response.text}")
