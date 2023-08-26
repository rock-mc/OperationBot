import datetime
import logging
import os
import threading
import time
import uuid
from typing import List

import config

logger = logging.getLogger(__name__)


def send_server_command(command) -> None:
    os.system(f'screen -S rock-server -p 0 -X eval \'stuff "{command}"\\015\'')


def server_cmd(command) -> List[str]:
    logger.info(f'Execute command: {command}')
    send_server_command(command)


def is_server_running() -> (bool, str):
    check_result = os.popen('ps aux | grep nogui').read()
    return 'paper' in check_result, check_result


last_log_size = 0


def get_server_log() -> List[str]:
    global last_log_size

    filename = 'logs/latest.log'

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines if x.strip() != '']

    for line in lines:
        logger.info(line)

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


next_check_time = 0

detect_server_lock = threading.Lock()


def detect_server(test: bool = False) -> dict:
    global detect_server_lock
    global next_check_time

    if test:
        random_id = uuid.uuid4().hex[:5]
        logger.info(f'id: {random_id}')

    joined_count = 0
    left_count = 0
    is_duplicate_uuid = False
    system_start_time = None
    is_lag = False
    database_error = False

    if time.time() < next_check_time:
        if test:
            logger.info(f'wait: {random_id}')
        return {
            'is_lag': is_lag,
            'system_start_time': system_start_time,
            'joined_count': joined_count,
            'left_count': left_count,
            'is_duplicate_uuid': is_duplicate_uuid,
            'database_error': database_error}
    next_check_time = time.time() + config.READ_LOG_TIME

    with detect_server_lock:

        if test:
            logger.info(f'read file: {random_id}')
        else:
            server_logs = get_server_log()
            for server_log in server_logs:
                if '>' in server_log:
                    continue

                if 'Done' in server_log and 'For help' in server_log:
                    if system_start_time is None:
                        system_start_time = time.time()
                if 'joined the game' in server_log:
                    joined_count += 1
                if 'left the game' in server_log:
                    left_count += 1
                if 'UUID of added entity already exists' in server_log:
                    is_duplicate_uuid = True
                if 'Can\'t keep up!' in server_log:
                    is_lag = True
                if 'java.sql.SQLTransientConnectionException' in server_log:
                    database_error = True

            if system_start_time is None:
                next_check_time = time.time() + 10

        return {'is_lag': is_lag,
                'system_start_time': system_start_time,
                'joined_count': joined_count,
                'left_count': left_count,
                'is_duplicate_uuid': is_duplicate_uuid,
                'database_error': database_error}


def get_logger(name: str):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s',
                        datefmt='%m.%d %H:%M:%S')
    return logging.getLogger(name)


if __name__ == '__main__':
    os.chdir(config.SERVER_ROOT)

    logger = get_logger('test')

    for i in range(25):
        print(detect_server(True))
        time.sleep(1)
