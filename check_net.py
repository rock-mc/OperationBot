import logging
import platform
import subprocess
import threading
import time


def ping_ip(ip_address, results):
    """
    檢查 IP 是否可連線，如果可連線則將結果寫入 results 變數中。
    :param ip_address: 要檢查的 IP 地址
    :param results: 用於存儲結果的共享變數
    """
    try:
        output = subprocess.check_output(
            "ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c', ip_address),
            shell=True, universal_newlines=True, timeout=1)
        if 'unreachable' in output:
            results.append(False)
        else:
            results.append(True)
    except Exception as e:
        results.append(False)


def check_network_status():
    """
    同時檢查多個 DNS 的連線狀態，返回整個網路狀態。
    """
    results = []
    threads = []
    ips = ['168.95.1.1', '1.1.1.1', '101.101.101.101', '8.8.8.8']
    for ip in ips:
        t = threading.Thread(target=ping_ip, args=(ip, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return any(results)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s',
                        datefmt='%m.%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    last_state = None

    wait_time = 2
    while True:
        if last_state is not None:
            time.sleep(max(0, wait_time - (end_time - start_time)))

        start_time = time.time()
        check_result = check_network_status()
        end_time = time.time()

        if check_result:
            if last_state == 'ok':
                continue
            last_state = 'ok'
            logger.info('連線狀態: 正常')
        else:
            if last_state == 'error':
                continue
            last_state = 'error'
            logger.info('連線狀態: ConnectionError')
