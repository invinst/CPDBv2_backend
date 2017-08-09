import itertools

from responsebot.handlers.base import BaseTweetHandler, BaseEventHandler
from responsebot.models import TweetFilter
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
from .response_loggers import DatabaseResponseLogger


class BaseOfficerTweetHandler(BaseTweetHandler):
    def __init__(self, *args, **kwargs):
        super(BaseOfficerTweetHandler, self).__init__(*args, **kwargs)
        self._context = {'client': self.client}
        self.incoming_tweet = None

    def get_officers(self, names):
        results = []
        for (source, name) in names:
            officer_name = HumanName(name)
            officer = Officer.objects.filter(
                first_name__iexact=officer_name.first, last_name__iexact=officer_name.last).first()

            if officer is not None and officer not in results:
                results.append((source, officer))
        return results

    def tweet(self, response):
        _, tweet_content, _ = response
        outgoing_tweet = self.client.tweet(tweet_content, in_reply_to=self._context['first_non_retweet'].id)
        for res_logger in self.response_loggers:
            res_logger.log_response(response, outgoing_tweet, self._context)

    def on_tweet(self, tweet):
        self.incoming_tweet = Tweet(tweet, client=self.client)
        self._context['incoming_tweet'] = self.incoming_tweet
        if not all([func(self.incoming_tweet) for func in self.incoming_tweet_filters]):
            return

        tweets = self.tweet_extractor.extract(self.incoming_tweet, self._context)

        texts = []
        for tweet, text_extractor in itertools.product(tweets, self.text_extractors):
            texts += text_extractor.extract(self.incoming_tweet)

        names = []
        for text_source, text in texts:
            names += [
                (source, name) for source, name in self.name_parser.parse((text_source, text))
                if (source, name) not in names]

        officers = self.get_officers(names)

        recipients = []
        for recipient_extractor in self.recipient_extractors:
            recipients += [
                name for name in recipient_extractor.extract(tweets, self._context) if name not in recipients]

        for recipient, builder in itertools.product(recipients, self.response_builders):
            responses = builder.build(officers, {'user_name': recipient}, self._context)
            for response in responses:
                self.tweet(response)


class OfficerTweetHandler(BaseOfficerTweetHandler):
    text_extractors = (TweetTextExtractor(), HashTagTextExtractor(), URLContentTextExtractor())
    tweet_extractor = RelatedTweetExtractor()
    incoming_tweet_filters = [
        lambda tweet: tweet.user_id not in [30582622, 4880788160, 4923697764],
        lambda tweet: not tweet.is_unfollow_tweet
    ]
    response_loggers = [DatabaseResponseLogger()]
    name_parser = RosettePersonNameParser()
    recipient_extractors = (TweetAuthorRecipientExtractor(), TweetMentionRecipientExtractor())
    response_builders = (
        SingleOfficerResponseBuilder(), CoaccusedPairResponseBuilder(), NotFoundResponseBuilder()
        )


class CPDBEventHandler(BaseEventHandler):
    def on_follow(self, event):
        if event.target.id == self.client.get_current_user().id:
            self.client.follow(event.source.id)


class CPDBUnfollowHandler(BaseTweetHandler):
    def get_filter(self):
        return TweetFilter(track=['{bot} stop'.format(bot=self.client.get_current_user().screen_name)])

    def on_tweet(self, tweet):
        incoming_tweet = Tweet(original_tweet=tweet, client=self.client)
        if incoming_tweet.is_unfollow_tweet:
            self.client.unfollow(tweet.user.id)
