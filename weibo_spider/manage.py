# @FILENAME : manage
# @AUTHOR : lonsty
# @DATE : 2020/3/28 18:46
from concurrent.futures import ThreadPoolExecutor, wait

import click
from pydantic import ValidationError

from weibo_spider.config import Config
from weibo_spider.models.dto import Parameters, PhotoAPI
from weibo_spider.models.errors import TokenUnavailable
from weibo_spider.spiders import query_user_by_name, crawl_worker, download_worker


@click.command()
@click.option('-u', '--username', 'USERNAME', help='Username')
@click.option('-d', '--destination', 'DESTINATION', default='download/', show_default=True,
              help='Directory to save images')
@click.option('-O', '--override', 'OVERRIDE', is_flag=True, default=False, show_default=True,
              help='Override existing files')
@click.option('--thumbnail', 'THUMBNAIL', is_flag=True, default=False, show_default=True,
              help='Download thumbnails with a maximum width of 1280px')
@click.option('--max-num', 'MAX_NUM', default=2000, show_default=True, type=int,
              help='Maximum images to download')
@click.option('--max-pages', 'MAX_PAGES', default=20, show_default=True, type=int,
              help='Maximum pages to download')
@click.option('--max-workers', 'MAX_WORKERS', default=15, show_default=True, type=int,
              help='Maximum thread workers')
@click.option('--proxies', 'PROXIES_RAW', help='Use proxies to access websites.\nExample:\n\'{"http": "user:passwd'
                                               '@www.example.com:port",\n"https": "user:passwd@www.example.com:port"}\'')
def weibo_command(**kwargs):
    try:
        paras = Parameters(**kwargs)
    except ValidationError as err:
        print(err.json)
        raise
    cfg = Config(**paras.dict())
    try:
        cfg.USER = query_user_by_name(cfg)
    except TokenUnavailable as err:
        cfg.COOKIES_RAW = input(str(err))
        cfg.USER = query_user_by_name(cfg)

    cfg.mkdirs_if_not_exist()

    cfg.PHOTO_API = PhotoAPI(action_data=f'type=photo&owner_uid={cfg.USER.uid}&viewer_uid=5560450764&since_id=-1',
                             page_id=int(f'100505{cfg.USER.uid}'), page=1)

    with ThreadPoolExecutor(max_workers=cfg.MAX_WORKERS) as executor:
        img_crawler = executor.submit(crawl_worker, cfg)
        img_downloader = [executor.submit(download_worker, cfg) for i in range(cfg.MAX_WORKERS - 1)]
        wait([img_crawler] + img_downloader)
    print('done.')
