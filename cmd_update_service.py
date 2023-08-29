import os
import subprocess
import time

import config
import server_util
import server_cmd

logger = server_util.get_logger(__name__)

os.chdir(config.SERVER_ROOT)

if __name__ == '__main__':
    os.system(f'touch {server_cmd.SERVER_UPDATE}')

    logger.info('update service success')