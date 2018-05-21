from datetime import date, datetime

import pytz
from django.test import SimpleTestCase
from django.test.testcases import TestCase
from django.utils.timezone import now
from mock import Mock, patch
from robber import expect

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, OfficerHistoryFactory, AttachmentFileFactory,
    AllegationCategoryFactory
)
from data.models import Officer
from officers.indexers import (
    OfficersIndexer,
    SocialGraphIndexer,
    OfficerPercentileIndexer,
    CRNewTimelineEventIndexer,
    UnitChangeNewTimelineEventIndexer,
    JoinedNewTimelineEventIndexer,
    TRRNewTimelineEventIndexer,
    AwardNewTimelineEventIndexer,
    OfficerCoaccusalsIndexer,
    CRTimelineEventIndexer,
    UnitChangeTimelineEventIndexer,
    JoinedTimelineEventIndexer,
)
from officers.serializers import OfficerMetricsSerializer
from trr.factories import TRRFactory


class OfficerMetricsSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock(**{
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 2,
            'honorable_mention_count': 3,
            'percentile_honorable_mention': 7,
            'sustained_count': 4,
            'discipline_count': 5,
            'civilian_compliment_count': 6,
            'first_name': 'Roberto',
            'last_name': 'Last Name',
            'race': 'Asian',
            'trr_count': 8,
            'major_award_count': 9,
            'single_percentiles': {
                'id': 123,
                'percentile_honorable_mention': 98.000,
            },
        })

        expect(OfficerMetricsSerializer(obj).data).to.eq({
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 2.0,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'discipline_count': 5,
            'civilian_compliment_count': 6,
            'trr_count': 8,
            'major_award_count': 9,
            'single_percentiles': {
                'id': 123,
                'honorable_mention_percentile': 98.000,
            }
        })


class OfficersIndexerTestCase(SimpleTestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficersIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            v2_to='',
            v1_url='',
            tags=[],
            id=123,
            full_name='Alex Mack',
            last_unit=Mock(id=1, unit_name='4', description=''),
            rank='5',
            race='White',
            current_badge='123456',
            historic_badges=['123', '456'],
            historic_units=[
                Mock(**{
                    'id': 1,
                    'unit_name': '1',
                    'description': 'Unit 001'
                }),
                Mock(**{
                    'id': 2,
                    'unit_name': '2',
                    'description': 'Unit 002'
                })],
            gender_display='Male',
            birth_year=1910,
            appointed_date=date(2017, 2, 27),
            resignation_date=date(2017, 12, 27),
            get_active_display=Mock(return_value='Active'),
            allegation_count=2,
            complaint_percentile=99.8,
            honorable_mention_count=1,
            sustained_count=1,
            discipline_count=1,
            civilian_compliment_count=0,
            percentiles=[],
            current_salary=9000,
            single_percentiles={
                'id': 123,
                'percentile_honorable_mention': 98,
            },
            total_complaints_aggregation=[{'year': 2000, 'count': 1, 'sustained_count': 0}],
            trr_count=1,
            major_award_count=9,
            complaint_category_aggregation=[
                {
                    'name': 'Illegal Search',
                    'count': 1,
                    'sustained_count': 0,
                    'items': [
                        {'year': 2000, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}
                    ]
                }
            ],
            complainant_race_aggregation=[
                {
                    'name': 'White',
                    'count': 1,
                    'sustained_count': 0,
                    'items': [
                        {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 0}
                    ]
                }
            ],
            complainant_age_aggregation=[
                {
                    'name': '<20',
                    'count': 1,
                    'sustained_count': 0,
                    'items': [
                        {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 0}
                    ]
                }
            ],
            complainant_gender_aggregation=[
                {
                    'name': 'Male',
                    'count': 1,
                    'sustained_count': 0,
                    'items': [
                        {'year': 2000, 'name': 'Male', 'count': 1, 'sustained_count': 0}
                    ]
                }
            ]
        )

        expect(OfficersIndexer().extract_datum(officer)).to.eq({
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': {
                'id': 1,
                'unit_name': '4',
                'description': '',
            },
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['123', '456'],
            'historic_units': [
                {
                    'id': 1,
                    'unit_name': '1',
                    'description': 'Unit 001'
                }, {
                    'id': 2,
                    'unit_name': '2',
                    'description': 'Unit 002'
                }
            ],
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'birth_year': 1910,
            'complaint_records': {
                'count': 2,
                'sustained_count': 1,
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
            },
            'allegation_count': 2,
            'complaint_percentile': 99.8,
            'honorable_mention_count': 1,
            'single_percentiles': {
                'id': 123,
                'honorable_mention_percentile': 98,
            },
            'sustained_count': 1,
            'discipline_count': 1,
            'civilian_compliment_count': 0,
            'percentiles': [],
            'trr_count': 1,
            'major_award_count': 9,
            'tags': [],
            'to': '',
            'url': '',
            'current_salary': 9000,
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


class OfficerPercentileIndexerTestCase(TestCase):
    def setUp(self):
        self.indexer = OfficerPercentileIndexer()

    def test_get_queryset_no_allegation(self):
        expect(self.indexer.get_queryset()).to.be.empty()

    def _prepare_data_up_to_2017(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
        officer2 = OfficerFactory(id=2, appointed_date=date(2016, 3, 14))

        OfficerAllegationFactory(
            officer=officer1,
            allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
            start_date=datetime(2015, 1, 1),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2016, 1, 22),
            allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory.create_batch(
            2, officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        OfficerAllegationFactory(
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 3, 15, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )

    def validate_object(self, obj, data):
        for key, value in data.iteritems():
            expect(getattr(obj, key, None)).to.eq(value)

    def test_get_queryset(self):
        self._prepare_data_up_to_2017()
        # expect officer 2 not have year 2017 since less than 1 year
        # expect no year 2018, since dataset only up to 2017
        queryset = self.indexer.get_queryset()
        expect(queryset).to.have.length(3)
        self.validate_object(queryset[0], {
            'percentile_trr': 0,
            'percentile_allegation_civilian': 0,
            'metric_allegation_civilian': 1.5,
            'service_year': 2.0,
            'metric_trr': 0.0,
            'metric_allegation_internal': 0.0,
            'metric_allegation': 1.5,
            'year': 2016,
            'officer_id': 1,
            'percentile_allegation': 0,
            'percentile_allegation_internal': 0
        })
        self.validate_object(queryset[1], {
            'percentile_trr': 0,
            'percentile_allegation_civilian': 0,
            'metric_allegation_civilian': 1.0714,
            'service_year': 2.8,
            'metric_trr': 0.0,
            'metric_allegation_internal': 0.0,
            'metric_allegation': 1.0714,
            'year': 2017,
            'officer_id': 1,
            'percentile_allegation': 0,
            'percentile_allegation_internal': 0
        })
        self.validate_object(queryset[2], {
            'percentile_trr': 0,
            'percentile_allegation_civilian': 50.0,
            'metric_allegation_civilian': 1.25,
            'service_year': 1.6,
            'metric_trr': 0.0,
            'metric_allegation_internal': 0.625,
            'metric_allegation': 1.875,
            'year': 2017,
            'officer_id': 2,
            'percentile_allegation': 50.0,
            'percentile_allegation_internal': 50.0
        })

    def test_get_queryset_with_dataset_up_to_now(self):
        self._prepare_data_up_to_2017()
        current_year = now().year
        officer1 = Officer.objects.get(id=1)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(current_year, 1, 2),
            allegation__incident_date=datetime(current_year, 1, 2, tzinfo=pytz.utc)
        )
        results = self.indexer.get_queryset()
        expect(results).to.have.length(3 + (current_year - 2017) * 2)
        expect(results[-1].year).to.eq(current_year)

    def test_extract_datum(self):
        data = {
            'year': 2016,
            'id': 1,
            'service_year': 2.2,
            'metric_trr': 0,
            'metric_allegation': 0,
            'metric_allegation_internal': 0,
            'metric_allegation_civilian': 0,
            'percentile_allegation': 66.6667,
            'percentile_allegation_internal': 50,
            'percentile_trr': 0,
            'percentile_allegation_civilian': 0
        }
        expect(self.indexer.extract_datum(data)).to.eq({
            'id': 1,
            'year': 2016,
            'percentile_allegation': '66.667',
            'percentile_allegation_internal': '50.000',
            'percentile_allegation_civilian': '0.000',
            'percentile_trr': '0.000',
        })


class JoinedNewTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.filter', return_value=[officer]):
            expect(JoinedNewTimelineEventIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            appointed_date=date(2012, 1, 1),
            get_unit_by_date=Mock(return_value=Mock(
                unit_name='001',
                description='Unit_001',
            )),
            rank='Police Officer',
        )
        expect(JoinedNewTimelineEventIndexer().extract_datum(officer)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 10,
            'date': '2012-01-01',
            'kind': 'JOINED',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class UnitChangeNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer_history = OfficerHistoryFactory(
            effective_date=date(2010, 1, 1),
            officer=OfficerFactory(appointed_date=date(2001, 2, 2))
        )
        OfficerHistoryFactory(
            effective_date=date(2010, 1, 1),
            officer=OfficerFactory(appointed_date=date(2010, 1, 1))
        )
        OfficerHistoryFactory(
            effective_date=None,
        )
        expect(list(UnitChangeNewTimelineEventIndexer().get_queryset())).to.eq([officer_history])

    def test_extract_datum(self):
        officer_history = Mock(
            officer_id=123,
            effective_date=date(2010, 3, 4),
            unit_name='003',
            unit_description='Unit_003',
            officer=Mock(rank='Police Officer')
        )
        expect(UnitChangeNewTimelineEventIndexer().extract_datum(officer_history)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 20,
            'date': '2010-03-04',
            'kind': 'UNIT_CHANGE',
            'unit_name': '003',
            'unit_description': 'Unit_003',
            'rank': 'Police Officer',
        })


class CRNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer_allegation = Mock()

        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[officer_allegation]):
            expect(CRNewTimelineEventIndexer().get_queryset()).to.eq([officer_allegation])

    def test_extract_datum(self):
        allegation = AllegationFactory(
            crid='123456',
        )
        AttachmentFileFactory(
            allegation=allegation,
            title='doc_2',
            url='url_2',
            preview_image_url='image_url_2',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            allegation=allegation,
            title='doc_1',
            url='url_1',
            preview_image_url='image_url_1',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        officer = OfficerFactory(
            id=123,
            rank='Police Officer'
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__unit_name='001',
            unit__description='Unit_001',
            effective_date=date(2011, 1, 1),
            end_date=date(2013, 1, 1))
        officer_allegation = OfficerAllegationFactory(
            allegation=allegation,
            officer=officer,
            start_date=date(2012, 1, 1),
            allegation_category=AllegationCategoryFactory(
                category='Illegal Search',
                allegation_name='Search of premise/vehicle without warrant',
            ),
            final_finding='UN',
            final_outcome=''
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        expect(CRNewTimelineEventIndexer().extract_datum(officer_allegation)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 30,
            'date': '2012-01-01',
            'kind': 'CR',
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'Search of premise/vehicle without warrant',
            'finding': 'Unfounded',
            'outcome': 'Unknown',
            'coaccused': 4,
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
            'attachments': [
                {
                    'title': 'doc_1',
                    'url': 'url_1',
                    'preview_image_url': 'image_url_1',
                },
                {
                    'title': 'doc_2',
                    'url': 'url_2',
                    'preview_image_url': 'image_url_2',
                },
            ]
        })


class AwardNewTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        award = Mock()

        with patch('officers.indexers.Award.objects.filter', return_value=[award]):
            expect(AwardNewTimelineEventIndexer().get_queryset()).to.eq([award])

    def test_extract_datum(self):
        award = Mock(
            officer_id=123,
            start_date=date(2010, 3, 4),
            award_type='Honorable Mention',
            officer=Mock(
                rank='Police Officer',
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(AwardNewTimelineEventIndexer().extract_datum(award)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 40,
            'date': '2010-03-04',
            'kind': 'AWARD',
            'award_type': 'Honorable Mention',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class TRRNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        TRRFactory(officer=None)

        expect([obj.id for obj in TRRNewTimelineEventIndexer().get_queryset()]).to.eq([trr.id])

    def test_extract_datum(self):
        trr = Mock(
            officer_id=123,
            trr_datetime=datetime(2010, 3, 4),
            firearm_used=False,
            taser=False,
            officer=Mock(
                rank='Police Officer',
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(TRRNewTimelineEventIndexer().extract_datum(trr)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 50,
            'date': '2010-03-04',
            'kind': 'FORCE',
            'taser': False,
            'firearm_used': False,
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class OfficerCoaccusalsIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficerCoaccusalsIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            coaccusals=[Mock(
                id=456,
                full_name='Officer 456',
                allegation_count=2,
                sustained_count=1,
                complaint_percentile=95.0,
                race='White',
                gender_display='Male',
                birth_year=1950,
                coaccusal_count=3,
                rank='Police Officer',
            ), Mock(
                id=789,
                full_name='Officer 789',
                allegation_count=3,
                sustained_count=2,
                complaint_percentile=99.0,
                race='Black',
                gender_display='Male',
                birth_year=1970,
                coaccusal_count=5,
                rank='Po As Detective',
            )],
        )
        expect(OfficerCoaccusalsIndexer().extract_datum(officer)).to.eq({
            'id': 123,
            'coaccusals': [{
                'id': 456,
                'full_name': 'Officer 456',
                'allegation_count': 2,
                'sustained_count': 1,
                'complaint_percentile': 95.0,
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1950,
                'coaccusal_count': 3,
                'rank': 'Police Officer',
            }, {
                'id': 789,
                'full_name': 'Officer 789',
                'allegation_count': 3,
                'sustained_count': 2,
                'complaint_percentile': 99.0,
                'race': 'Black',
                'gender': 'Male',
                'birth_year': 1970,
                'coaccusal_count': 5,
                'rank': 'Po As Detective',
            }]
        })
