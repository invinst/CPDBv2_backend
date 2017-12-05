import itertools
import logging

from responsebot.handlers import BaseTweetHandler, BaseEventHandler, register_handler
from responsebot.models import TweetFilter
from responsebot.common.exceptions import CharacterLimitError, StatusDuplicateError

from .recipient_extractors import TweetAuthorRecipientExtractor, TweetMentionRecipientExtractor
from .name_parsers import GoogleNaturalLanguageNameParser
from .response_builders import (
    SingleOfficerResponseBuilder, CoaccusedPairResponseBuilder, NotFoundResponseBuilder
)
from .text_extractors import TweetTextExtractor, HashTagTextExtractor, URLContentTextExtractor
from .tweet_extractors import RelatedTweetExtractor
from .tweets import Tweet
from .officer_extractors import ElasticSearchOfficerExtractor
from .models import TwitterBotResponseLog
from .utils.web_parsing import add_params
from .constants import IDS_OF_OTHER_BOTS
from .post_processors import ActivityGridUpdater

logger = logging.getLogger(__name__)


class BaseOfficerTweetHandler(BaseTweetHandler):
    def reset_context(self):
        self._context = {'client': self.client}

    def tweet(self, response):
        sources = response['source']
        tweet_content = response['tweet_content']
        entity_url = response['url']
        media_path = response['media_path']
        original_tweet = self._context['original_tweet']
        incoming_tweet = self._context['incoming_tweet']

        response_log = TwitterBotResponseLog.objects.create(
            sources=', '.join(sources),
            status=TwitterBotResponseLog.PENDING,
            incoming_tweet_username=incoming_tweet.screen_name,
            incoming_tweet_url=incoming_tweet.url,
            incoming_tweet_content=incoming_tweet.text,
            original_tweet_username=original_tweet.screen_name,
            original_tweet_url=original_tweet.url,
            original_tweet_content=original_tweet.text)

        if entity_url:
            entity_url = add_params(entity_url, {'twitterbot_log_id': response_log.id})
            tweet_content = '%s %s' % (tweet_content, entity_url)

        try:
            if media_path:
                file_name = media_path.split('/')[-1]
                with open(media_path) as media_file:
                    outgoing_tweet = self.client.tweet(
                        tweet_content, in_reply_to=self._context['first_non_retweet'].id,
                        filename=file_name, file=media_file)
            else:
                outgoing_tweet = self.client.tweet(tweet_content, in_reply_to=self._context['first_non_retweet'].id)
        except CharacterLimitError:
            logger.error('Tweet is too long - %s' % tweet_content)
            return
        except StatusDuplicateError:
            logger.error('Tweet already sent recently - tweet: %s' % tweet_content)
            return

        outgoing_tweet = Tweet(outgoing_tweet)

        response_log.tweet_url = outgoing_tweet.url
        response_log.status = TwitterBotResponseLog.SENT
        response_log.entity_url = entity_url
        response_log.tweet_content = tweet_content
        response_log.save()

        logger.info('%s - tweet "%s" %s' % (self.__class__.__name__, outgoing_tweet.text, outgoing_tweet.url))

    def on_tweet(self, tweet):
        self.incoming_tweet = Tweet(tweet, client=self.client)
        self.reset_context()
        logger.info('%s - received tweet: "%s" from %s %s' % (
            self.__class__.__name__, self.incoming_tweet.text, self.incoming_tweet.screen_name, self.incoming_tweet.url
        ))
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

        officers = self.officer_extractor.get_officers(names)

        recipients = []
        for recipient_extractor in self.recipient_extractors:
            recipients += [
                name for name in recipient_extractor.extract(tweets, self._context) if name not in recipients]

        for recipient, builder in itertools.product(recipients, self.response_builders):
            responses = builder.build(officers, {'user_name': recipient}, self._context)
            for response in responses:
                self.tweet(response)
                for processor in self.post_processors:
                    processor.process(response)


class CPDBEventHandler(BaseEventHandler):
    def on_follow(self, event):
        if event.target.id == self.client.get_current_user().id:
            logger.info('%s - follow back %s' % (self.__class__.__name__, event.source.screen_name))
            self.client.follow(event.source.id)


@register_handler
class OfficerTweetHandler(BaseOfficerTweetHandler):
    event_handler_class = CPDBEventHandler
    text_extractors = (TweetTextExtractor(), HashTagTextExtractor(), URLContentTextExtractor())
    tweet_extractor = RelatedTweetExtractor()
    incoming_tweet_filters = [
        lambda tweet: tweet.user_id not in IDS_OF_OTHER_BOTS,
        lambda tweet: not tweet.is_unfollow_tweet
    ]
    name_parser = GoogleNaturalLanguageNameParser()
    officer_extractor = ElasticSearchOfficerExtractor()
    recipient_extractors = (TweetAuthorRecipientExtractor(), TweetMentionRecipientExtractor())
    response_builders = (
        SingleOfficerResponseBuilder(), CoaccusedPairResponseBuilder(), NotFoundResponseBuilder()
    )
    post_processors = (ActivityGridUpdater(),)


@register_handler
class CPDBUnfollowHandler(BaseTweetHandler):
    def get_filter(self):
        return TweetFilter(track=['{bot} stop'.format(bot=self.client.get_current_user().screen_name)])

    def on_tweet(self, tweet):
        incoming_tweet = Tweet(original_tweet=tweet, client=self.client)
        if incoming_tweet.is_unfollow_tweet:
            logger.info('%s - unfollow %s %s' % (
                self.__class__.__name__, incoming_tweet.screen_name, incoming_tweet.url))
            self.client.unfollow(tweet.user.id)
