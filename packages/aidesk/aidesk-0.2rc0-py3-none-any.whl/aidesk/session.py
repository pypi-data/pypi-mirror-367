import time
from datetime import datetime
import os

from aidesk.utils import get_host_info
import logging

logger = logging.getLogger(__name__)
# 全局状态存储
server_state = {
    'start_time': datetime.now().isoformat(),
    'instances': {},  # 存储注册的实例信息
    'sessions': {},  # 存储用户会话
    'upload_dir': 'uploads',
    'generated_files_dir': 'generated_files'
}


def get_server_state():
    logger.info(f"server state: {server_state}")
    return server_state


def set_user_session(session_id, session_data):
    server_state['sessions'][session_id] = session_data


def set_master_state(port):
    # 获取并存储服务器信息
    hostname, ip_address = get_host_info()
    server_state['master_info'] = {
        'hostname': hostname,
        'ip': ip_address,
        'port': port,
        'start_time': server_state['start_time'],
        'last_ping': time.time()  # 主服务器自己的最后活动时间
    }


# 确保所需目录存在
os.makedirs(server_state['upload_dir'], exist_ok=True)
os.makedirs(server_state['generated_files_dir'], exist_ok=True)
