# @FILENAME : user_spider
# @AUTHOR : lonsty
# @DATE : 2020/3/28 15:12
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, ConnectionError

from weibo_spider.config import Config
from weibo_spider.models.dto import User
from weibo_spider.models.errors import ContentParserError
from weibo_spider.utils import get_session


def query_user_by_name(cfg: Config):
    session = get_session()

    try:
        resp = session.get(cfg.user_search_api, proxies=cfg.proxies, timeout=cfg.timeout)
    except Exception as err:
        # print(format_exc())
        raise ConnectionError(err)

    if resp.status_code != 200:
        raise RequestException(resp.status_code)

    try:
        first = BeautifulSoup(resp.text, 'html.parser').find('div', class_='card')
        host = first.find('a', class_='name').get('href')
        uid = first.find('a', class_='s-btn-c').get('uid')
    except AttributeError as err:
        raise ContentParserError(
            'Weibo website structure updated, please contact the author at lonsty@sina.com to update the code')

    return User(name=cfg.nickname, host=host, uid=uid)
