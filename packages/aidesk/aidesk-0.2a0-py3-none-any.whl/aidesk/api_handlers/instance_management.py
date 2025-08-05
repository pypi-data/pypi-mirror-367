import cgi
import json
import time
from ..utils import load_template, is_authenticated, format_timestamp

def handle_manage_instances_page(self, server_state):
    """处理实例管理页面请求"""
    # 检查认证状态
    session_id = self.headers.get('Cookie', '').split('session_id=')[-1].split(';')[0]
    if not is_authenticated(server_state, session_id):
        # 未认证，重定向到登录页面
        self.send_response(302)
        self.send_header('Location', '/login')
        self.end_headers()
        return
    
    template = load_template('manage-instances.html')
    
    # 准备主服务器信息
    master_info = server_state['master_info']
    master_html = f"""
    <tr class="master-row">
        <td>Master</td>
        <td>{master_info['hostname']}</td>
        <td>{master_info['ip']}</td>
        <td>{master_info['port']}</td>
        <td>{format_timestamp(master_info['start_time'])}</td>
        <td>Active</td>
        <td>N/A</td>
    </tr>
    """
    
    # 准备实例列表HTML
    instances_html = ""
    for instance_id, info in server_state['instances'].items():
        status = "Active" if (time.time() - info['last_ping']) < 300 else "Inactive"
        instances_html += f"""
        <tr>
            <td>Slave</td>
            <td>{info['hostname']}</td>
            <td>{info['ip']}</td>
            <td>{info['port']}</td>
            <td>{format_timestamp(info['start_time'])}</td>
            <td>{status}</td>
            <td>
                <button class="delete-btn" data-instance-id="{instance_id}">Delete</button>
            </td>
        </tr>
        """
    
    # 替换模板变量
    content = template.replace('{{ master_row }}', master_html)
    content = content.replace('{{ instances_rows }}', instances_html)
    
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(content.encode('utf-8'))

def handle_register_instance(self, server_state):
    """处理实例注册请求"""
    # 解析表单数据
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    form_data = cgi.parse_qs(post_data)
    
    # 提取实例信息
    hostname = form_data.get('hostname', ['unknown'])[0]
    ip = form_data.get('ip', ['unknown'])[0]
    port = form_data.get('port', ['0'])[0]
    start_time = form_data.get('start_time', [time.time()])[0]
    
    # 创建实例ID (ip:port)
    instance_id = f"{ip}:{port}"
    
    # 存储实例信息
    server_state['instances'][instance_id] = {
        'hostname': hostname,
        'ip': ip,
        'port': port,
        'start_time': start_time,
        'registered_time': time.time(),
        'last_ping': time.time()
    }
    
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response = {
        'success': True,
        'message': 'Instance registered successfully',
        'instance_id': instance_id
    }
    self.wfile.write(json.dumps(response).encode('utf-8'))

def handle_ping_instance(self, server_state):
    """处理实例心跳请求"""
    # 解析表单数据
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    form_data = cgi.parse_qs(post_data)
    
    instance_id = form_data.get('instance_id', [''])[0]
    
    if not instance_id or instance_id not in server_state['instances']:
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'success': False,
            'message': 'Instance not found'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    # 更新最后心跳时间
    server_state['instances'][instance_id]['last_ping'] = time.time()
    
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response = {
        'success': True,
        'message': 'Ping received'
    }
    self.wfile.write(json.dumps(response).encode('utf-8'))

def handle_get_instances(self, server_state):
    """处理获取实例列表请求"""
    # 检查认证状态
    session_id = self.headers.get('Cookie', '').split('session_id=')[-1].split(';')[0]
    if not is_authenticated(server_state, session_id):
        self.send_error(401, "Authentication required")
        return
    
    # 准备实例数据
    instances_data = {}
    for instance_id, info in server_state['instances'].items():
        instances_data[instance_id] = {
            'hostname': info['hostname'],
            'ip': info['ip'],
            'port': info['port'],
            'start_time': info['start_time'],
            'registered_time': info['registered_time'],
            'last_ping': info['last_ping'],
            'status': "Active" if (time.time() - info['last_ping']) < 300 else "Inactive"
        }
    
    # 添加主服务器信息
    master_info = server_state['master_info']
    response_data = {
        'master': {
            'hostname': master_info['hostname'],
            'ip': master_info['ip'],
            'port': master_info['port'],
            'start_time': master_info['start_time'],
            'status': 'Active'
        },
        'instances': instances_data
    }
    
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(response_data).encode('utf-8'))

def handle_delete_instance(self, server_state, instance_id):
    """处理删除实例请求"""
    # 检查认证状态
    session_id = self.headers.get('Cookie', '').split('session_id=')[-1].split(';')[0]
    if not is_authenticated(server_state, session_id):
        self.send_error(401, "Authentication required")
        return
    
    if instance_id not in server_state['instances']:
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'success': False,
            'message': 'Instance not found'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    # 删除实例
    del server_state['instances'][instance_id]
    
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    response = {
        'success': True,
        'message': f'Instance {instance_id} deleted successfully'
    }
    self.wfile.write(json.dumps(response).encode('utf-8'))
