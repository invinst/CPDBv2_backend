import re


DOCUMENTCLOUD_LINK_PATTERN = (
    r'https://www.documentcloud\.org/documents/(?P<id>\d+)-(?P<normalized_title>[^/]+)\.html'
)
DOCUMENTCLOUD_ID_PATTERN = r'(?P<id>\d+)-.*'

DEFAULT_DOCUMENT_TYPE = 'CR'


def parse_link(link):
    """
    Check if this link is valid DocumentCloud link
    Example link: https://www.documentcloud.org/documents/1273509-cr-1002643.html
    """
    pattern = re.compile(DOCUMENTCLOUD_LINK_PATTERN)

    matched = re.match(pattern, link)
    if matched:
        return {
            'id': matched.group('id'),
            'normalized_title': matched.group('normalized_title')
        }

    return {}


def parse_id(id):
    pattern = re.compile(DOCUMENTCLOUD_ID_PATTERN)
    matched = re.match(pattern, id)
    if matched:
        return matched.group('id')


def parse_crid_and_type_from_title(documentcloud_title, document_types=[DEFAULT_DOCUMENT_TYPE]):
    """
    Parse title to get allegation CRID
    """
    pattern = re.compile(
        r'^CRID([- ])(?P<crid>(C?)\d+)([- ](?P<document_type>\w+))?.*'
    )

    matched = re.match(pattern, documentcloud_title)
    if matched:
        document_type = matched.group('document_type')
        document_type = document_type if document_type in document_types else DEFAULT_DOCUMENT_TYPE
        return {'crid': matched.group('crid'), 'document_type': document_type}

    return {}


def get_url(document):
    document_url = document.canonical_url
    try:
        document_url = document.resources.pdf or document_url
    except AttributeError:
        pass
    return document_url


def format_copa_documentcloud_title(crid, attachment_title):
    return f'CRID {crid} CR {attachment_title}'
