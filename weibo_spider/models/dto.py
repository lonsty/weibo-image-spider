# @FILENAME : dto
# @AUTHOR : lonsty
# @DATE : 2020/3/28 15:30
import time
from queue import Queue

from pydantic import BaseModel

task_queue = Queue()


class User(BaseModel):
    name = ''
    uid: int = 0
    host: str = ''

    @property
    def page_id(self):
        return int('100505' + str(self.uid))


class PhotoAPI(BaseModel):
    action_data: str = ''
    page_id: int = 0
    page: int = 1
    api_pattern = 'https://weibo.com/p/aj/album/loading?ajwvr=6{action_data}&page_id={page_id}&page={page}&ajax_call=1&__rnd={rnd}'

    @property
    def action_data_fix(self):
        return '&' + self.action_data

    @property
    def api(self):
        return self.api_pattern.format(action_data=self.action_data_fix, page_id=self.page_id, page=self.page,
                                       rnd=self.rnd)

    @property
    def rnd(self):
        return int(time.time() * 1000)


class Parameters(BaseModel):
    USERNAME = ''
    DESTINATION = ''
    OVERRIDE: bool
    THUMBNAIL: bool
    MAX_NUM: int
    MAX_PAGES: int
    MAX_WORKERS: int
