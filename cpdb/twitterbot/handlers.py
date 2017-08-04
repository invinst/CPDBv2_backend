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
from .models import TwitterBotResponseLog


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
        self.save_tweet_response(response, outgoing_tweet)

    def save_tweet_response(self, response, outgoing_tweet):
        sources, tweet_content, entity_url = response
        response_log = TwitterBotResponseLog(
            sources=' '.join(sources),
            entity_url=entity_url,
            tweet_content=tweet_content,
            tweet_url=Tweet(outgoing_tweet).url,
            incoming_tweet_username=self.incoming_tweet.screen_name,
            incoming_tweet_url=self.incoming_tweet.url,
            incoming_tweet_content=self.incoming_tweet.text)
        original_tweet = self._context.get('original_tweet', None)
        if original_tweet:
            response_log.original_tweet_username = original_tweet.screen_name
            response_log.original_tweet_url = original_tweet.url
            response_log.original_tweet_content = original_tweet.text

        response_log.save()

    def on_tweet(self, tweet):
        self.incoming_tweet = Tweet(tweet, client=self.client)
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
        if tweet.text == '@{bot} STOP'.format(bot=self.client.get_current_user().screen_name):
            self.client.unfollow(tweet.user.id)
