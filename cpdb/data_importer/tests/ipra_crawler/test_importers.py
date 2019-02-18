import logging
from datetime import datetime

from django.test.testcases import TestCase

import pytz
from mock import patch
from robber import expect

from document_cloud.models import DocumentCrawler
from data.factories import AllegationCategoryFactory, AllegationFactory, AttachmentFileFactory
from data.models import Allegation, AttachmentFile

from data_importer.ipra_crawler.importers import IpraPortalAttachmentImporter, IpraSummaryReportsAttachmentImporter
from data.constants import AttachmentSourceType


class IpraPortalAttachmentImporterTestCase(TestCase):
    @patch('data_importer.ipra_crawler.importers.OpenIpraInvestigationCrawler')
    @patch('data_importer.ipra_crawler.importers.ComplaintCrawler')
    def test_crawl_ipra(self, complaint_crawler, link_crawler):
        complaint_crawler.return_value.crawl.return_value = 'something'
        link_crawler.return_value.crawl.return_value = ['link 1']
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        expect(IpraPortalAttachmentImporter(logger).crawl_ipra()).to.be.eq(['something'])

    def test_parse_incidents(self):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
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
        expect(IpraPortalAttachmentImporter(logger).parse_incidents(incidents)).to.be.eq([{
            'allegation': {
                'crid': '1',
                'incident_date': datetime(2013, 4, 30, 21, 30),
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

    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_ipra')
    def test_crawl_and_update_attachments(self, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Audio',
                    'link': 'http://chicagocopa.org/audio_link.mp3',
                    'title': 'Audio Clip',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                },
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/document.pdf',
                    'title': 'Some Document',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '123',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject', '', 'Unknown'],
        }, {
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/other.pdf',
                    'title': 'Some PDF',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '456',
            'time': '04-30-2013 9:30 pm',
            'subjects': ['Subject 2'],
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

        new_attachments = IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()

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

    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_ipra')
    def test_update(self, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/document.pdf',
                    'title': 'pdf file',
                    'last_updated': '2018-10-30T15:00:03+00:00'
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
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf')

        new_attachments = IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()

        expect(new_attachments).to.be.empty()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).title).to.eq('pdf file')

    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_ipra')
    @patch('data_importer.ipra_crawler.portal_crawler.VimeoSimpleAPI.crawl')
    def test_update_video_thumbnail(self, vimeo_api, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'video',
                    'link': 'https://player.vimeo.com/video/288225991',
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

        IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).title).to.eq('video file')
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).preview_image_url). \
            to.eq('https://i.vimeocdn.com/video/747800241_100x75.webp')

    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_ipra')
    def test_not_update_video_thumbnail_when_source_is_not_vimeo(self, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
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
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_id='288225991',
            original_url='https://player.fake_video.org/video/288225991',
            preview_image_url=None
        )

        IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).preview_image_url).be.none()

    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_ipra')
    def test_update_PORTAL_COPA_DOCUMENTCLOUD_file(self, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/document.pdf',
                    'title': 'pdf file',
                    'last_updated': '2018-10-30T15:00:03+00:00'
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
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf',
            external_last_updated=datetime(2017, 10, 30, tzinfo=pytz.utc)
        )

        new_attachments = IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()
        expect(new_attachments).to.be.empty()

        updated_attachment_file = AttachmentFile.objects.get(pk=attachment_file.pk)
        expect(updated_attachment_file.title).to.eq('CRID 123 CR pdf file')
        expect(updated_attachment_file.external_last_updated).to.eq(datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc))


class IpraSummaryReportsAttachmentImporterTestCase(TestCase):
    @patch('data_importer.ipra_crawler.importers.OpenIpraInvestigationCrawler')
    @patch('data_importer.ipra_crawler.importers.ComplaintCrawler')
    def test_crawl_ipra(self, complaint_crawler, link_crawler):
        complaint_crawler.return_value.crawl.return_value = 'something'
        link_crawler.return_value.crawl.return_value = ['link 1']
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        expect(IpraPortalAttachmentImporter(logger).crawl_ipra()).to.be.eq(['something'])

    def test_parse_incidents(self):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        incidents = [{
            'attachments': [
                {
                    'type': 'document',
                    'link': 'http://document_link',
                    'title': 'Document',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_num': '1',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject1', 'Unknown'],
        }]
        expect(IpraSummaryReportsAttachmentImporter(logger).parse_incidents(incidents)).to.be.eq([{
            'allegation': {
                'crid': '1',
                'attachment_files': [{
                    'file_type': 'document',
                    'url': 'http://document_link',
                    'original_url': 'http://document_link',
                    'source_type': 'SUMMARY_REPORTS_COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
            },
        }])

    @patch('data_importer.ipra_crawler.importers.IpraSummaryReportsAttachmentImporter.crawl_ipra')
    def test_crawl_and_update_attachments(self, crawl_ipra):
        logger = logging.getLogger('crawler.crawl_ipra_portal_data')
        crawl_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/document_link.pdf',
                    'title': 'Some Document',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                },
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/document.pdf',
                    'title': 'Some Document',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'log_num': '123',
        }, {
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://chicagocopa.org/other.pdf',
                    'title': 'Some PDF',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'log_num': '456',
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        allegation = AllegationFactory(crid='123')
        attachment_file = AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='document.pdf',
            original_url='http://chicagocopa.org/document.pdf')

        expect(expect(DocumentCrawler.objects.count())).to.eq(0)
        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').attachment_files.count()).to.eq(1)

        new_attachments = IpraSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()

        expect(Allegation.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.filter(allegation=allegation).count()).to.eq(2)
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).source_type).to.eq(
            AttachmentSourceType.SUMMARY_REPORTS_COPA
        )

        expect(DocumentCrawler.objects.count()).to.eq(1)
        crawler_log = DocumentCrawler.objects.first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.SUMMARY_REPORTS_COPA)
        expect(crawler_log.num_documents).to.eq(2)
        expect(crawler_log.num_new_documents).to.eq(1)
        expect(crawler_log.num_updated_documents).to.eq(1)

        expect(new_attachments).to.have.length(1)
        expect(new_attachments[0].url).to.eq('http://chicagocopa.org/document_link.pdf')
