from mock import patch

from django.test import TestCase

from robber import expect

from landing_page.models import LandingPage, StoryPage, FAQPage, RANDOMIZER_STRAT_LAST_N_ENTRIES


class LandingPageTestCase(TestCase):
    @patch('landing_page.models.randomize')
    def test_randomized_coverages(self, randomize):
        randomize.return_value = 'something'
        landing_page = LandingPage()
        landing_page.coverage_strat_n = 10
        expect(LandingPage().randomized_coverages()).to.eq('something')
        randomize.assert_called_with(StoryPage.objects, 10, 3, RANDOMIZER_STRAT_LAST_N_ENTRIES)

    @patch('landing_page.models.randomize')
    def test_randomized_faqs(self, randomize):
        randomize.return_value = 'something'
        landing_page = LandingPage()
        landing_page.coverage_strat_n = 10
        expect(LandingPage().randomized_faqs()).to.eq('something')
        randomize.assert_called_with(FAQPage.objects, 10, 3, RANDOMIZER_STRAT_LAST_N_ENTRIES)
