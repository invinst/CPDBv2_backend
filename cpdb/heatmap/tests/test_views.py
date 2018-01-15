from django.test import TestCase
from django.core.urlresolvers import reverse

from robber import expect

from data.factories import OfficerAllegationFactory, AllegationCategoryFactory


class CitySummaryViewSetTestCase(TestCase):
    def setUp(self):
        violation_category = AllegationCategoryFactory(category='Operation/Personnel Violations')
        use_of_force_category = AllegationCategoryFactory(category='Use Of Force')
        illegal_search_category = AllegationCategoryFactory(category='Illegal Search')
        false_arrest_category = AllegationCategoryFactory(category='False Arrest')
        OfficerAllegationFactory.create_batch(4, allegation_category=violation_category, final_outcome='001')
        OfficerAllegationFactory.create_batch(3, allegation_category=use_of_force_category, final_outcome='001')
        OfficerAllegationFactory.create_batch(2, allegation_category=illegal_search_category, final_outcome='900')
        OfficerAllegationFactory(allegation_category=false_arrest_category, final_outcome='900')

    def test_get_city_summary(self):
        response = self.client.get(reverse('api-v2:city-summary-list'))
        expect(response.data).to.eq({
            'allegation_count': 10,
            'discipline_count': 7,
            'most_common_complaints': [
                'Operation/Personnel Violations',
                'Use Of Force',
                'Illegal Search'
            ]
        })
