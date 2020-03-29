# @FILENAME : workers
# @AUTHOR : lonsty
# @DATE : 2020/3/29 14:57
import time

from weibo_spider.config import Config


def status_output(cfg: Config, cancel=None):
    while 1:
        print(f'{str(cfg.status)}', end='\r', flush=True)
        time.sleep(0.5)
        if cancel:
            break
