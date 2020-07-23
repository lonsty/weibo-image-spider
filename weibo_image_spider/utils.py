# @FILENAME : utils
# @AUTHOR : lonsty
# @DATE : 2020/3/28 14:23
import json
import os
import random
import sys
import threading
import time
from functools import wraps

from requests import Session

thread_local = threading.local()


def cookies_from_raw(raw):
    return dict([line.split('=')[0], line.split('=')[1]] for line in raw.split('; '))


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = Session()
    return thread_local.session


def retry(exceptions, tries=3, delay=1, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.
    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay or random.uniform(0.5, 1.5)
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if logger:
                        logger.warning('{}, Retrying in {} seconds...'.format(e, mdelay))
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry


def mkdirs_if_not_exist(dir):
    if not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except FileExistsError:
            pass


def convert_to_safe_filename(filename):
    return "".join([c for c in filename if c not in r'\/:*?"<>|']).strip()


def read_cookie():
    with open('cookie', 'r') as f:
        return f.read().strip()


def save_cookie(cookie):
    with open('cookie', 'w') as f:
        f.write(cookie)


def quit(msg, code=0):
    print(msg)
    sys.exit(code)


def save_records(c):
    filename = os.path.join(c.saved_dir, c.status.start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.json')
    with open(filename, 'w') as f:
        f.write(json.dumps({
            'nickname': c.user.name,
            'uid': c.user.uid,
            'datetime': c.status.start_time_repr,
            'succeed': {
                'count': len(c.status.succeed),
                'urls': c.status.succeed
            },
            'failed': {
                'count': len(c.status.failed),
                'urls': c.status.failed
            }
        }, ensure_ascii=False, indent=2))
