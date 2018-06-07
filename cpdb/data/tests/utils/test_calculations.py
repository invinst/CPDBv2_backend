from datetime import date, datetime

import pytz
from django.test import SimpleTestCase, TestCase
from robber import expect

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory
from data.utils.percentile import percentile
from data.utils.calculations import calculate_top_percentile
from officers.tests.ultils import create_object
from trr.factories import TRRFactory


class PercentileTestCase(SimpleTestCase):
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


class CalculateTopPercentileTestCase(TestCase):
    def test_calculate_top_percentile(self):
        allegation = AllegationFactory()
        officer = OfficerFactory(appointed_date=date(2002, 1, 1))
        officer1 = OfficerFactory(appointed_date=date(2000, 1, 1))
        officer2 = OfficerFactory(appointed_date=date(2001, 1, 1))
        OfficerAllegationFactory(officer=officer, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer1, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer2, allegation=allegation, final_finding='NS')
        TRRFactory(officer=officer1, trr_datetime=datetime(2017, 1, 3, tzinfo=pytz.utc))
        TRRFactory(officer=officer2, trr_datetime=datetime(2017, 1, 3, tzinfo=pytz.utc))

        expect(calculate_top_percentile()).to.eq({
            officer.id: {
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 0,
                'percentile_trr': 0,
                'percentile_allegation': 66.6667,
            },
            officer1.id: {
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 0,
                'percentile_trr': 33.3333,
                'percentile_allegation': 0,
            },
            officer2.id: {
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 0,
                'percentile_trr': 66.6667,
                'percentile_allegation': 33.3333,
            },
        })
