# @FILENAME : user
# @AUTHOR : lonsty
# @DATE : 2020/3/28 15:12
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, RequestException

from weibo_image_spider.constant import Constant
from weibo_image_spider.models.dto import User
from weibo_image_spider.models.exceptions import ContentParserError
from weibo_image_spider.utils import get_session, retry


@retry(ConnectionError)
def query_user_by_name(const: Constant):
    session = get_session()

    try:
        resp = session.get(const.user_search_api, proxies=const.proxies,
                           stream=True, timeout=const.timeout)
    except Exception as err:
        raise ConnectionError(err)

    if resp.status_code != 200:
        raise RequestException(resp.status_code)

    try:
        first = BeautifulSoup(resp.text, 'html.parser').find('div', class_='card')
        host = first.find('a', class_='name').get('href')
        uid = first.find('a', class_='s-btn-c').get('uid')
    except AttributeError as err:
        raise ContentParserError('Weibo website structure updated, please add a issue '
                                 'at https://github.com/lonsty/weibo-image-spider/issues.')

    return User(name=const.nickname, host=host, uid=uid)
