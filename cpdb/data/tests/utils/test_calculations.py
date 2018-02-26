from django.test import SimpleTestCase
from robber import expect

from data.utils.calculations import percentile


class CalculationsTestCase(SimpleTestCase):
    def test_percentile_with_(self):
        data = {'1': 0.1, '2': 0.2, '3': 0.3, '5': 0.4}
        percentile_rank = 50
        result = percentile(data, percentile_rank)
        expect(result).to.be.eq([('3', 50), ('5', 75)])
