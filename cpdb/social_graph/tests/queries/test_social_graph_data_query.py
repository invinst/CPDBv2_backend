import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from social_graph.queries.queries import SocialGraphDataQuery


class SocialGraphDataQueryTestCase(TestCase):
    def test_execute_default(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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
            {'full_name': 'Jerome Finnigan', 'id': 8562},
            {'full_name': 'Edward May', 'id': 8563},
            {'full_name': 'Joe Parker', 'id': 8564},
        ]

        expected_list_event = ['2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']
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

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3])
        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_1_show_civil_only_true(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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
            {'full_name': 'Jerome Finnigan', 'id': 8562},
            {'full_name': 'Edward May', 'id': 8563},
            {'full_name': 'Joe Parker', 'id': 8564},
        ]

        expected_list_event = ['2005-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3], threshold=1)
        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_3_show_civil_only_true(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='John', last_name='Snow')
        officer_5 = OfficerFactory(id=8566, first_name='John', last_name='Sena')

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
            {'full_name': 'Jerome Finnigan', 'id': 8562},
            {'full_name': 'Edward May', 'id': 8563},
            {'full_name': 'Joe Parker', 'id': 8564},
            {'full_name': 'John Snow', 'id': 8565},
            {'full_name': 'John Sena', 'id': 8566},
        ]

        expected_list_event = ['2007-12-31 00:00:00+00:00', '2008-12-31 00:00:00+00:00']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3, officer_4, officer_5], threshold=3)
        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_1_show_civil_only_false(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')

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
            {'full_name': 'Jerome Finnigan', 'id': 8562},
            {'full_name': 'Edward May', 'id': 8563},
            {'full_name': 'Joe Parker', 'id': 8564},
        ]

        expected_list_event = ['2005-12-31 00:00:00+00:00', '2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3], threshold=1, show_civil_only=False)
        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_threshold_3_show_civil_only_false(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='John', last_name='Snow')
        officer_5 = OfficerFactory(id=8566, first_name='John', last_name='Sena')

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
            {'full_name': 'Jerome Finnigan', 'id': 8562},
            {'full_name': 'Edward May', 'id': 8563},
            {'full_name': 'Joe Parker', 'id': 8564},
            {'full_name': 'John Snow', 'id': 8565},
            {'full_name': 'John Sena', 'id': 8566},
        ]

        expected_list_event = ['2007-12-31 00:00:00+00:00', '2008-12-31 00:00:00+00:00']

        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        results = SocialGraphDataQuery(
            [officer_1, officer_2, officer_3, officer_4, officer_5], threshold=3, show_civil_only=False
        )
        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_show_connected_officers(self):
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

        expected_graph_data = {
            'officers': [
                {'full_name': 'Edward May', 'id': 8001},
                {'full_name': 'Jerome Finnigan', 'id': 8000},
                {'full_name': 'Joe Parker', 'id': 8002},
                {'full_name': 'John Sena', 'id': 8004},
                {'full_name': 'John Snow', 'id': 8003},
                {'full_name': 'Tom Cruise', 'id': 8005},
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
                '2007-12-31 00:00:00+00:00',
                '2009-12-31 00:00:00+00:00',
                '2011-12-31 00:00:00+00:00',
                '2013-12-31 00:00:00+00:00',
            ]
        }

        results = SocialGraphDataQuery(
            [officer_1, officer_2, officer_3], threshold=2, show_civil_only=False, show_connected_officers=True
        )

        expect(results.graph_data()).to.eq(expected_graph_data)

    def test_graph_data_empty_officers(self):
        results = SocialGraphDataQuery([], threshold=2, show_civil_only=False)
        expect(results.graph_data()).to.be.empty()

    def test_detail_data(self):
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
                'full_name': 'Jerome Finnigan',
                'id': 8562,
                'percentile': {
                    'percentile_allegation_civilian': '88.8800',
                    'percentile_allegation_internal': '77.7700',
                    'percentile_trr': '66.6600',
                }
            },
            {
                'full_name': 'Edward May',
                'id': 8563,
                'percentile': {
                    'percentile_allegation_civilian': '55.6600',
                    'percentile_allegation_internal': '66.7700',
                    'percentile_trr': '77.8800',
                }
            },
            {
                'full_name': 'Joe Parker',
                'id': 8564,
                'percentile': {
                    'percentile_allegation_civilian': '44.4400',
                    'percentile_allegation_internal': '33.3300',
                    'percentile_trr': '22.2200',
                }
            },
        ]

        expected_list_event = ['2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']
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

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3], detail_data=True)
        expect(results.graph_data()).to.eq(expected_graph_data)

    # def test_allegations_default(self):
    #     officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
    #     officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
    #     officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
    #
    #     category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory 1')
    #     category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Subcategory 2')
    #
    #     allegation_1 = AllegationFactory(
    #         crid='123',
    #         is_officer_complaint=False,
    #         incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
    #         most_common_category=category_1,
    #     )
    #     allegation_2 = AllegationFactory(
    #         crid='456',
    #         is_officer_complaint=False,
    #         incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc),
    #         most_common_category=category_2,
    #     )
    #     allegation_3 = AllegationFactory(
    #         crid='789',
    #         is_officer_complaint=False,
    #         incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc),
    #         most_common_category=category_1,
    #     )
    #
    #     OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
    #     OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
    #     OfficerAllegationFactory(id=3, officer=officer_3, allegation=allegation_1)
    #     OfficerAllegationFactory(id=4, officer=officer_1, allegation=allegation_2)
    #     OfficerAllegationFactory(id=5, officer=officer_2, allegation=allegation_2)
    #     OfficerAllegationFactory(id=6, officer=officer_3, allegation=allegation_2)
    #     OfficerAllegationFactory(id=7, officer=officer_1, allegation=allegation_3)
    #     OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_3)
    #
    #     expected_allegations = [
    #         {
    #             'crid': '123',
    #             'incident_date': '2005-12-31',
    #             'most_common_category': {
    #                 'category': 'Use of Force',
    #                 'allegation_name': 'Subcategory 1'
    #             }
    #         },
    #         {
    #             'crid': '456',
    #             'incident_date': '2006-12-31',
    #             'most_common_category': {
    #                 'category': 'Illegal Search',
    #                 'allegation_name': 'Subcategory 2'
    #             }
    #         },
    #         {
    #             'crid': '789',
    #             'incident_date': '2007-12-31',
    #             'most_common_category': {
    #                 'category': 'Use of Force',
    #                 'allegation_name': 'Subcategory 1'
    #             }
    #         },
    #     ]
    #
    #     results = SocialGraphDataQuery([officer_1, officer_2, officer_3])
    #     expect(results.allegations()).to.eq(expected_allegations)
