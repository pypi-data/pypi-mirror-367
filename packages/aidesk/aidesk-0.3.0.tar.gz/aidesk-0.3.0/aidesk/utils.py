import os
import socket
import uuid
import time
import hashlib
from datetime import datetime
import json
import hashlib
from pathlib import Path

# Configuration
CONFIG_PATH = 'aidesk_config.json'
SESSIONS_PATH = 'aidesk_sessions.json'
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def load_template(template_name):
    """Load an HTML template file"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<html><body>Template {template_name} not found</body></html>"


def get_config():
    """Load configuration or create default if not exists"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Create default config with sample user (username: admin, password: admin)
    default_password = os.getenv("AIDESK_ADMIN_PASSWORD", "admin")
    default_config = {
        'users': {
            'admin': hashlib.sha256(default_password.encode()).hexdigest()
        }
    }

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)

    return default_config


def load_sessions():
    """Load sessions from file"""
    if os.path.exists(SESSIONS_PATH):
        try:
            with open(SESSIONS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_sessions(sessions):
    """Save sessions to file"""
    with open(SESSIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2)


def get_session_id(headers):
    """Extract session ID from cookies"""
    if 'Cookie' in headers:
        cookies = headers['Cookie'].split(';')
        for cookie in cookies:
            if cookie.strip().startswith('session_id='):
                return cookie.split('=')[1]
    return None


def validate_session(session_id):
    """Check if session is valid"""
    if not session_id:
        return False

    sessions = load_sessions()
    return session_id in sessions and sessions[session_id].get('valid', False)


def get_host_info():
    """获取主机名和IP地址"""
    hostname = socket.gethostname()
    try:
        # 获取非本地回环地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = socket.gethostbyname(hostname)
    return hostname, ip_address


def sanitize_filename(filename):
    """清理文件名，防止路径遍历攻击"""
    return os.path.basename(filename).replace('/', '').replace('\\', '')


def generate_session_id():
    """生成唯一的会话ID"""
    return str(uuid.uuid4())


def hash_password(password):
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def is_authenticated(server_state, session_id):
    """检查会话是否有效"""
    if not session_id:
        return False
    return session_id in server_state['sessions']


def format_timestamp(timestamp):
    """格式化时间戳为人类可读格式"""
    try:
        if isinstance(timestamp, float):
            dt = datetime.fromtimestamp(timestamp)
        else:
            dt = datetime.fromisoformat(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)
