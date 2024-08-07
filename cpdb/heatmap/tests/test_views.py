from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from robber import expect
from mock import patch
import pytz

from data.factories import OfficerAllegationFactory
from data.factories import OfficerAllegationFactory
from lawsuit.factories import LawsuitFactory, PaymentFactory
from lawsuit.cache_managers import lawsuit_cache_manager


class CitySummaryViewSetTestCase(TestCase):
    @freeze_time('2017-04-04 12:00:01', tz_offset=0)
    @patch('heatmap.views.ALLEGATION_MIN_DATETIME', datetime(1988, 1, 1, tzinfo=pytz.utc))
    def test_get_city_summary(self):
        before_min_date = datetime(1987, 12, 31, tzinfo=pytz.utc)
        valid_date = datetime(1988, 12, 31, tzinfo=pytz.utc)
        today = datetime.now(pytz.utc)

        lawsuit_1 = LawsuitFactory()
        PaymentFactory(settlement=5000, legal_fees=2000, lawsuit=lawsuit_1)
        PaymentFactory(settlement=0, legal_fees=5000, lawsuit=lawsuit_1)
        lawsuit_2 = LawsuitFactory()
        PaymentFactory(settlement=8500, legal_fees=0, lawsuit=lawsuit_2)
        LawsuitFactory()

        for date in [before_min_date, valid_date, today]:
            OfficerAllegationFactory.create_batch(
                4,
                allegation__incident_date=date,
                disciplined=True)
            OfficerAllegationFactory.create_batch(
                2,
                allegation__incident_date=date,
                disciplined=False)

        lawsuit_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:city-summary-list'))
        expect(response.data).to.eq({
            'start_year': 1988,
            'end_year': 2017,
            'allegation_count': 12,
            'discipline_count': 8,
            'lawsuits_count': 3,
            'total_lawsuit_settlements': '20500.00',
        })

    def test_get_city_summary_with_total_lawsuit_settlements_is_none(self):
        response = self.client.get(reverse('api-v2:city-summary-list'))
        expect(response.data.get('total_lawsuit_settlements')).to.be.none()
