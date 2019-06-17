from datetime import date

from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, PoliceUnitFactory

from pinboard.serializers.desktop.pinned import PinnedOfficerSerializer


class PinnedOfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004',
        )

        officer = OfficerFactory(
            id=123,
            first_name='Michael',
            last_name='Flynn',
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            birth_year=1950,
            race='Black',
            rank='Sergeant',
            complaint_percentile='99.9900',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            allegation_count=20,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            last_unit=unit,
        )
        serializer = PinnedOfficerSerializer(officer)
        expect(serializer.data).to.eq({
            'id': 123,
            'full_name': 'Michael Flynn',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/123/michael-flynn/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Sergeant',
            'percentile': {
                'year': 2010,
                'percentile_trr': '3.3000',
                'percentile_allegation': '99.9900',
                'percentile_allegation_civilian': '1.1000',
                'percentile_allegation_internal': '2.2000'
            },
            'allegation_count': 20,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': 88.88,
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004',
            },
        })
