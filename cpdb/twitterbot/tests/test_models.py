from django.test import TestCase

from robber import expect

from twitterbot.factories import ResponseTemplateFactory
from twitterbot.models import TweetResponseRoundRobin


class TweetResponseRoundRobinManagerTestCase(TestCase):
    def test_get_template(self):
        ResponseTemplateFactory(id=10, syntax='single_officer_template_1', response_type='single_officer')
        ResponseTemplateFactory(id=11, syntax='single_officer_template_2', response_type='single_officer')
        ResponseTemplateFactory(id=12, syntax='single_officer_template_3', response_type='single_officer')
        ResponseTemplateFactory(id=13, syntax='coaccused_pair_template', response_type='coaccused_pair')

        response_template = TweetResponseRoundRobin.objects.get_template(
            username='Somedude', response_type='single_officer')
        expect(response_template.syntax).to.eq('single_officer_template_1')

        response_template = TweetResponseRoundRobin.objects.get_template(
            username='Somedude', response_type='single_officer')
        expect(response_template.syntax).to.eq('single_officer_template_2')

        response_template = TweetResponseRoundRobin.objects.get_template(
            username='Somedude', response_type='coaccused_pair')
        expect(response_template.syntax).to.eq('coaccused_pair_template')

        response_template = TweetResponseRoundRobin.objects.get_template(
            username='Somedude', response_type='single_officer')
        expect(response_template.syntax).to.eq('single_officer_template_3')

        response_template = TweetResponseRoundRobin.objects.get_template(
            username='Somedude', response_type='single_officer')
        expect(response_template.syntax).to.eq('single_officer_template_1')
