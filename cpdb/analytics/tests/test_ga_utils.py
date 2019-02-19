from django.test import TestCase

from robber import expect
from mock import Mock

from analytics.ga_utils import extract_report_rows, get_ga_report_response


class GAUtilsTestCase(TestCase):
    def test_extract_report_rows(self):
        report = {
            'columnHeader': {
                'dimensions': ['ga:eventLabel'],
                'metricHeader': {
                    'metricHeaderEntries': [{'name': 'ga:totalEvents', 'type': 'INTEGER'}]
                }
            },
            'data': {
                'rows': [
                    {
                        'dimensions': ['Source URL: / - Target URL: https://example.com/doc1.pdf'],
                        'metrics': [{'values': ['10']}]
                    }
                ]
            },
            'nextPageToken': None
        }

        rows = list(extract_report_rows(report))

        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'ga:eventLabel': 'Source URL: / - Target URL: https://example.com/doc1.pdf',
            'ga:totalEvents': '10'
        })

    def test_ga_report_response_with_page_token(self):
        batchGet = Mock()

        reports = Mock()
        reports.batchGet = batchGet

        analytics = Mock()
        analytics.reports.return_value = reports

        get_ga_report_response(
            analytics,
            {
                'viewId': 123,
                'dateRanges': [
                    {
                        'startDate': '2018-01-01',
                        'endDate': '2018-01-01'
                    }
                ],
                'dimensions': [
                    {
                        'name': 'ga:eventLabel'
                    }
                ],
                'metrics': [
                    {
                        'expression': 'ga:totalEvents'
                    }
                ],
                'filtersExpression': 'ga:eventCategory==attachment_click'
            },
            2000
        )

        batchGet.assert_called_with(body={
            'reportRequests': [{
                'viewId': 123,
                'dateRanges': [
                    {
                        'startDate': '2018-01-01',
                        'endDate': '2018-01-01'
                    }
                ],
                'dimensions': [
                    {
                        'name': 'ga:eventLabel'
                    }
                ],
                'metrics': [
                    {
                        'expression': 'ga:totalEvents'
                    }
                ],
                'filtersExpression': 'ga:eventCategory==attachment_click',
                'pageToken': 2000
            }]
        })

    def test_ga_report_response_no_page_token(self):
        batchGet = Mock()

        reports = Mock()
        reports.batchGet = batchGet

        analytics = Mock()
        analytics.reports.return_value = reports

        get_ga_report_response(
            analytics,
            {
                'viewId': 123,
                'dateRanges': [
                    {
                        'startDate': '2018-01-01',
                        'endDate': '2018-01-01'
                    }
                ],
                'dimensions': [
                    {
                        'name': 'ga:eventLabel'
                    }
                ],
                'metrics': [
                    {
                        'expression': 'ga:totalEvents'
                    }
                ],
                'filtersExpression': 'ga:eventCategory==attachment_click'
            }
        )
