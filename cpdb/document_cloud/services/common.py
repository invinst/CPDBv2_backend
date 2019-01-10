from urllib.error import HTTPError


def get_full_text(cloud_document):
    try:
        return cloud_document.full_text
    except (HTTPError, NotImplementedError):
        return ''
