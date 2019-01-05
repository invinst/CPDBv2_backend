from django.test import TestCase

from robber import expect
from decimal import Decimal

from data.factories import OfficerFactory, OfficerAllegationFactory
from data.models import OfficerAllegation
from data.utils.getters import get_officers_most_complaints_from_query


class GettersUtilTestCase(TestCase):
    def test_get_officers_most_complaints(self):
        officer1 = OfficerFactory(
            first_name='A',
            last_name='B',
            complaint_percentile=11.1111,
            civilian_allegation_percentile=22.2222,
            internal_allegation_percentile=33.3333,
            trr_percentile=44.4444,
        )
        officer2 = OfficerFactory(
            first_name='C',
            last_name='D',
            complaint_percentile=33.3333,
            civilian_allegation_percentile=44.4444,
            internal_allegation_percentile=55.5555,
            trr_percentile=66.6666,
        )
        officer3 = OfficerFactory(
            first_name='E',
            last_name='F',
            complaint_percentile=66.6666,
            civilian_allegation_percentile=77.7777,
            internal_allegation_percentile=88.8888,
            trr_percentile=99.9999,
        )
        OfficerFactory.create_batch(2)

        OfficerAllegationFactory.create_batch(5, officer=officer1)
        OfficerAllegationFactory.create_batch(2, officer=officer2)
        OfficerAllegationFactory.create_batch(3, officer=officer3)

        query = OfficerAllegation.objects.all()
        officers_most_complaints = get_officers_most_complaints_from_query(query)
        expect(list(officers_most_complaints)).to.eq([
            {
                'id': officer1.id,
                'name': 'A B',
                'count': 5,
                'percentile_allegation': Decimal('11.1111'),
                'percentile_allegation_civilian': Decimal('22.2222'),
                'percentile_allegation_internal': Decimal('33.3333'),
                'percentile_trr': Decimal('44.4444')
            }, {
                'id': officer3.id,
                'name': 'E F',
                'count': 3,
                'percentile_allegation': Decimal('66.6666'),
                'percentile_allegation_civilian': Decimal('77.7777'),
                'percentile_allegation_internal': Decimal('88.8888'),
                'percentile_trr': Decimal('99.9999')
            }, {
                'id': officer2.id,
                'name': 'C D',
                'count': 2,
                'percentile_allegation': Decimal('33.3333'),
                'percentile_allegation_civilian': Decimal('44.4444'),
                'percentile_allegation_internal': Decimal('55.5555'),
                'percentile_trr': Decimal('66.6666')
            }
        ])
