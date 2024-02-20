from django.test import TestCase
from robber import expect

from document_cloud.utils import parse_link, parse_crid_and_type_from_title, parse_id, format_copa_documentcloud_title


class DocumentcloudUtilsTestCase(TestCase):

    def test_parse_document_cloud_link(self):
        link = 'https://www.documentcloud.org/documents/1273509-cr-1002643.html'
        expect(parse_link(link)).to.eq({
            'id': '1273509',
            'normalized_title': 'cr-1002643'
        })

    def test_parse_not_document_cloud_link(self):
        link = 'https://foo.com/bar/'
        expect(parse_link(link)).to.eq({})

    def test_parse_id(self):
        id = '789-CRID-123456-CR'
        expect(parse_id(id)).to.eq('789')

    def test_parse_not_existed_id(self):
        id = 'CRID-123456-CR'
        expect(parse_id(id)).to.be.none()

    def test_parse_existed_crid_and_type_from_title(self):
        document_title = 'CRID-123456 CR'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': '123456', 'document_type': 'CR'})

    def test_parse_existed_crid_and_document_type_from_title(self):
        document_title = 'CRID-123456 DOCUMENT CPD 00001234'
        expect(parse_crid_and_type_from_title(document_title, document_types=['DOCUMENT'])).to.eq(
            {'crid': '123456', 'document_type': 'DOCUMENT'}
        )

    def test_parse_existed_crid_and_type_from_title_with_extra_text_space_separator_after_document_type(self):
        document_title = 'CRID-123456 CR extra things'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': '123456', 'document_type': 'CR'})

    def test_parse_existed_crid_and_type_from_title_with_extra_text_after_document_type(self):
        document_title = 'CRID-123456-CR-extra things'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': '123456', 'document_type': 'CR'})

    def test_parse_existed_crid_from_title_and_set_defaut_document_type(self):
        document_title = 'CRID-123456'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': '123456', 'document_type': 'CR'})

    def test_parse_existed_c_prefix_crid_and_type_from_title(self):
        document_title = 'CRID-C123456 CR'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': 'C123456', 'document_type': 'CR'})

    def test_parse_existed_c_prefix_crid_from_title_and_set_defaut_document_type(self):
        document_title = 'CRID-C123456'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': 'C123456', 'document_type': 'CR'})

    def test_parse_not_existed_crid_from_title(self):
        document_title = 'DOCUMENT TITLE'
        expect(parse_crid_and_type_from_title(document_title)).to.be.empty()

    def test_parse_crid_from_title_with_invalid_document_type_and_set_defaut_document_type(self):
        document_title = 'CRID-123456 FOO'
        expect(parse_crid_and_type_from_title(document_title)).to.eq({'crid': '123456', 'document_type': 'CR'})

    def test_parse_crid_from_title_with_valid_document_type(self):
        document_title = 'CRID-123456 TRR'
        expect(parse_crid_and_type_from_title(document_title, document_types=['TRR'])).to.eq(
            {'crid': '123456', 'document_type': 'TRR'}
        )

    def test_format_portal_copa_documentcloud_title(self):
        crid = '123'
        attachment_title = 'Officer Battery Report (Lopez)'
        documentcloud_title = format_copa_documentcloud_title(crid, attachment_title)
        expect(documentcloud_title).to.eq('CRID 123 CR Officer Battery Report (Lopez)')
