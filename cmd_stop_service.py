import os

import server_util

logger = server_util.get_logger(__name__)

if __name__ == '__main__':
    os.system('touch /tmp/server_close')

    server_util.wait_service_stop()

