# @FILENAME : img_spider
# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:24
import os
from queue import Empty
from traceback import format_exc

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from termcolor import colored

from weibo_spider.config import Config
from weibo_spider.models.dto import task_queue
from weibo_spider.models.errors import NoImagesException, CookiesExpiredException
from weibo_spider.utils import get_session, retry, save_cookie


@retry(RequestException)
def crawl_image(cfg: Config, page_url, session):
    try:
        resp = session.get(page_url, cookies=cfg.cookies, proxies=cfg.proxies, timeout=cfg.timeout)
    except Exception as err:
        raise RequestException(err)

    try:
        soup = BeautifulSoup(resp.json().get('data'), 'html.parser')
        for a in soup.find_all('a', class_='ph_ar_box'):
            img = cfg.rex_pattern.search(a.find('img').get('src')).group(0)
            task_queue.put(img)
    except Exception as err:
        raise CookiesExpiredException('Cookie has expired, please copy and paste a new one:\n')

    try:
        cfg.photo_api.action_data = soup.find('div', class_='WB_cardwrap').get('action-data')
    except Exception as err:
        raise NoImagesException('No more images to crawl')


def crawl_worker(cfg: Config):
    index = 1
    session = get_session()

    while index <= cfg.max_pages:
        cfg.photo_api.page = index
        try:
            crawl_image(cfg, cfg.user_photo_api, session)
        except CookiesExpiredException as err:
            cfg.cookies_raw = input(str(err))
            save_cookie(cfg.cookies_raw)
            continue
        except (NoImagesException, Exception) as err:
            # print(format_exc())
            break
        index += 1
    cfg.end_crawler = True


@retry(RequestException)
def download_image(cfg: Config, img, session):
    url = cfg.img_url_prefix + img
    filename = os.path.join(cfg.saved_dir, img)

    if (not cfg.overwrite) and os.path.isfile(filename):
        return url

    try:
        resp = session.get(url, cookies=cfg.cookies, proxies=cfg.proxies, timeout=cfg.timeout)
        if resp.status_code != 200:
            raise Exception(f'Response status code: {resp.status_code}')
    except Exception as err:
        raise RequestException(err)
    with open(filename, 'wb') as f:
        f.write(resp.content)
    return url


def download_worker(cfg: Config):
    session = get_session()
    count = 0

    while count <= cfg.max_num:
        try:
            img = task_queue.get(timeout=1)
            result = download_image(cfg, img, session)
        except Empty:
            if cfg.cancel or cfg.end_crawler:
                break
        except Exception as e:
            print(format_exc())
            result = cfg.img_url_prefix + img
            cfg.status.failed.append(result)
            print(
                f'{colored("[x]", "red", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t{cfg.status.fmt_status}',
                end='\r', flush=True)
        else:
            cfg.status.succeed.append(result)
            print(
                f'{colored("[√]", "green", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t{cfg.status.fmt_status}',
                end='\r', flush=True)
        count += 1
