
from datetime import date, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.test.testcases import TestCase

from robber import expect
from mock import patch, Mock

from data.models import Officer
from data.factories import OfficerFactory
from shared.tests.utils import create_object


class CalculateOfficerPercentileTestCase(TestCase):

    @patch(
        'data.management.commands.calculate_officer_percentile.officer_percentile.latest_year_percentile',
        Mock(return_value=[
            create_object({
                'officer_id': 2,
                'year': 2014,
                'percentile_allegation': 66.6667,
                'percentile_trr': 0.0,
                'percentile_honorable_mention': 66.6667
            }),
            create_object({
                'officer_id': 1,
                'year': 2017,
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 66.6667,
                'percentile_trr': 33.3333,
                'percentile_honorable_mention': 33.3333,
            }),
            create_object({
                'officer_id': 3,
                'year': 2017,
                'percentile_allegation': 0.0,
                'percentile_allegation_civilian': 0.0000,
                'percentile_allegation_internal': 0.0000,
                'percentile_honorable_mention': 0.0
            }),
            create_object({
                'officer_id': 4,
                'year': 2017,
                'percentile_allegation': 0.0,
                'percentile_allegation_civilian': 0.0000,
                'percentile_allegation_internal': 0.0000,
                'percentile_trr': 66.6667,
            })
        ])
    )
    def test_handle(self):
        OfficerFactory(id=1, appointed_date=date.today() - timedelta(days=60), resignation_date=None)
        OfficerFactory(id=2, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerFactory(id=3, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerFactory(id=4, appointed_date=date(1980, 1, 1), resignation_date=None)

        call_command('calculate_officer_percentile')

        officer1 = Officer.objects.get(id=1)
        officer2 = Officer.objects.get(id=2)
        officer3 = Officer.objects.get(id=3)
        officer4 = Officer.objects.get(id=4)

        expect(officer1.complaint_percentile).to.be.none()
        expect(officer1.civilian_allegation_percentile).to.eq(Decimal('66.6667'))
        expect(officer1.internal_allegation_percentile).to.eq(Decimal('66.6667'))
        expect(officer1.trr_percentile).to.eq(Decimal('33.3333'))
        expect(officer1.honorable_mention_percentile).to.eq(Decimal('33.3333'))

        expect(officer2.complaint_percentile).to.eq(Decimal('66.6667'))
        expect(officer2.civilian_allegation_percentile).to.be.none()
        expect(officer2.internal_allegation_percentile).to.be.none()
        expect(officer2.trr_percentile).to.eq(Decimal('0.0'))
        expect(officer2.honorable_mention_percentile).to.eq(Decimal('66.6667'))

        expect(officer3.complaint_percentile).to.eq(Decimal('0.0000'))
        expect(officer3.civilian_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer3.internal_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer3.trr_percentile).to.be.none()
        expect(officer3.honorable_mention_percentile).to.eq(Decimal('0.0000'))

        expect(officer4.complaint_percentile).to.eq(Decimal('0.0000'))
        expect(officer4.civilian_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer4.internal_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer4.trr_percentile).to.eq(Decimal('66.6667'))
        expect(officer4.honorable_mention_percentile).to.be.none()
