from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from robber import expect
from mock import patch
import pytz

from data.factories import OfficerAllegationFactory, AllegationCategoryFactory
from data.constants import HEATMAP_END_YEAR


class CitySummaryViewSetTestCase(TestCase):

    def setUp(self):
        violation_category = AllegationCategoryFactory(category='Operation/Personnel Violations')
        use_of_force_category = AllegationCategoryFactory(category='Use Of Force')
        illegal_search_category = AllegationCategoryFactory(category='Illegal Search')
        false_arrest_category = AllegationCategoryFactory(category='False Arrest')

        before_min_date = datetime(1987, 12, 31, tzinfo=pytz.utc)
        valid_date = datetime(1988, 12, 31, tzinfo=pytz.utc)
        today = datetime.now(pytz.utc)

        for date in [before_min_date, valid_date, today]:
            OfficerAllegationFactory.create_batch(
                4,
                allegation_category=violation_category,
                allegation__incident_date=date,
                disciplined=True)
            OfficerAllegationFactory.create_batch(
                3,
                allegation_category=use_of_force_category,
                allegation__incident_date=date,
                disciplined=True)
            OfficerAllegationFactory.create_batch(
                2,
                allegation_category=illegal_search_category,
                allegation__incident_date=date,
                disciplined=False)
            OfficerAllegationFactory(
                allegation_category=false_arrest_category,
                allegation__incident_date=date,
                final_outcome='900')

    @patch('heatmap.views.ALLEGATION_MIN_DATETIME', datetime(1988, 1, 1, tzinfo=pytz.utc))
    def test_get_city_summary(self):
        response = self.client.get(reverse('api-v2:city-summary-list'))
        expect(response.data).to.eq({
            'start_year': 1988,
            'end_year': HEATMAP_END_YEAR,
            'allegation_count': 20,
            'discipline_count': 14,
            'most_common_complaints': [
                {
                    'name': 'Operation/Personnel Violations',
                    'count': 8
                },
                {
                    'name': 'Use Of Force',
                    'count': 6
                },
                {
                    'name': 'Illegal Search',
                    'count': 4
                }
            ]
        })
