#!/usr/bin/env python3
# @self-expose: {"id": "post_test", "name": "Post Test", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Post Test功能"]}}
# -*- coding: utf-8 -*-
"""
测试POST方法修复
"""

import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
from datetime import datetime

class TestHandler(BaseHTTPRequestHandler):
    """测试处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<h1>测试服务器</h1><p>GET请求成功</p>'.encode('utf-8'))
    
    def do_POST(self):
        """处理POST请求 - 直接从原文件复制的方法"""
        path = self.path.split('?')[0]  # 去除查询参数
        
        print(f"[测试服务器] 收到POST请求: {path}")
        
        # 处理聊天API请求
        if path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # 模拟聊天响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "response": "测试聊天响应",
                    "status": "success"
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f"处理聊天请求失败: {str(e)}")
        
        # 启动后端服务
        elif path == '/api/start-backend':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                port = data.get('port', 8888)
                
                print(f"[测试服务器] 启动后端服务请求，端口: {port}")
                
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': True,
                    'port': port,
                    'message': '后端服务启动请求已处理',
                    'result': '测试成功'
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f"启动后端服务失败: {str(e)}")
        else:
            self.send_error(404, "接口不存在")

def main():
    """主函数"""
    port = 10809  # 使用不同端口避免冲突
    
    print("🚀 测试服务器启动")
    print(f"🌐 测试地址: http://localhost:{port}")
    
    # 创建并启动服务器
    server = HTTPServer(('', port), TestHandler)
    
    print(f"✅ 测试服务器已启动在端口 {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 收到退出信号，正在关闭服务器...")
        server.shutdown()
        print("🛑 服务器已关闭")

if __name__ == '__main__':
    main()