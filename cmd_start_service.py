import importlib
import os
import sys
import time
import traceback
from types import ModuleType
from typing import Optional

import schedule

import config
import server_util

os.chdir(config.SERVER_ROOT)

logger = server_util.get_logger(__name__)


def check_server_cmd():
    global server_cmd
    global server_service

    if server_cmd.check_command_exists(server_cmd.SERVER_STOP):
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


if __name__ == '__main__':

    logger.info('磐石維運機器人 v ' + config.version + ' 啟動')

    server_service: Optional[ModuleType] = None
    server_cmd: Optional[ModuleType] = None

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

    schedule.every().monday.at("05:00").do(server_cmd.backup_map)
    schedule.every().friday.at("05:00").do(server_cmd.backup_map)

    schedule.every().day.at("05:25").do(server_cmd.clear_db)

    schedule.every(10).seconds.do(check_server_cmd)

    schedule.every(10).seconds.do(server_service.check)

    while True:
        if first_run:
            first_run = False
        else:
            time.sleep(1)

        schedule.run_pending()
