import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from social_graph.queries import SocialGraphDataQuery


class DataGeneratorTestCase(TestCase):
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
        ]
        expected_graph_data = {
            'officers': expected_officers,
            'coaccused_data': expected_coaccused_data,
            'list_event': expected_list_event
        }

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3])
        expect(results.coaccused_data).to.eq(expected_coaccused_data)
        expect(results.list_event).to.eq(expected_list_event)
        expect(results.graph_data).to.eq(expected_graph_data)

    def test_execute_threshold_1_show_civil_only_true(self):
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
        ]

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3], threshold=1)
        expect(results.coaccused_data).to.eq(expected_coaccused_data)
        expect(results.list_event).to.eq(['2005-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00'])

    def test_execute_threshold_3_show_civil_only_true(self):
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
        ]

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3, officer_4, officer_5], threshold=3)
        expect(results.coaccused_data).to.eq(expected_coaccused_data)
        expect(results.list_event).to.eq(['2007-12-31 00:00:00+00:00', '2008-12-31 00:00:00+00:00'])

    def test_execute_threshold_1_show_civil_only_false(self):
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
                'incident_date': datetime(2005, 12, 31, 0, 0, tzinfo=pytz.utc),
                'accussed_count': 1
            },
            {
                'officer_id_1': 8562,
                'officer_id_2': 8563,
                'incident_date': datetime(2006, 12, 31, 0, 0, tzinfo=pytz.utc),
                'accussed_count': 2
            },
            {
                'officer_id_1': 8562,
                'officer_id_2': 8563,
                'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                'accussed_count': 3
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
        ]

        results = SocialGraphDataQuery([officer_1, officer_2, officer_3], threshold=1, show_civil_only=False)
        expect(results.coaccused_data).to.eq(expected_coaccused_data)
        expect(results.list_event).to.eq(
            ['2005-12-31 00:00:00+00:00', '2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']
        )

    def test_execute_threshold_3_show_civil_only_false(self):
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
        ]

        results = SocialGraphDataQuery(
            [officer_1, officer_2, officer_3, officer_4, officer_5], threshold=3, show_civil_only=False
        )
        expect(results.coaccused_data).to.eq(expected_coaccused_data)
        expect(results.list_event).to.eq(['2007-12-31 00:00:00+00:00', '2008-12-31 00:00:00+00:00'])

    def test_handle_empty_officers(self):
        results = SocialGraphDataQuery([], threshold=2, show_civil_only=False)
        expect(results.coaccused_data).to.be.empty()
        expect(results.list_event).to.be.empty()
        expect(results.graph_data).to.be.empty()
