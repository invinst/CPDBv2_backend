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
    text_extractors = (TweetTextExtractor(), HashTagTextExtractor(), URLContentTextExtractor())
    name_parser = GoogleNaturalLanguageNameParser()
    officer_from_name_extractor = ElasticSearchOfficerExtractor()

    @classmethod
    def extract(cls, tweets):
        texts = []
        for tweet, text_extractor in itertools.product(tweets, cls.text_extractors):
            texts += text_extractor.extract(tweet)
        officer_names = []
        for text_source, text in texts:
            officer_names += [
                (source, name) for source, name in cls.name_parser.parse((text_source, text))
                if (source, name) not in officer_names
            ]

        return cls.officer_from_name_extractor.get_officers(officer_names)


class UrlPipeline(object):
    site_netloc = urlparse(settings.DOMAIN).netloc

    @classmethod
    def extract(cls, tweets):
        results = []
        for tweet in tweets:
            for url in tweet.urls:
                parsed = urlparse(url)
                if parsed.netloc == cls.site_netloc:
                    matches = re.match('^/officer/(\d+)', parsed.path)
                    try:
                        officer_id = matches.group(1)
                        officer = OfficerInfoDocType().get(officer_id)
                        results.append(('cpdb-url', OfficerSerializer(officer).data))
                    except (AttributeError, ObjectDoesNotExist, TransportError):
                        continue
        return results
