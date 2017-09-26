import re

from utils import web_parsing


class TweetTextExtractor:
    def extract(self, tweet):
        return [('text', tweet.text)]


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
