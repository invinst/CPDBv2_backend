from datetime import date, datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from cr.indexers import CRIndexer, CRPartialIndexer
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, AllegationCategoryFactory,
    AreaFactory, ComplainantFactory, AttachmentFileFactory, VictimFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory
)
from cr.doc_types import CRDocType
from cr.index_aliases import cr_index_alias


class CRIndexerTestCase(TestCase):
    def test_query_set(self):
        allegation = AllegationFactory()
        expect(list(CRIndexer().get_queryset())).to.eq([allegation])

    def test_passed_query_set(self):
        allegation_1 = AllegationFactory()
        allegation_2 = AllegationFactory()

        expect(
            set(CRIndexer().get_queryset())
        ).to.eq({allegation_1, allegation_2})

    def test_extract_datum(self):
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
            complaint_percentile=0.0,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3
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
        VictimFactory(allegation=allegation, gender='F', race='Black', age=25)
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

        result = CRIndexer().extract_datum(allegation)
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
                    'percentile_allegation': 0.0,
                    'percentile_allegation_civilian': 1.1,
                    'percentile_allegation_internal': 2.2,
                    'percentile_trr': 3.3,
                    'disciplined': True
                }
            ],
            'complainants': [{'gender': 'Male', 'race': 'White', 'age': 30}],
            'victims': [{'gender': 'Female', 'race': 'Black', 'age': 25}],
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
                    'percentile_allegation': 6.6,
                    'percentile_allegation_civilian': 7.7,
                    'percentile_allegation_internal': 8.8,
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
                    'percentile_allegation': 4.4,
                    'percentile_allegation_civilian': None,
                    'percentile_allegation_internal': None,
                    'percentile_trr': 5.5
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


class CRPartialIndexerTestCase(TestCase):
    def test_get_queryset(self):
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        AllegationFactory(crid='789')

        indexer = CRPartialIndexer(updating_keys=['123', '456'])
        expect(set(indexer.get_queryset())).to.eq({
            allegation_1,
            allegation_2,
        })

    def test_get_batch_querysets(self):
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        AllegationFactory(crid='789')

        expect(set(CRPartialIndexer().get_batch_querysets(keys=['123', '456']))).to.eq({
            allegation_1,
            allegation_2,
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
