from django.test import TestCase, override_settings
from robber import expect

from mock import MagicMock
from document_cloud.services.documentcloud_service import DocumentcloudService

from data.factories import AttachmentFileFactory


class DocumentcloudServiceTestCase(TestCase):
    def setUp(self):
        self.service = DocumentcloudService()

    def test_parse_document_cloud_link(self):
        link = 'https://www.documentcloud.org/documents/1273509-cr-1002643.html'
        expect(self.service.parse_link(link)).to.eq({
            'documentcloud_id': '1273509',
            'normalized_title': 'cr-1002643'
        })

    def test_parse_not_document_cloud_link(self):
        link = 'https://foo.com/bar/'
        expect(self.service.parse_link(link)).to.eq({})

    def test_parse_existed_crid_from_title(self):
        document_title = 'CRID-123456 CR'
        expect(self.service.parse_crid_from_title(document_title)).to.eq('123456')

    def test_parse_not_existed_crid_from_title(self):
        document_title = 'DOCUMENT TITLE'
        expect(self.service.parse_crid_from_title(document_title)).to.be.false()

    def test_parse_crid_from_title_with_different_document_type(self):
        document_title = 'CRID-123456 FOO'
        expect(self.service.parse_crid_from_title(document_title, document_type='BAR')).to.be.false()

    @override_settings(DOMAIN='http://localhost')
    def test_update_document_meta_data(self):
        attachment_file = AttachmentFileFactory(allegation__crid='123456')
        document = MagicMock(data={})

        self.service.update_document_meta_data(document, attachment_file)
        expect(document.published_url).to.eq('http://localhost/complaint/123456/')
        expect(document.data).to.eq({'tag': 'CRID 123456'})
        document.put.assert_called()
