# @FILENAME : image
# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:24
import os
from queue import Empty

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from termcolor import colored

from weibo_image_spider.constant import Constant
from weibo_image_spider.models.dto import appointment_jobs, downloading_jobs
from weibo_image_spider.models.exceptions import NoImagesException, CookiesExpiredException
from weibo_image_spider.utils import get_session, retry, save_cookie


@retry(RequestException)
def crawl_image(const: Constant, url, session):
    try:
        resp = session.get(url, cookies=const.cookies, proxies=const.proxies, stream=True,
                           timeout=const.timeout)
    except Exception as err:
        raise RequestException(err)

    try:
        soup = BeautifulSoup(resp.json().get('data'), 'html.parser')
        for a in soup.find_all('a', class_='ph_ar_box'):
            img = const.rex_pattern.search(a.find('img').get('src')).group(0)
            downloading_jobs.put(img)
    except Exception as err:
        raise CookiesExpiredException('Cookie has expired, please copy and paste a new one:\n')

    try:
        const.photo_api.action_data = soup.find('div', class_='WB_cardwrap').get('action-data')
    except Exception as err:
        raise NoImagesException('No more images to crawl')


def crawl_worker(const: Constant):
    page = 1
    session = get_session()

    while 1:
        const.photo_api.page = page
        try:
            crawl_image(const, const.user_photo_api, session)
        except CookiesExpiredException as err:
            const.cookies_raw = input(str(err))
            save_cookie(const.cookies_raw)
            continue
        except (NoImagesException, Exception) as err:
            break
        page += 1
    const.end_crawler = True


@retry(RequestException)
def download_image(const: Constant, img, session):
    url = const.img_url_prefix + img
    filename = os.path.join(const.saved_dir, img)

    if (not const.overwrite) and os.path.isfile(filename):
        return url

    try:
        resp = session.get(url, cookies=const.cookies, proxies=const.proxies, stream=True,
                           timeout=const.timeout)
        if resp.status_code != 200:
            raise Exception(f'Response status code: {resp.status_code}')
    except Exception as err:
        raise RequestException(err)
    with open(filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    return url


def download_worker(const: Constant):
    session = get_session()

    while appointment_jobs.qsize() < const.max_images:
        try:
            img = downloading_jobs.get_nowait()
            appointment_jobs.put(img)
            result = download_image(const, img, session)
        except Empty:
            if const.cancel or const.end_crawler:
                break
        except Exception as err:
            result = const.img_url_prefix + img
            const.status.failed.append(result)
            print(f'{colored("[x]", "red", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t'
                  f'{const.status.fmt_status}', end='\r', flush=True)
        else:
            const.status.succeed.append(result)
            print(f'{colored("[√]", "green", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t'
                  f'{const.status.fmt_status}', end='\r', flush=True)
