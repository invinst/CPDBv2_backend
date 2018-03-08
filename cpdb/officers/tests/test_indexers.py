from datetime import date, datetime

import pytz
from django.test import SimpleTestCase
from django.test.testcases import TestCase
from mock import Mock, patch
from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer,
    JoinedTimelineEventIndexer, SocialGraphIndexer, OfficerMetricsIndexer
)


class OfficersIndexerTestCase(SimpleTestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficersIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            full_name='Alex Mack',
            last_unit='4',
            rank='5',
            race='White',
            current_badge='123456',
            gender_display='Male',
            birth_year=1910,
            appointed_date=date(2017, 2, 27),
            resignation_date=date(2017, 12, 27),
            get_active_display=Mock(return_value='Active'),
        )

        expect(OfficersIndexer().extract_datum(officer)).to.eq({
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
            'birth_year': 1910,
        })


class OfficerMetricsIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficerMetricsIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            full_name='Alex Mack',
            appointed_date=date(2017, 2, 27),
            get_active_display=Mock(return_value='Active'),
            allegation_count=1,
            complaint_percentile=90.0,
            honorable_mention_count=2,
            sustained_count=1,
            discipline_count=2,
            civilian_compliment_count=2,
        )

        expect(OfficerMetricsIndexer().extract_datum(officer)).to.eq({
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 90.0,
            'honorable_mention_count': 2,
            'sustained_count': 1,
            'discipline_count': 2,
            'civilian_compliment_count': 2
        })


class CRTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer_allegation = Mock()

        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[officer_allegation]):
            expect(CRTimelineEventIndexer().get_queryset()).to.eq([officer_allegation])

    def test_extract_datum(self):
        officer_allegation = Mock(
            officer_id=123,
            start_date=date(2012, 1, 1),
            crid='123456',
            category='Illegal Search',
            subcategory='Search of premise/vehicle without warrant',
            final_finding_display='Unfounded',
            coaccused_count=4,
            allegation=Mock(
                complainant_races=['White', 'Unknown'],
                complainant_age_groups=['21-30', '51+'],
                complainant_genders=['Male'],
            )
        )

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
