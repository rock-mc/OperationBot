import datetime
import logging
import os
import re
import threading
import time
from typing import List

import config

logger = logging.getLogger(__name__)

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def send_server_command(command) -> None:
    os.system(f'screen -S rock-server -p 0 -X eval \'stuff "{command}"\\015\'')


def server_cmd(command) -> None:
    logger.info(f'Execute command: {command}')
    send_server_command(command)


def is_server_running() -> (bool, str):
    check_result = os.popen('ps aux | grep nogui').read()
    return 'paper' in check_result, check_result


last_log_index = 0


def get_server_log() -> List[str]:
    global last_log_index

    filename = 'logs/latest.log'

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        if len(lines) < last_log_index:
            last_log_index = 0
        lines = lines[last_log_index:]

    lines = [x.strip() for x in lines if x.strip() != '']

    return lines


def wait_server_stop() -> None:
    start_time = time.time()

    for i in range(300):
        end_time = time.time()
        if end_time - start_time >= 3 * 60:
            # 超過三分鐘還沒關機，啟動強制關閉程序
            server_running, _ = is_server_running()
            if server_running:
                os.system('sudo reboot')
            else:
                # server is closed
                break

        server_running, _ = is_server_running()
        if server_running:
            if i % 5 == 0:
                logger.info('Wait for server close..')
        else:
            logger.info('server is closed!')
            break
        time.sleep(1)


def wait_service_stop() -> None:
    for i in range(600):
        server_running, check_result = is_server_running()
        if server_running or 'start_service.py' in check_result:
            if i % 5 == 0:
                logger.info('Wait for service close..')
        else:
            logger.info('service is closed!')
            break

        time.sleep(1)


def is_in_time_range(start, end):
    now = datetime.datetime.now()

    if start <= end:
        return start <= now <= end
    else:
        return start <= now or now <= end


def get_time_range(start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> \
        (datetime.datetime, datetime.datetime):
    this_year = datetime.datetime.now().year
    this_month = datetime.datetime.now().month
    this_day = datetime.datetime.now().day

    start = datetime.datetime(this_year, this_month, this_day, start_hour, start_minute)
    end = datetime.datetime(this_year, this_month, this_day, end_hour, end_minute)
    return start, end


detect_server_lock = threading.Lock()


def get_server_status() -> dict:
    global detect_server_lock

    system_start_time = None
    database_error = False

    tps_pattern = r'TPS from last 1m, 5m, 15m: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)'
    online_pattern = r'目前有 (\d+) 個玩家在線'

    with detect_server_lock:
        server_logs = get_server_log()
        for server_log in server_logs:
            if '>' in server_log:
                continue

            matches = re.findall(tps_pattern, server_log)
            if matches:
                tps_numbers = [float(matches[0][i]) for i in range(3)]

            matches = re.findall(online_pattern, server_log)
            if matches:
                online_player_count = int(matches[0][0])

            if 'Done' in server_log and 'For help' in server_log:
                if system_start_time is None:
                    system_start_time = time.time()

            if 'java.sql.SQLTransientConnectionException' in server_log:
                database_error = True

        return {
            'system_start_time': system_start_time,
            'database_error': database_error,
            'tps': tps_numbers,
            'online_player_count': online_player_count
        }


def get_logger(name: str):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s',
                        datefmt='%m.%d %H:%M:%S')
    return logging.getLogger(name)


if __name__ == '__main__':
    os.chdir(config.SERVER_ROOT)

    logger = get_logger('test')

    for i in range(25):
        print(get_server_status())
        time.sleep(1)
