from django.test import TestCase

from robber import expect
from mock import patch, Mock

from twitterbot.response_builders import (
    SingleOfficerResponseBuilder, CoaccusedPairResponseBuilder, BaseResponseBuilder, NotFoundResponseBuilder)
from twitterbot.factories import ResponseTemplateFactory
from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory


class BaseResponseBuilderTestCase(TestCase):
    def setUp(self):
        class DumbResponseBuilder(BaseResponseBuilder):
            response_type = 'dumb'

            def get_variables_sets(self, entities, context):
                yield dict()

        self.builder_class = DumbResponseBuilder

    def test_build_with_randomized_syntax(self):
        builder = self.builder_class()

        with patch('twitterbot.response_builders.random.choice', return_value=Mock(syntax='a is {{number}}')):
            expect(list(builder.build(extra_variables={'number': 18}))).to.eq(['a is 18'])

    def test_build_with_syntax_depend_on_right_response_type(self):
        builder = self.builder_class()

        ResponseTemplateFactory(response_type='dumb', syntax='b')
        ResponseTemplateFactory(response_type='test', syntax='c')

        context = dict()

        expect(list(builder.build(context=context))).to.eq(['b'])

        expect(context['responses_count']).to.eq(1)


class SingleOfficerResponseBuilderTestCase(TestCase):
    def test_build(self):
        officer1 = Mock(full_name='Jerome Finnigan', complaints=3)
        officer1.get_absolute_url = Mock(return_value='/officer/1/')
        officer2 = Mock(full_name='Raymond Piwnicki', complaints=0)
        officer2.get_absolute_url = Mock(return_value='/officer/2/')

        ResponseTemplateFactory(
            response_type='single_officer',
            syntax='@{{user_name}} {{officer.full_name}} has {{officer.complaints}} complaints {{url}}')

        builder = SingleOfficerResponseBuilder()
        officers = [officer1, officer2]

        with self.settings(DOMAIN='http://foo.co'):
            expect(list(builder.build(officers, {'user_name': 'abc'}))).to.eq([
                '@abc Jerome Finnigan has 3 complaints http://foo.co/officer/1/',
                '@abc Raymond Piwnicki has 0 complaints http://foo.co/officer/2/'
            ])


class CoaccusedPairResponseBuilderTestCase(TestCase):
    def test_build(self):
        officer1 = OfficerFactory(first_name='Jerome', last_name='Finnigan')
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer1, allegation=allegation)

        officer2 = OfficerFactory(first_name='Raymond', last_name='Piwnicki')
        OfficerAllegationFactory(officer=officer2, allegation=allegation)

        officer3 = OfficerFactory(first_name='Jesse', last_name='Acosta')
        OfficerAllegationFactory(officer=officer3)

        ResponseTemplateFactory(
            response_type='coaccused_pair',
            syntax=(
                '@{{user_name}} {{officer1.full_name}} and {{officer2.full_name}} '
                'were co-accused in {{coaccused}} case'
            )
        )

        builder = CoaccusedPairResponseBuilder()

        expect(list(builder.build([officer1, officer2, officer3], {'user_name': 'abc'}))).to.eq([
            '@abc Jerome Finnigan and Raymond Piwnicki were co-accused in 1 case'
        ])


class NotFoundResponseBuilderTestCase(TestCase):
    def setUp(self):
        ResponseTemplateFactory(
            response_type='not_found',
            syntax='Sorry, @{{user_name}}, the bot find nothing')

    def test_build_with_0_response(self):
        builder = NotFoundResponseBuilder()
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context={'responses_count': 0}))).to.eq([
            'Sorry, @abc, the bot find nothing'
        ])

    def test_build_with_response(self):
        builder = NotFoundResponseBuilder()
        expect(list(builder.build(extra_variables={'user_name': 'abc'}, context={'responses_count': 1}))).to.eq([])
