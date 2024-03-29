import os
import sys
import time
from typing import Optional

import schedule
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

import config
import discord
import server_cmd
import server_func
import server_util
from check_net import check_network_status

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
            return

        if time.time() < self.next_check_time:
            return
        self.next_check_time = time.time() + config.READ_LOG_TIME

        server_cmd.tps()
        server_cmd.online()

        time.sleep(1)

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


observer: Optional[Observer] = None


def init():
    global observer
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='logs', recursive=False)
    observer.start()


def destroy():
    global is_stopping
    global observer

    is_stopping = True

    observer.stop()
    observer.join()


no_net_time = 0
last_net_status = None


def check():
    if not config.ENABLE_CHECK_NETWORK:
        is_net_ok = True
    else:
        global last_net_status
        global no_net_time
        is_net_ok = check_network_status()

        if is_net_ok:
            no_net_time = 0
            if last_net_status is None or not last_net_status:
                logger.info('連線狀態: 正常')
                last_net_status = True
        else:
            if last_net_status is None or last_net_status:
                last_net_status = False
                logger.info('連線狀態: ConnectionError')

            if no_net_time == 0:
                no_net_time = time.time()
            elif time.time() - no_net_time > config.WAIT_NETWORK_MINUTES * server_util.MINUTE:
                server_cmd.stop('連線狀態: ConnectionError')
                os.system('sudo shutdown -h now')

                sys.exit()

    if not is_net_ok:
        logger.info('The network is not ok, skip check server status.')
    else:
        server_running, _ = server_util.is_server_running()
        if not server_running:

            logger.info('The server is not running! start server.')

            is_updated, server_file = server_func.get_new_server_file()

            if not is_updated:
                server_cmd.start(server_file)


def run_pending():
    schedule.run_pending()
