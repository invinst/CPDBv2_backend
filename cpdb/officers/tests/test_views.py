import pytz
from datetime import date, datetime

from django.core.urlresolvers import reverse

from mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    ComplainantFactory, AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory
)
from .mixins import OfficerSummaryTestCaseMixin
from data.constants import ACTIVE_YES_CHOICE


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE
        )
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category, final_finding='SU',
            start_date=date(2000, 1, 1)
        )
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'unit': 'CAND',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'complaint_records': {
                'count': 1,
                'sustained_count': 1,
                'items': [{'count': 1, 'sustained_count': 1, 'year': 2000}],
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Use of Force', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Use of Force', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Female', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Female', 'count': 1, 'sustained_count': 1}
                        ]}]
                    }
                ]
            }
        })

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_items(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
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
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                },
                {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                }
            ]
        })

    def test_timeline_items_filter_params(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='Illegal Search', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(crid='654321')
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2017, 8, 23), allegation=allegation2,
            allegation_category=AllegationCategoryFactory(category='Use of Force', allegation_name='sub category')
        )
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}),
                                   data={'category': 'Illegal Search', 'finding': 'Unfounded', 'invalid': 'X'})
        # NOTE: 'finding' and 'invalid' should drop since this is not in ALLOWED LIST

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                }, {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'Illegal Search',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                }, {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                }
            ]
        })
        pass

    def test_timeline_no_data(self):
        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_next_request_url(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        OfficerHistoryFactory.create_batch(40, officer=officer, effective_date=date(2017, 1, 1))
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}), {'offset': 10})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(41)
        expect(response.data['next']).to.match(r'.+\?limit=20\&offset=30$')
        expect(response.data['previous']).to.match(r'.+\?limit=20$')
        expect(len(response.data['results'])).to.eq(20)

    def test_timeline_minimap_no_data(self):
        response = self.client.get(reverse('api-v2:officers-timeline-minimap', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_minimap(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='111222')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit__unit_name='69')
        OfficerAllegationFactory(officer=officer, start_date=date(2016, 8, 23), allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-minimap', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        # TODO: remap to the existing one
        expect(response.data).to.eq([
            {
                'kind': 'Unit',
                'year': 2017,
            }, {
                'kind': 'CR',
                'year': 2016,
            }, {
                'kind': 'Joined',
                'year': 2000,
            }
        ])

    def test_timeline_items_sort_asc(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}), {'sort': 'asc'})

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                },
                {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'category',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                },
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                }
            ]
        })

    def test_social_graph_success(self):
        officer1 = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater')
        officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
        allegation = AllegationFactory(incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-social-graph', kwargs={'pk': 1}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'links': [
                {
                    'source': 1,
                    'target': 2,
                    'cr_years': [2001]
                }
            ],
            'nodes': [
                {
                    'id': 1,
                    'name': 'Clarence Featherwater',
                    'cr_years': [2001]
                },
                {
                    'id': 2,
                    'name': 'Raymond Piwnicki',
                    'cr_years': [2001]
                }
            ]
        })

    def test_social_graph_not_found(self):
        officer1 = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater')
        officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
        allegation = AllegationFactory(incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-social-graph', kwargs={'pk': 3}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_top_officers_by_allegation(self):
        OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater',
                       complaint_percentile=100.0, gender='M', birth_year=1970)
        OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki', complaint_percentile=50.0)
        OfficerFactory(id=3, first_name='Ronald', last_name='Watts',
                       complaint_percentile=99.2, gender='M', birth_year=1960)
        response = self.client.get(reverse('api-v2:officers-top-by-allegation'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq([{
            'id': 1,
            'visual_token_background_color': '#f5f4f4',
            'full_name': 'Clarence Featherwater',
            'complaint_count': 0,
            'sustained_count': 0,
            'birth_year': 1970,
            'complaint_percentile': 100.0,
            'race': 'White',
            'gender': 'Male'
        }, {
            'id': 3,
            'visual_token_background_color': '#f5f4f4',
            'full_name': 'Ronald Watts',
            'complaint_count': 0,
            'sustained_count': 0,
            'birth_year': 1960,
            'complaint_percentile': 99.2,
            'race': 'White',
            'gender': 'Male'
        }])

    def test_top_officers_by_allegation_random(self):
        with patch('data.models.Officer.objects') as mock_func:
            self.client.get(reverse('api-v2:officers-top-by-allegation'), {'random': 1})
            expect(mock_func.filter.return_value.order_by).to.be.called_with('?')

    def test_officer_percentile(self):
        self.refresh_index()
        response = self.client.get(reverse('api-v2:officers-percentile', kwargs={'pk': 1}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'officer_id': 1,
            'year': 2006,
            'percentile_alL_trr': '0.000',
            'percentile_civilian': '67.000',
            'percentile_internal': '0.020',
            'percentile_shooting': '0.000',
            'percentile_taser': '0.100',
            'percentile_others': '0.000'
        }, {
            'officer_id': 1,
            'year': 2007,
            'percentile_alL_trr': '0.000',
            'percentile_civilian': '77.000',
            'percentile_internal': '0.020',
            'percentile_shooting': '45.000',
            'percentile_taser': '0.100',
            'percentile_others': '0.000'
        }])
