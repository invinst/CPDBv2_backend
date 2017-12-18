import re
from urlparse import urlparse

from django.conf import settings

from utils import web_parsing


class TweetTextExtractor:
    def extract(self, tweet):
        text = re.sub(r'\@[^\s]+\s+', '', tweet.text)
        return [('text', text)]


class HashTagTextExtractor:
    def extract(self, tweet):
        text_sources = []
        for hashtag in tweet.hashtags:
            words = re.findall('[A-Za-z][a-z]*', hashtag)
            text = ' '.join([word.title() for word in words])
            source = '#%s' % hashtag
            text_sources.append((source, text))
        return text_sources


class URLContentTextExtractor:
    def extract(self, tweet):
        text_sources = []
        for url in tweet.urls:
            text = web_parsing.parse(url)
            if 'CPD' in text or ('Chicago' in text and 'Police' in text):
                text_sources.append((url, text))
        return text_sources


class CPDBUrlExtractor:
    TEXT_SOURCE = 'cpdb-url'
    site_netloc = urlparse(settings.DOMAIN).netloc

    def extract(self, tweet):
        text_sources = []
        for url in tweet.urls:
            parsed = urlparse(url)
            if parsed.netloc == self.site_netloc:
                matches = re.match('^/officer/(\d+)', parsed.path)
                if matches is not None:
                    officer_id = matches.group(1)
                    text_sources.append((self.TEXT_SOURCE, officer_id))

        return text_sources
