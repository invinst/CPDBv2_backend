from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
from freezegun import freeze_time
import pytz

from cr.indexers import CRIndexer, CRPartialIndexer
from cr.doc_types import CRDocType
from cr.index_aliases import cr_index_alias
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, AllegationCategoryFactory,
    AreaFactory, ComplainantFactory, AttachmentFileFactory, VictimFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory
)


class CRIndexerTestCase(TestCase):
    @freeze_time('2018-04-04 12:00:01', tz_offset=0)
    def setUp(self):
        super(CRIndexerTestCase, self).setUp()
        self.maxDiff = None

    def extract_data(self):
        indexer = CRIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_emit_correct_format(self):
        allegation = AllegationFactory(
            crid='12345',
            summary='Summary',
            point=Point(12, 21),
            incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            add1='3510',
            add2='Michigan Ave',
            city='Chicago',
            location='Police Building',
            beat=AreaFactory(name='23'),
            is_officer_complaint=False
        )
        coaccused = OfficerFactory(
            id=1,
            first_name='Foo',
            last_name='Bar',
            gender='M',
            race='White',
            birth_year=1986,
            appointed_date=date(2001, 1, 1),
            rank='Officer',
            complaint_percentile=Decimal(0),
            civilian_allegation_percentile=Decimal(1.1),
            internal_allegation_percentile=Decimal(2.2),
            trr_percentile=Decimal(3.3)
        )
        OfficerAllegationFactory(
            officer=coaccused,
            allegation=allegation,
            final_finding='SU',
            recc_outcome='Separation',
            final_outcome='Reprimand',
            start_date=date(2003, 3, 28),
            end_date=date(2003, 4, 28),
            allegation_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY'
            ),
            disciplined=True
        )

        ComplainantFactory(allegation=allegation, gender='M', race='White', age=30)
        ComplainantFactory(allegation=allegation, gender='F', race='Black', age=25)
        VictimFactory(allegation=allegation, gender='F', race='Black', age=25)
        VictimFactory(allegation=allegation, gender='M', race='Hispanic', age=40)
        officer = OfficerFactory(
            id=2,
            first_name='Jerome',
            last_name='Finnigan',
            gender='M',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=4.4,
            trr_percentile=5.5
        )
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        investigator = OfficerFactory(
            id=3,
            first_name='German',
            last_name='Lauren',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=6.6,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
        )
        OfficerAllegationFactory(
            officer=investigator,
            final_finding='NS',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        investigator = InvestigatorFactory(officer=investigator)
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator,
            current_rank='IPRA investigator'
        )

        AttachmentFileFactory(
            allegation=allegation,
            file_type='document',
            title='CR document',
            url='http://foo.com/',
            preview_image_url='http://web.com/image'
        )
        indexer = CRIndexer()
        rows = list(indexer.get_queryset())
        row = [obj for obj in rows if obj['crid'] == '12345'][0]
        result = indexer.extract_datum(row)
        expect(dict(result)).to.eq({
            'crid': '12345',
            'most_common_category': {
                'category': 'Operation/Personnel Violations',
                'allegation_name': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY'
            },
            'category_names': ['Operation/Personnel Violations'],
            'coaccused': [
                {
                    'id': 1,
                    'full_name': 'Foo Bar',
                    'abbr_name': 'F. Bar',
                    'gender': 'Male',
                    'race': 'White',
                    'rank': 'Officer',
                    'final_finding': 'Sustained',
                    'recc_outcome': 'Separation',
                    'final_outcome': 'Reprimand',
                    'category': 'Operation/Personnel Violations',
                    'subcategory': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY',
                    'start_date': '2003-03-28',
                    'end_date': '2003-04-28',
                    'age': 32,
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_allegation': Decimal('0'),
                    'percentile_allegation_civilian': Decimal('1.1'),
                    'percentile_allegation_internal': Decimal('2.2'),
                    'percentile_trr': Decimal('3.3'),
                    'disciplined': True
                }
            ],
            'complainants': [
                {'gender': 'Male', 'race': 'White', 'age': 30},
                {'gender': 'Female', 'race': 'Black', 'age': 25}
            ],
            'victims': [
                {'gender': 'Female', 'race': 'Black', 'age': 25},
                {'gender': 'Male', 'race': 'Hispanic', 'age': 40}
            ],
            'summary': 'Summary',
            'point': {'lon': 12.0, 'lat': 21.0},
            'incident_date': '2002-02-28',
            'start_date': '2003-03-28',
            'end_date': '2003-04-28',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Building',
            'beat': '23',
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officer_id': 3,
                    'full_name': 'German Lauren',
                    'abbr_name': 'G. Lauren',
                    'num_cases': 1,
                    'current_rank': 'IPRA investigator',
                    'percentile_allegation': Decimal('6.6000'),
                    'percentile_allegation_civilian': Decimal('7.7000'),
                    'percentile_allegation_internal': Decimal('8.8000'),
                    'percentile_trr': None
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 2,
                    'full_name': 'Jerome Finnigan',
                    'abbr_name': 'J. Finnigan',
                    'gender': 'Male',
                    'race': 'White',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_allegation': Decimal('4.4000'),
                    'percentile_allegation_civilian': None,
                    'percentile_allegation_internal': None,
                    'percentile_trr': Decimal('5.5000')
                }
            ],
            'attachments': [
                {
                    'title': 'CR document',
                    'file_type': 'document',
                    'url': 'http://foo.com/',
                    'preview_image_url': 'http://web.com/image'
                }
            ]
        })

    def test_extract_datum_none_point(self):
        AllegationFactory(point=None)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['point']).to.be.none()

    def test_extract_datum_none_incident_date(self):
        AllegationFactory(incident_date=None)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['incident_date']).to.be.none()

    def test_extract_datum_start_date_end_date(self):
        allegation = AllegationFactory()
        OfficerAllegationFactory(
            allegation=allegation,
            start_date=date(2016, 8, 3),
            end_date=date(2017, 8, 3)
        )

        OfficerAllegationFactory(
            allegation=allegation,
            start_date=None,
            end_date=None
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['start_date']).to.eq('2016-08-03')
        expect(rows[0]['end_date']).to.eq('2017-08-03')

    def test_extract_datum_most_common_category(self):
        allegation = AllegationFactory()
        cat1 = AllegationCategoryFactory(
            category='Use Of Forces',
            allegation_name='Sub Force'
        )
        cat2 = AllegationCategoryFactory(
            category='Traffic',
            allegation_name='Sub traffic'
        )
        OfficerAllegationFactory.create_batch(
            2,
            allegation=allegation,
            allegation_category=cat1
        )

        OfficerAllegationFactory(
            allegation=allegation,
            allegation_category=cat2
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['most_common_category']).to.eq({
            'category': 'Use Of Forces',
            'allegation_name': 'Sub Force'
        })

    def test_extract_datum_none_most_common_category(self):
        AllegationFactory()
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['most_common_category']).to.be.none()

    def test_extract_datum_not_none_old_complaint_address(self):
        AllegationFactory(old_complaint_address='Old town')
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['address']).to.eq('Old town')

    def test_extract_datum_investigator_officer_name(self):
        InvestigatorAllegationFactory(
            investigator__officer=OfficerFactory(first_name='Jerome', last_name='Finnigan'),
            investigator__first_name='German',
            investigator__last_name='Lauren'
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['involvements'][0]['abbr_name']).to.eq('J. Finnigan')
        expect(rows[0]['involvements'][0]['full_name']).to.eq('Jerome Finnigan')

    def test_extract_datum_investigator_none_name(self):
        InvestigatorAllegationFactory(
            investigator__officer=None,
            investigator__first_name=None,
            investigator__last_name=None
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['involvements'][0]['abbr_name']).to.be.none()
        expect(rows[0]['involvements'][0]['full_name']).to.eq('')

    def test_extract_datum_investigator_investigator_name(self):
        InvestigatorAllegationFactory(
            investigator__officer=None,
            investigator__first_name='German',
            investigator__last_name='Lauren'
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['involvements'][0]['abbr_name']).to.eq('G. Lauren')
        expect(rows[0]['involvements'][0]['full_name']).to.eq('German Lauren')

    def test_extract_datum_victim_blank_gender(self):
        VictimFactory(gender='')

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['victims'][0]['gender']).to.be.none()

    def test_extract_beat_is_none(self):
        AllegationFactory(beat=None)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['beat']).to.be.none()

    def test_extract_coaccused_none_birth_year(self):
        OfficerAllegationFactory(
            officer__birth_year=None
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['coaccused'][0]['age']).to.be.none()

    def test_extract_investigator_multiple_cases(self):
        investigator = InvestigatorFactory(first_name='Luke', last_name='Skywalker')
        InvestigatorAllegationFactory.create_batch(3, investigator=investigator)
        rows = self.extract_data()
        expect(rows).to.have.length(3)
        for row in rows:
            expect(row['involvements']).to.have.length(1)
            expect(row['involvements'][0]['full_name']).to.eq('Luke Skywalker')

    def test_coaccused_counts(self):
        officer = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, officer=officer, final_finding='SU')
        OfficerAllegationFactory(officer=officer, final_finding='NS')
        rows = self.extract_data()
        expect(rows).to.have.length(3)
        for row in rows:
            expect(row['coaccused']).to.have.length(1)
            expect(row['coaccused'][0]['allegation_count']).to.eq(3)
            expect(row['coaccused'][0]['sustained_count']).to.eq(2)

    def test_police_witness_counts(self):
        officer = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, officer=officer, final_finding='SU')
        OfficerAllegationFactory(officer=officer, final_finding='NS')
        allegation = AllegationFactory()
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        rows = self.extract_data()
        expect(rows).to.have.length(4)
        expect(rows[-1]['involvements']).to.have.length(1)
        expect(rows[-1]['involvements'][0]['allegation_count']).to.eq(3)
        expect(rows[-1]['involvements'][0]['sustained_count']).to.eq(2)

    def test_investigator_num_cases(self):
        investigator = InvestigatorFactory()
        InvestigatorAllegationFactory.create_batch(3, investigator=investigator)
        allegation = AllegationFactory()
        InvestigatorAllegationFactory(investigator=investigator, allegation=allegation)
        rows = self.extract_data()
        expect(rows).to.have.length(4)
        expect(rows[-1]['involvements']).to.have.length(1)
        expect(rows[-1]['involvements'][0]['num_cases']).to.eq(4)


class CRPartialIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AllegationFactory(crid='123')
        AllegationFactory(crid='456')
        AllegationFactory(crid='789')

        indexer = CRPartialIndexer(updating_keys=['123', '456'])
        result = indexer.get_queryset()
        crids = [cr['crid'] for cr in result]
        expect(set(crids)).to.eq({
            '123',
            '456',
        })

    def test_get_batch_querysets(self):
        AllegationFactory(crid='123')
        AllegationFactory(crid='456')
        AllegationFactory(crid='789')

        result = CRPartialIndexer().get_batch_queryset(keys=['123', '456'])
        crids = [cr['crid'] for cr in result]
        expect(set(crids)).to.eq({
            '123',
            '456',
        })

    def test_get_batch_update_docs_queries(self):
        CRDocType(meta={'id': '1'}, **{
            'crid': '123456',
            'address': '30XX E NEW YORK ST , AURORA IL',
            'attachments': [],
            'beat': '3100',
            'category_names': [],
        }).save()

        CRDocType(meta={'id': '2'}, **{
            'crid': '789',
            'address': '30XX E NEW YORK ST , AURORA IL',
            'attachments': [],
            'beat': '3100',
            'category_names': [],
        }).save()

        CRDocType(meta={'id': '3'}, **{
            'crid': '789123',
            'address': 'AURORA IL',
            'attachments': [],
            'beat': '300',
            'category_names': [],
        }).save()
        cr_index_alias.read_index.refresh()

        update_docs_queries = CRPartialIndexer().get_batch_update_docs_queries(keys=['123456', '789', '432'])

        expect(set(update_docs_query.crid for update_docs_query in update_docs_queries)).to.eq({
            '123456', '789',
        })

    def test_extra_data_populated(self):
        allegation = AllegationFactory(id=1122)
        OfficerAllegationFactory(allegation=allegation)
        InvestigatorAllegationFactory(allegation=allegation)
        PoliceWitnessFactory(allegation=allegation)
        indexer = CRPartialIndexer(updating_keys=['123', '456'])
        expect(indexer.coaccused_dict[1122]).to.have.length(1)
        expect(indexer.investigator_dict[1122]).to.have.length(1)
        expect(indexer.policewitness_dict[1122]).to.have.length(1)
