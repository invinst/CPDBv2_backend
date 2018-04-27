from django.test import SimpleTestCase
from mock import Mock
from robber import expect

from data.utils.calculations import percentile


class CalculationsTestCase(SimpleTestCase):
    def test_percentile_with_no_data(self):
        expect(percentile([], 0)).to.be.eq([])

    def test_percentile(self):
        object1 = Mock(**{'id': '1', 'value': 0.1})
        object2 = Mock(**{'id': '2', 'value': 0.2})
        object3 = Mock(**{'id': '3', 'value': 0.4})
        object4 = Mock(**{'id': '4', 'value': 0.5})

        data = [object2, object4, object3, object1]
        result = percentile(data, percentile_rank=50)

        object3.percentile_value = 50
        object4.percentile_value = 75

        expect(result).to.be.eq([
            object1,
            object2,
            object3,
            object4,
        ])

    def test_percentile_with_custom_key(self):
        object1 = Mock(**{'id': '1', 'value': 0.1, 'custom_value': 0.1})
        object2 = Mock(**{'id': '2', 'value': 0.2, 'custom_value': 0.1})
        object3 = Mock(**{'id': '3', 'value': 0.4, 'custom_value': 0.3})
        object4 = Mock(**{'id': '4', 'value': 0.4, 'custom_value': 0.4})

        data = [object1, object2, object3, object4]
        result = percentile(data, 0, key='custom_value')

        object1.percentile_value = 0
        object2.percentile_value = 0
        object3.percentile_value = 50
        object4.percentile_value = 75

        expect(result).to.be.eq([
            object1,
            object2,
            object3,
            object4,
        ])

    def test_percentile_no_key_found(self):
        data = [
            {'id': '1', 'value': 0.1},
            {'id': '2', 'value': 0.2}
        ]
        expect(lambda: percentile(data, 50, key='not_exist')).to.throw_exactly(ValueError)
