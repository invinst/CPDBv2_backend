from mock import patch

from django.test import TestCase

from robber import expect

from landing_page.factories import LandingPageFactory
from story.factories import StoryPageFactory
from faq.factories import FAQPageFactory
from landing_page.serializers import LandingPageSerializer


class LandingPageSerializerTestCase(TestCase):
    @patch('landing_page.models.LandingPage.randomized_coverages')
    def test_get_reports(self, randomized_coverages):
        story_page = StoryPageFactory.build()
        randomized_coverages.return_value = [story_page]
        landing_page = LandingPageFactory.build()
        serializer = LandingPageSerializer()
        expect(serializer.get_reports(landing_page)).to.have.length(1)

    @patch('landing_page.models.LandingPage.randomized_faqs')
    def test_get_faqs(self, randomized_faqs):
        faq_page = FAQPageFactory.build()
        randomized_faqs.return_value = [faq_page]
        landing_page = LandingPageFactory.build()
        serializer = LandingPageSerializer()
        expect(serializer.get_faqs(landing_page)).to.have.length(1)
