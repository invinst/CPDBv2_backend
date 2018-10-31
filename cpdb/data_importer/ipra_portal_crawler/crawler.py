import inspect
import re
import requests

from bs4 import BeautifulSoup

HEADERS = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/51.0.2704.103 Safari/537.36"
}


class OpenIpraInvestigationCrawler(object):
    URL = 'https://www.chicagocopa.org/wp-content/themes/copa/DynamicSearch.php'

    def __init__(self, url=URL):
        response = requests.get(url, headers=HEADERS)
        content = response.json()['caseSearch']['items']
        self.soup = BeautifulSoup(content, 'html.parser')

    def crawl(self):
        list_items = self.soup.select('tr th a')
        links = []
        for item in list_items:
            links.append(item.get('href'))

        return links


class BaseComplaintCrawler(object):
    PREFIX = '_parse_'

    def __init__(self, url=''):
        self.url = url
        self.content = self.get_html_content(self.url)
        self.soup = BeautifulSoup(self.content, 'html.parser')

    def get_html_content(self, url):
        return requests.get(url, headers=HEADERS).text

    def crawl(self):
        records = {}
        rules = {name: rule for name, rule in inspect.getmembers(self, predicate=inspect.ismethod) if
                 name.startswith(self.PREFIX)}

        for key, rule in rules.items():
            key_name = key.replace(self.PREFIX, '')
            records[key_name] = rule()

        return records


class ComplaintCrawler(BaseComplaintCrawler):
    AUDIO_FILE_SELECTOR = 'fa-file-sound-o'
    VIDEO_FILE_SELECTOR = 'fa-file-video-o'
    DOCUMENT_FILE_SELECTOR = 'fa-file-pdf-o'

    def _complaint_info(self):
        info_row = self.soup.select('.entry-content .table-responsive.hidden-sm.hidden-xs tbody tr')[0]
        return info_row.select('th') + info_row.select('td')

    def _crawl_media(self, klass_name, link_getter):
        types_dictionary = {self.AUDIO_FILE_SELECTOR: 'audio', self.VIDEO_FILE_SELECTOR: 'video',
                            self.DOCUMENT_FILE_SELECTOR: 'document'}
        entries = self.soup.select('.col-sm-4')
        results = []

        for entry in entries:
            fa_span = entry.find('span', attrs={'class': 'fa'})
            if fa_span and klass_name in fa_span.get('class'):
                record = {'type': types_dictionary[klass_name], 'link': link_getter(entry),
                          'title': entry.select('.modal-title')[0].text.strip() if entry.select(
                              '.modal-title') else entry.text.strip()}

                results.append(record)

        return results

    def _parse_log_number(self):
        return self._complaint_info()[0].text.strip()

    def _parse_type(self):
        return self._complaint_info()[1].text.strip()

    def _parse_date(self):
        return self._complaint_info()[2].text.strip()

    def _parse_time(self):
        return self._complaint_info()[3].text.strip()

    def _parse_district(self):
        return self._complaint_info()[4].text.strip()

    def _parse_attachments(self):
        audios = self._crawl_media(self.AUDIO_FILE_SELECTOR,
                                   lambda x: re.search('\'http.+\'', x.find('script').text).group()[1:-1])
        videos = self._crawl_media(self.VIDEO_FILE_SELECTOR,
                                   lambda x: re.search('\'http.+\'', x.find('script').text).group()[1:-1])
        documents = self._crawl_media(self.DOCUMENT_FILE_SELECTOR, lambda x: x.a.get('href').strip())

        return audios + videos + documents

    def _parse_subjects(self):
        subjects = []
        if self.soup.select('.entry-content ul'):
            subject_items = self.soup.select('.entry-content ul li')
            for item in subject_items:
                subjects.append(item.text.strip())
        elif self.soup.select('.entry-content p'):
            subject_item = self.soup.select('.entry-content p')[0]
            subject_pattern = re.compile(r"Subject[^<:]*:([^<:]+)")
            found = subject_pattern.search(subject_item.text)
            if found:
                subjects.append(found.groups()[0].strip())

        return subjects
