from functools import wraps
import datetime

from django.test import SimpleTestCase, TestCase, override_settings

import pytz
from mock import Mock, patch, call
from robber import expect
from freezegun import freeze_time
from responsebot.common.exceptions import CharacterLimitError, StatusDuplicateError

from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory

from twitterbot.handlers import OfficerTweetHandler, CPDBEventHandler, CPDBUnfollowHandler
from twitterbot.factories import ResponseTemplateFactory, MockClientFactory
from twitterbot.tweets import Tweet
from twitterbot.models import ResponseTemplate
from twitterbot.models import TwitterBotResponseLog


def namepaser_returns(value):
    def _decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            with patch('twitterbot.name_parsers.GoogleNaturalLanguageNameParser.parse', return_value=value):
                return func(*args, **kwargs)
        return func_wrapper
    return _decorator


@override_settings(DOMAIN='http://foo.com')
class OfficerTweetHandlerTestCase(TestCase):
    def setUp(self):
        ResponseTemplate.objects.all().delete()
        self.officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        self.allegation = AllegationFactory()
        OfficerAllegationFactory(officer=self.officer, allegation=self.allegation)
        ResponseTemplateFactory(
            response_type='single_officer',
            syntax='@{{user_name}} {{officer.full_name}} has {{officer.allegation_count}} complaints')
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
            created_at=datetime.datetime(2017, 8, 3, 11, 59, 0, tzinfo=pytz.utc),
            entities={'user_mentions': [], 'hashtags': [], 'urls': []})
        self.client = MockClientFactory()
        self.outgoing_tweet = Mock(id=10, user=self.client.get_current_user())
        self.client.tweet = Mock(return_value=self.outgoing_tweet)
        self.handler = OfficerTweetHandler(client=self.client)

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @freeze_time('2017-08-03 12:00:01', tz_offset=0)
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_text(self, _):
        self.tweet.text = '@CPDPbot Jerome Finnigan'
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1
        )

    @namepaser_returns([('#jeromeFinnigan', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_hashtags(self, _):
        self.tweet.entities['hashtags'] = [{'text': 'jeromeFinnigan'}]
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1
        )

    @namepaser_returns([('http://fakeurl.com', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_link_content(self, _):
        self.tweet.entities['urls'] = [{'expanded_url': 'http://fakeurl.com'}]
        with patch('twitterbot.utils.web_parsing.parse', return_value='Chicago Police Jerome Finnigan'):
            self.handler.on_tweet(self.tweet)
            self.client.tweet.assert_called_with(
                '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
                in_reply_to=1
            )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_mention_recipients(self, _):
        self.tweet.entities['user_mentions'] = [{'screen_name': 'def'}]
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20', in_reply_to=1)
        ])

    @namepaser_returns([('text', 'Jerome Finnigan'), ('text', 'Raymond Piwnicki')])
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

    @namepaser_returns([('text', 'Raymond Piwnicki')])
    def test_tweet_not_found(self):
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_called_with(
            'Sorry, @abc, the bot find nothing',
            in_reply_to=1
        )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_officer_in_replied_tweet(self, _):
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
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20', in_reply_to=1)
        ])

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_officer_in_retweet_tweet(self, _):
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
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10', in_reply_to=2),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20', in_reply_to=2)
        ])

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch(
        'twitterbot.models.TwitterBotResponseLog.objects.create',
        side_effect=[Mock(id=10), Mock(id=20), Mock(id=30), Mock(id=40)])
    def test_tweet_officer_in_quoted_tweet(self, _):
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
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20', in_reply_to=1)
        ])

        self.client.tweet.reset_mock()
        self.tweet.quoted_tweet = None
        self.tweet.quoted_tweet_id = 2
        self.client.register(Tweet(original_tweet=quoted_tweet, client=self.client))
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_has_calls([
            call('@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=30', in_reply_to=1),
            call('@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=40', in_reply_to=1)
        ])

    def test_filter_tweets_from_other_bots(self):
        tweets = [Mock(user=Mock(id=bot)) for bot in [30582622, 4880788160, 4923697764]]
        for tweet in tweets:
            self.handler.on_tweet(tweet)
        self.client.tweet.assert_not_called()

    def test_filter_unfollow_tweets(self):
        self.tweet.text = '@ScreenName STOP'
        self.handler.on_tweet(self.tweet)
        self.client.tweet.assert_not_called()

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @freeze_time('2017-08-03 12:00:01', tz_offset=0)
    def test_save_log(self):
        self.tweet.text = '@CPDPbot Jerome Finnigan'
        self.handler.on_tweet(self.tweet)

        response_log = TwitterBotResponseLog.objects.all().first()
        entity_url = 'http://foo.com/officer/1/?twitterbot_log_id=%d' % (response_log.id)
        expect(response_log.sources).to.eq('text')
        expect(response_log.entity_url).to.eq(entity_url)
        expect(response_log.tweet_content).to.eq(
            '@abc Jerome Finnigan has 1 complaints %s' % (entity_url))
        expect(response_log.created_at).to.eq(datetime.datetime(2017, 8, 3, 12, 0, 1, tzinfo=pytz.utc))
        expect(response_log.tweet_url).to.eq('https://twitter.com/ScreenName/status/10/')
        expect(response_log.incoming_tweet_username).to.eq('abc')
        expect(response_log.incoming_tweet_url).to.eq('https://twitter.com/abc/status/1/')
        expect(response_log.incoming_tweet_content).to.eq('@CPDPbot Jerome Finnigan')
        expect(response_log.original_tweet_username).to.eq('abc')
        expect(response_log.original_tweet_url).to.eq('https://twitter.com/abc/status/1/')
        expect(response_log.original_tweet_content).to.eq('@CPDPbot Jerome Finnigan')
        expect(response_log.status).to.eq(TwitterBotResponseLog.SENT)

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=1))
    def test_character_limit_error(self, _):
        self.client.tweet = Mock(side_effect=CharacterLimitError)
        with patch('twitterbot.handlers.logger.error') as mock_error:
            self.handler.on_tweet(self.tweet)
            mock_error.assert_called_with(
                'Tweet is too long - '
                '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=1')

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=1))
    def test_status_duplicate_error(self, _):
        self.client.tweet = Mock(side_effect=StatusDuplicateError)
        with patch('twitterbot.handlers.logger.error') as mock_error:
            self.handler.on_tweet(self.tweet)
            mock_error.assert_called_with(
                'Tweet already sent recently - tweet: '
                '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=1')


class CPDBEventHandlerTestCase(SimpleTestCase):
    def setUp(self):
        self.client = MockClientFactory(id=111)
        self.client.follow = Mock(return_value=None)
        self.event = Mock(source=Mock(id=456))
        self.handler = CPDBEventHandler(client=self.client)

    def test_follow_back(self):
        self.event.target = Mock(id=111)
        self.handler.on_follow(self.event)
        self.client.follow.assert_called_with(456)

    def test_not_follow_back(self):
        self.event.target = Mock(id=123)
        self.handler.on_follow(self.event)
        self.client.follow.assert_not_called()


class CPDBUnfollowHandlerTestCase(SimpleTestCase):
    def setUp(self):
        self.tweet = Mock(user=Mock(id=123))
        self.client = MockClientFactory(screen_name='abc')
        self.client.unfollow = Mock(return_value=None)
        self.handler = CPDBUnfollowHandler(client=self.client)

    def test_unfollow(self):
        self.tweet.text = '@abc STOP'
        self.handler.on_tweet(self.tweet)
        self.client.unfollow.assert_called_with(123)

    def test_not_unfollow(self):
        self.tweet.text = 'Any text other than @{user} STOP'
        self.handler.on_tweet(self.tweet)
        self.client.unfollow.assert_not_called()
