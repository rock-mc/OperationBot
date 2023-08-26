import glob
import json
import logging
import os
import time

import requests

import server_cmd
from discord import discord_bot
import config

logger = logging.getLogger(__name__)


def get_new_server_file():
    is_updated = False

    try:
        current_server_file = None
        last_check_time = None
        with open('server_version.json', 'r') as f:
            server_version = json.load(f)
        if 'current_version' in server_version:
            current_server_file = server_version['current_version']
        if 'last_check_time' in server_version:
            last_check_time = int(server_version['last_check_time'])
    except FileNotFoundError:
        current_server_file = None
        last_check_time = None

    if current_server_file is None or not os.path.exists(current_server_file):

        max_main_version = None
        max_sub_version = None
        # find the current server version
        for file in glob.glob('paper-*.jar'):
            # server_version = int(file[:-4].split('-')[-1])
            logger.info(f'find server file: {file}')

            main_version = file.split('-')[1]
            sub_version = file[:-4].split('-')[2]

            if max_main_version is None:
                max_main_version = main_version
                max_sub_version = sub_version
            elif int(main_version.replace('.', '')) > int(max_main_version.replace('.', '')):
                max_main_version = main_version
                max_sub_version = sub_version
            elif int(main_version.replace('.', '')) == int(max_main_version.replace('.', '')):
                if int(sub_version) > int(max_sub_version):
                    max_sub_version = sub_version

            logger.debug(f'current main_version: {main_version}')
            logger.debug(f'current sub_version: {sub_version}')

        current_server_file = f'paper-{max_main_version}-{max_sub_version}.jar'
    elif last_check_time is None or time.time() - last_check_time < 60 * 60 * 3:
        return is_updated, current_server_file
    else:
        max_main_version = current_server_file.split('-')[1]
        max_sub_version = current_server_file[:-4].split('-')[2]

    logger.info(f'current server version: {current_server_file}')

    detect_range = 256

    start = 0
    end = detect_range - 1

    server_file_temp = None
    server_version_temp = 0

    # find the next server version
    # https://api.papermc.io/v2/projects/paper/versions/1.20.1/builds/132/downloads/paper-1.20.1-132.jar
    new_server_file = None
    while start <= end:

        version_offset = (start + end) // 2

        new_sub_version = int(max_sub_version) + version_offset
        current_new_server_file = f'paper-{max_main_version}-{new_sub_version}.jar'
        current_url = f'https://api.papermc.io/v2/projects/paper/versions/{max_main_version}/builds/{new_sub_version}/downloads/{current_new_server_file}'

        r = requests.get(current_url)
        if r.status_code != 200:
            logger.info(f'paper-{max_main_version}-{new_sub_version}.jar not found!')
            end = version_offset - 1
            continue
        if new_sub_version > server_version_temp:
            server_file_temp = r.content
            server_version_temp = new_sub_version

        new_sub_version = int(max_sub_version) + version_offset + 1
        current_new_server_file = f'paper-{max_main_version}-{new_sub_version}.jar'
        current_url = f'https://api.papermc.io/v2/projects/paper/versions/{max_main_version}/builds/{new_sub_version}/downloads/{current_new_server_file}'

        r = requests.get(current_url)
        if r.status_code == 200:
            logger.info(f'paper-{max_main_version}-{new_sub_version}.jar found!')
            start = version_offset + 1
            if new_sub_version > server_version_temp:
                server_file_temp = r.content
                server_version_temp = new_sub_version
            continue

        new_sub_version = int(max_sub_version) + version_offset
        current_new_server_file = f'paper-{max_main_version}-{new_sub_version}.jar'
        new_server_file = current_new_server_file

        logger.info(f'paper-{max_main_version}-{new_sub_version}.jar is the latest version!s')
        logger.info(f'write {new_server_file} to file')
        open(new_server_file, 'wb').write(server_file_temp)

        del server_file_temp

        break

    if current_server_file == new_server_file or new_server_file is None:
        logger.info(f'no new server version!')
        return is_updated, current_server_file

    logger.info(f'test new server version: {new_server_file}')

    # backup the logs/latest.log
    if os.path.exists('logs/latest.log'):
        os.system(f'mv logs/latest.log logs/latest.log.bak')

    # test the new server file
    server_cmd.start(new_server_file)
    for i in range(60):
        time.sleep(1)
        if i % 3 == 0:
            server_cmd.say('此為新版本伺服器自動測試...請勿登入！')

    # read the server log
    with open('logs/latest.log', 'r') as f:
        log = f.read().lower()
    # check the server log
    if 'error' in log or 'exception' in log:
        # stop the server
        server_cmd.stop('測試新版本伺服器失敗，關閉伺服器', 5)

        logger.info(f'{new_server_file} test failed!')
        return is_updated, current_server_file

    server_cmd.say('測試新版本伺服器成功！')
    logger.info(f'{new_server_file} test success!')
    is_updated = True

    # read the current server version
    try:
        with open('server_version.json', 'r') as f:
            server_version = json.load(f)

        # remove the old server file
        os.system(f'rm {server_version["pre_version"]}')

        server_version['pre_version'] = server_version['current_version']
        server_version['current_version'] = new_server_file
        server_version['last_check_time'] = int(time.time())

    except FileNotFoundError:
        server_version = {
            'pre_version': current_server_file,
            'current_version': new_server_file,
            'last_check_time': int(time.time())
        }

    with open('server_version.json', 'w') as f:
        json.dump(server_version, f, indent=4)

    try:
        discord_bot.post(content=f'<@694182416583098470> 伺服器版本更新：{current_server_file} -> {new_server_file}')
    except Exception as e:
        logger.error(e)
    return is_updated, new_server_file


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s',
                        datefmt='%m.%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    os.chdir(config.SERVER_ROOT)

    get_new_server_file()
