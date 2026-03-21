import inspect
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/51.0.2704.103 Safari/537.36"
}


class OpenCopaInvestigationCrawler(object):
    URL = 'https://www.chicagocopa.org/data-cases/case-portal/?sort_order=title%20desc'

    def __init__(self, url=URL):
        self.base_url = url

    def _get_page(self, url):
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def _extract_links_from_soup(self, soup):
        links = []
        list_items = soup.select('#ipra-case-search-data-table tbody tr th a')
        for item in list_items:
            href = item.get('href')
            if href:
                links.append(urljoin(self.base_url, href))
        return links

    def _get_next_page_url(self, soup, current_url):
        pagination = soup.select_one('.pagination .nav-next a')
        if not pagination:
            return None

        next_href = pagination.get('href')
        if not next_href:
            return None

        # Preserve host and query params from the provided next link.
        parsed = urlparse(next_href)
        # Ensure sort_order is preserved even if the base URL changes.
        query = parse_qs(parsed.query)
        if 'sort_order' not in query:
            base_parsed = urlparse(current_url)
            base_query = parse_qs(base_parsed.query)
            if 'sort_order' in base_query:
                query['sort_order'] = base_query['sort_order']

        new_query = urlencode({k: v[0] for k, v in query.items()}, doseq=False)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

    def crawl(self):
        links = []
        current_url = self.base_url

        while current_url:
            soup = self._get_page(current_url)
            links.extend(self._extract_links_from_soup(soup))
            current_url = self._get_next_page_url(soup, current_url)

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


class VimeoSimpleAPI(object):
    def __init__(self, video_id):
        self.url = 'http://vimeo.com/api/v2/video/{video_id}.json'.format(video_id=video_id)

    def crawl(self):
        response = requests.get(self.url, headers=HEADERS)
        try:
            content = response.json()[0]
        except ValueError:
            content = None
        return content


class ComplaintCrawler(BaseComplaintCrawler):
    AUDIO_FILE_SELECTOR = 'fa-file-sound-o'
    VIDEO_FILE_SELECTOR = 'fa-file-video-o'
    DOCUMENT_FILE_SELECTOR = 'fa-file-pdf-o'

    def _complaint_info(self):
        """
        Return [log_number, incident_type, notification_date, incident_date_time, district]
        as plain strings (same logical fields as the legacy single-row table).

        COPA has used both a 5-column IPRA-style row and a wider Case Portal row (7 columns);
        when type is omitted on the page, incident_type is ''.
        """
        if not hasattr(self, '_complaint_info_cache'):
            self._complaint_info_cache = self._extract_complaint_table_fields()
        return self._complaint_info_cache

    def _extract_complaint_table_fields(self):
        row = self._find_desktop_metadata_row()
        if row is not None:
            cells = row.select('th') + row.select('td')
            texts = [c.get_text(strip=True) for c in cells]
            n = len(texts)
            if n == 5:
                # Legacy: Log#, Incident Type(s), Notification Date, Incident Date & Time, District
                return texts
            if n >= 7:
                # Current Case Portal wide row: Log#, Incident Date & Time, District,
                # COPA Notification, Transparency, Closed, FSR/Memo (see chicagocopa.org case pages)
                return [
                    texts[0],
                    '',
                    texts[3],
                    texts[1],
                    texts[2],
                ]
            if n > 0:
                return self._normalize_variable_width_row(texts)

        stack_values = self._extract_stack_table_fields()
        if stack_values is not None:
            return stack_values

        raise ValueError(
            'Could not find complaint metadata table on this COPA case page; HTML layout may have changed.'
        )

    def _find_desktop_metadata_row(self):
        """Prefer the wide desktop table whose header mentions Log#."""
        for table in self.soup.select('.entry-content table.table-striped'):
            header = table.find('thead')
            if header and 'log' in header.get_text(strip=True).lower():
                body_rows = table.select('tbody tr')
                if body_rows:
                    return body_rows[0]

        # Legacy markup: Bootstrap visibility classes on .table-responsive
        selectors = [
            '.entry-content .table-responsive.hidden-sm.hidden-xs tbody tr',
            '.entry-content .table-responsive:not(.stack-table) tbody tr',
        ]
        for sel in selectors:
            rows = self.soup.select(sel)
            if rows:
                return rows[0]
        return None

    @staticmethod
    def _normalize_variable_width_row(texts):
        """Best-effort mapping when column count is unexpected."""
        if len(texts) >= 5:
            return texts[:5]
        padded = list(texts) + [''] * (5 - len(texts))
        return padded[:5]

    def _extract_stack_table_fields(self):
        """
        Mobile / stacked layout: one field per row (th label + td value).
        """
        tbody = self.soup.select_one('.entry-content .table-responsive.stack-table tbody')
        if not tbody:
            return None

        fields = {
            'log': '',
            'type': '',
            'notification': '',
            'time': '',
            'district': '',
        }
        for tr in tbody.find_all('tr'):
            th = tr.find('th')
            td = tr.find('td')
            if not th or not td:
                continue
            label = th.get_text(strip=True).lower()
            value = td.get_text(strip=True)
            if 'log' in label and 'number' in label:
                fields['log'] = value
            elif 'incident type' in label:
                fields['type'] = value
            elif 'incident date' in label and 'time' in label:
                fields['time'] = value
            elif 'district' in label:
                fields['district'] = value
            elif 'notification' in label:
                fields['notification'] = value

        if not fields['log'] and not fields['time']:
            return None

        return [
            fields['log'],
            fields['type'],
            fields['notification'],
            fields['time'],
            fields['district'],
        ]

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

    def _parse_last_updated(self):
        return self.soup.select('.entry-date.published')[0]['datetime']

    def _parse_log_number(self):
        return self._complaint_info()[0]

    def _parse_type(self):
        return self._complaint_info()[1]

    def _parse_date(self):
        return self._complaint_info()[2]

    def _parse_time(self):
        return self._complaint_info()[3]

    def _parse_district(self):
        return self._complaint_info()[4]

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
