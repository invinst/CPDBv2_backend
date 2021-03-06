from django.test import TestCase
from django.test.utils import override_settings
from mock.mock import mock_open

from robber import expect
from mock import patch, Mock

from twitterbot.response_builders import (
    SingleOfficerResponseBuilder, CoaccusedPairResponseBuilder, BaseResponseBuilder, NotFoundResponseBuilder)
from twitterbot.factories import ResponseTemplateFactory
from twitterbot.models import ResponseTemplate
from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory


class BaseResponseBuilderTestCase(TestCase):
    def setUp(self):
        ResponseTemplate.objects.all().delete()

        class DummyResponseBuilder(BaseResponseBuilder):
            response_type = 'single_officer'

            def get_variables_sets(self, entities, context):
                yield dict()

        self.builder_class = DummyResponseBuilder

    def test_build_with_round_robined_syntax(self):
        builder = self.builder_class()
        ResponseTemplateFactory(id=20, response_type='single_officer', syntax='temp1')
        ResponseTemplateFactory(id=21, response_type='single_officer', syntax='temp2')

        expect(list(builder.build(extra_variables={'user_name': 'abc'}))).to.eq([{
            'source': (),
            'tweet_content': 'temp1',
            'url': '',
            'type': 'single_officer',
            'entity': None,
            'coaccused': 0,
            'officer1': None,
            'officer2': None
        }])
        expect(list(builder.build(extra_variables={'user_name': 'def'}))).to.eq([{
            'source': (),
            'tweet_content': 'temp1',
            'url': '',
            'type': 'single_officer',
            'entity': None,
            'coaccused': 0,
            'officer1': None,
            'officer2': None
        }])
        expect(list(builder.build(extra_variables={'user_name': 'abc'}))).to.eq([{
            'source': (),
            'tweet_content': 'temp2',
            'url': '',
            'type': 'single_officer',
            'entity': None,
            'coaccused': 0,
            'officer1': None,
            'officer2': None
        }])
        expect(list(builder.build(extra_variables={'user_name': 'abc'}))).to.eq([{
            'source': (),
            'tweet_content': 'temp1',
            'url': '',
            'type': 'single_officer',
            'entity': None,
            'coaccused': 0,
            'officer1': None,
            'officer2': None
        }])

    def test_build_with_syntax_depend_on_right_response_type(self):
        builder = self.builder_class()

        ResponseTemplateFactory(response_type='single_officer', syntax='b')
        ResponseTemplateFactory(response_type='test', syntax='c')

        context = dict()

        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=context))).to.eq([{
            'source': (),
            'tweet_content': 'b',
            'url': '',
            'type': 'single_officer',
            'entity': None,
            'coaccused': 0,
            'officer1': None,
            'officer2': None
        }])

        expect(context['responses_count']).to.eq(1)

    def test_build_with_truncating_user_name_if_tweet_content_longer_than_140_characters(self):
        builder = self.builder_class()
        ResponseTemplateFactory(response_type='single_officer', syntax='@{{user_name}} anything else')
        with patch('twitterbot.response_builders.len', return_value=150):
            first_built = list(builder.build(extra_variables={'user_name': 'abc'}))[0]
            tweet_content = first_built['tweet_content']
            expect(tweet_content).to.eq('anything else')


class SingleOfficerResponseBuilderTestCase(TestCase):
    def setUp(self):
        ResponseTemplate.objects.all().delete()

    @override_settings(DOMAIN='http://foo.co')
    def test_build(self):
        _mock_open = mock_open()
        with patch('twitterbot.handlers.open', _mock_open, create=True):
            officer1 = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan', allegation_count=3)
            officer1_doc = {
                'id': officer1.id, 'full_name': officer1.full_name
            }

            officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
            officer2_doc = {
                'id': officer2.id, 'full_name': officer2.full_name
            }

            ResponseTemplateFactory(
                response_type='single_officer',
                syntax='@{{user_name}} {{officer.full_name}} has {{officer.allegation_count}} complaints')

            builder = SingleOfficerResponseBuilder()
            officers = [('source1', officer1_doc), ('source2', officer2_doc)]

            expect(list(builder.build(officers, {'user_name': 'abc'}))).to.eq([{
                'source': ('source1',),
                'tweet_content': '@abc Jerome Finnigan has 3 complaints',
                'url': 'http://foo.co/officer/1/',
                'type': 'single_officer',
                'entity': officer1_doc,
                'officer1': None,
                'officer2': None,
                'coaccused': 0,
            }, {
                'source': ('source2',),
                'tweet_content': '@abc Raymond Piwnicki has 0 complaints',
                'url': 'http://foo.co/officer/2/',
                'type': 'single_officer',
                'entity': officer2_doc,
                'officer1': None,
                'officer2': None,
                'coaccused': 0,
            }])


class CoaccusedPairResponseBuilderTestCase(TestCase):
    def setUp(self):
        ResponseTemplate.objects.all().delete()

    def test_build(self):
        officer1 = OfficerFactory(first_name='Jerome', last_name='Finnigan')
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        officer1_doc = {
            'id': officer1.id, 'full_name': officer1.full_name, 'complaints': 3
        }

        officer2 = OfficerFactory(first_name='Raymond', last_name='Piwnicki')
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        officer2_doc = {
            'id': officer2.id, 'full_name': officer2.full_name, 'complaints': 3
        }

        officer3 = OfficerFactory(first_name='Jesse', last_name='Acosta')
        OfficerAllegationFactory(officer=officer3)
        officer3_doc = {
            'id': officer3.id, 'full_name': officer3.full_name, 'complaints': 3
        }

        ResponseTemplateFactory(
            response_type='coaccused_pair',
            syntax=(
                '@{{user_name}} {{officer1.full_name}} and {{officer2.full_name}} '
                'were co-accused in {{coaccused}} case'
            )
        )

        builder = CoaccusedPairResponseBuilder()

        expect(list(builder.build(
            [('source1', officer1_doc), ('source2', officer2_doc), ('source3', officer3_doc)],
            {'user_name': 'abc'}))
        ).to.eq([{
            'source': ('source1', 'source2'),
            'tweet_content': '@abc Jerome Finnigan and Raymond Piwnicki were co-accused in 1 case',
            'url': '',
            'type': 'coaccused_pair',
            'entity': None,
            'officer1': officer1,
            'officer2': officer2,
            'coaccused': 1,
        }])


class NotFoundResponseBuilderTestCase(TestCase):
    def setUp(self):
        ResponseTemplate.objects.all().delete()
        ResponseTemplateFactory(
            response_type='not_found',
            syntax='Sorry, @{{user_name}}, the bot find nothing')

    def test_build_with_0_response(self):
        builder = NotFoundResponseBuilder()
        tweet = Mock(
            is_tweet_from_followed_accounts=False,
            is_retweet_of_twitterbot=False,
            is_quoted_tweet_of_twitterbot=False)
        context = {
            'response_count': 0,
            'incoming_tweet': tweet
        }
        with self.settings(DOMAIN='http://foo.co'):
            expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=context))).to.eq([{
                'source': (),
                'tweet_content': 'Sorry, @abc, the bot find nothing',
                'url': 'http://foo.co',
                'type': 'not_found',
                'entity': None,
                'officer1': None,
                'officer2': None,
                'coaccused': 0
            }])

    def test_build_with_response(self):
        builder = NotFoundResponseBuilder()
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context={'responses_count': 1}))).to.eq([])

    def test_do_nothing_if_retweet_of_twitterbot(self):
        builder = NotFoundResponseBuilder()
        tweet = Mock(
            is_tweet_from_followed_accounts=False,
            is_retweet_of_twitterbot=True,
            is_quoted_tweet_of_twitterbot=False)
        context = {
            'responses_count': 0,
            'incoming_tweet': tweet
        }
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=context))).to.eq([])

    def test_do_nothing_if_quoted_tweet_of_twitterbot(self):
        builder = NotFoundResponseBuilder()
        tweet = Mock(
            is_tweet_from_followed_accounts=False,
            is_retweet_of_twitterbot=False,
            is_quoted_tweet_of_twitterbot=True)
        context = {
            'responses_count': 0,
            'incoming_tweet': tweet
        }
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=context))).to.eq([])

    def test_do_nothing_if_there_is_no_incoming_tweet(self):
        builder = NotFoundResponseBuilder()
        context = {
            'responses_count': 0,
            'incoming_tweet': None
        }
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=context))).to.eq([])

    def test_do_nothing_if_there_is_no_context(self):
        builder = NotFoundResponseBuilder()
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context=None))).to.eq([])
