from datetime import datetime

from django.test.testcases import TestCase
from mock import patch
from robber import expect

from data.factories import AllegationCategoryFactory, AllegationFactory
from data.models import Allegation
from data_importer.ipra_portal_crawler.service import AutoOpenIPRA


class AutoOpenIPRATest(TestCase):
    def test_parse_incidents(self):
        incidents = [{
            'attachments': [{'type': 'Audio', 'link': 'http://audio_link', 'title': 'Audio Clip'}],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '1',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject1', 'Unknown'],
        }]
        expect(AutoOpenIPRA.parse_incidents(incidents)).to.be.eq([{
            'allegation': {
                'crid': '1',
                'incident_date': datetime(2013, 4, 30, 21, 30),
                'attachment_files': [{
                    'file_type': 'audio',
                    'title': 'Audio Clip',
                    'url': 'http://audio_link',
                    'original_url': 'http://audio_link',
                    'tag': 'Audio'
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }])

    @patch('data_importer.ipra_portal_crawler.service.OpenIpraInvestigationCrawler')
    @patch('data_importer.ipra_portal_crawler.service.ComplaintCrawler')
    def test_crawl_open_ipra(self, complaint_crawler, link_crawler):
        link_crawler.return_value.crawl.return_value = ['link 1']
        complaint_crawler.return_value.crawl.return_value = 'something'
        expect(AutoOpenIPRA.crawl_open_ipra()).to.be.eq(['something'])

    @patch('data_importer.ipra_portal_crawler.service.AutoOpenIPRA.crawl_open_ipra')
    def test_import_new(self, open_ipra):
        open_ipra.return_value = [{
            'attachments': [{'type': 'Audio', 'link': 'http://audio_link', 'title': 'Audio Clip'}],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '123',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject', '', 'Unknown'],
        }, {
            'attachments': [{'type': 'Audio', 'link': 'http://audio_link', 'title': 'Audio Clip'}],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '456',
            'time': '04-30-2013 9:30 pm',
            'subjects': ['Subject 2'],
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        AllegationFactory(crid='123')
        expect(Allegation.objects.all()).to.have.length(1)

        AutoOpenIPRA.import_new()

        expect(Allegation.objects.all()).to.have.length(1)
        allegation = Allegation.objects.get(crid='123')
        expect(allegation.attachment_files.all()).to.have.length(1)
        expect(allegation.subjects).to.eq(['Subject'])
