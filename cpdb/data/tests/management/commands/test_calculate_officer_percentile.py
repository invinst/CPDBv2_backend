from django.core.management import call_command
from django.test.testcases import TestCase
from robber import expect
from datetime import date, timedelta

from data.models import Officer
from data.factories import OfficerFactory, OfficerAllegationFactory


class CalculateOfficerPercentileTestCase(TestCase):
    def test_handle(self):
        officer1 = OfficerFactory(id=1, appointed_date=date.today() - timedelta(days=60), resignation_date=None)
        OfficerAllegationFactory.create_batch(1, officer=officer1)
        officer2 = OfficerFactory(id=2, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerAllegationFactory.create_batch(1, officer=officer2)
        officer3 = OfficerFactory(id=3, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerAllegationFactory.create_batch(2, officer=officer3)

        call_command('calculate_officer_percentile')
        expect(Officer.objects.get(id=1).complaint_percentile).to.be.none()
        expect(Officer.objects.get(id=2).complaint_percentile).to.eq(0.0)
        expect(Officer.objects.get(id=3).complaint_percentile).to.eq(50.0)
