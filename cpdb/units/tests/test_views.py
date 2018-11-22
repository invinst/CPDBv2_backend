from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import (
    OfficerFactory, OfficerHistoryFactory, PoliceUnitFactory, AllegationFactory,
    AllegationCategoryFactory, OfficerAllegationFactory, ComplainantFactory
)
from .mixins import UnitSummaryTestCaseMixin


class UnitsViewSetTestCase(UnitSummaryTestCaseMixin, APITestCase):
    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:units-summary', kwargs={'pk': '123'}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_summary(self):
        unit = PoliceUnitFactory(unit_name='123', description='foo')
        officer = OfficerFactory(race='White', gender='F', birth_year='1980')
        OfficerHistoryFactory(unit=unit, officer=officer, end_date=None)
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category,
            final_finding='SU'
        )
        ComplainantFactory(allegation=allegation, race='Black', age=25, gender='M')

        self.refresh_index()

        response = self.client.get(reverse('api-v2:units-summary', kwargs={'pk': '123'}))
        expect(response.data).to.be.eq({
            'unit_name': '123',
            'description': 'foo',
            'member_records': {
                'active_members': 1,
                'total': 1,
                'facets': [
                    {
                        'name': 'race',
                        'entries': [{'name': 'White', 'count': 1}]
                    },
                    {
                        'name': 'age',
                        'entries': [{'name': '31-40', 'count': 1}]
                    },
                    {
                        'name': 'gender',
                        'entries': [{'name': 'Female', 'count': 1}]
                    }
                ]
            },
            'complaint_records': {
                'count': 1,
                'sustained_count': 1,
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Use of Force', 'count': 1, 'sustained_count': 1}]
                    },
                    {
                        'name': 'race',
                        'entries': [{'name': 'Black', 'count': 1, 'sustained_count': 1}]
                    },
                    {
                        'name': 'age',
                        'entries': [{'name': '21-30', 'count': 1, 'sustained_count': 1}]
                    },
                    {
                        'name': 'gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 1}]
                    }
                ]
            }
        })
