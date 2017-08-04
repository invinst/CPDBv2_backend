import itertools

from responsebot.handlers.base import BaseTweetHandler
from nameparser.parser import HumanName

from data.models import Officer

from .recipient_extractors import TweetAuthorRecipientExtractor, TweetMentionRecipientExtractor
from .name_parsers import RosettePersonNameParser
from .response_builders import (
    SingleOfficerResponseBuilder, CoaccusedPairResponseBuilder, NotFoundResponseBuilder
)
from .text_extractors import TweetTextExtractor, HashTagTextExtractor, URLContentTextExtractor
from .tweet_extractors import RelatedTweetExtractor
from .tweets import Tweet


class BaseOfficerTweetHandler(BaseTweetHandler):
    def __init__(self, *args, **kwargs):
        super(BaseOfficerTweetHandler, self).__init__(*args, **kwargs)
        self._context = {'client': self.client}

    def get_officers(self, names):
        results = []
        for name in names:
            name = HumanName(name)
            officer = Officer.objects.filter(first_name__iexact=name.first, last_name__iexact=name.last).first()

            if officer is not None and officer not in results:
                results.append(officer)
        return results

    def tweet(self, response):
        self.client.tweet(response, in_reply_to=self._context['first_non_retweet'].id)

    def on_tweet(self, tweet):
        tweet = Tweet(tweet, client=self.client)
        tweets = self.tweet_extractor.extract(tweet, self._context)

        texts = []
        for tweet, text_extractor in itertools.product(tweets, self.text_extractors):
            texts += text_extractor.extract(tweet)

        names = []
        for _, text in texts:
            names += [name for name in self.name_parser.parse(text) if name not in names]

        officers = self.get_officers(names)

        recipients = []
        for recipient_extractor in self.recipient_extractors:
            recipients += [
                name for name in recipient_extractor.extract(tweets, self._context)
                if name not in recipients]
        for recipient, builder in itertools.product(recipients, self.response_builders):
            responses = builder.build(officers, {'user_name': recipient}, self._context)
            for response in responses:
                self.tweet(response)


class OfficerTweetHandler(BaseOfficerTweetHandler):
    text_extractors = (TweetTextExtractor(), HashTagTextExtractor(), URLContentTextExtractor())
    tweet_extractor = RelatedTweetExtractor()
    name_parser = RosettePersonNameParser()
    recipient_extractors = (TweetAuthorRecipientExtractor(), TweetMentionRecipientExtractor())
    response_builders = (
        SingleOfficerResponseBuilder(), CoaccusedPairResponseBuilder(), NotFoundResponseBuilder()
        )
