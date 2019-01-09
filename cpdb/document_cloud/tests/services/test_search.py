from django.test import TestCase
from mock import patch
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory, AllegationFactory
from document_cloud.constants import AUTO_UPLOAD_DESCRIPTION
from document_cloud.factories import DocumentCloudSearchQueryFactory
from document_cloud.services.search import (
    remove_invalid_documents, remove_duplicated, add_attributes, search_all,
)
from shared.tests.utils import create_object


class SearchTestCase(TestCase):
    def test_remove_invalid_documents(self):
        AttachmentFileFactory(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            external_id='1'
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA,
            external_id='2'
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='3'
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='4'
        )

        copa_document = create_object({
            'documentcloud_id': '3',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
        })
        should_be_filtered_copa_document = create_object({
            'documentcloud_id': '5',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
        })
        cloud_document = create_object({
            'documentcloud_id': '6',
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
        })

        result = list(remove_invalid_documents([
            copa_document, should_be_filtered_copa_document, cloud_document
        ]))

        expect(result).to.have.length(2)
        expect(result[0]).to.eq(copa_document)
        expect(result[1]).to.eq(cloud_document)

    def test_remove_duplicated(self):
        AttachmentFileFactory(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            external_id='4'
        )

        copa_document_1 = create_object({
            'title': 'copa_document_1',
            'documentcloud_id': '1',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
        })
        copa_document_2 = create_object({
            'title': 'copa_document_2',
            'documentcloud_id': '2',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
        })
        duplicated_cloud_document = create_object({
            'title': 'duplicated_title',
            'documentcloud_id': '3',
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
        })
        cloud_document = create_object({
            'title': 'duplicated_title',
            'documentcloud_id': '4',
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
        })
        new_cloud_document = create_object({
            'title': 'new_cloud_document',
            'documentcloud_id': '5',
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
        })

        result = remove_duplicated([
            duplicated_cloud_document, new_cloud_document, cloud_document,
            copa_document_2, copa_document_1
        ])

        expect(result).to.have.length(4)
        expect({document.documentcloud_id for document in result}).to.eq(
            {'1', '2', '4', '5'}
        )

    def test_add_attributes(self):
        allegation = AllegationFactory(crid='123')

        document_1 = create_object({
            'description': 'some description',
            'id': '1-CRID-CR',
            'canonical_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'no crid'
        })
        document_2 = create_object({
            'description': AUTO_UPLOAD_DESCRIPTION,
            'id': '2-CRID-123-CR',
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-123456-CR.html',
            'title': 'CRID-123 CR'
        })
        document_3 = create_object({
            'id': '3-CRID-456-CR',
            'canonical_url': 'https://www.documentcloud.org/documents/3-CRID-123456-CR.html',
            'title': 'CRID-456 CR'
        })

        documents = add_attributes([document_1, document_2, document_3], 'CR')

        expect(documents).to.have.length(3)

        expect(documents[0].source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(documents[0].url).to.eq('https://www.documentcloud.org/documents/1-CRID-123456-CR.html')
        expect(documents[0].documentcloud_id).to.eq('1')
        expect(documents[0].document_type).to.eq('CR')
        expect(documents[0].allegation).to.be.none()

        expect(documents[1].source_type).to.eq(AttachmentSourceType.COPA_DOCUMENTCLOUD)
        expect(documents[1].url).to.eq('https://www.documentcloud.org/documents/2-CRID-123456-CR.html')
        expect(documents[1].documentcloud_id).to.eq('2')
        expect(documents[1].document_type).to.eq('CR')
        expect(documents[1].allegation).to.eq(allegation)

        expect(documents[2].source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(documents[2].url).to.eq('https://www.documentcloud.org/documents/3-CRID-123456-CR.html')
        expect(documents[2].documentcloud_id).to.eq('3')
        expect(documents[2].document_type).to.eq('CR')
        expect(documents[2].allegation).to.be.none()

    @patch('document_cloud.services.search.DocumentCloud')
    def test_search_all(self, DocumentCloudMock):
        DocumentCloudSearchQueryFactory(type='CR', query='CR')
        DocumentCloudSearchQueryFactory(type='TRR', query='')

        allegation = AllegationFactory(crid='123')

        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='1',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='2',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            external_id='4',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA,
            external_id='5',
            allegation=allegation
        )
        AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='6',
            allegation=allegation
        )

        copa_document_no_crid = create_object({
            'id': '1-CRID-CR',
            'description': AUTO_UPLOAD_DESCRIPTION,
            'canonical_url': 'https://www.documentcloud.org/documents/1-CRID-CR.html',
            'title': 'no crid'
        })

        copa_document = create_object({
            'id': '2-CRID-123-CR',
            'title': 'CRID-123 CR',
            'description': AUTO_UPLOAD_DESCRIPTION,
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
        })
        should_be_filtered_copa_document = create_object({
            'id': '3-CRID-123-CR',
            'title': 'CRID-123 CR',
            'description': AUTO_UPLOAD_DESCRIPTION,
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

        DocumentCloudMock().documents.search.return_value = [
            copa_document_no_crid, copa_document, should_be_filtered_copa_document,
            duplicated_cloud_document, cloud_document, new_cloud_document
        ]

        documents = search_all()

        expectation_dict = {
            '1-CRID-CR': {
                'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
                'documentcloud_id': '1',
                'url': 'https://www.documentcloud.org/documents/1-CRID-CR.html',
                'document_type': 'CR',
                'allegation': None
            },
            '2-CRID-123-CR': {
                'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
                'documentcloud_id': '2',
                'url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
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
            }
        }

        expect(documents).to.have.length(4)
        for document in documents:
            expect(document.id in expectation_dict).to.be.true()
            expectation = expectation_dict[document.id]
            for field, value in expectation.items():
                expect(getattr(document, field)).to.eq(value)
