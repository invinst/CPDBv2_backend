from datetime import date

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    ComplainantFactory, AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory
)
from .mixins import OfficerSummaryTestCaseMixin


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO'
        )
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerAllegationFactory(officer=officer, allegation=allegation, allegation_category=allegation_category)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'unit': 'CAND',
            'date_of_appt': '2017-02-27',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'complaint_records': {
                'count': 1,
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Use of Force', 'count': 1}]
                    },
                    {
                        'name': 'race',
                        'entries': [{'name': 'White', 'count': 1}]
                    },
                    {
                        'name': 'age',
                        'entries': [{'name': '18', 'count': 1}]
                    },
                    {
                        'name': 'gender',
                        'entries': [{'name': 'Female', 'count': 1}]
                    }
                ]
            }
        })

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline(self):
        officer = OfficerFactory(id=123)
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 2,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                },
                {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'category',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4
                }
            ]
        })

    def test_timeline_no_data(self):
        response = self.client.get(reverse('api-v2:officers-timeline', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_next_request_url(self):
        officer = OfficerFactory(id=123)
        OfficerHistoryFactory.create_batch(40, officer=officer)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline', kwargs={'pk': 123}), {'offset': 10})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(40)
        expect(response.data['next']).to.match(r'.+\?limit=20\&offset=30$')
        expect(response.data['previous']).to.match(r'.+\?limit=20$')
        expect(len(response.data['results'])).to.eq(20)
