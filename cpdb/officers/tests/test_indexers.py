from datetime import date, datetime

from django.contrib.gis.geos import Point
from django.test import SimpleTestCase
from django.test.testcases import TestCase

from mock import Mock, patch
from robber import expect
import pytz

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, OfficerHistoryFactory, AttachmentFileFactory,
    AllegationCategoryFactory, VictimFactory, AwardFactory,
    SalaryFactory,
)
from officers.tests.utils import validate_object, create_object
from officers.indexers import (
    OfficersIndexer,
    OfficerPercentileIndexer,
    CRNewTimelineEventIndexer,
    CRNewTimelineEventPartialIndexer,
    UnitChangeNewTimelineEventIndexer,
    JoinedNewTimelineEventIndexer,
    TRRNewTimelineEventIndexer,
    AwardNewTimelineEventIndexer,
    OfficerCoaccusalsIndexer,
    RankChangeNewTimelineEventIndexer,
)
from officers.serializers.doc_serializers import OfficerMetricsSerializer
from trr.factories import TRRFactory
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias


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
            'honorable_mention_percentile': 98.000,
            'unsustained_count': 24,
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
            'honorable_mention_percentile': 98.000,
            'unsustained_count': 24,
        })


class OfficersIndexerTestCase(SimpleTestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficersIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = create_object({
            'v2_to': '',
            'v1_url': '',
            'tags': [],
            'id': 123,
            'full_name': 'Alex Mack',
            'last_unit': Mock(id=1, unit_name='4', description=''),
            'rank': '5',
            'race': 'White',
            'current_badge': '123456',
            'historic_badges': ['123', '456'],
            'historic_units': [
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
            'gender_display': 'Male',
            'birth_year': 1910,
            'has_visual_token': False,
            'appointed_date': date(2017, 2, 27),
            'resignation_date': date(2017, 12, 27),
            'get_active_display': Mock(return_value='Active'),
            'allegation_count': 2,
            'complaint_percentile': 99.8,
            'honorable_mention_count': 1,
            'sustained_count': 1,
            'unsustained_count': 2,
            'discipline_count': 1,
            'civilian_compliment_count': 0,
            'percentiles': [],
            'coaccusals': [{
                'id': 1,
                'coaccusal_count': 5
            }],
            'current_salary': 9000,
            'honorable_mention_percentile': 98,
            'total_complaints_aggregation': [{'year': 2000, 'count': 1, 'sustained_count': 0}],
            'trr_count': 1,
            'major_award_count': 9,
        })

        expected_result = {
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': {
                'id': 1,
                'unit_name': '4',
                'description': '',
                'long_unit_name': 'Unit 4',
            },
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['123', '456'],
            'historic_units': [
                {
                    'id': 1,
                    'unit_name': '1',
                    'description': 'Unit 001',
                    'long_unit_name': 'Unit 1',
                }, {
                    'id': 2,
                    'unit_name': '2',
                    'description': 'Unit 002',
                    'long_unit_name': 'Unit 2',
                }
            ],
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'birth_year': 1910,
            'allegation_count': 2,
            'complaint_percentile': 99.8,
            'honorable_mention_count': 1,
            'honorable_mention_percentile': 98,
            'has_visual_token': False,
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
            'unsustained_count': 2,
            'coaccusals': [{
                'id': 1,
                'coaccusal_count': 5,
            }],
        }
        expect(OfficersIndexer().extract_datum(officer)).to.eq(expected_result)


class OfficerPercentileIndexerTestCase(TestCase):

    @patch('django.conf.settings.ALLEGATION_MIN', '1988-01-01')
    @patch('django.conf.settings.ALLEGATION_MAX', '2016-07-01')
    @patch('django.conf.settings.INTERNAL_CIVILIAN_ALLEGATION_MIN', '2000-01-01')
    @patch('django.conf.settings.INTERNAL_CIVILIAN_ALLEGATION_MAX', '2016-07-01')
    @patch('django.conf.settings.TRR_MIN', '2004-01-08')
    @patch('django.conf.settings.TRR_MAX', '2016-04-12')
    def setUp(self):
        self.indexer = OfficerPercentileIndexer()

    def test_get_queryset_no_allegation(self):
        expect(self.indexer.get_queryset()).to.be.empty()

    def _prepare_data_up_to_2017(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
        officer2 = OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2014, 3, 1), resignation_date=date(2015, 4, 14))

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
            2,
            officer=officer2,
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
        OfficerAllegationFactory(
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2017, 3, 15, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        TRRFactory(
            officer=officer1,
            trr_datetime=datetime(2017, 3, 15, tzinfo=pytz.utc),
        )
        TRRFactory(
            officer=officer1,
            trr_datetime=datetime(2016, 3, 15, tzinfo=pytz.utc),
        )

    def validate_object(self, obj, data):
        for key, value in data.iteritems():
            expect(getattr(obj, key, None)).to.eq(value)

    def test_get_queryset(self):
        self._prepare_data_up_to_2017()
        # expect officer 2 not have year 2017 since less than 1 year
        # expect no year 2017, since dataset only up to 2016
        queryset = self.indexer.get_queryset()
        expect(queryset).to.have.length(5)
        validate_object(queryset[0], {
            'officer_id': 1,
            'year': 2014,
            'metric_allegation': 0.0,
            'metric_allegation_civilian': 0.0,
            'metric_allegation_internal': 0.0,
            'metric_trr': 0.0,
            'percentile_allegation': 0.0,
            'percentile_allegation_civilian': 0.0,
            'percentile_allegation_internal': 0.0,
            'percentile_trr': 0.0,
        })
        validate_object(queryset[1], {
            'officer_id': 1,
            'year': 2015,
            'metric_allegation': 0.6673,
            'metric_allegation_civilian': 0.6673,
            'metric_allegation_internal': 0.0,
            'metric_trr': 0.0,
            'percentile_allegation': 50.0,
            'percentile_allegation_civilian': 50.0,
            'percentile_allegation_internal': 0.0,
            'percentile_trr': 0.0,
        })
        validate_object(queryset[2], {
            'officer_id': 3,
            'year': 2015,
            'metric_allegation': 0.0,
            'metric_allegation_civilian': 0.0,
            'metric_allegation_internal': 0.0,
            'metric_trr': 0.0,
            'percentile_allegation': 0.0,
            'percentile_allegation_civilian': 0.0,
            'percentile_allegation_internal': 0.0,
            'percentile_trr': 0.0,
        })
        validate_object(queryset[3], {
            'officer_id': 1,
            'year': 2016,
            'metric_allegation': 0.8575,
            'metric_allegation_civilian': 0.8575,
            'metric_allegation_internal': 0.0,
            'metric_trr': 0.3049,
            'percentile_allegation': 33.3333,
            'percentile_allegation_civilian': 33.3333,
            'percentile_allegation_internal': 0.0,
            'percentile_trr': 66.6667,
        })
        validate_object(queryset[4], {
            'officer_id': 2,
            'year': 2016,
            'metric_allegation': 2.3052,
            'metric_allegation_civilian': 1.5368,
            'metric_allegation_internal': 0.7684,
            'metric_trr': 0.0,
            'percentile_allegation': 66.6667,
            'percentile_allegation_civilian': 66.6667,
            'percentile_allegation_internal': 66.6667,
            'percentile_trr': 0.0,
        })

    def test_extract_datum(self):
        data = {
            'year': 2016,
            'id': 1,
            'service_year': 2.2,
            'metric_trr': 0.0,
            'metric_allegation': 0.0,
            'metric_allegation_internal': 0.0,
            'metric_allegation_civilian': 0.0,
            'percentile_allegation': 66.6667,
            'percentile_allegation_internal': 50,
            'percentile_trr': 0.0,
            'percentile_allegation_civilian': 0.0
        }
        expect(self.indexer.extract_datum(data)).to.eq({
            'id': 1,
            'year': 2016,
            'percentile_allegation': '66.6667',
            'percentile_allegation_internal': '50.0000',
            'percentile_allegation_civilian': '0.0000',
            'percentile_trr': '0.0000',
        })

    def test_extract_datum_missing_percentile(self):
        data = {
            'year': 2016,
            'id': 1,
            'service_year': 2.2,
            'metric_allegation': 0,
            'metric_allegation_internal': 0,
            'metric_allegation_civilian': 0,
            'percentile_allegation': 66.6667,
            'percentile_allegation_internal': 50,
            'percentile_allegation_civilian': 0
        }
        expect(self.indexer.extract_datum(data)).to.eq({
            'id': 1,
            'year': 2016,
            'percentile_allegation': '66.6667',
            'percentile_allegation_internal': '50.0000',
            'percentile_allegation_civilian': '0.0000',
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
            get_rank_by_date=Mock(return_value='Police Officer'),
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
            officer=Mock(get_rank_by_date=Mock(return_value='Police Officer'))
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
            point=Point(35.5, 68.9),
            coaccused_count=4
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
            final_outcome='Unknown'
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        VictimFactory(allegation=allegation, gender='M', race='White', age=34)
        SalaryFactory(officer=officer, rank='Police Officer', spp_date=date(2012, 1, 1))

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
            'victims': [
                {
                    'race': 'White',
                    'age': 34,
                    'gender': 'Male',
                }
            ],
            'point': {
                'lon': 35.5,
                'lat': 68.9
            },
            'attachments': [
                {
                    'title': 'doc_1',
                    'url': 'url_1',
                    'preview_image_url': 'image_url_1',
                    'file_type': 'document',
                },
                {
                    'title': 'doc_2',
                    'url': 'url_2',
                    'preview_image_url': 'image_url_2',
                    'file_type': 'document',
                },
            ]
        })


class CRNewTimelineEventPartialIndexerTestCase(TestCase):
    def test_get_queryset(self):
        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        officer_allegation_1 = OfficerAllegationFactory(allegation=allegation_123)
        officer_allegation_2 = OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        indexer = CRNewTimelineEventPartialIndexer(updating_keys=['123'])
        expect(set(indexer.get_queryset())).to.eq({
            officer_allegation_1,
            officer_allegation_2,
        })

    def test_get_batch_querysets(self):
        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        officer_allegation_1 = OfficerAllegationFactory(allegation=allegation_123)
        officer_allegation_2 = OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        expect(set(CRNewTimelineEventPartialIndexer().get_batch_querysets(keys=['123']))).to.eq({
            officer_allegation_1,
            officer_allegation_2,
        })

    def test_get_batch_update_docs_queries(self):
        OfficerNewTimelineEventDocType(meta={'id': '1'}, **{
            'crid': '123456',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '2'}, **{
            'crid': '789',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '3'}, **{
            'crid': '789123',
            'kind': 'CR',
        }).save()
        officers_index_alias.read_index.refresh()

        update_docs_queries = CRNewTimelineEventPartialIndexer().get_batch_update_docs_queries(
            keys=['123456', '789', '432']
        )

        expect(set(update_docs_query.crid for update_docs_query in update_docs_queries)).to.eq({
            '123456', '789',
        })


class AwardNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AwardFactory(award_type='Honorable Mention')
        AwardFactory(award_type='Honorable Mention Ribbon Award')
        AwardFactory(award_type="Superintendent'S Honorable Mention")
        AwardFactory(award_type='Special Honorable Mention')
        AwardFactory(award_type='Complimentary Letter')
        AwardFactory(award_type='Department Commendation')
        award1 = AwardFactory(award_type='Life Saving Award')
        award2 = AwardFactory(award_type='Award Of Appreciation')
        award3 = AwardFactory(award_type='Problem Solving Award')
        expect(set([
            obj.pk for obj in AwardNewTimelineEventIndexer().get_queryset()
        ])).to.eq(set([award1.id, award2.id, award3.id]))

    def test_extract_datum(self):
        award = Mock(
            officer_id=123,
            start_date=date(2010, 3, 4),
            award_type='Honorable Mention',
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
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
            id=2,
            officer_id=123,
            trr_datetime=datetime(2010, 3, 4),
            firearm_used=False,
            taser=False,
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
            point=Mock(
                x=34.5,
                y=67.8
            ),
        )

        expect(TRRNewTimelineEventIndexer().extract_datum(trr)).to.eq({
            'trr_id': 2,
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
            'point': {
                'lat': 67.8,
                'lon': 34.5
            },
        })


class OfficerCoaccusalsIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer = OfficerFactory()
        expect(list(OfficerCoaccusalsIndexer().get_queryset())).to.eq([officer])

    def test_extract_datum(self):
        officer1 = OfficerFactory(
            appointed_date=date(2001, 1, 1),
            allegation_count=1,
            sustained_count=0,
            unsustained_count=1
        )
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='456',
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
            appointed_date=date(2002, 1, 1),
            civilian_allegation_percentile=11.1111,
            internal_allegation_percentile=22.2222,
            trr_percentile=33.3333,
            complaint_percentile=44.4444,
            allegation_count=2,
            sustained_count=1,
            unsustained_count=1
        )
        officer3 = OfficerFactory(
            first_name='Officer',
            last_name='789',
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Po As Detective',
            appointed_date=date(2003, 1, 1),
            civilian_allegation_percentile=55.5555,
            internal_allegation_percentile=66.6666,
            trr_percentile=77.7777,
            complaint_percentile=88.8888,
            allegation_count=3,
            sustained_count=1,
            unsustained_count=2
        )

        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc))
        allegation4 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))

        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation3, final_finding='NS', start_date=date(2005, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )

        expect(dict(OfficerCoaccusalsIndexer().extract_datum(officer1))).to.eq({
            'id': officer1.id,
            'coaccusals': [{
                'id': officer2.id,
                'full_name': 'Officer 456',
                'allegation_count': 2,
                'sustained_count': 1,
                'complaint_percentile': 44.4444,
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1950,
                'coaccusal_count': 1,
                'rank': 'Police Officer',
                'percentile_allegation_civilian': 11.1111,
                'percentile_allegation_internal': 22.2222,
                'percentile_trr': 33.3333,
            }, {
                'id': officer3.id,
                'full_name': 'Officer 789',
                'allegation_count': 3,
                'sustained_count': 1,
                'complaint_percentile': 88.8888,
                'race': 'Black',
                'gender': 'Male',
                'birth_year': 1970,
                'coaccusal_count': 1,
                'rank': 'Po As Detective',
                'percentile_allegation_civilian': 55.5555,
                'percentile_allegation_internal': 66.6666,
                'percentile_trr': 77.7777,
            }]
        })


class RankChangeNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        salary1 = SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary2 = SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary3 = SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary4 = SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(RankChangeNewTimelineEventIndexer().get_queryset()).to.eq([salary1, salary2, salary3, salary4])

    def test_extract_datum(self):
        salary = Mock(
            officer_id=123,
            spp_date=date(2005, 1, 1),
            salary=10000,
            year=2015,
            rank='Police Officer',
            start_date=date(2010, 3, 4),
            officer=Mock(
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(RankChangeNewTimelineEventIndexer().extract_datum(salary)).to.eq({
            'officer_id': 123,
            'date_sort': date(2005, 1, 1),
            'priority_sort': 25,
            'date': '2005-01-01',
            'kind': 'RANK_CHANGE',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })
