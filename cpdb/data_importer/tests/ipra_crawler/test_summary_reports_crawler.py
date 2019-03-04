import codecs

from django.test.testcases import SimpleTestCase

from mock import MagicMock, patch
from robber import expect
from bs4 import BeautifulSoup

from data_importer.ipra_crawler.summary_reports_crawler import (
    OpenIpraSummaryReportsCrawler,
    OpenIpraYearSummaryReportsCrawler,
    ReportCrawler,
)


class OpenIpraSummaryReportsCrawlerTestCase(SimpleTestCase):
    @patch('data_importer.ipra_crawler.summary_reports_crawler.requests')
    def test_parse(self, requests):
        response_text = codecs.open(
            'data_importer/tests/data/summary_reports/summary_reports_copa.html', 'r', 'utf-8'
        ).read()
        requests.get = MagicMock(return_value=MagicMock(text=response_text))
        links = [
            'https://www.chicagocopa.org/news-publications/publications/summary-reports/2018-summary-reports/',
            'https://www.chicagocopa.org/news-publications/publications/summary-reports/2017-summary-reports/'
        ]
        expect(OpenIpraSummaryReportsCrawler().crawl()).to.be.eq(links)


class OpenIpraYearSummaryReportsCrawlerTestCase(SimpleTestCase):
    @patch('data_importer.ipra_crawler.summary_reports_crawler.requests')
    def test_parse(self, requests):
        url = 'https://www.chicagocopa.org/news-publications/publications/summary-reports/2018-summary-reports/'
        response_text = codecs.open(
            'data_importer/tests/data/summary_reports/2018_summary_reports_copa.html', 'r', 'utf-8'
        ).read()
        requests.get = MagicMock(return_value=MagicMock(text=response_text))

        records = [{
            'attachments': [
                {
                    'link': 'https://www.chicagocopa.org/wp-content/uploads/2018/12/Log-1086683-9.27.pdf',
                    'last_updated': 'October 25, 2018'
                }
            ],
            'log_num': '1086683',
        }, {
            'attachments': [],
            'log_num': '1085949',
        }, {
            'attachments': [
                {
                    'link': 'https://www.chicagocopa.org/wp-content/uploads/2018/11/1083324-FINAL-with-redactions.pdf',
                    'last_updated': 'September 26, 2018'
                }
            ],
            'log_num': '1083324',
        }, {
            'attachments': [],
            'log_num': '1087965',
        }]
        expect(OpenIpraYearSummaryReportsCrawler(url=url).crawl()).to.be.eq(records)


class ReportCrawlerTestCase(SimpleTestCase):
    def test_parse(self):
        report = codecs.open('data_importer/tests/data/summary_reports/report_crawler_data.html', 'r', 'utf-8').read()
        header_fields = ['Log #', 'Date Closed', '# of Allegations', 'COPA Findings', 'Download*']
        result = {
            'attachments': [
                {
                    'link': 'https://www.chicagocopa.org/wp-content/uploads/2018/11/1083324-FINAL-with-redactions.pdf',
                    'last_updated': 'September 26, 2018'
                }
            ],
            'log_num': '1083324',
        }
        soup = BeautifulSoup(report, 'html.parser')
        expect(ReportCrawler(soup, header_fields).crawl()).to.eq(result)
