from django.test import SimpleTestCase
from robber import expect

from data.utils.calculations import percentile


class CalculationsTestCase(SimpleTestCase):
    def test_percentile_with_no_data(self):
        expect(percentile([], 0)).to.be.eq([])

    def test_percentile_with_no_inline(self):
        data = [
            {'id': '2', 'value': 0.2},
            {'id': '4', 'value': 0.5},
            {'id': '3', 'value': 0.4},
            {'id': '1', 'value': 0.1}
        ]
        result = percentile(data, percentile_rank=50)
        expect(result).to.be.eq([
            ({'id': '3', 'value': 0.4}, 50),
            ({'id': '4', 'value': 0.5}, 75)
        ])

    def test_percentile_with_custom_key(self):
        data = [
            {'id': '1', 'value': 0.1, 'custom_value': 0.1},
            {'id': '3', 'value': 0.4, 'custom_value': 0.3},
            {'id': '4', 'value': 0.4, 'custom_value': 0.4},
            {'id': '2', 'value': 0.2, 'custom_value': 0.1},
        ]
        result = percentile(data, 0, key='custom_value')
        expect(result).to.be.eq([
            ({'id': '1', 'value': 0.1, 'custom_value': 0.1}, 0),
            ({'id': '2', 'value': 0.2, 'custom_value': 0.1}, 0),
            ({'id': '3', 'value': 0.4, 'custom_value': 0.3}, 50),
            ({'id': '4', 'value': 0.4, 'custom_value': 0.4}, 75),
        ])

    def test_percentile_with_inline(self):
        data = [
            {'id': '2', 'value': 0.2},
            {'id': '4', 'value': 0.5},
            {'id': '3', 'value': 0.4},
            {'id': '1', 'value': 0.1}
        ]
        result = percentile(data, percentile_rank=50)
        expect(result).to.be.eq([
            {'id': '1', 'value': 0.1},
            {'id': '2', 'value': 0.2},
            {'id': '3', 'value': 0.4, 'percentile_value': 50},
            {'id': '4', 'value': 0.5, 'percentile_value': 75},
        ])

    def test_percentile_no_key_found(self):
        data = [
            {'id': '1', 'value': 0.1},
            {'id': '2', 'value': 0.2}
        ]
        expect(lambda: percentile(data, 50, key='not_exist')).to.throw_exactly(ValueError)
