import re


class DocumentcloudService(object):
    DOCUMENTCLOUD_LINK_PATTERN = (
        r'https://www.documentcloud\.org/documents/(?P<documentcloud_id>\d+)-(?P<normalized_title>[^/]+)\.html'
    )
    DOCUMENTCLOUD_ID_PATTERN = r'(?P<documentcloud_id>\d+)-.*'

    def parse_link(self, link):
        '''
        Check if this link is valid DocumentCloud link
        Example link: https://www.documentcloud.org/documents/1273509-cr-1002643.html
        '''
        pattern = re.compile(self.DOCUMENTCLOUD_LINK_PATTERN)

        matched = re.match(pattern, link)
        if matched:
            return {
                'documentcloud_id': matched.group('documentcloud_id'),
                'normalized_title': matched.group('normalized_title')
            }

        return {}

    def parse_id(self, documentcloud_id):
        pattern = re.compile(self.DOCUMENTCLOUD_ID_PATTERN)
        matched = re.match(pattern, documentcloud_id)
        if matched:
            return matched.group('documentcloud_id')

    def parse_crid_from_title(self, documentcloud_title, document_type='CR'):
        '''
        Parse title to get allegation CRID
        '''
        pattern = re.compile(
            r'^CRID([- ])(?P<crid>\d+)([- ])(?P<document_type>{document_type}).*'.format(document_type=document_type)
        )

        matched = re.match(pattern, documentcloud_title)
        if matched:
            return matched.group('crid')

        return
