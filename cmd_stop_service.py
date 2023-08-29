import os

import server_util
import server_cmd

logger = server_util.get_logger(__name__)

if __name__ == '__main__':
    os.system(f'touch {server_cmd.SERVER_CLOSE}')

    server_util.wait_service_stop()

