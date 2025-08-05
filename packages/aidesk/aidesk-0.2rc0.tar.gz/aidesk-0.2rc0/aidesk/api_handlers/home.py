import json
import os
import time

from ..utils import load_template, format_timestamp


def handle_index(handler, is_authenticated):
    """Handle the main index page"""
    template = load_template('index.html')
    content = template
    # 替换模板变量
    # content = template.replace('{{ master_hostname }}', master_info['hostname'])
    # content = content.replace('{{ master_ip }}', master_info['ip'])
    # content = content.replace('{{ master_port }}', str(master_info['port']))
    # content = content.replace('{{ master_start_time }}', format_timestamp(master_info['start_time']))

    handler.send_response(200)
    handler.send_header('Content-type', 'text/html')
    handler.end_headers()
    handler.wfile.write(content.encode('utf-8'))


def handle_static_file(self):
    """处理静态文件请求"""
    # 提取静态文件路径
    static_path = self.path[len('/static/'):]
    file_path = os.path.join(os.path.dirname(__file__), '..', 'static', static_path)

    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        self.send_error(404, "File not found")
        return

    # 确定MIME类型
    if file_path.endswith('.css'):
        mime_type = 'text/css'
    elif file_path.endswith('.js'):
        mime_type = 'text/javascript'
    elif file_path.endswith('.png'):
        mime_type = 'image/png'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    else:
        mime_type = 'application/octet-stream'

    # 发送文件内容
    try:
        with open(file_path, 'rb') as f:
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.end_headers()
            self.wfile.write(f.read())
    except Exception as e:
        self.send_error(500, f"Error serving file: {str(e)}")


def handle_health_check(self, server_state):
    """处理健康检查请求"""
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response = {
        'status': 'healthy',
        'timestamp': format_timestamp(time.time()),
        'start_time': server_state['start_time']
    }
    self.wfile.write(json.dumps(response).encode('utf-8'))
