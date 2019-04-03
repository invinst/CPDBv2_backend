import pytz
from datetime import datetime

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import PoliceUnitFactory, OfficerFactory, AllegationFactory, \
    OfficerAllegationFactory, OfficerHistoryFactory


class SocialGraphViewSetTestCase(APITestCase):
    def test_list_default(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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

        expected_data = {
            'officers': [
                {'full_name': 'Jerome Finnigan', 'id': 8562},
                {'full_name': 'Edward May', 'id': 8563},
                {'full_name': 'Joe Parker', 'id': 8564},
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2006, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2006, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2006, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                }
            ],
            'list_event': [
                '2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00'
            ]
        }

        url = reverse('api-v2:social-graph-list', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_list_with_specific_threshold_and_show_civil_only(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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
            is_officer_complaint=True,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=7, officer=officer_3, allegation=allegation_3)

        expected_data = {
            'officers': [
                {'full_name': 'Jerome Finnigan', 'id': 8562},
                {'full_name': 'Edward May', 'id': 8563},
                {'full_name': 'Joe Parker', 'id': 8564},
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2005, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
            ],
            'list_event': ['2005-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']
        }

        url = reverse('api-v2:social-graph-list', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
            'threshold': 1,
            'show_civil_only': True
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_list_with_unit_id_param(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='John', last_name='Snow')
        officer_5 = OfficerFactory(id=8566, first_name='John', last_name='Sena')

        unit = PoliceUnitFactory(id=123)

        OfficerHistoryFactory(unit=unit, officer=officer_1)
        OfficerHistoryFactory(unit=unit, officer=officer_2)
        OfficerHistoryFactory(unit=unit, officer=officer_3)
        OfficerHistoryFactory(unit=unit, officer=officer_4)
        OfficerHistoryFactory(unit=unit, officer=officer_5)

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
        allegation_4 = AllegationFactory(
            crid='987',
            is_officer_complaint=False,
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
                {'full_name': 'Jerome Finnigan', 'id': 8562},
                {'full_name': 'Edward May', 'id': 8563},
                {'full_name': 'Joe Parker', 'id': 8564},
                {'full_name': 'John Snow', 'id': 8565},
                {'full_name': 'John Sena', 'id': 8566},
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8565,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8566,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8565,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8566,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8565,
                    'officer_id_2': 8566,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8565,
                    'officer_id_2': 8566,
                    'incident_date': datetime(2008, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 4
                },
            ],
            'list_event': ['2007-12-31 00:00:00+00:00', '2008-12-31 00:00:00+00:00']
        }

        url = reverse('api-v2:social-graph-list', kwargs={})
        response = self.client.get(url, {
            'unit_id': 123,
            'threshold': 3,
            'show_civil_only': True
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])
