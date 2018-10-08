from datetime import datetime

import factory
from mock import Mock
from faker import Faker

from twitterbot.tweets import TweetContext
from twitterbot.models import ResponseTemplate, TYPE_CHOICES, TwitterBotResponseLog

fake = Faker()


class MockTweepyWrapperFactory:
    def __init__(self, id=111, screen_name='ScreenName', subscription_screen_name='subscriber', followed_by=False):
        self.tweets = dict()
        self.screen_name = screen_name
        self.subscription_screen_name = subscription_screen_name
        self.id = id
        self.config = {'user_stream': True}
        self.tweepy_api = Mock(show_friendship=Mock(return_value=(Mock(), Mock(followed_by=followed_by))))

    def register(self, tweet):
        self.tweets[tweet._original_tweet['id']] = tweet._original_tweet

    def get_tweet(self, id):
        return self.tweets[id]

    def get_current_user(self):
        return Mock(id=self.id, screen_name=self.screen_name)

    def get_user(self, id):
        return Mock(id=id, screen_name=self.subscription_screen_name)


class TweetFactory(factory.Factory):
    class Meta:
        model = TweetContext

    original_tweet = factory.LazyAttribute(lambda o: {
        'text': o.text,
        'id': o.id,
        'in_reply_to_status_id': o.in_reply_to_tweet._original_tweet['id'] if o.in_reply_to_tweet is not None else None,
        'retweeted_status': o.retweeted_status._original_tweet if o.retweeted_status is not None else None,
        'quoted_status_id': o.quoted_status._original_tweet['id'] if o.quoted_status is not None else None,
        'quoted_status': o.quoted_status._original_tweet if o.quoted_status is not None else None,
        'user': {
            'id': o.user_id,
            'screen_name': o.author_screen_name
        },
        'created_at': o.created_at,
        'entities': {
            'urls': [{'expanded_url': url} for url in o.urls],
            'hashtags': [{'text': text} for text in o.hashtags],
            'user_mentions': [
                {
                    'screen_name': user.get('screen_name'),
                    'id': user.get('id')
                } for user in o.user_mentions
            ]
        }
    })
    context = None

    class Params:
        text = 'some content'
        hashtags = []
        urls = []
        in_reply_to_tweet = None
        retweeted_status = None
        quoted_status = None
        user_id = factory.Faker('random_number', digits=17)
        id = factory.Faker('random_number', digits=17)
        author_screen_name = None
        user_mentions = []
        created_at = factory.LazyFunction(lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))


class ResponseTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResponseTemplate

    response_type = factory.Faker('random_element', elements=TYPE_CHOICES)


class TwitterBotResponseLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TwitterBotResponseLog

    sources = factory.Faker('word')
    tweet_content = factory.Faker('text', max_nb_chars=200)
