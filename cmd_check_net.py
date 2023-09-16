import subprocess
import time

import server_util
from check_net import check_network_status

logger = server_util.get_logger(__name__)

if __name__ == '__main__':
    last_state = None

    no_net_time = 0

    wait_time = 2
    while True:
        if last_state is not None:
            time.sleep(max(0, wait_time - (end_time - start_time)))

        start_time = time.time()
        is_net_ok = check_network_status()
        end_time = time.time()

        if is_net_ok:
            no_net_time = 0
            if last_state == 'ok':
                continue
            last_state = 'ok'
            logger.info('連線狀態: 正常')
        else:
            if last_state == 'error':
                continue
            last_state = 'error'
            logger.info('連線狀態: ConnectionError')

            if no_net_time == 0:
                no_net_time = time.time()
            elif time.time() - no_net_time > 5 * server_util.MINUTE:
                logger.info('連線狀態: 連線中斷超過 5 分鐘，關閉主機。')
                subprocess.run(["shutdown", "-s"])


