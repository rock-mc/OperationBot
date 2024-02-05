import datetime
import importlib
import os
import sys
import time
import traceback
from types import ModuleType
from typing import Optional, List

import config
import server_util

os.chdir(config.SERVER_ROOT)

logger = server_util.get_logger(__name__)

if __name__ == '__main__':

    server_service: Optional[ModuleType] = None
    logger.info('磐石維運機器人 v ' + config.version + ' 啟動')

    first_run = True

    next_check_service_time = 0

    try:
        server_cmd = importlib.import_module('server_cmd')
        server_cmd.clear()
    except Exception as e:
        logger.error(e)
        traceback.print_exc(file=sys.stdout)
        sys.exit()
    else:
        logger.info('server_cmd is loaded')

    try:
        server_service = importlib.import_module('server_service')
        server_service.init()
    except Exception as e:
        logger.error(e)
        traceback.print_exc(file=sys.stdout)
        sys.exit()
    else:
        logger.info('server_service is loaded')

    checked_time: List[str] = []

    while True:
        if not first_run:
            time.sleep(10)
        first_run = False

        if server_cmd.check_command_exists(server_cmd.SERVER_CLOSE):
            logger.info('stop service')

            server_service.destroy()

            server_cmd.stop('老大下指令關閉伺服器囉')

            sys.exit()

        if server_cmd.check_command_exists(server_cmd.SERVER_UPDATE):
            logger.info('update service')
            server_cmd.say('老大下指令更新磐石機器人囉')

            update_error = False

            try:
                new_server_cmd = importlib.reload(server_cmd)
            except Exception as e:
                update_error = True
                logger.error(e)
                server_cmd.say('server_cmd 更新失敗')
            else:
                server_cmd = new_server_cmd
                server_cmd.say('server_cmd 更新完成')

            try:
                new_service = importlib.reload(server_service)
            except Exception as e:
                update_error = True
                logger.error(e)
                server_cmd.say('service 更新失敗')
            else:
                server_service = new_service

                server_service.destroy()
                server_service.init()

                server_cmd.say('service 更新完成')

            if update_error:
                server_cmd.say('磐石機器人更新失敗，請手動更新')
            else:
                server_cmd.say('磐石機器人更新完成')

        # check schedule time every minute
        current_time = datetime.datetime.now().strftime('%M')
        if current_time not in checked_time:
            checked_time.append(current_time)
            while len(checked_time) > 10:
                checked_time.pop(0)

            server_service.run_pending()

        server_service.check()
