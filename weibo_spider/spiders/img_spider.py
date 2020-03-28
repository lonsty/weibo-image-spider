# @FILENAME : img_spider
# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:24
from os.path import join as pjoin
from traceback import format_exc

from bs4 import BeautifulSoup

from weibo_spider.models.dto import task_queue
from weibo_spider.models.errors import NoMoreImages, TokenUnavailable
from weibo_spider.utils import get_session, retry, save_cookie


@retry(Exception, tries=1)
def crawl_image(cfg, page_url, session):
    try:
        resp = session.get(page_url, cookies=cfg.COOKIES, proxies=cfg.PROXIES, timeout=cfg.TIMEOUT)
    except Exception as err:
        print(format_exc())
        raise

    try:
        soup = BeautifulSoup(resp.json().get('data'), 'html.parser')
        for a in soup.find_all('a', class_='ph_ar_box'):
            img = cfg.PATTERN.search(a.find('img').get('src')).group(0)
            task_queue.put(img)
    except Exception as err:
        raise TokenUnavailable('Token has expired, please input a new cookie:\n')

    try:
        action_data = soup.find('div', class_='WB_cardwrap').get('action-data')
        cfg.PHOTO_API.action_data = action_data
    except Exception as err:
        raise NoMoreImages('No more images to crawl')


def crawl_worker(cfg):
    session = get_session()
    for page in range(1, cfg.MAX_PAGES + 1):
        cfg.PHOTO_API.page = page
        try:
            crawl_image(cfg, cfg.USER_PHOTO_API, session)
        except TokenUnavailable as err:
            cfg.COOKIES_RAW = input(str(err))
            save_cookie(cfg.COOKIES_RAW)
            crawl_image(cfg, cfg.USER_PHOTO_API, session)
        except NoMoreImages as err:
            print(format_exc())
            break
        except Exception:
            cfg.END_CRAWLER = True
    cfg.END_CRAWLER = True


@retry(Exception, tries=1)
def download_image(cfg, img, session):
    url = cfg.IMG_HOST + img
    print(url)
    try:
        with session.get(url, cookies=cfg.COOKIES, proxies=cfg.PROXIES, timeout=cfg.TIMEOUT) as resp:
            if resp.status_code != 200:
                raise Exception(f'Response status code: {resp.status_code}')
    except Exception as err:
        print(format_exc())
        raise

    with open(pjoin(cfg.SAVED_DIR, img), 'wb') as f:
        f.write(resp.content)
        print(pjoin(cfg.SAVED_DIR, img))


def download_worker(cfg):
    session = get_session()
    while 1:
        try:
            img = task_queue.get(timeout=1)
        except Exception as err:
            if cfg.END_CRAWLER:
                return
        else:
            download_image(cfg, img, session)
