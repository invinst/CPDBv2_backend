import itertools
import re
from urlparse import urlparse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from data.models import Officer
from .name_parsers import GoogleNaturalLanguageNameParser
from .text_extractors import TweetTextExtractor, HashTagTextExtractor, URLContentTextExtractor
from .officer_extractors import ElasticSearchOfficerExtractor


class TextPipeline:
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
                if (source, name) not in officer_names]

        return cls.officer_from_name_extractor.get_officers(officer_names)


class UrlPipeline:
    site_netloc = urlparse(settings.DOMAIN).netloc

    @classmethod
    def extract(cls, tweets):
        results = []
        for tweet in tweets:
            for url in tweet.urls:
                parsed = urlparse(url)
                if parsed.netloc == cls.site_netloc:
                    matches = re.match('^/officer/(\d+)', parsed.path)
                    if matches is not None:
                        officer_id = matches.group(1)
                        try:
                            officer = Officer.objects.get(pk=officer_id)
                            results.append(('cpdb-url', officer))
                        except ObjectDoesNotExist:
                            continue
        return results
