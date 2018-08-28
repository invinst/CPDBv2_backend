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
        OfficerAllegationFactory.create_batch(
            2,
            allegation=allegation,
            allegation_category__category='Use Of Forces',
            allegation_category__allegation_name='Sub Force'
        )

        OfficerAllegationFactory(
            allegation=allegation,
            allegation_category__category='Traffic',
            allegation_category__allegation_name='Sub traffic'
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
