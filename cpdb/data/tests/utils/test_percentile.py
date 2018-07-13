from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from data.utils.percentile import percentile, merge_metric
from officers.tests.utils import create_object, validate_object


class PercentileTestCase(SimpleTestCase):
    def test_percentile_with_no_data(self):
        expect(percentile([], 0)).to.be.eq([])

    def test_percentile(self):
        object1 = create_object({'id': 1, 'metric_value': 0.1})
        object2 = create_object({'id': 2, 'metric_value': 0.2})
        object3 = create_object({'id': 3, 'metric_value': 0.4})
        object4 = create_object({'id': 4, 'metric_value': 0.5})

        data = [object2, object4, object3, object1]
        percentile(data, percentile_type='value')

        expect(object3.percentile_value).to.eq(50)
        expect(object4.percentile_value).to.eq(75)

    def test_percentile_with_custom_key(self):
        object1 = create_object({'id': 1, 'value': 0.1, 'metric_custom_value': 0.1})
        object2 = create_object({'id': 2, 'value': 0.2, 'metric_custom_value': 0.1})
        object3 = create_object({'id': 3, 'value': 0.4, 'metric_custom_value': 0.3})
        object4 = create_object({'id': 4, 'value': 0.4, 'metric_custom_value': 0.4})

        data = [object1, object2, object3, object4]
        percentile(data, percentile_type='custom_value')

        expect(object1.percentile_custom_value).to.eq(0)
        expect(object2.percentile_custom_value).to.eq(0)
        expect(object3.percentile_custom_value).to.eq(50)
        expect(object4.percentile_custom_value).to.eq(75)

    def test_percentile_with_missing_value(self):
        object1 = create_object({'id': 1, 'value': 0.1, 'metric_custom_value': 0.1})
        object2 = create_object({'id': 2, 'value': 0.2, 'metric_custom_value': 0.2})
        object3 = create_object({'id': 3, 'value': 0.4})

        data = [object1, object2, object3]
        percentile(data, percentile_type='custom_value')

        expect(object1.percentile_custom_value).to.eq(0)
        expect(object2.percentile_custom_value).to.eq(50)
        expect(hasattr(object3, 'percentile_custom_value')).to.be.false()

    def test_merge_percentile(self):
        objects = [
            create_object({'id': 1, 'value_a': 0.1, 'metric_value_a': 0.1}),
            create_object({'id': 2, 'value_a': 0.2, 'metric_value_a': 0.1}),
            create_object({'id': 3, 'value_a': 0.4, 'metric_value_a': 0.3}),
        ]

        new_metric_query_set = Mock(
            exclude=Mock(return_value=[
                create_object({'id': 4, 'value_b': 0.3, 'value_c': 0.4, 'metric_value_b': 0.3, 'metric_value_c': 0.4}),
            ]),
            filter=Mock(
                return_value=Mock(
                    in_bulk=Mock(return_value={
                        2: create_object({'id': 2, 'metric_value_b': 0.3, 'metric_value_c': 0.4}),
                        3: create_object({'id': 3, 'metric_value_b': 0.6, 'metric_value_c': 0.8}),
                    })
                )
            )
        )

        results = merge_metric(objects, new_metric_query_set, ['value_b', 'value_c'])
        validate_object(results[0], {
            'id': 1,
            'value_a': 0.1,
            'metric_value_a': 0.1,
        })
        validate_object(results[1], {
            'id': 2,
            'value_a': 0.2,
            'metric_value_a': 0.1,
            'metric_value_b': 0.3,
            'metric_value_c': 0.4
        })
        validate_object(results[2], {
            'id': 3,
            'value_a': 0.4,
            'metric_value_a': 0.3,
            'metric_value_b': 0.6,
            'metric_value_c': 0.8
        })
        validate_object(results[3], {
            'id': 4,
            'value_b': 0.3,
            'value_c': 0.4,
            'metric_value_b': 0.3,
            'metric_value_c': 0.4
        })
