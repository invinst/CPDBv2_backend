import pytz
from datetime import datetime

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import PoliceUnitFactory, OfficerFactory, AllegationFactory, \
    OfficerAllegationFactory, OfficerHistoryFactory, AttachmentFileFactory, AllegationCategoryFactory


class SocialGraphViewSetTestCase(APITestCase):
    def test_network_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
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

        expected_data = {
            'officers': [
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile': {
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000'
                    }
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile': {
                        'percentile_allegation_civilian': '4.4000',
                        'percentile_allegation_internal': '5.5000',
                        'percentile_trr': '6.6000'
                    }
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile': {
                        'percentile_allegation_civilian': '7.7000',
                        'percentile_allegation_internal': '8.8000',
                        'percentile_trr': '9.9000'
                    }
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

        url = reverse('api-v2:social-graph-network', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officers']).to.contain(*expected_data['officers'])
        expect(len(response.data['officers'])).to.eq(len(expected_data['officers']))
        expect(response.data['coaccused_data']).to.eq(expected_data['coaccused_data'])
        expect(response.data['list_event']).to.eq(expected_data['list_event'])

    def test_network_with_specific_threshold_and_show_civil_only(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
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
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile': {
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000'
                    }
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile': {
                        'percentile_allegation_civilian': '4.4000',
                        'percentile_allegation_internal': '5.5000',
                        'percentile_trr': '6.6000'
                    }
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile': {
                        'percentile_allegation_civilian': '7.7000',
                        'percentile_allegation_internal': '8.8000',
                        'percentile_trr': '9.9000'
                    }
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2005-12-31',
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': '2007-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': '2007-12-31',
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': '2007-12-31',
                    'accussed_count': 1
                },
            ],
            'list_event': ['2005-12-31', '2007-12-31']
        }

        url = reverse('api-v2:social-graph-network', kwargs={})
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

    def test_network_with_unit_id_param(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
        )
        officer_4 = OfficerFactory(
            id=8565,
            first_name='John',
            last_name='Snow',
            civilian_allegation_percentile=10.10,
            internal_allegation_percentile=11.11,
            trr_percentile=12.12,
        )
        officer_5 = OfficerFactory(
            id=8566,
            first_name='John',
            last_name='Sena',
            civilian_allegation_percentile=13.13,
            internal_allegation_percentile=14.14,
            trr_percentile=15.15,
        )

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
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8562,
                    'percentile': {
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000'
                    }
                },
                {
                    'full_name': 'Edward May',
                    'id': 8563,
                    'percentile': {
                        'percentile_allegation_civilian': '4.4000',
                        'percentile_allegation_internal': '5.5000',
                        'percentile_trr': '6.6000'
                    }
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8564,
                    'percentile': {
                        'percentile_allegation_civilian': '7.7000',
                        'percentile_allegation_internal': '8.8000',
                        'percentile_trr': '9.9000'
                    }
                },
                {
                    'full_name': 'John Snow',
                    'id': 8565,
                    'percentile': {
                        'percentile_allegation_civilian': '10.1000',
                        'percentile_allegation_internal': '11.1100',
                        'percentile_trr': '12.1200'
                    }
                },
                {
                    'full_name': 'John Sena',
                    'id': 8566,
                    'percentile': {
                        'percentile_allegation_civilian': '13.1300',
                        'percentile_allegation_internal': '14.1400',
                        'percentile_trr': '15.1500'
                    }
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

        url = reverse('api-v2:social-graph-network', kwargs={})
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
                'percentile': {
                    'percentile_allegation_civilian': '55.6600',
                    'percentile_allegation_internal': '66.7700',
                    'percentile_trr': '77.8800',
                }
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
                'percentile': {
                    'percentile_allegation_civilian': '88.8800',
                    'percentile_allegation_internal': '77.7700',
                    'percentile_trr': '66.6600',
                }
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
                'percentile': {
                    'percentile_allegation_civilian': '44.4400',
                    'percentile_allegation_internal': '33.3300',
                    'percentile_trr': '22.2200',
                }
            },
        ]

        url = reverse('api-v2:social-graph-officers', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_allegations_default(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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
            most_common_category=category_1
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_2
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc),
            most_common_category=category_3
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)

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

        url = reverse('api-v2:social-graph-allegations', kwargs={})
        response = self.client.get(url, {
            'officer_ids': '8562, 8563, 8564',
        })

        expected_data = [
            {
                'crid': '456',
                'incident_date': '2006-12-31',
                'most_common_category': {
                    'category': 'Illegal Search',
                    'allegation_name': 'Illegal Arrest / False Arrest'
                },
                'attachments': [
                    {
                        'id': '1',
                        'title': 'Attachment Title',
                        'file_type': 'document',
                        'url': 'http://lvh.me/document',
                    }
                ]

            },
            {
                'crid': '789',
                'incident_date': '2007-12-31',
                'most_common_category': {
                    'category': 'Operation/Personnel Violations',
                    'allegation_name': 'Improper Search Of Person'
                },
                'attachments': []

            }
        ]

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)
