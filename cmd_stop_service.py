import logging
import os
import server_util

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%m.%d %H:%M:%S')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    os.system('touch /tmp/server_close')

    server_util.wait_service_stop()

