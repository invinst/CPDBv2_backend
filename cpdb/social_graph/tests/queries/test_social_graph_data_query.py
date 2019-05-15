import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from data.models import Officer
from social_graph.queries import SocialGraphDataQuery


class SocialGraphDataQueryTestCase(TestCase):
    def test_execute_default(self):
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

        expected_officers = [
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
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
        ]

        expected_list_event = ['2006-12-31', '2007-12-31']
        expected_coaccused_data = [
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
        ]
        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(officers)
        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_1_show_civil_only_true(self):
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

        expected_coaccused_data = [
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
        ]

        expected_officers = [
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
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
        ]

        expected_list_event = ['2005-12-31', '2007-12-31']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(officers, threshold=1)
        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_3_show_civil_only_true(self):
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

        expected_coaccused_data = [
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
        ]

        expected_officers = [
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
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
                'full_name': 'John Sena',
                'id': 8566,
                'percentile': {
                    'percentile_allegation_civilian': '13.1300',
                    'percentile_allegation_internal': '14.1400',
                    'percentile_trr': '15.1500'
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
        ]

        expected_list_event = ['2007-12-31', '2008-12-31']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3, officer_4, officer_5]]
        )

        social_graph_data_query = SocialGraphDataQuery(officers, threshold=3)
        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_1_show_civil_only_false(self):
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

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=True,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=True,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=7, officer=officer_3, allegation=allegation_3)

        expected_coaccused_data = [
            {
                'officer_id_1': 8562,
                'officer_id_2': 8563,
                'incident_date': '2005-12-31',
                'accussed_count': 1
            },
            {
                'officer_id_1': 8562,
                'officer_id_2': 8563,
                'incident_date': '2006-12-31',
                'accussed_count': 2
            },
            {
                'officer_id_1': 8562,
                'officer_id_2': 8563,
                'incident_date': '2007-12-31',
                'accussed_count': 3
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
        ]

        expected_officers = [
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
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
        ]

        expected_list_event = ['2005-12-31', '2006-12-31', '2007-12-31']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(
            officers,
            threshold=1,
            show_civil_only=False
        )
        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_3_show_civil_only_false(self):
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
            is_officer_complaint=True,
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

        expected_coaccused_data = [
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
        ]

        expected_officers = [
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000'
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
                'full_name': 'John Sena',
                'id': 8566,
                'percentile': {
                    'percentile_allegation_civilian': '13.1300',
                    'percentile_allegation_internal': '14.1400',
                    'percentile_trr': '15.1500'
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
        ]

        expected_list_event = ['2007-12-31', '2008-12-31']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3, officer_4, officer_5]]
        )

        social_graph_data_query = SocialGraphDataQuery(
            officers, threshold=3, show_civil_only=False
        )
        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_show_connected_officers(self):
        officer_1 = OfficerFactory(
            id=8000,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )
        officer_2 = OfficerFactory(
            id=8001,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile=4.4,
            internal_allegation_percentile=5.5,
            trr_percentile=6.6,
        )
        officer_3 = OfficerFactory(
            id=8002,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            trr_percentile=9.9,
        )
        officer_4 = OfficerFactory(
            id=8003,
            first_name='John',
            last_name='Snow',
            civilian_allegation_percentile=10.10,
            internal_allegation_percentile=11.11,
            trr_percentile=12.12,
        )
        officer_5 = OfficerFactory(
            id=8004,
            first_name='John',
            last_name='Sena',
            civilian_allegation_percentile=13.13,
            internal_allegation_percentile=14.14,
            trr_percentile=15.15,
        )
        officer_6 = OfficerFactory(
            id=8005,
            first_name='Tom',
            last_name='Cruise',
            civilian_allegation_percentile=16.16,
            internal_allegation_percentile=17.17,
            trr_percentile=18.18,
        )
        officer_7 = OfficerFactory(
            id=8006,
            first_name='Robert',
            last_name='Long',
            civilian_allegation_percentile=19.19,
            internal_allegation_percentile=20.20,
            trr_percentile=21.21,
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
            is_officer_complaint=True,
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

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)

        OfficerAllegationFactory(id=3, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_3)

        OfficerAllegationFactory(id=7, officer=officer_2, allegation=allegation_4)
        OfficerAllegationFactory(id=8, officer=officer_4, allegation=allegation_4)
        OfficerAllegationFactory(id=9, officer=officer_2, allegation=allegation_5)
        OfficerAllegationFactory(id=10, officer=officer_4, allegation=allegation_5)

        OfficerAllegationFactory(id=11, officer=officer_3, allegation=allegation_6)
        OfficerAllegationFactory(id=12, officer=officer_5, allegation=allegation_6)
        OfficerAllegationFactory(id=13, officer=officer_3, allegation=allegation_7)
        OfficerAllegationFactory(id=14, officer=officer_5, allegation=allegation_7)
        OfficerAllegationFactory(id=15, officer=officer_3, allegation=allegation_8)
        OfficerAllegationFactory(id=16, officer=officer_6, allegation=allegation_8)
        OfficerAllegationFactory(id=17, officer=officer_3, allegation=allegation_9)
        OfficerAllegationFactory(id=18, officer=officer_6, allegation=allegation_9)

        OfficerAllegationFactory(id=19, officer=officer_3, allegation=allegation_10)
        OfficerAllegationFactory(id=20, officer=officer_7, allegation=allegation_10)

        expected_graph_data = {
            'officers': [
                {
                    'full_name': 'Edward May',
                    'id': 8001,
                    'percentile': {
                        'percentile_allegation_civilian': '4.4000',
                        'percentile_allegation_internal': '5.5000',
                        'percentile_trr': '6.6000'
                    }
                },
                {
                    'full_name': 'Jerome Finnigan',
                    'id': 8000,
                    'percentile': {
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000'
                    }
                },
                {
                    'full_name': 'Joe Parker',
                    'id': 8002,
                    'percentile': {
                        'percentile_allegation_civilian': '7.7000',
                        'percentile_allegation_internal': '8.8000',
                        'percentile_trr': '9.9000'
                    }
                },
                {
                    'full_name': 'John Sena',
                    'id': 8004,
                    'percentile': {
                        'percentile_allegation_civilian': '13.1300',
                        'percentile_allegation_internal': '14.1400',
                        'percentile_trr': '15.1500'
                    }
                },
                {
                    'full_name': 'John Snow',
                    'id': 8003,
                    'percentile': {
                        'percentile_allegation_civilian': '10.1000',
                        'percentile_allegation_internal': '11.1100',
                        'percentile_trr': '12.1200'
                    }
                },
                {
                    'full_name': 'Tom Cruise',
                    'id': 8005,
                    'percentile': {
                        'percentile_allegation_civilian': '16.1600',
                        'percentile_allegation_internal': '17.1700',
                        'percentile_trr': '18.1800'
                    }
                },
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8001,
                    'officer_id_2': 8002,
                    'incident_date': '2007-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8001,
                    'officer_id_2': 8003,
                    'incident_date': '2009-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8002,
                    'officer_id_2': 8004,
                    'incident_date': '2011-12-31',
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8002,
                    'officer_id_2': 8005,
                    'incident_date': '2013-12-31',
                    'accussed_count': 2
                }
            ],
            'list_event': [
                '2007-12-31',
                '2009-12-31',
                '2011-12-31',
                '2013-12-31',
            ]
        }

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(
            officers, threshold=2, show_civil_only=False, show_connected_officers=True
        )

        expect(social_graph_data_query.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_empty_officers(self):
        social_graph_data_query = SocialGraphDataQuery(Officer.objects.none(), threshold=2, show_civil_only=False)
        expect(social_graph_data_query.graph_data()).to.be.empty()

    def test_all_officers_default(self):
        officer_1 = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile='88.8800',
            internal_allegation_percentile='77.7700',
            trr_percentile='66.6600',
        )
        officer_2 = OfficerFactory(
            id=8563,
            first_name='Edward',
            last_name='May',
            civilian_allegation_percentile='55.6600',
            internal_allegation_percentile='66.7700',
            trr_percentile='77.8800',
        )
        officer_3 = OfficerFactory(
            id=8564,
            first_name='Joe',
            last_name='Parker',
            civilian_allegation_percentile='44.4400',
            internal_allegation_percentile='33.3300',
            trr_percentile='22.2200',
        )

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(officers)
        expect(list(social_graph_data_query.all_officers())).to.eq([officer_2, officer_1, officer_3])

    def test_all_officers_with_show_connected_officers(self):
        officer_1 = OfficerFactory(id=8000, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8001, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8002, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8003, first_name='John', last_name='Snow')
        officer_5 = OfficerFactory(id=8004, first_name='John', last_name='Sena')
        officer_6 = OfficerFactory(id=8005, first_name='Tom', last_name='Cruise')
        officer_7 = OfficerFactory(id=8006, first_name='Robert', last_name='Long')

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
            is_officer_complaint=True,
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

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)

        OfficerAllegationFactory(id=3, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_3)

        OfficerAllegationFactory(id=7, officer=officer_2, allegation=allegation_4)
        OfficerAllegationFactory(id=8, officer=officer_4, allegation=allegation_4)
        OfficerAllegationFactory(id=9, officer=officer_2, allegation=allegation_5)
        OfficerAllegationFactory(id=10, officer=officer_4, allegation=allegation_5)

        OfficerAllegationFactory(id=11, officer=officer_3, allegation=allegation_6)
        OfficerAllegationFactory(id=12, officer=officer_5, allegation=allegation_6)
        OfficerAllegationFactory(id=13, officer=officer_3, allegation=allegation_7)
        OfficerAllegationFactory(id=14, officer=officer_5, allegation=allegation_7)
        OfficerAllegationFactory(id=15, officer=officer_3, allegation=allegation_8)
        OfficerAllegationFactory(id=16, officer=officer_6, allegation=allegation_8)
        OfficerAllegationFactory(id=17, officer=officer_3, allegation=allegation_9)
        OfficerAllegationFactory(id=18, officer=officer_6, allegation=allegation_9)

        OfficerAllegationFactory(id=19, officer=officer_3, allegation=allegation_10)
        OfficerAllegationFactory(id=20, officer=officer_7, allegation=allegation_10)

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3, officer_4, officer_5, officer_6]]
        )

        social_graph_data_query = SocialGraphDataQuery(
            officers,
            threshold=2,
            show_civil_only=False,
            show_connected_officers=True
        )

        expected_officers = [officer_2, officer_1, officer_3, officer_5, officer_4, officer_6]

        expect(list(social_graph_data_query.all_officers())).to.eq(expected_officers)

    def test_allegations_default(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=False,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc),
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc),
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
        OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)

        officers = Officer.objects.filter(
            id__in=[officer.id for officer in [officer_1, officer_2, officer_3]]
        )

        social_graph_data_query = SocialGraphDataQuery(officers)
        expect(list(social_graph_data_query.allegations())).to.eq([allegation_2, allegation_3])
