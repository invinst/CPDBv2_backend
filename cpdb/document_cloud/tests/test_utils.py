from django.test import TestCase
from robber import expect

from data.constants import AttachmentSourceType
from document_cloud.utils import parse_link, parse_crid_from_title, parse_id, format_copa_documentcloud_title


class DocumentcloudUtilsTestCase(TestCase):

    def test_parse_document_cloud_link(self):
        link = 'https://www.documentcloud.org/documents/1273509-cr-1002643.html'
        expect(parse_link(link)).to.eq({
            'documentcloud_id': '1273509',
            'normalized_title': 'cr-1002643'
        })

    def test_parse_not_document_cloud_link(self):
        link = 'https://foo.com/bar/'
        expect(parse_link(link)).to.eq({})

    def test_parse_id(self):
        documentcloud_id = '789-CRID-123456-CR'
        expect(parse_id(documentcloud_id)).to.eq('789')

    def test_parse_not_existed_id(self):
        documentcloud_id = 'CRID-123456-CR'
        expect(parse_id(documentcloud_id)).to.be.none()

    def test_parse_existed_crid_from_title(self):
        document_title = 'CRID-123456 CR'
        expect(parse_crid_from_title(document_title)).to.eq('123456')

    def test_parse_not_existed_crid_from_title(self):
        document_title = 'DOCUMENT TITLE'
        expect(parse_crid_from_title(document_title)).to.be.false()

    def test_parse_crid_from_title_with_different_document_type(self):
        document_title = 'CRID-123456 FOO'
        expect(parse_crid_from_title(document_title, document_type='BAR')).to.be.false()

    def test_format_portal_copa_documentcloud_title(self):
        crid = '123'
        attachment_title = 'Officer Battery Report (Lopez)'
        documentcloud_title = format_copa_documentcloud_title(crid, attachment_title, AttachmentSourceType.PORTAL_COPA)
        expect(documentcloud_title).to.eq('CRID 123 CR Officer Battery Report (Lopez)')

    def test_format_summary_reports_copa_documentcloud_title(self):
        crid = '123'
        attachment_title = 'COPA Summary Report'
        documentcloud_title = format_copa_documentcloud_title(
            crid, attachment_title, AttachmentSourceType.SUMMARY_REPORTS_COPA
        )
        expect(documentcloud_title).to.eq('CRID 123 COPA Summary Report')
