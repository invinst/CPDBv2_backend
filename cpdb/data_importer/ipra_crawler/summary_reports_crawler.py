import inspect
import requests

from bs4 import BeautifulSoup

HEADERS = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/51.0.2704.103 Safari/537.36"
}


class OpenIpraSummaryReportsCrawler(object):
    URL = 'https://www.chicagocopa.org/news-publications/publications/summary-reports/'

    def __init__(self, url=URL):
        content = requests.get(url, headers=HEADERS).text
        self.soup = BeautifulSoup(content, 'html.parser')

    def crawl(self):
        list_items = self.soup.select('.entry-content .row a')
        return [item.get('href') for item in list_items]


class OpenIpraYearSummaryReportsCrawler(object):
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(self.get_html_content(), 'html.parser')

    def get_html_content(self):
        return requests.get(self.url, headers=HEADERS).text

    def crawl(self):
        elements = self.soup.select('.panel-group .panel-default')

        all_reports = []
        for element in elements:
            table = element.find('table')
            header_fields = [header.text for header in table.find('thead').select('th')]

            reports = table.find('tbody').select('tr')
            for report in reports:
                report = ReportCrawler(report, header_fields).crawl()
                all_reports.append(report)

        return all_reports


class ReportCrawler(object):
    PREFIX = '_parse_'

    def __init__(self, report, header_fields):
        self.report = report
        self.header_fields = header_fields
        self.cells = self.report.select('td')

    def crawl(self):
        records = {}
        rules = {name: rule for name, rule in inspect.getmembers(self, predicate=inspect.ismethod) if
                 name.startswith(self.PREFIX)}

        for key, rule in rules.items():
            key_name = key.replace(self.PREFIX, '')
            records[key_name] = rule()

        return records

    def _data_cell(self, header):
        return self.cells[self.header_fields.index(header) - 1]

    def _parse_log_num(self):
        return self.report.find('th').text.strip()

    def _parse_attachments(self):
        download_file = self._data_cell('Download*').find('a')
        download_url = download_file.get('href') if download_file else None
        if download_url:
            date_closed = self._data_cell('Date Closed').text.strip()
            return [{'link': download_url, 'last_updated': date_closed}]
        else:
            return []
