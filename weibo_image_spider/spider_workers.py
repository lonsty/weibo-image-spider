# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:24
import logging
import os
import queue
import threading

from bs4 import BeautifulSoup
from requests import Session
from requests.exceptions import ConnectionError, RequestException
from termcolor import colored

from .constants import Constant
from .exceptions import ContentParserError, CookiesExpiredException, NoImagesException, UserNotFound
from .models import User, appointment_jobs, downloading_jobs
from .utils import get_session, retry, save_cookie

lock = threading.RLock()


@retry(logger=logging)
def query_user_by_name(const: Constant):
    session = get_session()

    try:
        logging.info(f"Getting information of username: {const.nickname}...")
        resp = session.get(const.user_search_api, cookies=const.cookies, proxies=const.proxies, timeout=const.timeout)
        resp.raise_for_status()
    except Exception as e:
        logging.info(f"Getting user information error: {e}")
        raise ConnectionError(e)

    try:
        logging.info("Initialing a BeautifulSoup...")
        first = resp.json()["user"][0]
        name = first["u_name"]
        uid = first["u_id"]
    except (KeyError, IndexError) as e:
        logging.info(f"Parsing user information error: {e}")
        raise ContentParserError(
            "Weibo API updated, please add a issue " "to https://github.com/lonsty/weibo-image-spider/issues."
        )
    user = User(name=name, host=f"https://weibo.com/u/{uid}", uid=uid)
    logging.info(f"Got information of username: {const.nickname}, {user}")

    return user


@retry((RequestException, CookiesExpiredException), logger=logging)
def crawl_image(const: Constant, url: str, session: Session):
    try:
        logging.info(f"Getting urls from page...")
        resp = session.get(url, cookies=const.cookies, proxies=const.proxies, timeout=const.timeout)
        resp.raise_for_status()
    except Exception as e:
        logging.info(f"Getting urls from page error: {e}")
        raise RequestException(e)

    try:
        logging.info(f"Parsing urls from page...")
        soup = BeautifulSoup(resp.json().get("data"), "html.parser")
        boxes = soup.find_all("a", class_="ph_ar_box")
        for box in boxes:
            img = const.rex_pattern.search(box.find("img").get("src")).group(0)
            downloading_jobs.put(img)
        logging.info(f"Parsed {len(boxes)} urls from page")
    except Exception as e:
        logging.info(f"Parsing urls from page error: {e}")
        raise CookiesExpiredException("Cookie has expired, please get a new one and paste to here:\n")

    logging.info(f"Parsing action-data from page...")
    card = soup.find("div", class_="WB_cardwrap")
    if not card:
        logging.info(f"No action-data in page")
        raise NoImagesException("No more images to crawl")

    action_data = card.get("action-data")
    const.photo_api.action_data = action_data
    logging.info(f"Got action-data from page: {action_data}")


def crawl_worker(const: Constant):
    page = 1
    session = get_session()

    while appointment_jobs.qsize() < const.max_images:
        const.photo_api.page = page
        try:
            logging.info(f"Crawling page {page}...")
            crawl_image(const, const.user_photo_api, session)
            logging.info(f"Crawled page {page}")
        except CookiesExpiredException as e:
            logging.info(f"Cookies has expired, need new cookies")
            const.cookies_raw = input(str(e))
            save_cookie(const.cookies_raw)
            logging.info(f"Saved new cookies")
            continue
        except (NoImagesException, Exception) as e:
            logging.info(f"Crawling page: {e}")
            break
        page += 1
    const.end_crawler = True


@retry(logger=logging)
def download_image(const: Constant, img: str, session: Session):
    url = const.img_url_prefix + img
    filename = os.path.join(const.saved_dir, img)

    if (not const.overwrite) and os.path.isfile(filename):
        logging.info(f"Skipped downloaded image: {filename}")
        return url

    try:
        logging.info(f"Heading image...")
        head = session.get(url, cookies=const.cookies, proxies=const.proxies, timeout=const.timeout)
        head.raise_for_status()
        image_size = int(head.headers["Content-Length"].strip())
        logging.info(f"Got image: {url} size: {image_size}")
    except Exception as e:
        logging.info(f"Heading image error: {e}")
        raise RequestException(e)

    try:
        logging.info(f"Downloading image...")
        resp = session.get(url, cookies=const.cookies, proxies=const.proxies, stream=True, timeout=const.timeout)
        resp.raise_for_status()
        logging.info(f"Downloaded image")
    except Exception as e:
        logging.info(f"Downloading image error: {e}")
        raise RequestException(e)

    write_size = 0
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            write_size += len(chunk)

    if write_size < image_size:
        os.remove(filename)
        logging.info(f"Saving image error: image is incomplete")
        raise RequestException("The downloaded image is incomplete")
    logging.info(f"Saved image: {filename}")

    return url


def download_worker(const: Constant):
    session = get_session()

    while appointment_jobs.qsize() < const.max_images:
        try:
            img = downloading_jobs.get_nowait()
            with lock:
                if appointment_jobs.qsize() < const.max_images:
                    appointment_jobs.put(img)
                else:
                    break
            logging.info(f"Download worker start...")
            result = download_image(const, img, session)
        except queue.Empty:
            if const.cancel or const.end_crawler:
                break
        except Exception as e:
            logging.info(f"Download worker error: {e}")
            result = const.img_url_prefix + img
            const.status.failed.append(result)
            print(
                f'{colored("[x]", "red", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t'
                f"{const.status.fmt_status}",
                end="\r" if not const.verbose else "\n",
                flush=True,
            )
        else:
            logging.info(f"Download worker succeed")
            const.status.succeed.append(result)
            print(
                f'{colored("[√]", "green", attrs=["reverse"])} {colored(result, attrs=["underline"])}\t'
                f"{const.status.fmt_status}",
                end="\r" if not const.verbose else "\n",
                flush=True,
            )
