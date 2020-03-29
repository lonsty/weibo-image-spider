# @FILENAME : dto
# @AUTHOR : lonsty
# @DATE : 2020/3/28 15:30
import time
from datetime import datetime
from queue import Queue

from pydantic import BaseModel
from termcolor import colored

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

    # api_pattern = 'https://weibo.com/p/aj/album/loading?ajwvr=6{action_data}&page_id={page_id}&page={page}&ajax_call=1&__rnd={rnd}'
    #
    # @property
    # def action_data_fix(self):
    #     return '&' + self.action_data

    @property
    def api(self):
        return f'https://weibo.com/p/aj/album/loading?ajwvr=6&{self.action_data}' \
               f'&page_id={self.page_id}&page={self.page}&ajax_call=1&__rnd={self.rnd}'

    @property
    def rnd(self):
        return int(time.time() * 1000)


class Parameters(BaseModel):
    nickname = ''
    uid: int = None
    destination: str
    overwrite: bool
    thumbnail: bool
    max_num: int
    max_pages: int
    max_workers: int


class Status(BaseModel):
    succeed = []
    failed = []
    start_time = datetime.now()

    @property
    def total(self):
        return len(self.succeed) + len(self.failed)

    @property
    def start_time_repr(self):
        return self.start_time.ctime()

    @property
    def time_used(self):
        return str(datetime.now() - self.start_time)[:-7]

    @property
    def fmt_status(self):
        return f'[Succeed: {colored(str(len(self.succeed)), "green")} | Failed: {colored(str(len(self.failed)), "red")}]'
