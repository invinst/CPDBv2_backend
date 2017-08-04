from functools import wraps

from django.test import TestCase, override_settings

from mock import Mock, patch, call

from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory

from twitterbot.handlers import OfficerTweetHandler
from twitterbot.factories import ResponseTemplateFactory, MockClientFactory
from twitterbot.tweets import Tweet


def rosette_return(value):
    def _decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            with patch('twitterbot.name_parsers.RosettePersonNameParser.parse', return_value=value):
                return func(*args, **kwargs)
        return func_wrapper
    return _decorator


@override_settings(DOMAIN='http://foo.com')
class OfficerTweetHandlerTestCase(TestCase):
    def setUp(self):
        self.officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        self.allegation = AllegationFactory()
        OfficerAllegationFactory(officer=self.officer, allegation=self.allegation)
        ResponseTemplateFactory(
            response_type='single_officer',
            syntax='@{{user_name}} {{officer.full_name}} has {{officer.allegation_count}} complaints {{url}}')
        ResponseTemplateFactory(
            response_type='coaccused_pair',
            syntax=('@{{user_name}} {{officer1.full_name}} and {{officer2.full_name}} '
                    'were co-accused in {{coaccused}} case'))
        ResponseTemplateFactory(
            response_type='not_found',
            syntax='Sorry, @{{user_name}}, the bot find nothing')
        self.tweet = Mock(
            id=1,
            user=Mock(id=123, screen_name='abc'),
            text='',
            in_reply_to_tweet_id=None,
            retweeted_tweet=None,
            quoted_tweet=None,
            quoted_tweet_id=None,
            entities={'user_mentions': [], 'hashtags': [], 'urls': []})
        self.client = MockClientFactory()
        self.client.tweet = Mock(return_value=None)
        self.handler = OfficerTweetHandler(client=self.client)

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_tweet_text(self):
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/',
            in_reply_to=1
        )

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_tweet_hashtags(self):
        self.tweet.entities['hashtags'] = [{'text': 'jeromeFinnigan'}]
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/',
            in_reply_to=1
        )

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_tweet_link_content(self):
        self.tweet.entities['urls'] = [{'expanded_url': 'http://fakeurl.com'}]
        with patch('twitterbot.utils.web_parsing.parse', return_value='Chicago Police Jerome Finnigan'):
            self.handler.on_tweet(self.tweet)
            self.client.tweet.assert_called_with(
                '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/',
                in_reply_to=1
            )

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_mention_recipients(self):
        self.tweet.entities['user_mentions'] = [{'screen_name': 'def'}]
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1)
        ])

    @rosette_return(['Jerome Finnigan', 'Raymond Piwnicki'])
    def test_tweet_coaccused_pair(self):
        OfficerAllegationFactory(
            officer=OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki'),
            allegation=self.allegation
        )
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            '@abc Jerome Finnigan and Raymond Piwnicki were co-accused in 1 case',
            in_reply_to=1
        )

    @rosette_return(['Raymond Piwnicki'])
    def test_tweet_not_found(self):
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            'Sorry, @abc, the bot find nothing',
            in_reply_to=1
        )

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_replied_tweet(self):
        replied_tweet = Mock(
            id=2,
            user=Mock(id=456, screen_name='def'),
            text='',
            in_reply_to_tweet_id=None,
            retweeted_tweet=None,
            quoted_tweet=None,
            quoted_tweet_id=None,
            entities={'user_mentions': [], 'hashtags': [], 'urls': []})
        self.tweet.in_reply_to_tweet_id = 2
        self.client.register(Tweet(original_tweet=replied_tweet, client=self.client))
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1)
        ])

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_retweet_tweet(self):
        retweeted_tweet = Mock(
            id=2,
            user=Mock(id=456, screen_name='def'),
            text='',
            in_reply_to_tweet_id=None,
            retweeted_tweet=None,
            quoted_tweet=None,
            quoted_tweet_id=None,
            entities={'user_mentions': [], 'hashtags': [], 'urls': []})
        self.tweet.retweeted_tweet = retweeted_tweet
        self.client.register(Tweet(original_tweet=retweeted_tweet, client=self.client))
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=2),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=2)
        ])

    @rosette_return(['Jerome Finnigan'])
    def test_tweet_officer_in_quoted_tweet(self):
        quoted_tweet = Mock(
            id=2,
            user=Mock(id=456, screen_name='def'),
            text='',
            in_reply_to_tweet_id=None,
            retweeted_tweet=None,
            quoted_tweet=None,
            quoted_tweet_id=None,
            entities={'user_mentions': [], 'hashtags': [], 'urls': []})
        self.tweet.quoted_tweet = quoted_tweet
        self.client.register(Tweet(original_tweet=quoted_tweet, client=self.client))
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1)
        ])

        self.tweet.quoted_tweet = None
        self.tweet.quoted_tweet_id = 2
        self.client.register(Tweet(original_tweet=quoted_tweet, client=self.client))
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/', in_reply_to=1)
        ])
