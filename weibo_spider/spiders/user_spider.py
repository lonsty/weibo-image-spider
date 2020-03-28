# @FILENAME : user_spider
# @AUTHOR : lonsty
# @DATE : 2020/3/28 15:12
from traceback import format_exc

from bs4 import BeautifulSoup

from weibo_spider.models.dto import User
from weibo_spider.models.errors import TokenUnavailable
from weibo_spider.utils import get_session


def query_user_by_name(cfg):
    session = get_session()

    try:
        resp = session.get(cfg.USER_SEARCH_API, cookies=cfg.COOKIES, proxies=cfg.PROXIES, timeout=cfg.TIMEOUT)
    except Exception as err:
        print(format_exc())
        raise

    try:
        first = BeautifulSoup(resp.text, 'html.parser').find('div', class_='card')
        host = first.find('a', class_='name').get('href')
        uid = first.find('a', class_='s-btn-c').get('uid')
    except AttributeError as err:
        raise TokenUnavailable('Token has expired, please input a new cookies:\n')

    return User(name=cfg.USERNAME, host=host, uid=uid)
