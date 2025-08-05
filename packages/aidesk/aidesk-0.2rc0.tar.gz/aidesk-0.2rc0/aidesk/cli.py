import argparse
import logging
from .server import run_server
from .client.registration import SlaveRegistrar


def main():
    parser = argparse.ArgumentParser(description='启动aidesk服务')

    # 通用参数
    parser.add_argument('--host', default='localhost', help='服务绑定的主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务绑定的端口号')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--log-level', default='INFO', help='日志级别 (DEBUG, INFO, WARNING, ERROR)')

    # Slave模式参数
    parser.add_argument('--slave', action='store_true', help='以slave模式运行，注册到master')
    parser.add_argument('--master-url', help='master服务器的URL (当以slave模式运行时需要)')

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 如果是slave模式，启动注册器
    slave_registrar = None
    if args.slave:
        if not args.master_url:
            parser.error("当使用--slave选项时，必须指定--master-url")

        slave_registrar = SlaveRegistrar(
            master_url=args.master_url,
            slave_host=args.host,
            slave_port=args.port
        )
        slave_registrar.start()

    try:
        # 启动主服务器
        run_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    finally:
        # 确保在服务器关闭时停止注册器
        if slave_registrar:
            slave_registrar.stop()


if __name__ == '__main__':
    main()
