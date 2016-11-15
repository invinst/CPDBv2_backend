from datetime import date, timedelta

from django.test import SimpleTestCase

from mock import patch, Mock

from cms.randomizers import (
    last_n_days, last_n_entries, randomize, RANDOMIZER_FUNCS)


class RandomizerTestCase(SimpleTestCase):
    def setUp(self):
        self.objects = Mock()
        self.objects.filter.return_value = ['1', '2', '3']
        self.objects.order_by.return_value = ['a', 'b', 'c']

    def test_last_n_days(self):
        results = last_n_days(self.objects, 10, 3)
        self.assertEqual(set(results), set(['1', '2', '3']))
        self.objects.filter.assert_called_with(created__gte=date.today() - timedelta(days=10))

    def test_last_n_days_sample_larger_than_pool(self):
        results = last_n_days(self.objects, 10, 10)
        self.assertEqual(len(results), 3)

    def test_last_n_entries(self):
        results = last_n_entries(self.objects, 10, 3)
        self.assertEqual(set(results), set(['a', 'b', 'c']))
        self.objects.order_by.assert_called_with('-created')

    def test_last_n_entries_sample_larger_than_pool(self):
        results = last_n_entries(self.objects, 3, 10)
        self.assertEqual(len(results), 3)

    def test_randomize(self):
        mock_last_n_days = Mock()
        mock_last_n_entries = Mock()
        with patch.dict(RANDOMIZER_FUNCS, {1: mock_last_n_days}):
            randomize(self.objects, 1, 0, 1)
            self.assertTrue(mock_last_n_days.called)
        with patch.dict(RANDOMIZER_FUNCS, {2: mock_last_n_entries}):
            randomize(self.objects, 1, 0, 2)
            self.assertTrue(mock_last_n_entries.called)
