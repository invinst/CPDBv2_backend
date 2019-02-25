import re

from data.constants import AttachmentSourceType

DOCUMENTCLOUD_LINK_PATTERN = (
    r'https://www.documentcloud\.org/documents/(?P<documentcloud_id>\d+)-(?P<normalized_title>[^/]+)\.html'
)
DOCUMENTCLOUD_ID_PATTERN = r'(?P<documentcloud_id>\d+)-.*'


def parse_link(link):
    """
    Check if this link is valid DocumentCloud link
    Example link: https://www.documentcloud.org/documents/1273509-cr-1002643.html
    """
    pattern = re.compile(DOCUMENTCLOUD_LINK_PATTERN)

    matched = re.match(pattern, link)
    if matched:
        return {
            'documentcloud_id': matched.group('documentcloud_id'),
            'normalized_title': matched.group('normalized_title')
        }

    return {}


def parse_id(documentcloud_id):
    pattern = re.compile(DOCUMENTCLOUD_ID_PATTERN)
    matched = re.match(pattern, documentcloud_id)
    if matched:
        return matched.group('documentcloud_id')


def parse_crid_from_title(documentcloud_title, document_type='CR'):
    """
    Parse title to get allegation CRID
    """
    pattern = re.compile(
        r'^CRID([- ])(?P<crid>\d+)([- ])(?P<document_type>{document_type}).*'.format(document_type=document_type)
    )

    matched = re.match(pattern, documentcloud_title)
    if matched:
        return matched.group('crid')

    return


def get_url(document):
    document_url = document.canonical_url
    try:
        document_url = document.resources.pdf or document_url
    except AttributeError:
        pass
    return document_url


def format_copa_documentcloud_title(crid, attachment_title, copa_source):
    if copa_source == AttachmentSourceType.SUMMARY_REPORTS_COPA:
        return f'CRID {crid} {attachment_title}'
    else:
        return f'CRID {crid} CR {attachment_title}'
