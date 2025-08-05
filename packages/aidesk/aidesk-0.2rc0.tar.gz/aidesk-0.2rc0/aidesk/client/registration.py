import time
import requests
import threading
import socket
from datetime import datetime
from ..utils import get_host_info
import logging

logger = logging.getLogger(__name__)


class SlaveRegistrar:
    def __init__(self, master_url, slave_host=None, slave_port=None, register_interval=30):
        """
        初始化slave注册器

        :param master_url: master服务器的URL，如"http://localhost:8000"
        :param slave_host: slave的主机地址，默认自动获取
        :param slave_port: slave的端口号
        :param register_interval: 心跳发送间隔（秒）
        """
        self.master_url = master_url.rstrip('/')
        self.slave_host = slave_host or get_host_info()['ip']
        self.slave_port = slave_port
        self.register_interval = register_interval
        self.registration_success = False
        self.instance_id = f"{self.slave_host}:{self.slave_port}"
        self.start_time = datetime.now().isoformat()
        self.registration_thread = None
        self.running = False

    def start(self):
        """启动注册和心跳线程"""
        if not self.slave_port:
            raise ValueError("必须指定slave的端口号")

        self.running = True
        self.registration_thread = threading.Thread(
            target=self._registration_loop,
            daemon=True,
            name="slave-registration"
        )
        self.registration_thread.start()
        logger.info(f"开始向master {self.master_url} 注册slave实例 {self.instance_id}")

    def stop(self):
        """停止注册和心跳线程"""
        self.running = False
        if self.registration_thread:
            self.registration_thread.join()
        logger.info(f"已停止向master注册slave实例 {self.instance_id}")

    def _registration_loop(self):
        """注册和心跳循环"""
        # 立即尝试注册
        self._register()

        # 定期发送心跳
        while self.running:
            if self.registration_success:
                self._send_heartbeat()
            else:
                # 如果注册失败，重试注册
                self._register()

            time.sleep(self.register_interval)

    def _register(self):
        """向master注册当前slave实例"""
        try:
            # 获取当前slave的信息
            host_info = get_host_info()

            data = {
                "hostname": host_info['hostname'],
                "ip": self.slave_host,
                "port": self.slave_port,
                "start_time": self.start_time
            }

            response = requests.post(
                f"{self.master_url}/api/instances/register",
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.registration_success = True
                    logger.info(f"Slave实例 {self.instance_id} 成功注册到master")
                    return True
                else:
                    logger.warning(f"注册失败: {result.get('message', '未知错误')}")
            else:
                logger.warning(f"注册请求失败，状态码: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"注册到master时发生错误: {str(e)}")
        except Exception as e:
            logger.error(f"注册过程中发生意外错误: {str(e)}")

        self.registration_success = False
        return False

    def _send_heartbeat(self):
        """向master发送心跳信号"""
        try:
            response = requests.post(
                f"{self.master_url}/api/instances/ping",
                data={"instance_id": self.instance_id},
                timeout=10
            )

            if response.status_code != 200:
                logger.warning(f"心跳发送失败，状态码: {response.status_code}")
                self.registration_success = False
            else:
                # 心跳成功
                pass

        except requests.exceptions.RequestException as e:
            logger.error(f"发送心跳时发生错误: {str(e)}")
            self.registration_success = False
