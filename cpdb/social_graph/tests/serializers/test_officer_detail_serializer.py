from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from social_graph.serializers.officer_detail_serializer import OfficerDetailSerializer


class OfficerDetailSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            rank='Police Officer',
            current_badge='123',
            race='White',
            birth_year='1972',
            gender='M',
            allegation_count=1,
            sustained_count=1,
            honorable_mention_count=1,
            major_award_count=1,
            trr_count=1,
            discipline_count=1,
            civilian_compliment_count=1,
            appointed_date='1976-06-10',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )

        expect(OfficerDetailSerializer(officer).data).to.eq({
            'id': 8562,
            'full_name': 'Jerome Finnigan',
            'rank': 'Police Officer',
            'badge': '123',
            'race': 'White',
            'birth_year': '1972',
            'gender': 'M',
            'allegation_count': 1,
            'sustained_count': 1,
            'honorable_mention_count': 1,
            'major_award_count': 1,
            'trr_count': 1,
            'discipline_count': 1,
            'civilian_compliment_count': 1,
            'appointed_date': '1976-06-10',
            'percentile': {
                'percentile_allegation_civilian': '1.1000',
                'percentile_allegation_internal': '2.2000',
                'percentile_trr': '3.3000',
            }
        })
