from datetime import date

from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer, YearTimelineEventIndexer,
    JoinedTimelineEventIndexer, TimelineMinimapIndexer
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
        officer.allegation_count = 1
        officer.sustained_count = 0
        officer.complaint_category_aggregation = [
            {
                'name': 'Illegal Search',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_race_aggregation = [
            {
                'name': 'White',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_age_aggregation = [
            {
                'name': '<20',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_gender_aggregation = [
            {
                'name': 'Male',
                'count': 1,
                'sustained_count': 0
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
            'complaint_records': {
                'count': 1,
                'sustained_count': 0,
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 0}]
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
        officer_allegation.finding = 'Unfounded'
        officer_allegation.coaccused_count = 4
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
            'coaccused': 4
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


class YearTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(YearTimelineEventIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.pk = 123
        officer.appointed_date = date(2012, 1, 1)
        oa_1 = Mock()
        oa_1.start_date = date(2012, 1, 3)
        oa_2 = Mock()
        oa_2.start_date = date(2015, 2, 3)
        oa_3 = Mock()
        oa_3.start_date = date(2015, 5, 3)
        oh = Mock()
        oh.effective_date = date(2015, 7, 3)
        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[oa_1, oa_2, oa_3]):
            with patch('officers.indexers.OfficerHistory.objects.filter', return_value=[oh]):
                expect(sorted(
                    list(YearTimelineEventIndexer().extract_datum(officer)),
                    key=lambda item: item['year']
                )).to.eq([
                    {
                        'officer_id': 123,
                        'kind': 'YEAR',
                        'year': 2012,
                        'date_sort': date(2012, 12, 31),
                        'year_sort': 2012,
                        'priority_sort': 20,
                        'crs': 1
                    },
                    {
                        'officer_id': 123,
                        'kind': 'YEAR',
                        'year': 2015,
                        'date_sort': date(2015, 12, 31),
                        'year_sort': 2015,
                        'priority_sort': 20,
                        'crs': 2
                    }
                ])


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


class TimelineMinimapIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(TimelineMinimapIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.pk = 123
        officer.appointed_date = date(2000, 1, 1)
        oa = Mock()
        oa.start_date = date(2012, 1, 1)
        unit = Mock()
        unit.effective_date = date(2001, 1, 1)
        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[oa]):
            with patch('officers.indexers.OfficerHistory.objects.filter', return_value=[unit]):
                expect(TimelineMinimapIndexer().extract_datum(officer)).to.eq({
                    'officer_id': 123,
                    'items': [
                        {
                            'kind': 'CR',
                            'year': 2012
                        },
                        {
                            'kind': 'Unit',
                            'year': 2001
                        },
                        {
                            'kind': 'Joined',
                            'year': 2000
                        }
                    ]
                })
