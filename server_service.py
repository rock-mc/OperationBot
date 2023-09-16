import datetime
import os
import time
from typing import Optional

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

import config
import discord
import server_cmd
import server_func
import server_util

logger = server_util.get_logger(__name__)

is_stopping = False
is_database_explode = False

os.chdir(config.SERVER_ROOT)


class LogHandler(FileSystemEventHandler):
    next_check_time = time.time() + config.READ_LOG_TIME

    def on_modified(self, event: FileModifiedEvent):
        global is_stopping
        global is_database_explode

        if not str(event.src_path).endswith('latest.log'):
            return

        if is_stopping:
            server_util.wait_server_stop()
            return

        if time.time() < self.next_check_time:
            return
        self.next_check_time = time.time() + config.READ_LOG_TIME

        server_cmd.tps()
        server_cmd.online()

        server_status = server_util.get_server_status()

        if server_status['tps'][0] < config.TPS_LAG_THRESHOLD:
            server_cmd.say('偵測到 lag 問題，請停止飛行、使用大量紅石等動作')

        if server_status['tps'][0] < config.TPS_LAG_THRESHOLD and server_status['tps'][1] < config.TPS_LAG_THRESHOLD:
            # it means the server is lagging for 5 minutes
            server_cmd.stop('持續偵測到 lag 問題，伺服器重新啟動')
        if server_status['database_error'] and not is_database_explode:
            is_database_explode = True
            # mention ops in discord
            try:
                if discord.enabled:
                    discord.discord_bot.post(
                        content=f"資料庫爆炸了，<@{config.DISCORD_OP_USER_ID}> 請趕快處理")
            except Exception as e:
                logger.error(e)


wait_player_max_min = 10
check_server_status_time_sec = 60

backup_day = [
    # Monday and friday
    0, 4
]

observer: Optional[Observer] = None


def init():
    global observer
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='logs', recursive=False)
    observer.start()


def destroy():

    global is_stopping

    is_stopping = True

    observer.stop()
    observer.join()


def check():
    server_running, _ = server_util.is_server_running()
    if not server_running:

        logger.info('The server is not running! start server.')

        is_updated, server_file = server_func.get_new_server_file()

        if not is_updated:
            server_cmd.start(server_file)


run_clear_db_date = set()


def schedule():
    global run_clear_db_date

    start_time, end_time = server_util.get_time_range(
        5, 0,
        5, 5)

    if server_util.is_in_time_range(start_time, end_time):
        if datetime.datetime.today().weekday() in backup_day:
            server_cmd.backup_map()

    start_time, end_time = server_util.get_time_range(
        5, 25,
        5, 30)

    today = datetime.date.today()
    if server_util.is_in_time_range(start_time, end_time) and today not in run_clear_db_date:
        run_clear_db_date.add(today)

        server_cmd.clear_db()
