import os
import subprocess
import time

import config
import server_util

logger = server_util.get_logger(__name__)

os.chdir(config.SERVER_ROOT)

if __name__ == '__main__':
    subprocess.Popen("kill $(ps aux | grep 'cmd_start_service' | grep -v grep | awk '{print $2}')", shell=True)
    time.sleep(1)
    subprocess.Popen(f'python3 operation_bot/cmd_start_service.py', shell=True)

    logger.info('update service success')