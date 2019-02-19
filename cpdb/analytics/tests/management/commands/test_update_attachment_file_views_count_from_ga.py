from django.core import management
from django.test import TestCase

from mock import patch, Mock
from robber import expect

from data.factories import AttachmentFileFactory


class UpdateAttachmentFileViewsCountFromGA(TestCase):
    @patch('analytics.management.commands.update_attachment_file_views_count_from_ga.initialize_analyticsreporting')
    def test_update_attachment_file_views_count_from_ga(self, init):
        attachment1 = AttachmentFileFactory(
            url='https://example.com/doc1.pdf',
            original_url='',
            views_count=0,
        )
        attachment2 = AttachmentFileFactory(
            url='',
            original_url='https://example.com/doc2.pdf',
            views_count=1
        )

        column_header = {
            'dimensions': ['ga:eventLabel'],
            'metricHeader': {
                'metricHeaderEntries': [{'name': 'ga:totalEvents', 'type': 'INTEGER'}]
            }
        }

        executer = Mock()
        executer.execute.side_effect = [
            {
                'reports': [{
                    'columnHeader': column_header,
                    'data': {
                        'rows': [
                            {
                                'dimensions': ['Source URL: / - Target URL: /complaint/1002813/'],
                                'metrics': [{'values': ['17']}]
                            },
                            {
                                'dimensions': ['Source URL: / - Target URL: https://example.com/doc1.pdf'],
                                'metrics': [{'values': ['2']}]
                            }
                        ]
                    },
                    'nextPageToken': 2,
                }]
            },
            {
                'reports': [{
                    'columnHeader': column_header,
                    'data': {
                        'rows': [
                            {
                                'dimensions': ['Source URL: / - Target URL: https://example.com/doc2.pdf'],
                                'metrics': [{'values': ['10']}]
                            }
                        ]
                    },
                    'nextPageToken': None
                }]
            },
        ]

        batcher = Mock()
        batcher.batchGet = Mock(return_value=executer)

        analytics = Mock()
        analytics.reports = Mock(return_value=batcher)

        init.return_value = analytics

        management.call_command('update_attachment_file_views_count_from_ga')

        attachment1.refresh_from_db()
        attachment2.refresh_from_db()

        expect(attachment1.views_count).to.eq(2)
        expect(attachment2.views_count).to.eq(10)
