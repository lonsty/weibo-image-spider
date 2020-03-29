# @FILENAME : manage
# @AUTHOR : lonsty
# @DATE : 2020/3/28 18:46
from concurrent.futures import ThreadPoolExecutor, wait

import click
from pydantic import ValidationError
from requests.exceptions import RequestException, ConnectionError

from weibo_spider.config import Config
from weibo_spider.models.dto import Parameters, PhotoAPI
from weibo_spider.spiders import query_user_by_name, crawl_worker, download_worker
from weibo_spider.utils import mkdirs_if_not_exist, quit, save_records


@click.command()
@click.option('-u', '--nickname', 'nickname', help='Username')
@click.option('-d', '--destination', 'destination', default='weibo_images/', show_default=True,
              help='Directory to save images')
@click.option('-O', '--overwrite', 'overwrite', is_flag=True, default=False, show_default=True,
              help='Override existing files')
@click.option('--thumbnail', 'thumbnail', is_flag=True, default=False, show_default=True,
              help='Download thumbnails with a maximum width of 690px')
@click.option('--max-num', 'max_num', default=2000, show_default=True, type=int,
              help='Maximum images to download')
@click.option('--max-pages', 'max_pages', default=20, show_default=True, type=int,
              help='Maximum pages to download')
@click.option('--max-workers', 'max_workers', default=15, show_default=True, type=int,
              help='Maximum thread workers')
@click.option('--proxies', 'proxies_raw', help='Use proxies to access websites.\nExample:\n\'{"http": "user:passwd'
                                               '@www.example.com:port",\n"https": "user:passwd@www.example.com:port"}\'')
def weibo_command(**kwargs):
    try:
        paras = Parameters(**kwargs)
        cfg = Config(**paras.dict())
    except ValidationError as err:
        quit(str(err.json), 1)

    print(cfg)
    return
    try:
        cfg.user = query_user_by_name(cfg)
    except (ConnectionError, RequestException) as err:
        quit(f'Network error: {err}', 1)

    mkdirs_if_not_exist(cfg.saved_dir)
    print(f'\n - - - - - -+-+ {cfg.status.start_time_repr} +-+- - - - - -\n'
          f'Nickname: {cfg.user.name}\n'
          f'User ID: {cfg.user.uid}\n'
          f'Images save path: {cfg.saved_dir}\n')

    cfg.photo_api = PhotoAPI(action_data=f'type=photo&owner_uid={cfg.user.uid}&viewer_uid=5560450764&since_id=-1',
                             page_id=int(f'100505{cfg.user.uid}'), page=1)

    with ThreadPoolExecutor(max_workers=cfg.max_workers + 1) as executor:
        img_crawler = executor.submit(crawl_worker, cfg)
        img_downloader = [executor.submit(download_worker, cfg) for i in range(cfg.max_workers)]

    wait([img_crawler] + img_downloader)
    save_records(cfg)
    quit('\n\nDownload completed, bye bye ~')
