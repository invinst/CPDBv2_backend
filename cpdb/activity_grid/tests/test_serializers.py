from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from activity_grid.serializers import OfficerCardSerializer


class ActivityCardSerializerTestCase(SimpleTestCase):
    def test_serialize_officer_card(self):
        obj = Mock(
            full_name='ABC',
            id=10,
            complaint_count_metric=2,
            sustained_count_metric=1,
            birth_year=1950,
            race='Asian',
            complaint_percentile=99.0,
            gender_display='Male',
            percentile={
                'officer_id': 1,
                'year': 2016,
                'percentile_trr': '0.000',
                'percentile_allegation': '0.088',
                'percentile_allegation_civilian': '77.000',
                'percentile_allegation_internal': '0.020'
            }
        )

        expect(OfficerCardSerializer(obj).data).to.eq({
            'full_name': 'ABC',
            'id': 10,
            'complaint_count': 2,
            'sustained_count': 1,
            'birth_year': 1950,
            'race': 'Asian',
            'gender': 'Male',
            'percentile': {
                'officer_id': 1,
                'year': 2016,
                'percentile_trr': '0.000',
                'percentile_allegation': '0.088',
                'percentile_allegation_civilian': '77.000',
                'percentile_allegation_internal': '0.020'
            }
        })
