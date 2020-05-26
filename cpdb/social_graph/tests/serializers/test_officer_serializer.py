from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from social_graph.serializers import OfficerSerializer


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            complaint_percentile=1.1,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )

        expect(OfficerSerializer(officer).data).to.eq({
            'id': 8562,
            'full_name': 'Jerome Finnigan',
            'percentile_allegation': '1.1000',
            'percentile_allegation_civilian': '1.1000',
            'percentile_allegation_internal': '2.2000',
            'percentile_trr': '3.3000'
        })
