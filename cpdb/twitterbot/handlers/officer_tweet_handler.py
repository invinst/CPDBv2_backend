import itertools
import logging

from twitterbot.officer_extractor_pipelines import TextPipeline, UrlPipeline
from twitterbot.recipient_extractors import TweetAuthorRecipientExtractor, TweetMentionRecipientExtractor
from twitterbot.response_builders import (
    SingleOfficerResponseBuilder, CoaccusedPairResponseBuilder, NotFoundResponseBuilder
)
from twitterbot.tweet_extractors import DirectMentionTweetExtractor
from twitterbot.post_processors import ActivityGridUpdater
from twitterbot.tweets import TweetContext
from twitterbot.models import TwitterBotResponseLog
from twitterbot.utils.web_parsing import add_params
from twitterbot.message_queue import send_tweet
from .base import SubEventHandler

logger = logging.getLogger(__name__)


class OfficerTweetHandler(SubEventHandler):
    tweet_extractor = DirectMentionTweetExtractor()
    officer_extractor_pipelines = (TextPipeline, UrlPipeline)
    recipient_extractors = (TweetAuthorRecipientExtractor(), TweetMentionRecipientExtractor())
    response_builders = (
        SingleOfficerResponseBuilder(), CoaccusedPairResponseBuilder(), NotFoundResponseBuilder()
    )
    post_processors = (ActivityGridUpdater(),)

    def __init__(self, event_data, for_user_id, original_event, *args, **kwargs):
        super(OfficerTweetHandler, self).__init__(event_data, for_user_id, original_event, *args, **kwargs)
        self._context = {
            'client': self.client,
            'for_user_id': self.for_user_id
        }
        self.incoming_tweet = TweetContext(self.event_data, self._context)
        self._context['incoming_tweet'] = self.incoming_tweet
        self.original_event = original_event
        self.officer_pipelines = (pipeline() for pipeline in self.officer_extractor_pipelines)

    def match_tweet(self):
        return not self.incoming_tweet.is_unfollow_tweet

    def tweet(self, response):
        sources = response['source']
        tweet_content = response['tweet_content']
        entity_url = response['url']
        entity = response['entity']
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

        send_tweet(tweet_content, in_reply_to=self._context['first_non_retweet'].id, entity=entity)

        response_log.status = TwitterBotResponseLog.SENT
        response_log.entity_url = entity_url
        response_log.tweet_content = tweet_content
        response_log.original_event_object = self.original_event
        response_log.save()

        logger.info('%s - tweet "%s"' % (self.__class__.__name__, tweet_content))

    def handle(self):
        logger.info('%s - received tweet: "%s" from %s %s' % (
            self.__class__.__name__, self.incoming_tweet.text, self.incoming_tweet.screen_name, self.incoming_tweet.url
        ))

        tweets = self.tweet_extractor.extract(self.incoming_tweet, self._context)

        # Extract officers:
        officer_extractor_pipeline_results = [
            pipeline.extract(tweets)
            for pipeline in self.officer_pipelines
        ]

        # Eliminate duplicate officers
        officers = []
        existing_ids = []
        for result in officer_extractor_pipeline_results:
            for source, officer in result:
                if officer['id'] not in existing_ids:
                    officers.append((source, officer))
                    existing_ids.append(officer['id'])

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
