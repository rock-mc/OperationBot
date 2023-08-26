import datetime
import json
import logging
import os
import time
from typing import Optional

import server_util
import config

logger = logging.getLogger(__name__)


def clear():
    try:
        os.remove('/tmp/server_close')
    except FileNotFoundError:
        pass


def say(msg: str):
    server_util.server_cmd(f'say {msg}')


def kick_all(reason: Optional[str] = None):
    cmd = f'kickall {reason}' if reason else 'kickall'
    server_util.server_cmd(cmd)

    with open('ops.json', 'r') as f:
        ops = json.load(f)
    for op in ops:
        cmd = f'kick {op["name"]} {reason}' if reason else f'kick {op["name"]}'
        server_util.server_cmd(cmd)


def stop(reason: str, count_down_sec: int = 10):
    if count_down_sec <= 0:
        raise ValueError('count_down_sec should be greater than 2')

    for count_down in reversed(range(0, count_down_sec + 1)):
        say(f'{reason}，倒數...{count_down}')
        time.sleep(1)

    kick_all()

    time.sleep(2)

    server_util.server_cmd('stop')
    server_util.wait_server_stop()


def backup_map(force: bool = False):
    backup_root = '/data/backup'
    mc_root = config.SERVER_ROOT

    now = datetime.datetime.now()

    date_mark = now.strftime("%Y-%m-%d")
    backup_path = f'{backup_root}/{datetime.datetime.today().weekday()}'

    if os.path.exists(f"{backup_path}/{date_mark}") and not force:
        # backup_path should not exist
        return
    os.system(f'touch {backup_path}/{date_mark}')

    stop('伺服器即將開始備份，準備關閉伺服器', count_down_sec=30)

    # rsync -auvz world/ /data/backup/qq/world/

    os.system(f'mkdir -p {backup_path}')

    backup_folders = ['world', 'world_nether', 'world_the_end']
    for backup_folder in backup_folders:
        backup_folder_path = f'{backup_path}/{backup_folder}'
        # print(backup_world_path)
        os.system(f'mkdir -p {backup_folder_path}')
        os.system(f'rsync -avh {mc_root}/{backup_folder}/ {backup_folder_path}')

    # delete old folder

    # for day in range(8, 15):
    #     old_day = datetime.datetime.now() - datetime.timedelta(days=day)
    #     old_day_folder = old_day.strftime('%Y-%m-%d')
    #     old_day_backup_path = f'{backup_root}/{old_day_folder}'
    #
    #     if not os.path.exists(old_day_backup_path):
    #         continue
    #
    #     os.system(f'rm -r {old_day_backup_path}')

    os.system('sudo reboot')
    time.sleep(30)


def clear_db():
    server_util.server_cmd('co purge t:60d')


def start(server_file: str):
    logger.info(f'start server: {server_file}')
    os.system(f'screen -S rock-server -d -m sh run_server.sh {server_file}')
    time.sleep(10)


if __name__ == '__main__':
    kick_all()
