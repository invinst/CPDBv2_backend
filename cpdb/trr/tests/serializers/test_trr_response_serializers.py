from datetime import datetime

import pytz
from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from trr.serializers.trr_response_serializers import TRRSerializer
from trr.factories import TRRFactory


class TRRSerializerTestCase(TestCase):
    def test_get_subject_gender(self):
        trr = TRRFactory(subject_gender='M')

        result = TRRSerializer(trr).data
        expect(result['subject_gender']).to.eq('Male')

    def test_get_subject_gender_other_gender(self):
        trr = TRRFactory(subject_gender='A')

        result = TRRSerializer(trr).data
        expect(result['subject_gender']).to.eq('A')

    def test_get_address(self):
        trr = TRRFactory(block='34XX', street='Douglas Blvd')
        result = TRRSerializer(trr).data
        expect(result['address']).to.eq('34XX Douglas Blvd')

    def test_get_address_missing_data(self):
        trr_no_street = TRRFactory(block='34XX')
        trr_no_block = TRRFactory(block=None, street='Douglas Blvd')
        trr_no_address = TRRFactory()

        expect(TRRSerializer(trr_no_street).data['address']).to.eq('34XX')
        expect(TRRSerializer(trr_no_block).data['address']).to.eq('Douglas Blvd')
        expect(TRRSerializer(trr_no_address).data['address']).to.eq('')

    def test_get_date_of_incident(self):
        trr = TRRFactory(trr_datetime=datetime(2012, 1, 23, tzinfo=pytz.utc))
        expect(TRRSerializer(trr).data['date_of_incident']).to.eq('2012-01-23')

    def test_get_point(self):
        trr = TRRFactory(point=None)
        result = TRRSerializer(trr).data
        expect(result.get('point')).to.be.none()

        trr = TRRFactory(point=Point(1.0, 1.0))
        result = TRRSerializer(trr).data
        expect(result['point']).to.eq({'lng': 1.0, 'lat': 1.0})
