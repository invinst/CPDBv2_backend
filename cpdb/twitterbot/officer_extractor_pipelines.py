import itertools
import re
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from elasticsearch.exceptions import TransportError

from officers.doc_types import OfficerInfoDocType
from .name_parsers import GoogleNaturalLanguageNameParser
from .text_extractors import TweetTextExtractor, HashTagTextExtractor, URLContentTextExtractor
from .officer_extractors import ElasticSearchOfficerExtractor
from .serializers import OfficerSerializer


class TextPipeline(object):
    def __init__(self):
        self.text_extractors = (TweetTextExtractor(), HashTagTextExtractor(), URLContentTextExtractor())
        self.name_parser = GoogleNaturalLanguageNameParser()
        self.officer_from_name_extractor = ElasticSearchOfficerExtractor()

    def extract(self, tweets):
        texts = []
        for tweet, text_extractor in itertools.product(tweets, self.text_extractors):
            texts += text_extractor.extract(tweet)
        officer_names = []
        for text_source, text in texts:
            officer_names += [
                (source, name) for source, name in self.name_parser.parse((text_source, text))
                if (source, name) not in officer_names
            ]

        return self.officer_from_name_extractor.get_officers(officer_names)


class UrlPipeline(object):
    def __init__(self):
        self.site_netloc = urlparse(settings.DOMAIN).netloc

    def extract(self, tweets):
        results = []
        for tweet in tweets:
            for url in tweet.urls:
                parsed = urlparse(url)
                if parsed.netloc == self.site_netloc:
                    matches = re.match('^/officer/(\d+)', parsed.path)
                    try:
                        officer_id = matches.group(1)
                        officer = OfficerInfoDocType().get(officer_id)
                        results.append(('cpdb-url', OfficerSerializer(officer).data))
                    except (AttributeError, ObjectDoesNotExist, TransportError):
                        continue
        return results
