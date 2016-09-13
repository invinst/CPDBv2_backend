from datetime import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailcore.models import Page
from freezegun import freeze_time
import pytz
from mock import patch, Mock

from landing_page.randomizers import (
    last_n_days, last_n_entries, randomize,
    RANDOMIZER_STRAT_LAST_N_DAYS, RANDOMIZER_STRAT_LAST_N_ENTRIES, RANDOMIZER_FUNCS)
from faq.factories import FAQPageFactory
from faq.models import FAQPage


class RandomizerTestCase(TestCase):
    def setUp(self):
        self.root = Page.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

    @freeze_time('2016-09-21')
    def test_last_n_days(self):
        for i in xrange(1, 21):
            dt = datetime(2016, 9, i)
            self.root.add_child(instance=FAQPageFactory.build(created=dt))
        results = last_n_days(FAQPage.objects, 10, 3)
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result.created >= datetime(2016, 9, 11, tzinfo=pytz.utc))

    @freeze_time('2016-09-25')
    def test_last_n_days_sample_larger_than_population(self):
        for i in xrange(1, 4):
            dt = datetime(2016, 9, i)
            self.root.add_child(instance=FAQPageFactory.build(created=dt))
        results = last_n_days(FAQPage.objects, 10, 10)
        self.assertEqual(len(results), 3)

    def test_last_n_entries(self):
        for i in xrange(20):
            self.root.add_child(instance=FAQPageFactory.build())
        results = last_n_entries(FAQPage.objects, 10, 3)
        self.assertEqual(len(results), 3)
        sorted_faq_pages = FAQPage.objects.all().order_by('-created')
        for result in results:
            self.assertTrue(result in sorted_faq_pages)

    def test_last_n_entries_sample_larger_than_population(self):
        for i in xrange(3):
            self.root.add_child(instance=FAQPageFactory.build())
        results = last_n_entries(FAQPage.objects, 10, 10)
        self.assertEqual(len(results), 3)

    def test_randomize(self):
        mock_last_n_days = Mock()
        mock_last_n_entries = Mock()
        with patch.dict(RANDOMIZER_FUNCS, {RANDOMIZER_STRAT_LAST_N_DAYS: mock_last_n_days}):
            randomize(FAQPage.objects, 1, 0, RANDOMIZER_STRAT_LAST_N_DAYS)
            self.assertTrue(mock_last_n_days.called)
        with patch.dict(RANDOMIZER_FUNCS, {RANDOMIZER_STRAT_LAST_N_ENTRIES: mock_last_n_entries}):
            randomize(FAQPage.objects, 1, 0, RANDOMIZER_STRAT_LAST_N_ENTRIES)
            self.assertTrue(mock_last_n_entries.called)
