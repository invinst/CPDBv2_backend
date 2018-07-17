from datetime import date, datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
from freezegun import freeze_time
import pytz

from cr.indexers import CRIndexer
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, AllegationCategoryFactory,
    AreaFactory, ComplainantFactory, AttachmentFileFactory, VictimFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory
)
from data.tests.officer_percentile_utils import mock_percentile_map_range


class CRIndexerTestCase(TestCase):
    @freeze_time('2018-04-04 12:00:01', tz_offset=0)
    def setUp(self):
        super(CRIndexerTestCase, self).setUp()
        self.maxDiff = None

    def test_query_set(self):
        allegation = AllegationFactory()
        expect(list(CRIndexer().get_queryset())).to.eq([allegation])

    @mock_percentile_map_range(
        allegation_min=datetime(2002, 2, 28, tzinfo=pytz.utc),
        allegation_max=datetime(2003, 4, 28, tzinfo=pytz.utc),
        internal_civilian_min=datetime(2002, 2, 28, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2003, 4, 28, tzinfo=pytz.utc),
        trr_min=datetime(2002, 2, 28, tzinfo=pytz.utc),
        trr_max=datetime(2003, 4, 28, tzinfo=pytz.utc)
    )
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
            rank='Officer'
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
            )
        )

        ComplainantFactory(allegation=allegation, gender='M', race='White', age=30)
        VictimFactory(allegation=allegation, gender='F', race='Black', age=25)
        officer = OfficerFactory(
            id=2,
            first_name='Jerome',
            last_name='Finnigan',
            gender='M',
            appointed_date=date(2001, 5, 1))
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
            appointed_date=date(2001, 5, 1)
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
                    'percentile_allegation': 0,
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0
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
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0,
                    'percentile_allegation': 0
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
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0,
                    'percentile_allegation': 0
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

    def test_extract_datum_ignore_officers_not_in_top_percentile(self):
        indexer = CRIndexer()
        allegation = AllegationFactory()
        OfficerAllegationFactory(allegation=allegation)
        InvestigatorAllegationFactory(allegation=allegation)
        result = indexer.extract_datum(allegation)
        expect(result['coaccused'][0]).to.exclude(
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr',
            'percentile_allegation'
        )
        expect(result['involvements'][0]).to.exclude(
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr',
            'percentile_allegation'
        )
