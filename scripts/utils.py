# import urllib
import math
import urllib.error
import urllib.parse
import ssl
from urllib.request import Request, urlopen

from . import proxy_handling
from .logger import logger


# Try to send request through a TOR
# try:
#     import socks  # SocksiPy module
#     import socket
#     SOCKS_PORT = 9150 # 9050
#     def create_connection(address, timeout=None, source_address=None):
#         sock = socks.socksocket()
#         sock.connect(address)
#         return sock
#     socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT)
#     socket.socket = socks.socksocket
#     socket.create_connection = create_connection
#     print("WITH PROXY")
# except:
#     pass


def y2lat(y):
    return (2 * math.atan(math.exp(y / 6378137)) - math.pi / 2) / (math.pi / 180)


def x2lon(x):
    return x / (math.pi / 180.0) / 6378137.0


def xy2lonlat(x, y):
    return [x2lon(x), y2lat(y)]


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'


class TimeoutException(Exception):
    pass


def get_rosreestr_headers():
    return {
        'pragma': 'no-cache',
        'referer': 'https://pkk.rosreestr.ru/',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }


def make_request(url, with_proxy=False):
    # original function
    if url:
        logger.debug(url)
        if with_proxy:
            return make_request_with_proxy(url)
        try:
            headers = get_rosreestr_headers()
            request = Request(url, headers=headers)
            context = ssl._create_unverified_context()
            with urlopen(request, context=context, timeout=3000) as response:
                read = response.read()
            return read
        except Exception as er:
            logger.warning(er)
            print(er)
            # raise TimeoutException()
    return False


def make_request_with_proxy(url):
    proxies = proxy_handling.load_proxies()
    if not proxies:
        proxy_handling.update_proxies()
        proxies = proxy_handling.load_proxies_from_file()
    tries = 3  # number of tries for each proxy
    for proxy in reversed(proxies):
        for i in range(1, tries + 1):  # how many tries for each proxy
            try:
                # print('%i iteration of proxy %s' % (i, proxy), end="")
                proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
                opener = urllib.request.build_opener(proxy_handler)
                urllib.request.install_opener(opener)
                headers = get_rosreestr_headers()

                request = Request(url, headers=headers)
                context = ssl._create_unverified_context()
                with urlopen(request, context=context, timeout=3000) as response:
                    read = response.read()
                return read
            except Exception as er:
                print(er)
                logger.warning(er)
            if i == tries:
                proxies.remove(proxy)
                proxy_handling.dump_proxies_to_file(proxies)

    # if here, the result is not received
    # try with the new proxy list
    return make_request_with_proxy(url)
