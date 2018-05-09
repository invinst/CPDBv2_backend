from django.test import SimpleTestCase
from robber import expect

from data.utils.calculations import percentile
from officers.tests.ultils import create_object


class CalculationsTestCase(SimpleTestCase):
    def test_percentile_with_no_data(self):
        expect(percentile([], 0)).to.be.eq([])

    def test_percentile(self):
        object1 = create_object({'id': '1', 'value': 0.1})
        object2 = create_object({'id': '2', 'value': 0.2})
        object3 = create_object({'id': '3', 'value': 0.4})
        object4 = create_object({'id': '4', 'value': 0.5})

        data = [object2, object4, object3, object1]
        result = percentile(data, percentile_rank=50)

        expect(result).to.be.eq([
            object1,
            object2,
            object3,
            object4,
        ])

        expect(object3.percentile_value).to.eq(50)
        expect(object4.percentile_value).to.eq(75)

    def test_percentile_with_custom_key(self):
        object1 = create_object({'id': '1', 'value': 0.1, 'custom_value': 0.1})
        object2 = create_object({'id': '2', 'value': 0.2, 'custom_value': 0.1})
        object3 = create_object({'id': '3', 'value': 0.4, 'custom_value': 0.3})
        object4 = create_object({'id': '4', 'value': 0.4, 'custom_value': 0.4})

        data = [object1, object2, object3, object4]
        result = percentile(data, 0, key='custom_value')

        expect(result).to.be.eq([
            object1,
            object2,
            object3,
            object4,
        ])
        expect(object1.percentile_custom_value).to.eq(0)
        expect(object2.percentile_custom_value).to.eq(0)
        expect(object3.percentile_custom_value).to.eq(50)
        expect(object4.percentile_custom_value).to.eq(75)

    def test_percentile_no_key_found(self):
        data = [
            {'id': '1', 'value': 0.1},
            {'id': '2', 'value': 0.2}
        ]
        expect(lambda: percentile(data, 50, key='not_exist')).to.throw_exactly(ValueError)
