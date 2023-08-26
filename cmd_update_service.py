import os
import subprocess
import time

import config
import server_util

logger = server_util.get_logger(__name__)

os.chdir(config.SERVER_ROOT)

if __name__ == '__main__':
    subprocess.Popen("kill $(ps aux | grep 'python3' | grep -v grep | awk '{print $2}')")
    time.sleep(1)
    subprocess.Popen(f'python3 operation_bot/cmd_start_service.py')

    logger.info('update service success')