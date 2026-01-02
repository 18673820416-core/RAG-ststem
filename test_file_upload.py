import requests

# 测试文件上传
url = "http://localhost:10808/api/upload"
files = {'file': open('test_upload.txt', 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")
