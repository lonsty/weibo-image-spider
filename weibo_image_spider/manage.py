# @FILENAME : manage
# @AUTHOR : lonsty
# @DATE : 2020/3/28 18:46
import json
from concurrent.futures import ThreadPoolExecutor, wait

import click
from pydantic import ValidationError
from requests.exceptions import RequestException, ConnectionError
from termcolor import colored

from weibo_image_spider.constant import Constant
from weibo_image_spider.models.dto import Parameters, PhotoAPI
from weibo_image_spider.utils import mkdirs_if_not_exist, quit, save_records
from weibo_image_spider.workers import query_user_by_name, crawl_worker, download_worker


@click.command(help='A Weibo image spider, visit https://github.com/lonsty/weibo-image-spider.')
@click.option('-u', '--nickname', 'nickname', help='Nickname')
@click.option('-d', '--destination', 'destination', default='weibo_images/', show_default=True,
              help='Directory to save images')
@click.option('-o', '--overwrite', 'overwrite', is_flag=True, default=False, show_default=True,
              help='Overwrite existing files')
@click.option('-t', '--thumbnail', 'thumbnail', is_flag=True, default=False, show_default=True,
              help='Download thumbnails with a maximum width of 690px')
@click.option('-n', '--max-images', 'max_images', default=2000, show_default=True, type=int,
              help='Maximum number of images to download')
@click.option('-w', '--max-workers', 'max_workers', default=15, show_default=True, type=int,
              help='Maximum thread workers')
@click.option('-P', '--proxies', 'proxies_raw', help='Use proxies to access websites.\nExample:\n\''
                                                     '{"http": "user:passwd@www.example.com:port",\n'
                                                     '"https": "user:passwd@www.example.com:port"}\'')
def weibo_command(**kwargs):
    try:
        paras = Parameters(**kwargs)
        const = Constant(**paras.dict())
    except ValidationError as err:
        quit('Invalid arguments: ' + ', '.join([f'{e["loc"][0]} - {e["msg"]}' for e in json.loads(err.json())]), 1)

    try:
        const.user = query_user_by_name(const)
    except (ConnectionError, RequestException) as err:
        quit(f'Network error: {err}', 1)

    mkdirs_if_not_exist(const.saved_dir)
    print(f'\n - - - - - -+-+ {const.status.start_time_repr} +-+- - - - - -\n'
          f'   Nickname: {colored(const.user.name, "cyan")}\n'
          f'    User ID: {colored(const.user.uid, "cyan")}\n'
          f'Destination: {colored(const.saved_dir, attrs=["underline"])}\n'
          f'  Overwrite: {const.overwrite}\n'
          f'  Thumbnail: {const.thumbnail}\n'
          f' Max images: {const.max_images}\n')

    const.photo_api = PhotoAPI(action_data=f'type=photo&owner_uid={const.user.uid}&viewer_uid={const.user.uid}'
                                           f'&since_id=-1',
                               page_id=int(f'100505{const.user.uid}'), page=1)

    with ThreadPoolExecutor(max_workers=const.max_workers + 1) as pool:
        img_crawler = pool.submit(crawl_worker, const)
        img_downloader = [pool.submit(download_worker, const) for i in range(const.max_workers)]
    wait([img_crawler] + img_downloader)

    save_records(const)
    quit('\n\nDownload completed, bye bye ~')
