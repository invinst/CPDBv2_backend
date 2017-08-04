import factory
from mock import Mock
from faker import Faker

from twitterbot.tweets import Tweet
from twitterbot.models import ResponseTemplate, TYPE_CHOICES

fake = Faker()


class MockClientFactory:
    def __init__(self, screen_name='ScreenName'):
        self.tweets = dict()
        self.screen_name = screen_name
        self.config = {'user_stream': True}

    def register(self, tweet):
        self.tweets[tweet._original_tweet.id] = tweet._original_tweet

    def get_tweet(self, id):
        try:
            return self.tweets[id]
        except KeyError:
            return None

    def get_current_user(self):
        return Mock(id=111, screen_name=self.screen_name)


class TweetFactory(factory.Factory):
    class Meta:
        model = Tweet

    original_tweet = factory.LazyAttribute(lambda o: Mock(
        text=o.text,
        id=o.id,
        in_reply_to_tweet_id=o.in_reply_to_tweet._original_tweet.id if o.in_reply_to_tweet is not None else None,
        retweeted_tweet=o.retweeted_tweet._original_tweet if o.retweeted_tweet is not None else None,
        quoted_tweet_id=o.quoted_tweet._original_tweet.id if o.quoted_tweet is not None else None,
        quoted_tweet=o.quoted_tweet._original_tweet if o.quoted_tweet is not None else None,
        user=Mock(id=o.user_id, screen_name=o.author_screen_name),
        entities={
            'urls': [{'expanded_url': url} for url in o.urls],
            'hashtags': [{'text': text} for text in o.hashtags],
            'user_mentions': [{'screen_name': screen_name} for screen_name in o.mentioned_screen_names]
        }))
    client = None

    class Params:
        text = 'some content'
        hashtags = []
        urls = []
        in_reply_to_tweet = None
        retweeted_tweet = None
        quoted_tweet = None
        user_id = factory.Faker('random_number', digits=17)
        id = factory.Faker('random_number', digits=17)
        author_screen_name = None
        mentioned_screen_names = []


class ResponseTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResponseTemplate

    response_type = factory.Faker('random_element', elements=TYPE_CHOICES)
