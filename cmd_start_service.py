import datetime
import os
import sys
import time

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

import server_cmd
import server_func
import server_util
from discord import discord_bot

logger = server_util.get_logger(__name__)

is_stopping = False
is_wait_stop = False
is_database_explode = False

parent = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(parent)
os.chdir(parent)


class LogHandler(FileSystemEventHandler):

    def on_modified(self, event: FileModifiedEvent):
        global is_stopping
        global is_wait_stop
        global is_database_explode

        logger.info(f'log file modified: {event.src_path}')

        if not str(event.src_path).endswith('latest.log'):
            return

        if is_stopping:
            if not is_wait_stop:
                is_wait_stop = True
                server_util.wait_server_stop()
            return

        detect_log_result = server_util.detect_server()
        if False and detect_log_result['is_duplicate_uuid']:
            server_cmd.stop('偵測到問題實體，伺服器重新啟動')
        if detect_log_result['is_lag']:
            server_cmd.stop('偵測到 lag 問題，伺服器重新啟動')
        if detect_log_result['database_error'] and not is_database_explode:
            is_database_explode = True
            discord_bot.post(
                content="資料庫爆炸了，<@694182416583098470> 請趕快處理")


wait_player_max_min = 10
check_time_sec = 10
check_server_status_time_sec = 60

backup_day = [
    # Monday and friday
    0, 4
]

if __name__ == '__main__':

    # disable log observer
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='logs', recursive=False)
    observer.start()

    server_cmd.clear()

    log_check = list()
    log_count = None
    check_time_start = time.time()
    save_map = False
    update_list = []
    first_run = True

    no_player_time = None

    run_clear_db_date = set()
    while True:
        if not first_run:
            time.sleep(check_time_sec)
        first_run = False

        if os.path.exists('/tmp/server_close'):
            logger.info('stop service')
            server_cmd.stop('老大下指令關閉伺服器囉')

            sys.exit()

        server_running, _ = server_util.is_server_running()
        if server_running:
            if time.time() - check_time_start < check_server_status_time_sec:
                continue

            # if datetime.datetime.now().minute == 0:
            #     command.say(
            #         f'現在時間 {datetime.datetime.now().hour} 點 {datetime.datetime.now().minute} 分，磐石維運機器人 v {config.version} 關心您')

            check_time_start = time.time()

            start_time, end_time = server_util.get_time_range(5, 0, 5, 5)

            if server_util.is_in_time_range(start_time, end_time):
                if datetime.datetime.today().weekday() in backup_day:
                    server_cmd.backup_map()

            start_time, end_time = server_util.get_time_range(5, 25, 5, 30)

            today = datetime.date.today()
            if server_util.is_in_time_range(start_time, end_time) and today not in run_clear_db_date:
                run_clear_db_date.add(today)

                server_cmd.clear_db()

        else:
            logger.info('The server is not running! start server.')

            is_updated, server_file = server_func.get_new_server_file()

            if not is_updated:
                server_cmd.start(server_file)

            check_time_start = time.time()
