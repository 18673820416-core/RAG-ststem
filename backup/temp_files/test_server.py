#!/usr/bin/env python
# @self-expose: {"id": "test_server", "name": "Test Server", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Test Server功能"]}}
# -*- coding: utf-8 -*-
"""
测试HTTP服务器
"""

import http.server
import socketserver
import logging
import os

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'test_server.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_server')

PORT = 10809

class TestHandler(http.server.SimpleHTTPRequestHandler):
    """测试HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("测试服务器运行正常！".encode('utf-8'))


def start_test_server():
    """启动测试服务器"""
    try:
        logger.info(f"启动测试服务器，端口: {PORT}")
        
        # 创建TCP服务器实例
        httpd = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), TestHandler)
        logger.info(f"测试服务器已启动，监听: http://localhost:{PORT}")
        print(f"测试服务器已启动，监听: http://localhost:{PORT}")
        
        # 启动服务器
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("测试服务器正在关闭...")
        print("\n测试服务器正在关闭...")
        httpd.server_close()
        logger.info("测试服务器已成功关闭")
        print("测试服务器已成功关闭")
    except Exception as e:
        logger.error(f"测试服务器启动失败: {e}")
        print(f"测试服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    start_test_server()
