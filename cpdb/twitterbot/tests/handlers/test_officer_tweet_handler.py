from datetime import datetime
from functools import wraps

from django.test import TestCase, override_settings

import pytz
from freezegun import freeze_time
from mock import Mock, patch
from robber import expect

from activity_grid.models import ActivityCard
from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory
from twitterbot.factories import ResponseTemplateFactory, MockTweepyWrapperFactory
from twitterbot.models import ResponseTemplate
from twitterbot.models import TwitterBotResponseLog
from twitterbot.tweets import TweetContext
from twitterbot.handlers.officer_tweet_handler import OfficerTweetHandler
from twitterbot.tests.mixins import RebuildIndexMixin


def namepaser_returns(value):
    def _decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            with patch('twitterbot.name_parsers.GoogleNaturalLanguageNameParser.parse', return_value=value):
                return func(*args, **kwargs)
        return func_wrapper
    return _decorator


@override_settings(DOMAIN='http://foo.com')
class OfficerTweetHandlerTestCase(RebuildIndexMixin, TestCase):
    def setUp(self):
        super(OfficerTweetHandlerTestCase, self).setUp()
        ResponseTemplate.objects.all().delete()

        self.officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan', allegation_count=1)
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
            syntax='Sorry, @{{user_name}}, the bot finds nothing')
        self.screen_name = 'CPDPbot'
        self.tweet = {
            'id': 1,
            'user': {'id': 121, 'screen_name': 'abc'},
            'text': '',
            'in_reply_to_status_id': None,
            'retweeted_status': None,
            'quoted_status': None,
            'quoted_status_id': None,
            'created_at': '2017-08-03T11:59:00Z',
            'entities': {'user_mentions': [{'id': 123, 'screen_name': self.screen_name}], 'hashtags': [], 'urls': []}
        }
        self.client = MockTweepyWrapperFactory(screen_name=self.screen_name, subscription_screen_name='CPDPbot')
        self.client_patch = patch('twitterbot.handlers.base.TweepyWrapper', return_value=self.client)
        self.client_patch.start()
        self.outgoing_tweet = Mock(id=10, user=self.client.get_current_user())
        self.client.tweet = Mock(return_value=self.outgoing_tweet)
        self.send_tweet_patcher = patch('twitterbot.handlers.officer_tweet_handler.send_tweet')
        self.send_tweet = self.send_tweet_patcher.start()
        self.percentile_patch = patch(
            'officers.indexers.officers_indexer.officer_percentile.top_percentile',
            return_value=[]
        )
        self.percentile_patch.start()

    def tearDown(self):
        self.client_patch.stop()
        self.send_tweet_patcher.stop()
        self.percentile_patch.stop()

    @patch('twitterbot.handlers.officer_tweet_handler.TweetContext')
    def test_match_tweet(self, tweet_context):
        handler = OfficerTweetHandler(event_data=None, for_user_id=123, original_event=None)
        tweet_context_mock = tweet_context()
        tweet_context_mock.is_unfollow_tweet = False

        expect(handler.match_tweet()).to.be.true()

        tweet_context_mock.is_unfollow_tweet = True

        expect(handler.match_tweet()).to.be.false()

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @freeze_time('2017-08-03 12:00:01', tz_offset=0)
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_text(self, _):
        self.tweet['text'] = '@CPDPbot Jerome Finnigan'
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        expect(self.send_tweet).to.be.called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity={'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        )
        expect(ActivityCard.objects.get(officer=self.officer).last_activity).to.eq(
            datetime(2017, 8, 3, 12, 0, 1, tzinfo=pytz.utc))

    @namepaser_returns([])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_cpdb_officer_page_url(self, _):
        self.tweet['text'] = '@CPDPbot http://foo.com/officer/1/'
        self.tweet['entities']['urls'] = [
            {'expanded_url': 'http://foo.com/officer/1/'}
        ]

        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        expect(self.send_tweet).to.be.called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity={'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        )

    @namepaser_returns([('#jeromeFinnigan', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_hashtags(self, _):
        self.tweet['entities']['hashtags'] = [{'text': 'jeromeFinnigan'}]
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        expect(self.send_tweet).to.be.called_with(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity={'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        )

    @namepaser_returns([('http://fakeurl.com', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=10))
    def test_tweet_officer_in_tweet_link_content(self, _):
        self.tweet['entities']['urls'] = [{'expanded_url': 'http://fakeurl.com'}]
        with patch('twitterbot.utils.web_parsing.parse', return_value='Chicago Police Jerome Finnigan'):
            self.refresh_index()
            handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
            handler.handle()
            expect(self.send_tweet).to.be.called_with(
                '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
                in_reply_to=1,
                entity={'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
            )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_mention_recipients(self, _):
        self.tweet['entities']['user_mentions'] = [
            {'id': 123, 'screen_name': self.screen_name},
            {'id': 124, 'screen_name': 'def'}
        ]
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        entity = {'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        expect(self.send_tweet).to.be.any_call(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity=entity
        )
        expect(self.send_tweet).to.be.any_call(
            '@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20',
            in_reply_to=1,
            entity=entity
        )

    @namepaser_returns([('text', 'Jerome Finnigan'), ('text', 'Raymond Piwnicki')])
    def test_tweet_coaccused_pair(self):
        OfficerAllegationFactory(
            officer=OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki'),
            allegation=self.allegation
        )

        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        expect(self.send_tweet).to.be.called_with(
            '@abc Jerome Finnigan and Raymond Piwnicki were co-accused in 1 case',
            in_reply_to=1,
            entity=None
        )

    @namepaser_returns([('text', 'Raymond Piwnicki')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=5))
    def test_tweet_not_found(self, _):
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        self.send_tweet.assert_called_with(
            'Sorry, @abc, the bot finds nothing http://foo.com?twitterbot_log_id=5',
            in_reply_to=1,
            entity=None
        )

    @namepaser_returns([('text', 'Raymond Piwnicki')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', return_value=Mock(id=5))
    def test_tweet_context_is_reset(self, _):
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        self.send_tweet.assert_called_with(
            'Sorry, @abc, the bot finds nothing http://foo.com?twitterbot_log_id=5',
            in_reply_to=1,
            entity=None
        )
        self.send_tweet.reset_mock()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        self.send_tweet.assert_called_with(
            'Sorry, @abc, the bot finds nothing http://foo.com?twitterbot_log_id=5',
            in_reply_to=1,
            entity=None
        )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    def test_retweet_twitterbot_status(self):
        self.tweet['retweeted_status'] = {'user': {'id': 123}}
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        self.send_tweet.assert_not_called()

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_officer_in_replied_tweet(self, _):
        replied_tweet = {
            'id': 2,
            'user': {'id': 456, 'screen_name': 'def'},
            'text': '',
            'in_reply_to_status_id': None,
            'retweeted_status': None,
            'quoted_status': None,
            'quoted_status_id': None,
            'created_at': '2017-08-03T11:59:00Z',
            'entities': {'user_mentions': [{'id': 123, 'screen_name': self.screen_name}], 'hashtags': [], 'urls': []}
        }
        self.tweet['in_reply_to_status_id'] = 2
        self.client.register(TweetContext(original_tweet=replied_tweet, context={'client': self.client}))
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        entity = {'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        expect(self.send_tweet).to.be.any_call(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity=entity
        )
        expect(self.send_tweet).to.be.any_call(
            '@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20',
            in_reply_to=1,
            entity=entity
        )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch('twitterbot.models.TwitterBotResponseLog.objects.create', side_effect=[Mock(id=10), Mock(id=20)])
    def test_tweet_officer_in_retweet_tweet(self, _):
        retweeted_status = {
            'id': 2,
            'user': {'id': 456, 'screen_name': 'def'},
            'text': '',
            'in_reply_to_status_id': None,
            'retweeted_status': None,
            'quoted_status': None,
            'quoted_status_id': None,
            'created_at': '2017-08-03T11:59:00Z',
            'entities': {'user_mentions': [{'id': 123, 'screen_name': self.screen_name}], 'hashtags': [], 'urls': []}
        }
        self.tweet['retweeted_status'] = retweeted_status
        self.client.register(TweetContext(original_tweet=retweeted_status, context={'client': self.client}))
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        entity = {'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        expect(self.send_tweet).to.be.any_call(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=2,
            entity=entity
        )
        expect(self.send_tweet).to.be.any_call(
            '@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20',
            in_reply_to=2,
            entity=entity
        )

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @patch(
        'twitterbot.models.TwitterBotResponseLog.objects.create',
        side_effect=[Mock(id=10), Mock(id=20), Mock(id=30), Mock(id=40)])
    def test_tweet_officer_in_quoted_tweet(self, _):
        quoted_status = {
            'id': 2,
            'user': {'id': 456, 'screen_name': 'def'},
            'text': '',
            'in_reply_to_status_id': None,
            'retweeted_status': None,
            'quoted_status': None,
            'quoted_status_id': None,
            'created_at': '2017-08-03T11:59:00Z',
            'entities': {'user_mentions': [{'id': 123, 'screen_name': self.screen_name}], 'hashtags': [], 'urls': []}
        }
        self.tweet['quoted_status'] = quoted_status
        self.client.register(
            TweetContext(original_tweet=quoted_status, context={'client': self.client, 'for_user_id': 123})
        )
        self.refresh_index()
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        entity = {'allegation_count': 1, 'percentiles': [], 'id': 1, 'full_name': u'Jerome Finnigan'}
        expect(self.send_tweet).to.be.any_call(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=10',
            in_reply_to=1,
            entity=entity
        )
        expect(self.send_tweet).to.be.any_call(
            '@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=20',
            in_reply_to=1,
            entity=entity
        )

        self.send_tweet.reset_mock()
        self.tweet['quoted_status'] = None
        self.tweet['quoted_status_id'] = 2
        self.client.register(TweetContext(original_tweet=quoted_status, context={'client': self.client}))
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        expect(self.send_tweet).to.be.any_call(
            '@abc Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=30',
            in_reply_to=1,
            entity=entity
        )
        expect(self.send_tweet).to.be.any_call(
            '@def Jerome Finnigan has 1 complaints http://foo.com/officer/1/?twitterbot_log_id=40',
            in_reply_to=1,
            entity=entity
        )

    @namepaser_returns([('text', 'Raymond Piwnicki')])
    def test_tweet_not_mentioning_twitterbot(self):
        self.tweet['entities']['user_mentions'] = []
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=None)
        handler.handle()
        self.send_tweet.assert_not_called()

    @namepaser_returns([('text', 'Jerome Finnigan')])
    @freeze_time('2017-08-03 12:00:01', tz_offset=0)
    def test_save_log(self):
        self.tweet['text'] = '@CPDPbot Jerome Finnigan'
        self.refresh_index()
        original_event = {
            'tweet_create_events': [
                {
                    'text': '@CPDPbot Jerome Finnigan'
                }
            ],
            'for_user_id': 123
        }
        handler = OfficerTweetHandler(event_data=self.tweet, for_user_id=123, original_event=original_event)
        handler.handle()

        response_log = TwitterBotResponseLog.objects.all().first()
        entity_url = 'http://foo.com/officer/1/?twitterbot_log_id=%d' % (response_log.id)
        expect(response_log.sources).to.eq('text')
        expect(response_log.entity_url).to.eq(entity_url)
        expect(response_log.tweet_content).to.eq(
            '@abc Jerome Finnigan has 1 complaints %s' % (entity_url))
        expect(response_log.created_at).to.eq(datetime(2017, 8, 3, 12, 0, 1, tzinfo=pytz.utc))
        expect(response_log.incoming_tweet_username).to.eq('abc')
        expect(response_log.incoming_tweet_url).to.eq('https://twitter.com/abc/status/1/')
        expect(response_log.incoming_tweet_content).to.eq('@CPDPbot Jerome Finnigan')
        expect(response_log.original_tweet_username).to.eq('abc')
        expect(response_log.original_tweet_url).to.eq('https://twitter.com/abc/status/1/')
        expect(response_log.original_tweet_content).to.eq('@CPDPbot Jerome Finnigan')
        expect(response_log.original_event_object).to.eq(original_event)
        expect(response_log.status).to.eq(TwitterBotResponseLog.SENT)
