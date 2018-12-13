import datetime

from django.core import management
from django.test import TestCase

from mock import patch, MagicMock, call
from robber import expect
import pytz

from data.constants import MEDIA_TYPE_DOCUMENT, AttachmentSourceType
from data.factories import AllegationFactory, AttachmentFileFactory
from data.models import AttachmentFile, Allegation
from document_cloud.factories import DocumentCloudSearchQueryFactory
from document_cloud.management.commands.update_documents import Command
from document_cloud.models import DocumentCrawler
from document_cloud.tests.mixins import DocumentcloudTestCaseMixin
from email_service.factories import EmailTemplateFactory
from email_service.constants import ATTACHMENT_AVAILABLE
from shared.tests.utils import create_object


class UpdateDocumentsCommandTestCase(DocumentcloudTestCaseMixin, TestCase):
    def test_get_search_syntaxes(self):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)

        queries = DocumentCloudSearchQueryFactory.create_batch(2)

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            mock_search = mock_documentcloud().documents.search
            mock_search.return_value = None
            management.call_command('update_documents')

            expect(mock_search.call_args_list).to.eq([
                call(queries[0].query),
                call(queries[1].query)
            ])

    def test_get_call_process_documentcloud_document(self):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)
        query = DocumentCloudSearchQueryFactory()

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            with patch(
                'document_cloud.management.commands.update_documents.Command.process_documentcloud_document',
                return_value=None
            ) as mock_process:
                cleaned_result = MagicMock(title='title')
                mock_search = mock_documentcloud().documents.search
                mock_search.return_value = [cleaned_result]

                management.call_command('update_documents')

                mock_process.assert_called_with(cleaned_result, query.type)

    def test_skip_empty_syntaxes(self):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)
        queries = [
            DocumentCloudSearchQueryFactory(),
            DocumentCloudSearchQueryFactory(query='')
        ]

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            mock_search = mock_documentcloud().documents.search
            mock_search.return_value = None

            management.call_command('update_documents')

            mock_search.assert_called_once_with(queries[0].query)

    def test_create_crawler_log(self):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)

        expect(DocumentCrawler.objects.count()).to.eq(0)

        management.call_command('update_documents')

        expect(DocumentCrawler.objects.count()).to.eq(1)

    def test_clean_results_remove_duplicate(self):
        command = Command()
        raw_results = [
            MagicMock(title='abc'),
            MagicMock(title='abc')
        ]

        results = command.clean_documents(raw_results)

        expect(results).to.eq(raw_results[:1])

    @patch('document_cloud.management.commands.update_documents.AUTO_UPLOAD_DESCRIPTION', 'AUTO_UPLOAD_DESCRIPTION')
    def test_clean_results_remove_invalid_source(self):
        command = Command()
        raw_results = [
            MagicMock(title='abc 1', description=''),
            MagicMock(title='abc 2', description='AUTO_UPLOAD_DESCRIPTION')
        ]

        results = command.clean_documents(raw_results)

        expect(results).to.eq(raw_results[:1])

    def test_process_no_crid(self):
        command = Command()
        AttachmentFileFactory(title='old')

        command.process_documentcloud_document(MagicMock(title='new', id='456-CRID-123456-CR'), 'CR')

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('old')

    def test_process_invalid_crid(self):
        command = Command()
        AttachmentFileFactory(title='old')

        command.process_documentcloud_document(MagicMock(title='CRID 12 CR', id='456-CRID-123456-CR'), 'CR')

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('old')

    def test_process_invalid_document_cloud_id(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')
        AttachmentFileFactory(title='old', allegation=allegation)

        command.process_documentcloud_document(MagicMock(title='CRID 123456 CR', id='invalid id'), 'CR')

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('old')

    def test_update_title_if_title_changed(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')
        AttachmentFileFactory(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            external_id='789',
            title='CRID 123456 CR',
            allegation=allegation,
            url='https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'
        )

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR New',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'})
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('CRID 123456 CR New')
        expect(AttachmentFile.objects.first().source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)

    def test_update_source_type_if_empty(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')
        AttachmentFileFactory(
            source_type='',
            external_id='789',
            title='CRID 123456 CR',
            allegation=allegation,
            original_url='https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf',
            url='https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf',
            external_created_at=datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
            external_last_updated=datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
            preview_image_url='https://www.documentcloud.org/documents/789-CRID-123456-CR.html'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().source_type).to.eq('')

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'}),
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)

    def test_insert_new_document_if_allegation_existed(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')

        expect(AttachmentFile.objects.count()).to.eq(0)

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'})
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        media = AttachmentFile.objects.first()
        expect(media.title).to.eq('CRID 123456 CR')
        expect(media.source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(media.url).to.eq('https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf')
        expect(media.allegation.id).to.eq(allegation.id)

    def test_insert_new_document_with_missing_resources_object(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')

        expect(AttachmentFile.objects.count()).to.eq(0)

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        media = AttachmentFile.objects.first()
        expect(media.title).to.eq('CRID 123456 CR')
        expect(media.source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(media.url).to.eq('https://www.documentcloud.org/documents/789-CRID-123456-CR.html')
        expect(media.allegation.id).to.eq(allegation.id)

    def test_insert_new_document_with_missing_resources_pdf_link(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')

        expect(AttachmentFile.objects.count()).to.eq(0)

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({})
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(1)
        media = AttachmentFile.objects.first()
        expect(media.title).to.eq('CRID 123456 CR')
        expect(media.source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(media.url).to.eq('https://www.documentcloud.org/documents/789-CRID-123456-CR.html')
        expect(media.allegation.id).to.eq(allegation.id)

    def test_not_process_if_allegation_not_existed(self):
        command = Command()

        expect(AttachmentFile.objects.count()).to.eq(0)

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID CRID CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-CRID-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-CRID-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-CRID-CR.pdf'})
            }), 'CR'
        )

        expect(AttachmentFile.objects.count()).to.eq(0)

    def test_replace_hyphen_with_space(self):
        command = Command()
        allegation = AllegationFactory(crid='123456')

        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR new-document',
                'id': '456-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/456-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/456-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/456/CRID-123456-CR.pdf'})
            }), 'CR'
        )
        command.process_documentcloud_document(
            create_object({
                'title': 'CRID 123456 CR new - document',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'})
            }), 'CR'
        )

        media456 = AttachmentFile.objects.first()
        expect(media456.allegation.id).to.eq(allegation.id)
        expect(media456.external_id).to.eq('456')
        expect(media456.title).to.eq('CRID 123456 CR new document')

        media789 = AttachmentFile.objects.last()
        expect(media789.allegation.id).to.eq(allegation.id)
        expect(media789.external_id).to.eq('789')
        expect(media789.title).to.eq('CRID 123456 CR new - document')

    @patch('document_cloud.management.commands.update_documents.DocumentCloud')
    def test_clean_not_exist_attachments(self, DocumentCloudMock):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)
        allegation = AllegationFactory(crid=123456)
        DocumentCloudSearchQueryFactory(type='CR', query='CR')
        AttachmentFileFactory(
            external_id='456',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            allegation=allegation,
            title='To be deleted',
            url='https://www.documentcloud.org/documents/456/to-be-deleted-CRID-123456-CR.pdf'
        )
        AttachmentFileFactory(
            external_id='789',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            allegation=allegation,
            title='To be updated',
            url='https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'
        )

        DocumentCloudMock().documents.search.return_value = [
            create_object({
                'title': 'CRID 123456 CR',
                'id': '789-CRID-123456-CR',
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'normal_image_url': 'normal_image.jpg',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'}),
            }),
            create_object({
                'title': 'CRID 123456 CR 2',
                'id': '012-CRID-123456-CR-2',
                'canonical_url': 'https://www.documentcloud.org/documents/012-CRID-123456-CR-2.html',
                'normal_image_url': 'normal_image_2.jpg',
                'created_at': datetime.datetime(2015, 12, 31, tzinfo=pytz.utc),
                'updated_at': datetime.datetime(2016, 1, 1, tzinfo=pytz.utc),
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/012/CRID-123456-CR-2.pdf'}),
            })
        ]

        old_cr = Allegation.objects.get(crid='123456')
        expect(old_cr.attachment_files.count()).to.eq(2)
        old_titles = set([attachment.title for attachment in old_cr.attachment_files.all()])
        expect(old_titles).to.eq({'To be deleted', 'To be updated'})

        management.call_command('update_documents')

        cr = Allegation.objects.get(crid='123456')

        expect(cr.attachment_files.count()).to.eq(2)
        titles = set([attachment.title for attachment in cr.attachment_files.all()])
        expect(titles).to.eq({'CRID 123456 CR', 'CRID 123456 CR 2'})

        expect(AttachmentFile.objects.filter(allegation=allegation).count()).to.eq(2)
        expect(Allegation.objects.get(crid='123456').attachment_files.count()).to.eq(2)

        crawling_log = DocumentCrawler.objects.last()
        expect(crawling_log.num_documents).to.equal(2)
        expect(crawling_log.num_new_documents).to.equal(1)
        expect(crawling_log.num_updated_documents).to.equal(1)

    @patch('document_cloud.management.commands.update_documents.DocumentCloud')
    def test_attachments_unchanged(self, DocumentCloudMock):
        EmailTemplateFactory(type=ATTACHMENT_AVAILABLE)
        DocumentCloudSearchQueryFactory(type='CR', query='CR')
        AttachmentFileFactory(
            external_id='789',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            allegation__crid='123456',
            title='CRID 123456 CR',
            tag='CR',
            url='https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf',
            preview_image_url='https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
            external_last_updated=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
            external_created_at=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc)
        )

        DocumentCloudMock().documents.search.return_value = [
            create_object({
                'id': '789-CRID-123456-CR',
                'title': 'CRID 123456 CR',
                'url': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf',
                'normal_image_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'updated_at': datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                'created_at': datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                'canonical_url': 'https://www.documentcloud.org/documents/789-CRID-123456-CR.html',
                'resources': create_object({'pdf': 'https://www.documentcloud.org/documents/789/CRID-123456-CR.pdf'}),
            })
        ]

        management.call_command('update_documents')

        cr = Allegation.objects.get(crid='123456')
        expect(cr.attachment_files.count()).to.eq(1)
        titles = set([attachment.title for attachment in cr.attachment_files.all()])
        expect(titles).to.eq({'CRID 123456 CR'})

        crawling_log = DocumentCrawler.objects.last()
        expect(crawling_log.num_documents).to.equal(1)
        expect(crawling_log.num_new_documents).to.equal(0)
        expect(crawling_log.num_updated_documents).to.equal(0)
