from datetime import date, datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz
from freezegun import freeze_time

from cr.indexers import CRIndexer
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, AllegationCategoryFactory,
    AreaFactory, ComplainantFactory, InvolvementFactory, AttachmentFileFactory, VictimFactory,
    OfficerBadgeNumberFactory
)


class CRIndexerTestCase(TestCase):
    @freeze_time('2018-04-04 12:00:01', tz_offset=0)
    def setUp(self):
        super(CRIndexerTestCase, self).setUp()
        self.maxDiff = None

    def test_query_set(self):
        allegation = AllegationFactory()
        expect(list(CRIndexer().get_queryset())).to.eq([allegation])

    def test_extract_datum(self):
        allegation = AllegationFactory(
            crid='12345',
            summary='Summary',
            point=Point(12, 21),
            incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            add1='3510',
            add2='Michigan Ave',
            city='Chicago',
            location='04',
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
            appointed_date=date(2001, 1, 1)
        )

        OfficerAllegationFactory(
            officer=coaccused,
            allegation=allegation,
            final_finding='SU',
            final_outcome='100',
            start_date=date(2003, 2, 28),
            end_date=date(2004, 4, 28),
            allegation_category=AllegationCategoryFactory(category='Operation/Personnel Violations')
        )

        ComplainantFactory(allegation=allegation, gender='M', race='White', age=30)
        VictimFactory(allegation=allegation, gender='F', race='Black', age=25)
        investigator = OfficerFactory(id=2, first_name='Jerome', last_name='Finnigan', appointed_date=date(2001, 5, 1))
        InvolvementFactory(
            allegation=allegation,
            involved_type='investigator',
            officer=investigator
        )

        OfficerBadgeNumberFactory(officer=investigator, current=True, star=11111)
        AttachmentFileFactory(
            allegation=allegation,
            file_type='document',
            title='CR document',
            url='http://foo.com/',
            preview_image_url='http://web.com/image'
        )

        result = CRIndexer().extract_datum(allegation)
        expect(result).to.eq({
            'crid': '12345',
            'category_names': ['Operation/Personnel Violations'],
            'coaccused': [
                {
                    'id': 1,
                    'full_name': 'Foo Bar',
                    'gender': 'Male',
                    'race': 'White',
                    'final_outcome': 'Reprimand',
                    'category': 'Operation/Personnel Violations',
                    'age': 32,
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_allegation': 50.0,
                    'percentile_allegation_civilian': 50.0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0
                }
            ],
            'complainants': [{'gender': 'Male', 'race': 'White', 'age': 30}],
            'victims': [{'gender': 'Female', 'race': 'Black', 'age': 25}],
            'summary': 'Summary',
            'point': {'lon': 12.0, 'lat': 21.0},
            'incident_date': '2002-02-28',
            'start_date': '2003-02-28',
            'end_date': '2004-04-28',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Building',
            'beat': '23',
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officers': [{'id': 2, 'abbr_name': 'J. Finnigan', 'extra_info': 'Badge 11111'}]
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
