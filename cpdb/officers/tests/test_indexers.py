from datetime import date, datetime

import pytz
from django.test import SimpleTestCase
from django.test.testcases import TestCase

from mock import Mock, patch
from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer,
    JoinedTimelineEventIndexer, SocialGraphIndexer
)


class OfficersIndexerTestCase(SimpleTestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficersIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.id = 123
        officer.full_name = 'Alex Mack'
        officer.last_unit = '4'
        officer.rank = '5'
        officer.race = 'White'
        officer.current_badge = '123456'
        officer.gender_display = 'Male'
        officer.appointed_date = date(2017, 2, 27)
        officer.resignation_date = date(2017, 12, 27)
        officer.get_active_display = Mock(return_value='Active')
        officer.allegation_count = 1
        officer.sustained_count = 0
        officer.total_complaints_aggregation = [{'year': 2000, 'count': 1, 'sustained_count': 0}]
        officer.complaint_category_aggregation = [
            {
                'name': 'Illegal Search',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {'year': 2000, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}
                ]
            }
        ]
        officer.complainant_race_aggregation = [
            {
                'name': 'White',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 0}
                ]
            }
        ]
        officer.complainant_age_aggregation = [
            {
                'name': '<20',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 0}
                ]
            }
        ]
        officer.complainant_gender_aggregation = [
            {
                'name': 'Male',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {'year': 2000, 'name': 'Male', 'count': 1, 'sustained_count': 0}
                ]
            }
        ]

        self.assertDictEqual(OfficersIndexer().extract_datum(officer), {
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': '4',
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'complaint_records': {
                'count': 1,
                'sustained_count': 0,
                'items': [{'year': 2000, 'count': 1, 'sustained_count': 0}],
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 0, 'items': [
                            {'year': 2000, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}
                        ]}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 0, 'items': [
                            {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 0}
                        ]}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 0, 'items': [
                            {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 0}
                        ]}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 0, 'items': [
                            {'year': 2000, 'name': 'Male', 'count': 1, 'sustained_count': 0}
                        ]}]
                    }
                ]
            }
        })


class CRTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer_allegation = Mock()

        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[officer_allegation]):
            expect(CRTimelineEventIndexer().get_queryset()).to.eq([officer_allegation])

    def test_extract_datum(self):
        officer_allegation = Mock()
        officer_allegation.officer_id = 123
        officer_allegation.start_date = date(2012, 1, 1)
        officer_allegation.crid = '123456'
        officer_allegation.category = 'Illegal Search'
        officer_allegation.subcategory = 'Search of premise/vehicle without warrant'
        officer_allegation.final_finding_display = 'Unfounded'
        officer_allegation.coaccused_count = 4
        officer_allegation.allegation.complainant_races = ['White', 'Unknown']
        officer_allegation.allegation.complainant_age_groups = ['21-30', '51+']
        officer_allegation.allegation.complainant_genders = ['Male']

        expect(CRTimelineEventIndexer().extract_datum(officer_allegation)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'date': '2012-01-01',
            'year_sort': 2012,
            'priority_sort': 40,
            'kind': 'CR',
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'Search of premise/vehicle without warrant',
            'finding': 'Unfounded',
            'coaccused': 4,
            'race': ['White', 'Unknown'],
            'age': ['21-30', '51+'],
            'gender': ['Male']
        })


class UnitChangeTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer_history = Mock()

        with patch('officers.indexers.OfficerHistory.objects.filter', return_value=[officer_history]):
            expect(UnitChangeTimelineEventIndexer().get_queryset()).to.eq([officer_history])

    def test_extract_datum(self):
        officer_history = Mock()
        officer_history.officer_id = 123
        officer_history.effective_date = date(2010, 3, 4)
        officer_history.unit_name = '003'
        expect(UnitChangeTimelineEventIndexer().extract_datum(officer_history)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'date': '2010-03-04',
            'kind': 'UNIT_CHANGE',
            'unit_name': '003',
            'year_sort': 2010,
            'priority_sort': 30,
        })


class JoinedTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.filter', return_value=[officer]):
            expect(JoinedTimelineEventIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.id = 123
        officer.appointed_date = date(2012, 1, 1)
        expect(JoinedTimelineEventIndexer().extract_datum(officer)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'kind': 'JOINED',
            'date': '2012-01-01',
            'year_sort': 2012,
            'priority_sort': 10,
        })


class SocialGraphIndexerTestCase(TestCase):
    def setUp(self):
        self.indexer = SocialGraphIndexer()

        self.officer1 = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater')
        allegation1 = AllegationFactory(incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=None)
        allegation4 = AllegationFactory(incident_date=datetime(2002, 12, 12, tzinfo=pytz.utc))

        OfficerAllegationFactory(officer=self.officer1, allegation=allegation1)
        OfficerAllegationFactory(officer=self.officer1, allegation=allegation2)
        OfficerAllegationFactory(officer=self.officer1, allegation=allegation3)
        OfficerAllegationFactory(officer=self.officer1, allegation=allegation4)

        self.officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
        OfficerAllegationFactory(officer=self.officer2, allegation=allegation1)
        OfficerAllegationFactory(officer=self.officer2, allegation=allegation2)

        unrelated_allegation = AllegationFactory(incident_date=datetime(2003, 3, 3, tzinfo=pytz.utc))
        unrelated_officer = OfficerFactory(id=3, first_name='Some', last_name='Unrelated Guy')
        OfficerAllegationFactory(officer=unrelated_officer, allegation=unrelated_allegation)
        OfficerAllegationFactory(officer=self.officer2, allegation=unrelated_allegation)

    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(SocialGraphIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        expect(self.indexer.extract_datum(self.officer1)).to.eq({
            'officer_id': 1,
            'graph': {
                'links': [
                    {
                        'source': 1,
                        'target': 2,
                        'cr_years': [2001, 2002]
                    }
                ],
                'nodes': [
                    {
                        'id': 1,
                        'name': 'Clarence Featherwater',
                        'cr_years': [None, 2001, 2002, 2002]
                    },
                    {
                        'id': 2,
                        'name': 'Raymond Piwnicki',
                        'cr_years': [2001, 2002, 2003]
                    }
                ]
            }
        })
