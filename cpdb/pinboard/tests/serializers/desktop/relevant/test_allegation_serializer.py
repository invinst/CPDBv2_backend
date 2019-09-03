from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

import pytz
from robber import expect

from pinboard.serializers.desktop.relevant.allegation_serializer import AllegationSerializer
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    VictimFactory,
)
from pinboard.factories import PinboardFactory


class AllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        pinned_officer = OfficerFactory(
            id=1,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            allegation_count=2,
        )

        relevant_allegation = AllegationFactory(
            crid='1',
            incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc),
            most_common_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='Subcategory'
            ),
            point=Point([0.01, 0.02])
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=relevant_allegation
        )
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        OfficerAllegationFactory(officer=pinned_officer, allegation=relevant_allegation)

        expect(pinboard.relevant_complaints.count()).to.eq(1)
        expect(AllegationSerializer(pinboard.relevant_complaints.first()).data).to.eq({
            'crid': '1',
            'address': '',
            'category': 'Operation/Personnel Violations',
            'incident_date': '2002-02-21',
            'victims': [{
                'gender': 'Male',
                'race': 'Black',
                'age': 35
            }],
            'point': {
                'lon': 0.01,
                'lat': 0.02
            },
            'to': '/complaint/1/',
            'sub_category': 'Subcategory',
            'coaccused': [{
                'id': 1,
                'rank': 'Police Officer',
                'full_name': 'Jerome Finnigan',
                'coaccusal_count': None,
                'percentile': {
                    'percentile_trr': '11.1100',
                    'percentile_allegation_civilian': '33.3300',
                    'percentile_allegation_internal': '44.4400',
                    'percentile_allegation': '22.2200', 'year': 2016,
                },
                'allegation_count': 2,
            }],
        })
