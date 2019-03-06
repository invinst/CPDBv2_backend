from django.test import TestCase
from mock import patch
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory, AllegationFactory
from document_cloud.factories import DocumentCloudSearchQueryFactory
from document_cloud.search import search_all
from shared.tests.utils import create_object


class SearchTestCase(TestCase):
    @patch('document_cloud.search.DocumentCloud')
    def test_search_all(self, DocumentCloudMock):
        DocumentCloudSearchQueryFactory(type='CR', query='CR')
        DocumentCloudSearchQueryFactory(type='TRR', query='')

        allegation = AllegationFactory(crid='123')

        AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='1',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='2',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            external_id='7',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            external_id='4',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_id='5',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='6',
            allegation=allegation
        )

        copa_document_no_crid = create_object({
            'id': '1-CRID-CR',
            'description': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/1-CRID-CR.html',
            'title': 'no crid'
        })

        copa_document = create_object({
            'id': '2-CRID-123-CR',
            'title': 'CRID-123 CR',
            'description': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
        })
        should_be_filtered_copa_document = create_object({
            'id': '3-CRID-123-CR',
            'title': 'CRID-123 CR',
            'description': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/3-CRID-123-CR.html',
        })
        cloud_document = create_object({
            'id': '4-CRID-123-CR',
            'title': 'CRID-123 CR',
            'description': 'some description',
            'canonical_url': 'https://www.documentcloud.org/documents/4-CRID-123-CR.html',
        })
        new_cloud_document = create_object({
            'id': '5-CRID-123-CR',
            'title': 'CRID-123 CR 2',
            'canonical_url': 'https://www.documentcloud.org/documents/5-CRID-123-CR.html',
        })
        duplicated_cloud_document = create_object({
            'id': '9999-CRID-456-CR',
            'title': 'CRID-123 CR',
            'canonical_url': 'https://www.documentcloud.org/documents/999-CRID-123-CR.html',
        })
        summary_reports_copa_document = create_object({
            'id': '7-CRID-123-CR',
            'title': 'CRID-123 CR 7',
            'description': AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/7-CRID-123-CR.html',
        })

        DocumentCloudMock().documents.search.return_value = [
            copa_document_no_crid, copa_document, should_be_filtered_copa_document,
            duplicated_cloud_document, cloud_document, new_cloud_document, summary_reports_copa_document
        ]

        documents = search_all()

        expectation_dict = {
            '1-CRID-CR': {
                'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
                'documentcloud_id': '1',
                'url': 'https://www.documentcloud.org/documents/1-CRID-CR.html',
                'document_type': 'CR',
                'allegation': None
            },
            '2-CRID-123-CR': {
                'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
                'documentcloud_id': '2',
                'url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
                'document_type': 'CR',
                'allegation': allegation
            },
            '7-CRID-123-CR': {
                'source_type': AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
                'documentcloud_id': '7',
                'url': 'https://www.documentcloud.org/documents/7-CRID-123-CR.html',
                'document_type': 'CR',
                'allegation': allegation
            },
            '4-CRID-123-CR': {
                'source_type': AttachmentSourceType.DOCUMENTCLOUD,
                'documentcloud_id': '4',
                'url': 'https://www.documentcloud.org/documents/4-CRID-123-CR.html',
                'document_type': 'CR',
                'allegation': allegation
            },
            '5-CRID-123-CR': {
                'source_type': AttachmentSourceType.DOCUMENTCLOUD,
                'documentcloud_id': '5',
                'url': 'https://www.documentcloud.org/documents/5-CRID-123-CR.html',
                'document_type': 'CR',
                'allegation': allegation
            },
        }

        expect(documents).to.have.length(5)
        for document in documents:
            expect(document.id in expectation_dict).to.be.true()
            expectation = expectation_dict[document.id]
            for field, value in expectation.items():
                expect(getattr(document, field)).to.eq(value)
