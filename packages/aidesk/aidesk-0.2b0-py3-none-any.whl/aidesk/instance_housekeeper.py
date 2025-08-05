import threading
import time


def cleanup_inactive_instances(server_state_callback, interval=300):
    """定期清理不活跃的实例"""
    while True:
        time.sleep(interval)
        now = time.time()
        inactive_threshold = 300  # 5分钟无响应视为不活跃
        to_remove = []
        server_state = server_state_callback()
        for instance_id, info in server_state['instances'].items():
            if now - info['last_ping'] > inactive_threshold:
                to_remove.append(instance_id)

        for instance_id in to_remove:
            del server_state['instances'][instance_id]
            print(f"Removed inactive instance: {instance_id}")


def hook_state_for_cleanup(server_state_callback):
    cleanup_thread = threading.Thread(
        target=cleanup_inactive_instances,
        args=(server_state_callback,),
        daemon=True
    )
    cleanup_thread.start()
