from datetime import date, timedelta

from django.test import SimpleTestCase

from mock import patch, Mock

from cms.randomizers import (
    last_n_days, last_n_entries, starred_only, randomize, RANDOMIZER_FUNCS)


class RandomizerTestCase(SimpleTestCase):
    def setUp(self):
        self.objects = Mock()

    def test_last_n_days(self):
        self.objects.filter.return_value = ['1', '2', '3']

        results = last_n_days(self.objects, 10)
        self.assertEqual(results, ['1', '2', '3'])
        self.objects.filter.assert_called_with(created__gte=date.today() - timedelta(days=10))

    def test_last_n_entries(self):
        self.objects.order_by.return_value = ['a', 'b', 'c']

        results = last_n_entries(self.objects, 10)
        self.assertEqual(results, ['a', 'b', 'c'])
        self.objects.order_by.assert_called_with('-created')

    def test_starred_only(self):
        mock = Mock()
        mock.order_by.return_value = ['A', 'B', 'C']
        self.objects.filter.return_value = mock

        results = starred_only(self.objects, 10)
        self.objects.filter.assert_called_with(starred=True)
        mock.order_by.assert_called_with('-created')
        self.assertEqual(results, ['A', 'B', 'C'])

    def test_randomize(self):
        mock_last_n_days = Mock(return_value=['1', '2', '3'])
        mock_last_n_entries = Mock(return_value=['a', 'b', 'c'])
        mock_starred_only = Mock(return_value=['A', 'B', 'C'])

        with patch.dict(RANDOMIZER_FUNCS, {1: mock_last_n_days, 2: mock_last_n_entries, 3: mock_starred_only}):
            randomize(self.objects, 1, 0, 1)
            self.assertTrue(mock_last_n_days.called)

            randomize(self.objects, 1, 0, 2)
            self.assertTrue(mock_last_n_entries.called)

            randomize(self.objects, 1, 0, 3)
            self.assertTrue(mock_starred_only.called)

    def test_randomize_sample_larger_than_pool(self):
        strategy = Mock(return_value=['1', '2', '3', '4', '5'])

        with patch.dict(RANDOMIZER_FUNCS, {1: strategy}):
            results = randomize(self.objects, 5, 3, 1)
            self.assertEqual(len(results), 3)
