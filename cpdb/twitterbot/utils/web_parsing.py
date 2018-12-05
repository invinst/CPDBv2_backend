import logging
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

import requests

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError


USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/41.0.2227.1 Safari/537.36')

logger = logging.getLogger(__name__)


def parse(url):
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT})
        html = response.content.decode('utf-8')
    except ConnectionError:
        logger.error('ConnectionError while parsing %s' % url)
        return ''
    except UnicodeError:
        logger.error('UnicodeError while parsing %s' % url)
        html = response.content.decode('utf-8', 'replace')
    soup = BeautifulSoup(html, 'html.parser')
    [s.decompose() for s in soup([
        'style',
        'script',
        '[document]',
        'head',
        'title'
    ])]
    text = ' '.join(soup.stripped_strings)

    return text


def add_params(url, params):
    url_parts = list(urlparse(url))
    query = parse_qs(url_parts[4])
    query.update(params)
    url_parts[4] = urlencode(query, True)
    return urlunparse(url_parts)
