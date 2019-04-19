import logging
from datetime import datetime

from django.test import override_settings
from django.test.testcases import TestCase

import pytz
from mock import patch, Mock, PropertyMock
from robber import expect
from freezegun import freeze_time

from document_cloud.constants import DOCUMENT_CRAWLER_SUCCESS, DOCUMENT_CRAWLER_FAILED
from document_cloud.factories import DocumentCrawlerFactory
from document_cloud.models import DocumentCrawler
from data.factories import AllegationCategoryFactory, AllegationFactory, AttachmentFileFactory
from data.models import Allegation, AttachmentFile

from data_importer.copa_crawler.importers import (
    CopaPortalAttachmentImporter,
    CopaSummaryReportsAttachmentImporter,
    CopaBaseAttachmentImporter
)
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO


class CopaBaseAttachmentImporterTestCase(TestCase):
    def test_raise_NotImplementedError(self):
        logger = logging.getLogger('crawler.crawl_copa_data')
        expect(CopaBaseAttachmentImporter(logger).crawl_copa).to.throw(NotImplementedError)


@override_settings(S3_BUCKET_CRAWLER_LOG='crawler_logs_bucket')
class CopaPortalAttachmentImporterTestCase(TestCase):
    @patch('data_importer.copa_crawler.importers.OpenCopaInvestigationCrawler')
    @patch('data_importer.copa_crawler.importers.ComplaintCrawler')
    def test_crawl_copa(self, complaint_crawler, link_crawler):
        link_crawler.return_value.crawl.return_value = ['link 1']
        complaint_crawler.return_value.crawl.return_value = {
            'attachments': [
                {
                    'type': 'Audio',
                    'link': 'http://audio_link',
                    'title': 'Audio Clip',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '1',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject1', 'Unknown'],
        }
        logger = logging.getLogger('crawler.crawl_copa_data')
        expect(CopaPortalAttachmentImporter(logger).crawl_copa()).to.be.eq([{
            'allegation': {
                'crid': '1',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'audio',
                    'title': 'Audio Clip',
                    'url': 'http://audio_link',
                    'original_url': 'http://audio_link',
                    'tag': 'Audio',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }])

    def test_parse_incidents(self):
        logger = logging.getLogger('crawler.crawl_copa_data')
        incidents = [{
            'attachments': [
                {
                    'type': 'Audio',
                    'link': 'http://audio_link',
                    'title': 'Audio Clip',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '1',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject1', 'Unknown'],
        }]
        expect(CopaPortalAttachmentImporter(logger).parse_incidents(incidents)).to.be.eq([{
            'allegation': {
                'crid': '1',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'audio',
                    'title': 'Audio Clip',
                    'url': 'http://audio_link',
                    'original_url': 'http://audio_link',
                    'tag': 'Audio',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }])

    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.upload_to_documentcloud')
    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa')
    @patch('shared.attachment_importer.aws')
    def test_crawl_and_update_attachments(self, aws_mock, crawl_copa, _):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'allegation': {
                'crid': '123',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'audio',
                    'title': 'Audio Clip',
                    'url': 'http://chicagocopa.org/audio_link.mp3',
                    'original_url': 'http://chicagocopa.org/audio_link.mp3',
                    'tag': 'Audio',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }, {
                    'file_type': 'document',
                    'title': 'Document',
                    'url': 'http://chicagocopa.org/document.pdf',
                    'original_url': 'http://chicagocopa.org/document.pdf',
                    'tag': 'Document',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2017, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject', '', 'Unknown'],
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }, {
            'allegation': {
                'crid': '456',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'Document',
                    'url': 'http://chicagocopa.org/other.pdf',
                    'original_url': 'http://chicagocopa.org/other.pdf',
                    'tag': 'Document',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2017, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject 2'],
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        allegation = AllegationFactory(crid='123')
        attachment_file = AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf')
        expect(DocumentCrawler.objects.count()).to.eq(0)
        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').attachment_files.count()).to.eq(1)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()

        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').subjects).to.eq(['Subject'])
        expect(AttachmentFile.objects.filter(allegation=allegation).count()).to.eq(2)
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).source_type).to.eq(AttachmentSourceType.PORTAL_COPA)

        expect(DocumentCrawler.objects.count()).to.eq(1)
        crawler_log = DocumentCrawler.objects.first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.PORTAL_COPA)
        expect(crawler_log.num_documents).to.eq(2)
        expect(crawler_log.num_new_documents).to.eq(1)
        expect(crawler_log.num_updated_documents).to.eq(1)

        expect(new_attachments).to.have.length(1)
        expect(new_attachments[0].title).to.eq('Audio Clip')
        expect(new_attachments[0].url).to.eq('http://chicagocopa.org/audio_link.mp3')

        log_content = b'Creating 1 attachments' \
                      b'\nUpdating 1 attachments' \
                      b'\nCurrent Total portal_copa attachments: 2' \
                      b'\nDone importing!'

        log_args = aws_mock.s3.put_object.call_args[1]
        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(log_content)
        expect(log_args['Bucket']).to.eq('crawler_logs_bucket')
        expect(log_args['Key']).to.eq('portal_copa/portal-copa-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.upload_to_documentcloud')
    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa')
    @patch('shared.attachment_importer.aws')
    def test_update(self, _, crawl_copa, __):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'allegation': {
                'crid': '123',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'CRID 123 CR pdf file',
                    'url': 'http://chicagocopa.org/document.pdf',
                    'original_url': 'http://chicagocopa.org/document.pdf',
                    'tag': 'Document',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        attachment_file = AttachmentFileFactory(
            allegation__crid='123',
            title='old_title',
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf')

        new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()

        expect(new_attachments).to.be.empty()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).title).to.eq('CRID 123 CR pdf file')

    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.upload_to_documentcloud')
    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa')
    @patch('data_importer.copa_crawler.portal_crawler.VimeoSimpleAPI.crawl')
    @patch('shared.attachment_importer.aws')
    def test_update_video_thumbnail(self, _, vimeo_api, crawl_copa, __):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'allegation': {
                'crid': '123',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'video',
                    'title': 'video file',
                    'url': 'https://player.vimeo.com/video/288225991',
                    'original_url': 'https://player.vimeo.com/video/288225991',
                    'tag': 'Video',
                    'source_type': 'PORTAL_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }]
        vimeo_api.return_value = {
            'id': 288225991,
            'title': 'Log# 1082195 3rd Party Clip',
            'description': 'Log# 1082195 3rd Party Clip',
            'url': 'https://vimeo.com/307768537',
            'upload_date': '2018-12-21 15:47:48',
            'thumbnail_small': 'https://i.vimeocdn.com/video/747800241_100x75.webp',
            'thumbnail_medium': 'https://i.vimeocdn.com/video/747800241_200x150.webp',
            'thumbnail_large': 'https://i.vimeocdn.com/video/747800241_640.webp',
        }
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        attachment_file = AttachmentFileFactory(
            allegation__crid='123',
            title='old_title',
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_id='288225991',
            original_url='https://player.vimeo.com/video/288225991',
            preview_image_url=None
        )

        CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).title).to.eq('video file')
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).preview_image_url). \
            to.eq('https://i.vimeocdn.com/video/747800241_100x75.webp')

    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa')
    @patch('shared.attachment_importer.aws')
    def test_not_update_video_thumbnail_when_source_is_not_vimeo(self, _, crawl_copa):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'attachments': [
                {
                    'type': 'video',
                    'link': 'https://player.fake_video.org/video/288225991',
                    'title': 'video file',
                    'last_updated': '2018-10-30T15:00:03+00:00',
                }
            ],
            'date': '04-30-2013',
            'log_number': '123',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject', '', 'Unknown'],
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        attachment_file = AttachmentFileFactory(
            allegation__crid='123',
            title='old_title',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='288225991',
            original_url='https://player.fake_video.org/video/288225991',
            preview_image_url=None
        )

        CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).preview_image_url).be.none()

    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa')
    @patch('shared.attachment_importer.aws')
    def test_update_PORTAL_COPA_DOCUMENTCLOUD_file(self, _, crawl_copa):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'allegation': {
                'crid': '123',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'pdf file',
                    'url': 'http://chicagocopa.org/document.pdf',
                    'original_url': 'http://chicagocopa.org/document.pdf',
                    'tag': 'Document',
                    'source_type': 'PORTAL_COPA_DOCUMENTCLOUD',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        attachment_file = AttachmentFileFactory(
            allegation__crid='123',
            title='old_title',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf',
            external_last_updated=datetime(2017, 10, 30, tzinfo=pytz.utc)
        )

        new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(new_attachments).to.be.empty()

        updated_attachment_file = AttachmentFile.objects.get(pk=attachment_file.pk)
        expect(updated_attachment_file.title).to.eq('CRID 123 CR pdf file')
        expect(updated_attachment_file.external_last_updated).to.eq(datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc))

    @patch(
        'data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_copa',
        side_effect=Mock(side_effect=[Exception()])
    )
    @patch('shared.attachment_importer.aws')
    def test_failed_crawl_and_update_attachments(self, aws_mock, _):
        logger = logging.getLogger('crawler.crawl_copa_data')

        with freeze_time(datetime(2018, 4, 2, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.PORTAL_COPA,
                status=DOCUMENT_CRAWLER_SUCCESS,
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1,
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.PORTAL_COPA,
                status=DOCUMENT_CRAWLER_FAILED,
                num_successful_run=1,
            )

        expect(expect(DocumentCrawler.objects.count())).to.eq(2)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()

        expect(new_attachments).to.eq([])
        expect(DocumentCrawler.objects.count()).to.eq(3)
        crawler_log = DocumentCrawler.objects.order_by('-created_at').first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.PORTAL_COPA)
        expect(crawler_log.status).to.eq(DOCUMENT_CRAWLER_FAILED)
        expect(crawler_log.num_documents).to.eq(0)
        expect(crawler_log.num_new_documents).to.eq(0)
        expect(crawler_log.num_updated_documents).to.eq(0)
        expect(crawler_log.num_successful_run).to.eq(1)
        expect(crawler_log.log_key).to.eq('portal_copa/portal-copa-2018-04-04-120001.txt')

        log_content = b'\nCreating 0 attachments' \
                      b'\nUpdating 0 attachments' \
                      b'\nCurrent Total portal_copa attachments: 0' \
                      b'\nERROR: Error occurred while CRAWLING!'

        log_args = aws_mock.s3.put_object.call_args[1]
        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(log_content)
        expect(log_args['Bucket']).to.contain('crawler_logs_bucket')
        expect(log_args['Key']).to.contain('portal_copa/portal-copa-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    @patch('data_importer.copa_crawler.importers.DocumentCloud')
    def test_upload_portal_copa_documents(self, DocumentCloudMock):
        logger = logging.getLogger('crawler.crawl_copa_data')
        DocumentCloudMock().documents.upload.return_value = PropertyMock(
            id='5396984-crid-123-cr-tactical-response-report',
            title='CRID 123 CR Tactical Response Report',
            canonical_url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            normal_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
            created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            updated_at=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            resources=None
        )

        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            external_id='123-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            upload_fail_attempts=1
        )

        CopaPortalAttachmentImporter(logger).upload_to_documentcloud()

        AttachmentFile.objects.get(pending_documentcloud_id='5396984')
        expect(DocumentCloudMock().documents.upload).to.be.called_with(
            'https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            title='CRID 123 CR Tactical Response Report',
            description=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            access='public',
            force_ocr=True
        )

    @patch('data_importer.copa_crawler.importers.DocumentCloud')
    def test_upload_portal_copa_documents_no_upload(self, DocumentCloudMock):
        logger = logging.getLogger('crawler.crawl_copa_data')
        allegation = AllegationFactory()
        AttachmentFileFactory(
            external_id='456-OCIR-2-Redacted.pdf',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            external_id='log-1086285-oemc-transmission-1',
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_AUDIO
        )
        AttachmentFileFactory(
            external_id='456-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2018/10/Log-1086456-TRR-Redacted.pdf',
            upload_fail_attempts=6
        )

        CopaPortalAttachmentImporter(logger).upload_to_documentcloud()
        expect(DocumentCloudMock().documents.upload).not_to.be.called()


@override_settings(S3_BUCKET_CRAWLER_LOG='crawler_logs_bucket')
class CopaSummaryReportsAttachmentImporterTestCase(TestCase):
    @patch('data_importer.copa_crawler.importers.OpenCopaYearSummaryReportsCrawler')
    @patch('data_importer.copa_crawler.importers.OpenCopaSummaryReportsCrawler')
    def test_crawl_copa(self, reports_crawler, year_crawler):
        reports_crawler.return_value.crawl.return_value = ['link 1']
        year_crawler.return_value.crawl.return_value = [{
            'attachments': [
                {
                    'link': 'https://www.chicagocopa.org/wp-content/uploads/2018/12/Log-1086683-9.27.pdf',
                    'last_updated': 'October 25, 2018'
                }
            ],
            'log_num': '1086683',
        }]

        logger = logging.getLogger('crawler.crawl_copa_data')
        expect(CopaSummaryReportsAttachmentImporter(logger).crawl_copa()).to.be.eq([{
            'allegation': {
                'crid': '1086683',
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'COPA Summary Report',
                    'url': 'https://www.chicagocopa.org/wp-content/uploads/2018/12/Log-1086683-9.27.pdf',
                    'original_url': 'https://www.chicagocopa.org/wp-content/uploads/2018/12/Log-1086683-9.27.pdf',
                    'source_type': 'SUMMARY_REPORTS_COPA',
                    'external_last_updated': datetime(2018, 10, 25, 0, 0, 0, tzinfo=pytz.utc),
                }],
            },
        }])

    @patch('data_importer.copa_crawler.importers.CopaSummaryReportsAttachmentImporter.upload_to_documentcloud')
    @patch('data_importer.copa_crawler.importers.CopaSummaryReportsAttachmentImporter.crawl_copa')
    @patch('shared.attachment_importer.aws')
    def test_crawl_and_update_attachments(self, aws_mock, crawl_copa, _):
        logger = logging.getLogger('crawler.crawl_copa_data')
        crawl_copa.return_value = [{
            'allegation': {
                'crid': '123',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'Some Document',
                    'url': 'http://chicagocopa.org/document_link.pdf',
                    'original_url': 'http://chicagocopa.org/document_link.pdf',
                    'tag': 'Document',
                    'source_type': 'SUMMARY_REPORTS_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }, {
                    'file_type': 'document',
                    'title': 'Some Document',
                    'url': 'http://chicagocopa.org/document.pdf',
                    'original_url': 'http://chicagocopa.org/document.pdf',
                    'tag': 'Document',
                    'source_type': 'SUMMARY_REPORTS_COPA',
                    'external_last_updated': datetime(2017, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }, {
            'allegation': {
                'crid': '456',
                'incident_date': datetime(2013, 4, 30, 21, 30, tzinfo=pytz.utc),
                'attachment_files': [{
                    'file_type': 'document',
                    'title': 'Some PDF',
                    'url': 'http://chicagocopa.org/other.pdf',
                    'original_url': 'http://chicagocopa.org/other.pdf',
                    'tag': 'Document',
                    'source_type': 'SUMMARY_REPORTS_COPA',
                    'external_last_updated': datetime(2017, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }]

        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        with freeze_time(datetime(2018, 4, 2, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
                status=DOCUMENT_CRAWLER_SUCCESS,
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1,
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
                status=DOCUMENT_CRAWLER_FAILED,
                num_successful_run=1,
            )
        allegation = AllegationFactory(crid='123')
        attachment_file = AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf')

        expect(expect(DocumentCrawler.objects.count())).to.eq(2)
        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').attachment_files.count()).to.eq(1)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            new_attachments = CopaSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()

        expect(Allegation.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.filter(allegation=allegation).count()).to.eq(2)
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).source_type).to.eq(
            AttachmentSourceType.SUMMARY_REPORTS_COPA
        )

        expect(DocumentCrawler.objects.count()).to.eq(3)
        crawler_log = DocumentCrawler.objects.order_by('-created_at').first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.SUMMARY_REPORTS_COPA)
        expect(crawler_log.status).to.eq(DOCUMENT_CRAWLER_SUCCESS)
        expect(crawler_log.num_documents).to.eq(2)
        expect(crawler_log.num_new_documents).to.eq(1)
        expect(crawler_log.num_updated_documents).to.eq(1)
        expect(crawler_log.num_successful_run).to.eq(2)

        expect(new_attachments).to.have.length(1)
        expect(new_attachments[0].url).to.eq('http://chicagocopa.org/document_link.pdf')

        log_content = b'\nCreating 1 attachments' \
                      b'\nUpdating 1 attachments' \
                      b'\nCurrent Total summary_reports_copa attachments: 2' \
                      b'\nDone importing!'
        log_args = aws_mock.s3.put_object.call_args[1]
        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(log_content)
        expect(log_args['Bucket']).to.contain('crawler_logs_bucket')
        expect(log_args['Key']).to.contain('summary_reports_copa/summary-reports-copa-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    @patch(
        'data_importer.copa_crawler.importers.CopaSummaryReportsAttachmentImporter.crawl_copa',
        side_effect=Mock(side_effect=[Exception()])
    )
    @patch('shared.attachment_importer.aws')
    def test_failed_crawl_and_update_attachments(self, aws_mock, _):
        logger = logging.getLogger('crawler.crawl_copa_data')

        with freeze_time(datetime(2018, 4, 2, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
                status=DOCUMENT_CRAWLER_SUCCESS,
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1,
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
                status=DOCUMENT_CRAWLER_FAILED,
                num_successful_run=1,
            )

        expect(expect(DocumentCrawler.objects.count())).to.eq(2)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            new_attachments = CopaSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()

        expect(new_attachments).to.eq([])
        expect(DocumentCrawler.objects.count()).to.eq(3)
        crawler_log = DocumentCrawler.objects.order_by('-created_at').first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.SUMMARY_REPORTS_COPA)
        expect(crawler_log.status).to.eq(DOCUMENT_CRAWLER_FAILED)
        expect(crawler_log.num_documents).to.eq(0)
        expect(crawler_log.num_new_documents).to.eq(0)
        expect(crawler_log.num_updated_documents).to.eq(0)
        expect(crawler_log.num_successful_run).to.eq(1)
        expect(crawler_log.log_key).to.eq('summary_reports_copa/summary-reports-copa-2018-04-04-120001.txt')

        log_content = b'\nCreating 0 attachments' \
                      b'\nUpdating 0 attachments' \
                      b'\nCurrent Total summary_reports_copa attachments: 0' \
                      b'\nERROR: Error occurred while CRAWLING!'

        log_args = aws_mock.s3.put_object.call_args[1]
        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(log_content)
        expect(log_args['Bucket']).to.eq('crawler_logs_bucket')
        expect(log_args['Key']).to.eq('summary_reports_copa/summary-reports-copa-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    @patch('data_importer.copa_crawler.importers.DocumentCloud')
    def test_upload_summary_reports_copa_documents(self, DocumentCloudMock):
        logger = logging.getLogger('crawler.crawl_copa_data')
        DocumentCloudMock().documents.upload.return_value = PropertyMock(
            id='5396984-crid-123-cr-tactical-response-report',
            title='CRID 123 CR Tactical Response Report',
            canonical_url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            normal_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
            created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            updated_at=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            resources=None
        )

        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            external_id='123-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='COPA Summary Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            upload_fail_attempts=1,
        )

        CopaSummaryReportsAttachmentImporter(logger).upload_to_documentcloud()

        AttachmentFile.objects.get(pending_documentcloud_id='5396984')
        expect(DocumentCloudMock().documents.upload).to.be.called_with(
            'https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            title='CRID 123 CR COPA Summary Report',
            description=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            access='public',
            force_ocr=True
        )

    @patch('data_importer.copa_crawler.importers.DocumentCloud')
    def test_upload_summary_reports_copa_documents_no_upload(self, DocumentCloudMock):
        logger = logging.getLogger('crawler.crawl_copa_data')
        allegation = AllegationFactory()
        AttachmentFileFactory(
            external_id='456-OCIR-2-Redacted.pdf',
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            external_id='log-1086285-oemc-transmission-1',
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
            file_type=MEDIA_TYPE_AUDIO
        )
        AttachmentFileFactory(
            external_id='456-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2018/10/Log-1086456-TRR-Redacted.pdf',
            upload_fail_attempts=6
        )

        CopaSummaryReportsAttachmentImporter(logger).upload_to_documentcloud()
        expect(DocumentCloudMock().documents.upload).not_to.be.called()
