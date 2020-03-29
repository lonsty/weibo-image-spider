# @FILENAME : config
# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:27
import json
import os
import re
# from os.path import join as path_join, abspath
from random import choice

from pydantic import BaseModel

from weibo_spider.models.dto import User, PhotoAPI, Status
from weibo_spider.utils import read_cookie


class Config(BaseModel):
    cookies_raw = 'SINAGLOBAL=6546016478247.141.1575286326378; SSOLoginState=1584878679; Ugrow-G0=6fd5ded' \
                  'c9d0f894fec342d051b79679e; login_sid_t=e49e6d89c9f4bfcfeb4c8bb238c84ca1; cross_origin_' \
                  'proto=SSL; TC-V5-G0=799b73639653e51a6d82fb007f218b2f; _s_tentry=passport.weibo.com; UO' \
                  'R=login.sina.com.cn,widget.weibo.com,www.baidu.com; wb_view_log=1920*10801; Apache=913' \
                  '3499080801.512.1585228757104; ULV=1585228757110:3:1:1:9133499080801.512.1585228757104:' \
                  '1577097353384; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW5U36EM_hJ7zug98hI5yFy5JpX5K2hUg' \
                  'L.Fo-fSo5XSK5NSoB2dJLoI79jdc40UG.t; ALF=1616764756; SCF=AqG8ih_WFRhJAfYpt-svWY-VlGjjbT' \
                  'Jxiu09fG4sBFzCiFanAU852kJofLqi09pnPkFKQoYZT3x8ncE41STtnhQ.; SUB=_2A25zeNuFDeRhGeNL7VIV' \
                  '9S7LzTiIHXVQDEpNrDV8PUNbmtAKLVf2kW9NSONTaErreoD6wzGX6vd-6abUEY8WZ7Cz; SUHB=0wn1lzkwcw7' \
                  'eD8; un=lonsty@sina.com; wvr=6; wb_view_log_5560450764=1920*10801; webim_unReadCount=%' \
                  '7B%22time%22%3A1585234643120%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C' \
                  '%22allcountNum%22%3A79%2C%22msgbox%22%3A0%7D; TC-Page-G0=7f6863db1952ff8adac0858ad5825' \
                  'a3b|1585234646|158523464'
    # cookies_raw = 'SINAGLOBAL=6546016478247.141.1575286326378; un=lonsty@sina.com; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW5U36EM_hJ7zug98hI5yFy5JpX5KMhUgL.Fo-fSo5XSK5NSoB2dJLoI79jdc40UG.t; ALF=1616910325; SSOLoginState=1585374326; SCF=AqG8ih_WFRhJAfYpt-svWY-VlGjjbTJxiu09fG4sBFzCRvVxAu6as7gbuLBWKi5NwWk-5wZPYPYEUSOvZKo_U1c.; SUB=_2A25zepQmDeRhGeNL7VIV9S7LzTiIHXVQ8YLurDV8PUNbmtAKLXSgkW9NSONTaDHwXt5LRV50NeO2llQ1J6ycfowE; SUHB=0laFlB6b0F7O8u; TC-V5-G0=eb26629f4af10d42f0485dca5a8e5e20; _s_tentry=login.sina.com.cn; Apache=1859324291635.7068.1585374329766; ULV=1585374329931:4:2:2:1859324291635.7068.1585374329766:1585228757110; Ugrow-G0=5c7144e56a57a456abed1d1511ad79e8; UOR=login.sina.com.cn,widget.weibo.com,www.baidu.com; wb_view_log_5560450764=1920*10801; webim_unReadCount=%7B%22time%22%3A1585390178030%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A77%2C%22msgbox%22%3A0%7D; TC-Page-G0=51e9db4bd1cd84f5fb5f9b32772c2750|1585390196|158539019'
    search_api = 'https://s.weibo.com/user?q={user}&Refer=SUer_box'
    # photo_homepage = 'https://weibo.com/p/100505{uid}/photos?from=page_100505&mod=TAB#place'
    # photo_api = 'https://weibo.com/p/aj/album/loading?ajwvr=6&type=photo&owner_uid={uid}&viewer_uid=55604' \
    #             '50764&since_id=4445464137133834_4368389503918048_20191224_-1&page_id=100505{uid}&ajax_ca' \
    #             'll=1&__rnd=1585234648606'
    timeout = (3, 5)
    img_hosts = ['https://wx1.sinaimg.cn', 'https://wx2.sinaimg.cn', 'https://wx3.sinaimg.cn']

    user = User()
    photo_api = PhotoAPI()
    status = Status()

    nickname = 'lonsty'
    destination: str = 'weibo_images'
    overwrite: bool = False
    thumbnail: bool = False
    max_num: int = 2000
    max_pages: int = 20
    max_workers: int = 15
    proxies_raw: str = None

    cancel: bool = False
    end_crawler = False

    def __init__(self, **kargs):
        super(Config, self).__init__(**kargs)
        self.cookies_raw = read_cookie()

    @property
    def cookies(self):
        try:
            return dict([line.split('=')[0], line.split('=')[1]] for line in self.cookies_raw.split('; '))
        except Exception as e:
            return None

    @property
    def img_url_prefix(self):
        return f'{choice(self.img_hosts)}/{"large" if not self.thumbnail else "mw690"}/'

    @property
    def saved_dir(self):
        return os.path.join(os.path.abspath(self.destination), self.user.name)

    @property
    def rex_pattern(self):
        return re.compile('(?<=/)\w*?\.(?:jpg|gif)', re.IGNORECASE)

    # @property
    # def user_photo_homepage(self):
    #     return self.photo_homepage.format(uid=self.user.uid)

    @property
    def user_photo_api(self):
        return self.photo_api.api

    @property
    def user_search_api(self):
        return self.search_api.format(user=self.nickname)

    # def mkdirs_if_not_exist(self):
    #     mkdirs_if_not_exist(self.saved_dir)

    #
    # @property
    # def COOKIES(self):
    #     return dict([line.split('=')[0], line.split('=')[1]] for line in self.cookies_raw.split('; '))
    #
    # @COOKIES.setter
    # def COOKIES(self, value):
    #     self.cookies_raw = value

    @property
    def proxies(self):
        if isinstance(self.proxies_raw, str):
            try:
                return json.loads(self.proxies_raw)
            except Exception:
                print('Warning: proxy has not taken effect due to malformed')
                return None
        return None
