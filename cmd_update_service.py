import os
import time

import server_util
import config

logger = server_util.get_logger(__name__)

os.chdir(config.SERVER_ROOT)

if __name__ == '__main__':
    os.system("kill $(ps aux | grep 'start_service.py' | grep -v grep | awk '{print $2}')")
    time.sleep(3)
    os.system('python3 operation_bot/cmd_start_service.py &')

    logger.info('update service success')