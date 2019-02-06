import re
from urllib.error import HTTPError


def get_full_text(cloud_document):
    try:
        return re.sub(r'(\n *)+', '\n', cloud_document.full_text.decode('utf8')).strip()
    except (HTTPError, NotImplementedError):
        return ''
