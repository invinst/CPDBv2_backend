import pytz
from datetime import datetime

from django.contrib.gis.geos import Point
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
from mock import patch

from data.factories import PoliceUnitFactory, OfficerFactory, AllegationFactory, \
    OfficerAllegationFactory, OfficerHistoryFactory, AttachmentFileFactory, AllegationCategoryFactory, VictimFactory
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory


class SocialGraphMobileViewSetTestCase(APITestCase):
    def test_network_with_officer_ids_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            complaint_percentile=1.1,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            complaint_percentile=4.4,
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            complaint_percentile=7.7,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
        )

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)

        expected_data = {
            'officers': [
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile_allegation': '1.1000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '4.4000',
                    'percentile_allegation_internal': '5.5000',
                    'percentile_trr': '6.6000'
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile_allegation': '7.7000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                    'percentile_trr': '9.9000'
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                }
            ],
            'list_event': [
                '2006-12-31', '2007-12-31'
            ]
        }

        url = reverse('api-v2:social-graph-mobile-network', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_network_with_unit_id_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            complaint_percentile=1.1,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
            complaint_percentile=4.4,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
            complaint_percentile=7.7,
        )

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)

        expected_data = {
            'officers': [
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile_allegation': '1.1000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '4.4000',
                    'percentile_allegation_internal': '5.5000',
                    'percentile_trr': '6.6000'
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile_allegation': '7.7000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                    'percentile_trr': '9.9000'
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': '2006-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                }
            ],
            'list_event': [
                '2006-12-31', '2007-12-31'
            ]
        }

        url = reverse('api-v2:social-graph-mobile-network', kwargs={})
        response = self.client.get(url, {
            'unit_id': 123,
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_network_with_pinboard_id_param(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            complaint_percentile=1.1,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            complaint_percentile=4.4,
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            complaint_percentile=7.7,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
        )
        officer_4 = OfficerFactory(
            id=8565,
            first_name='William',
            last_name='People',
            complaint_percentile=10.10,
            civilian_allegation_percentile=10.10,
            internal_allegation_percentile=11.11,
            trr_percentile=12.12,
        )
        officer_5 = OfficerFactory(
            id=8566,
            first_name='John',
            last_name='Sena',
            complaint_percentile=13.13,
            civilian_allegation_percentile=13.13,
            internal_allegation_percentile=14.14,
            trr_percentile=15.15,
        )
        officer_6 = OfficerFactory(
            id=8567,
            first_name='Tom',
            last_name='Cruise',
            complaint_percentile=16.16,
            civilian_allegation_percentile=16.16,
            internal_allegation_percentile=17.17,
            trr_percentile=18.18,
        )
        officer_7 = OfficerFactory(
            id=8568,
            first_name='Robert',
            last_name='Long',
            complaint_percentile=19.19,
            civilian_allegation_percentile=19.19,
            internal_allegation_percentile=20.20,
            trr_percentile=21.21,
        )
        officer_8 = OfficerFactory(
            id=8569,
            first_name='Jaeho',
            last_name='Jung',
            complaint_percentile=22.22,
            civilian_allegation_percentile=22.22,
            internal_allegation_percentile=23.23,
            trr_percentile=24.24,
        )

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=True,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )
        allegation_4 = AllegationFactory(
            crid='987',
            is_officer_complaint=False,
            incident_date=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )
        allegation_5 = AllegationFactory(
            crid='555',
            is_officer_complaint=False,
            incident_date=datetime(2009, 12, 31, tzinfo=pytz.utc)
        )
        allegation_6 = AllegationFactory(
            crid='666',
            is_officer_complaint=False,
            incident_date=datetime(2010, 12, 31, tzinfo=pytz.utc)
        )
        allegation_7 = AllegationFactory(
            crid='777',
            is_officer_complaint=False,
            incident_date=datetime(2011, 12, 31, tzinfo=pytz.utc)
        )
        allegation_8 = AllegationFactory(
            crid='888',
            is_officer_complaint=False,
            incident_date=datetime(2012, 12, 31, tzinfo=pytz.utc)
        )
        allegation_9 = AllegationFactory(
            crid='999',
            is_officer_complaint=False,
            incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc)
        )
        allegation_10 = AllegationFactory(
            crid='1000',
            is_officer_complaint=False,
            incident_date=datetime(2014, 12, 31, tzinfo=pytz.utc)
        )
        trr_1 = TRRFactory(
            id=1,
            officer=officer_4,
            trr_datetime=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=7, officer=officer_3, allegation=allegation_3)

        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_4)
        OfficerAllegationFactory(id=9, officer=officer_7, allegation=allegation_4)
        OfficerAllegationFactory(id=10, officer=officer_2, allegation=allegation_5)
        OfficerAllegationFactory(id=11, officer=officer_7, allegation=allegation_5)

        OfficerAllegationFactory(id=12, officer=officer_3, allegation=allegation_6)
        OfficerAllegationFactory(id=13, officer=officer_5, allegation=allegation_6)
        OfficerAllegationFactory(id=14, officer=officer_3, allegation=allegation_7)
        OfficerAllegationFactory(id=15, officer=officer_5, allegation=allegation_7)
        OfficerAllegationFactory(id=16, officer=officer_3, allegation=allegation_8)
        OfficerAllegationFactory(id=17, officer=officer_6, allegation=allegation_8)
        OfficerAllegationFactory(id=18, officer=officer_3, allegation=allegation_9)
        OfficerAllegationFactory(id=19, officer=officer_6, allegation=allegation_9)

        OfficerAllegationFactory(id=20, officer=officer_3, allegation=allegation_10)
        OfficerAllegationFactory(id=21, officer=officer_8, allegation=allegation_10)

        pinboard = PinboardFactory(
            title='My Pinboard',
            description='abc',
        )

        pinboard.officers.set([officer_1, officer_2])
        pinboard.allegations.set([allegation_3])
        pinboard.trrs.set([trr_1])

        expected_data = {
            'officers': [
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '4.4000',
                    'percentile_allegation_internal': '5.5000',
                    'percentile_trr': '6.6000'
                },
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile_allegation': '1.1000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile_allegation': '7.7000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                    'percentile_trr': '9.9000'
                },
                {
                    'full_name': 'William People',
                    'id': 8565,
                    'percentile_allegation': '10.1000',
                    'percentile_allegation_civilian': '10.1000',
                    'percentile_allegation_internal': '11.1100',
                    'percentile_trr': '12.1200'
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2007-12-31',
                    'accussed_count': 2
                },
            ],
            'list_event': ['2007-12-31']
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-network'), {'pinboard_id': pinboard.id})

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_network_with_specific_threshold_and_complaint_origin(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            complaint_percentile=1.1,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            complaint_percentile=4.4,
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            complaint_percentile=7.7,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
        )
        officer_4 = OfficerFactory(
            id=8565,
            first_name='John',
            last_name='Snow',
            complaint_percentile=10.10,
            civilian_allegation_percentile=10.10,
            internal_allegation_percentile=11.11,
            trr_percentile=12.12,
        )
        officer_5 = OfficerFactory(
            id=8566,
            first_name='John',
            last_name='Sena',
            complaint_percentile=13.13,
            civilian_allegation_percentile=13.13,
            internal_allegation_percentile=14.14,
            trr_percentile=15.15,
        )

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=True,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )
        allegation_4 = AllegationFactory(
            crid='987',
            is_officer_complaint=True,
            incident_date=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)

        OfficerAllegationFactory(id=3, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_3)

        OfficerAllegationFactory(id=7, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=8, officer=officer_4, allegation=allegation_1)
        OfficerAllegationFactory(id=9, officer=officer_4, allegation=allegation_2)
        OfficerAllegationFactory(id=10, officer=officer_4, allegation=allegation_3)

        OfficerAllegationFactory(id=11, officer=officer_5, allegation=allegation_1)
        OfficerAllegationFactory(id=12, officer=officer_5, allegation=allegation_2)
        OfficerAllegationFactory(id=13, officer=officer_5, allegation=allegation_3)
        OfficerAllegationFactory(id=14, officer=officer_4, allegation=allegation_4)
        OfficerAllegationFactory(id=15, officer=officer_5, allegation=allegation_4)

        expected_data = {
            'officers': [
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile_allegation': '1.1000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '4.4000',
                    'percentile_allegation_internal': '5.5000',
                    'percentile_trr': '6.6000'
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile_allegation': '7.7000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                    'percentile_trr': '9.9000'
                },
                {
                    'full_name': 'John Snow',
                    'id': 8565,
                    'percentile_allegation': '10.1000',
                    'percentile_allegation_civilian': '10.1000',
                    'percentile_allegation_internal': '11.1100',
                    'percentile_trr': '12.1200'
                },
                {
                    'full_name': 'John Sena',
                    'id': 8566,
                    'percentile_allegation': '13.1300',
                    'percentile_allegation_civilian': '13.1300',
                    'percentile_allegation_internal': '14.1400',
                    'percentile_trr': '15.1500'
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8565,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8566,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8565,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8566,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8565,
                    'officer_id_2': 8566,
                    'incident_date': '2007-12-31',
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8565,
                    'officer_id_2': 8566,
                    'incident_date': '2008-12-31',
                    'accussed_count': 4
                },
            ],
            'list_event': ['2007-12-31', '2008-12-31']
        }

        url = reverse('api-v2:social-graph-mobile-network', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562,8563,8564,8565,8566',
            'threshold': 3,
            'complaint_origin': 'ALL'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_officers_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            rank='Police Officer',
            current_badge='123',
            race='White',
            birth_year='1972',
            gender='M',
            allegation_count=1,
            sustained_count=1,
            honorable_mention_count=1,
            major_award_count=1,
            trr_count=1,
            discipline_count=1,
            civilian_compliment_count=1,
            appointed_date='1976-06-10',
            civilian_allegation_percentile='88.8800',
            internal_allegation_percentile='77.7700',
            trr_percentile='66.6600',
            complaint_percentile='88.8800',
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            rank='Police Officer',
            current_badge='456',
            race='White',
            birth_year='1972',
            gender='M',
            allegation_count=2,
            sustained_count=2,
            honorable_mention_count=2,
            major_award_count=2,
            trr_count=2,
            discipline_count=2,
            civilian_compliment_count=2,
            appointed_date='1976-06-10',
            civilian_allegation_percentile='55.6600',
            internal_allegation_percentile='66.7700',
            trr_percentile='77.8800',
            complaint_percentile='55.6600',
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            rank='Police Officer',
            current_badge='789',
            race='White',
            birth_year='1972',
            gender='M',
            allegation_count=3,
            sustained_count=3,
            honorable_mention_count=3,
            major_award_count=3,
            trr_count=3,
            discipline_count=3,
            civilian_compliment_count=3,
            appointed_date='1976-06-10',
            civilian_allegation_percentile='44.4400',
            internal_allegation_percentile='33.3300',
            trr_percentile='22.2200',
            complaint_percentile='44.4400',
        )

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(officer=officer_1, unit=unit)
        OfficerHistoryFactory(officer=officer_2, unit=unit)
        OfficerHistoryFactory(officer=officer_3, unit=unit)

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)

        expected_data = [
            {
                'full_name': 'Edward May',
                'id': 8563,
                'rank': 'Police Officer',
                'badge': '456',
                'race': 'White',
                'birth_year': '1972',
                'gender': 'M',
                'allegation_count': 2,
                'sustained_count': 2,
                'honorable_mention_count': 2,
                'major_award_count': 2,
                'trr_count': 2,
                'discipline_count': 2,
                'civilian_compliment_count': 2,
                'appointed_date': '1976-06-10',
                'percentile_allegation_civilian': '55.6600',
                'percentile_allegation_internal': '66.7700',
                'percentile_trr': '77.8800',
                'percentile_allegation': '55.6600',
            },
            {
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'rank': 'Police Officer',
                'badge': '123',
                'race': 'White',
                'birth_year': '1972',
                'gender': 'M',
                'allegation_count': 1,
                'sustained_count': 1,
                'honorable_mention_count': 1,
                'major_award_count': 1,
                'trr_count': 1,
                'discipline_count': 1,
                'civilian_compliment_count': 1,
                'appointed_date': '1976-06-10',
                'percentile_allegation_civilian': '88.8800',
                'percentile_allegation_internal': '77.7700',
                'percentile_trr': '66.6600',
                'percentile_allegation': '88.8800',
            },
            {
                'full_name': 'Joe Parker',
                'id': 8564,
                'rank': 'Police Officer',
                'badge': '789',
                'race': 'White',
                'birth_year': '1972',
                'gender': 'M',
                'allegation_count': 3,
                'sustained_count': 3,
                'honorable_mention_count': 3,
                'major_award_count': 3,
                'trr_count': 3,
                'discipline_count': 3,
                'civilian_compliment_count': 3,
                'appointed_date': '1976-06-10',
                'percentile_allegation_civilian': '44.4400',
                'percentile_allegation_internal': '33.3300',
                'percentile_trr': '22.2200',
                'percentile_allegation': '44.4400',
            },
        ]

        url = reverse('api-v2:social-graph-mobile-officers', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_allegations_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=5,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            allegation_count=10,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            allegation_count=20,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95
        )
        officer_4 = OfficerFactory(id=8565, first_name='Jon', last_name='Snow')

        category_1 = AllegationCategoryFactory(
            category='Use of Force',
            allegation_name='Miscellaneous'
        )
        category_2 = AllegationCategoryFactory(
            category='Illegal Search',
            allegation_name='Illegal Arrest / False Arrest'
        )
        category_3 = AllegationCategoryFactory(
            category='Operation/Personnel Violations',
            allegation_name='Improper Search Of Person'
        )

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_1,
            old_complaint_address='3XX W. 58TH ST.',
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_2,
            old_complaint_address='34XX Douglas Blvd'
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_3,
            old_complaint_address='3510 Michigan Ave, Chicago'
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation_2
        )
        VictimFactory(
            gender='F',
            race='White',
            age=40,
            allegation=allegation_3
        )
        allegation_4 = AllegationFactory(
            crid='987',
            is_officer_complaint=False,
            incident_date=datetime(2008, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_3
        )

        OfficerAllegationFactory(
            id=1,
            officer=officer_1,
            allegation=allegation_1,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=2,
            officer=officer_2,
            allegation=allegation_1,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=3,
            officer=officer_3,
            allegation=allegation_1,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=4,
            officer=officer_1,
            allegation=allegation_2,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=5,
            officer=officer_2,
            allegation=allegation_2,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=6,
            officer=officer_3,
            allegation=allegation_2,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=7,
            officer=officer_1,
            allegation=allegation_3,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )
        OfficerAllegationFactory(
            id=8,
            officer=officer_2,
            allegation=allegation_3,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category_3
        )

        OfficerAllegationFactory(id=9, officer=officer_2, allegation=allegation_4)
        OfficerAllegationFactory(id=10, officer=officer_4, allegation=allegation_4)

        AttachmentFileFactory(
            id=1,
            tag='Other',
            allegation=allegation_2,
            title='Attachment Title',
            file_type='document',
            url='http://lvh.me/document',
        )
        AttachmentFileFactory(id=2, tag='OCIR', allegation=allegation_2)
        AttachmentFileFactory(id=3, tag='AR', allegation=allegation_2)
        AttachmentFileFactory(id=4, tag='CR', allegation=allegation_2, show=False)
        AttachmentFileFactory(id=5, tag='CR', allegation=allegation_2, title='arrest report')

        url = reverse('api-v2:social-graph-mobile-allegations', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expected_data = [
            {
                'kind': 'CR',
                'crid': '123',
                'to': '/complaint/123/',
                'incident_date': '2005-12-31',
                'category': 'Use of Force',
                'subcategory': 'Miscellaneous',
                'attachments': [],
                'officer_ids': [8562, 8563, 8564],
                'address': '3XX W. 58TH ST.',
                'victims': [],
                'coaccused': [
                    {
                        'id': 8562,
                        'full_name': 'Jerome Finnigan',
                        'allegation_count': 5,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                    {
                        'id': 8563,
                        'full_name': 'Edward May',
                        'allegation_count': 10,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                    {
                        'id': 8564,
                        'full_name': 'Joe Parker',
                        'allegation_count': 20,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    }
                ],
            },
            {
                'kind': 'CR',
                'crid': '456',
                'to': '/complaint/456/',
                'category': 'Illegal Search',
                'subcategory': 'Illegal Arrest / False Arrest',
                'incident_date': '2006-12-31',
                'address': '34XX Douglas Blvd',
                'victims': [
                    {
                        'gender': 'Male',
                        'race': 'Black',
                        'age': 35
                    }
                ],
                'coaccused': [
                    {
                        'id': 8562,
                        'full_name': 'Jerome Finnigan',
                        'allegation_count': 5,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                    {
                        'id': 8563,
                        'full_name': 'Edward May',
                        'allegation_count': 10,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                    {
                        'id': 8564,
                        'full_name': 'Joe Parker',
                        'allegation_count': 20,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    }
                ],
                'attachments': [
                    {
                        'id': '1',
                        'title': 'Attachment Title',
                        'file_type': 'document',
                        'url': 'http://lvh.me/document',
                    }
                ],
                'officer_ids': [8562, 8563, 8564],

            },
            {
                'kind': 'CR',
                'crid': '789',
                'to': '/complaint/789/',

                'category': 'Operation/Personnel Violations',
                'subcategory': 'Improper Search Of Person',
                'incident_date': '2007-12-31',
                'address': '3510 Michigan Ave, Chicago',
                'victims': [
                    {
                        'gender': 'Female',
                        'race': 'White',
                        'age': 40
                    }
                ],
                'coaccused': [
                    {
                        'id': 8562,
                        'full_name': 'Jerome Finnigan',
                        'allegation_count': 5,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                    {
                        'id': 8563,
                        'full_name': 'Edward May',
                        'allegation_count': 10,
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
                ],
                'attachments': [],
                'officer_ids': [8562, 8563],
            }
        ]

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_geographic_crs_with_officer_ids_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        OfficerFactory(id=4)

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Miscellaneous')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Improper Search Of Person')
        allegation_1 = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_1,
            coaccused_count=15,
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=20,
            point=Point(37.3, 86.2),
        )
        allegation_3 = AllegationFactory(
            crid=789,
            incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=18,
            point=Point(37.3, 80.2),
        )
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_3)

        expected_data = {
            'count': 3,
            'limit': 500,
            'results': [
                {
                    'date': '2002-01-01',
                    'crid': '123',
                    'category': 'Use of Force',
                    'kind': 'CR',
                    'point': {
                        'lon': -35.5,
                        'lat': 68.9
                    },
                },
                {
                    'date': '2003-01-01',
                    'crid': '456',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 86.2
                    },
                },
                {
                    'date': '2004-01-01',
                    'crid': '789',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 80.2
                    },
                },
            ]
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-crs'), {'officer_ids': '1,2,3,4'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq(expected_data)

    def test_geographic_trrs_with_officer_ids_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        OfficerFactory(id=3)

        TRRFactory(
            id=1,
            officer=officer_1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )
        TRRFactory(
            id=2,
            officer=officer_2,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )

        expected_data = {
            'count': 2,
            'limit': 500,
            'results': [
                {
                    'trr_id': 1,
                    'date': '2004-01-01',
                    'kind': 'FORCE',
                    'taser': True,
                    'firearm_used': False,
                    'point': {
                        'lon': -32.5,
                        'lat': 61.3
                    }
                },
                {
                    'trr_id': 2,
                    'date': '2005-01-01',
                    'kind': 'FORCE',
                    'taser': False,
                    'firearm_used': True,
                    'point': {
                        'lon': 33.3,
                        'lat': 78.4
                    }
                },
            ]
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-trrs'), {'officer_ids': '1,2,3'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    @patch('social_graph.views.DEFAULT_LIMIT', 2)
    def test_geographic_crs_with_unit_id_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)
        OfficerHistoryFactory(unit=unit, officer=officer_4)

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Miscellaneous')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Improper Search Of Person')
        allegation_1 = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_1,
            coaccused_count=15,
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=20,
            point=Point(37.3, 86.2),
        )
        allegation_3 = AllegationFactory(
            crid=789,
            incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=18,
            point=Point(37.3, 80.2),
        )
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_3)

        expected_data = {
            'count': 3,
            'limit': 2,
            'results': [
                {
                    'date': '2002-01-01',
                    'crid': '123',
                    'category': 'Use of Force',
                    'kind': 'CR',
                    'point': {
                        'lon': -35.5,
                        'lat': 68.9
                    },
                },
                {
                    'date': '2003-01-01',
                    'crid': '456',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 86.2
                    },
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-crs'), {'unit_id': 123})
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq(expected_data)

    @patch('social_graph.views.DEFAULT_LIMIT', 2)
    def test_geographic_crs_with_unit_id_param_and_pagination(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)
        OfficerHistoryFactory(unit=unit, officer=officer_4)

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Miscellaneous')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Improper Search Of Person')
        allegation_1 = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_1,
            coaccused_count=15,
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=20,
            point=Point(37.3, 86.2),
        )
        allegation_3 = AllegationFactory(
            crid=789,
            incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=18,
            point=Point(37.3, 80.2),
        )
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_3)

        expected_data = {
            'count': 3,
            'limit': 2,
            'results': [
                {
                    'date': '2004-01-01',
                    'crid': '789',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 80.2
                    },
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-crs'), {'unit_id': 123, 'offset': 2})
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq(expected_data)

    @patch('social_graph.views.DEFAULT_LIMIT', 2)
    def test_geographic_trrs_with_unit_id_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)
        OfficerHistoryFactory(unit=unit, officer=officer_4)

        TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )
        TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )
        TRRFactory(
            id=3,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )

        expected_data = {
            'count': 3,
            'limit': 2,
            'results': [
                {
                    'trr_id': 1,
                    'date': '2004-01-01',
                    'kind': 'FORCE',
                    'taser': True,
                    'firearm_used': False,
                    'point': {
                        'lon': -32.5,
                        'lat': 61.3
                    }
                },
                {
                    'trr_id': 2,
                    'date': '2005-01-01',
                    'kind': 'FORCE',
                    'taser': False,
                    'firearm_used': True,
                    'point': {
                        'lon': 33.3,
                        'lat': 78.4
                    }
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-trrs'), {'unit_id': 123})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    @patch('social_graph.views.DEFAULT_LIMIT', 2)
    def test_geographic_trrs_with_unit_id_param_and_pagination(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)
        OfficerHistoryFactory(unit=unit, officer=officer_4)

        TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )
        TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )
        TRRFactory(
            id=3,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )

        expected_data = {
            'count': 3,
            'limit': 2,
            'results': [
                {
                    'trr_id': 3,
                    'date': '2005-01-01',
                    'kind': 'FORCE',
                    'taser': False,
                    'firearm_used': True,
                    'point': {
                        'lon': 33.3,
                        'lat': 78.4
                    }
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-trrs'), {'unit_id': 123, 'offset': 2})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_geographic_crs_with_pinboard_id_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Miscellaneous')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Improper Search Of Person')
        allegation_1 = AllegationFactory(
            crid=123,
            most_common_category=category_1,
            coaccused_count=15,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            most_common_category=category_2,
            coaccused_count=20,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 86.2),
        )
        allegation_3 = AllegationFactory(
            crid=789,
            most_common_category=category_2,
            coaccused_count=18,
            incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 80.2),
        )
        allegation_4 = AllegationFactory(
            crid=987,
            incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc),
        )
        AllegationFactory(
            crid=654,
            incident_date=datetime(2006, 1, 1, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_3)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_4)

        pinboard = PinboardFactory()

        pinboard.officers.set([officer_1, officer_2])
        pinboard.allegations.set([allegation_3])

        expected_data = {
            'count': 3,
            'limit': 500,
            'results': [
                {
                    'date': '2002-01-01',
                    'crid': '123',
                    'category': 'Use of Force',
                    'kind': 'CR',
                    'point': {
                        'lon': -35.5,
                        'lat': 68.9
                    },
                },
                {
                    'date': '2003-01-01',
                    'crid': '456',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 86.2
                    },
                },
                {
                    'date': '2004-01-01',
                    'crid': '789',
                    'category': 'Illegal Search',
                    'kind': 'CR',
                    'point': {
                        'lon': 37.3,
                        'lat': 80.2
                    },
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-crs'), {'pinboard_id': pinboard.id})
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq(expected_data)

    def test_geographic_trrs_with_pinboard_id_param(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officer_5 = OfficerFactory(id=5)

        trr_1 = TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )
        trr_2 = TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )
        TRRFactory(
            id=3,
            officer=officer_1,
            trr_datetime=datetime(2006, 1, 1, tzinfo=pytz.utc),
            point=Point(34.3, 79.4),
            taser=False,
            firearm_used=True,
        )
        TRRFactory(
            id=4,
            officer=officer_3,
            trr_datetime=datetime(2007, 1, 1, tzinfo=pytz.utc),
        )
        TRRFactory(
            id=5,
            officer=officer_5,
            trr_datetime=datetime(2008, 1, 1, tzinfo=pytz.utc),
        )

        pinboard = PinboardFactory()

        pinboard.officers.set([officer_1, officer_2])
        pinboard.trrs.set([trr_1, trr_2])

        expected_data = {
            'count': 3,
            'limit': 500,
            'results': [
                {
                    'trr_id': 1,
                    'date': '2004-01-01',
                    'kind': 'FORCE',
                    'taser': True,
                    'firearm_used': False,
                    'point': {
                        'lon': -32.5,
                        'lat': 61.3
                    }
                },
                {
                    'trr_id': 2,
                    'date': '2005-01-01',
                    'kind': 'FORCE',
                    'taser': False,
                    'firearm_used': True,
                    'point': {
                        'lon': 33.3,
                        'lat': 78.4
                    }
                },
                {
                    'trr_id': 3,
                    'date': '2006-01-01',
                    'kind': 'FORCE',
                    'taser': False,
                    'firearm_used': True,
                    'point': {
                        'lon': 34.3,
                        'lat': 79.4
                    }
                },
            ],
        }

        response = self.client.get(reverse('api-v2:social-graph-mobile-geographic-trrs'), {'pinboard_id': pinboard.id})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)
