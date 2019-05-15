from datetime import datetime

from django.test import TestCase

import pytz
from robber import expect

from activity_grid.factories import ActivityCardFactory, ActivityPairCardFactory
from activity_grid.serializers import OfficerCardSerializer, SimpleCardSerializer, PairCardSerializer
from data.factories import OfficerFactory


class ActivityCardSerializerTestCase(TestCase):
    def test_serialize_officer_card(self):
        officer = OfficerFactory(
            id=123,
            first_name='Alex',
            last_name='Mack',
            race='White',
            gender='M',
            birth_year=1910,
            allegation_count=2,
            honorable_mention_count=1,
            sustained_count=1,
            discipline_count=1,
            civilian_compliment_count=0,
            complaint_percentile='0.088',
            rank='Police Officer',
            civilian_allegation_percentile='77.000',
            internal_allegation_percentile='0.020',
            trr_percentile='0.000'
        )

        activity_card = ActivityCardFactory(
            officer=officer,
            important=True,
            last_activity=datetime(2002, 2, 28, tzinfo=pytz.utc)
        )
        setattr(activity_card, 'null_position', 2)

        expect(OfficerCardSerializer(activity_card).data).to.eq({
            'id': 123,
            'full_name': 'Alex Mack',
            'race': 'White',
            'gender': 'Male',
            'birth_year': 1910,
            'complaint_count': 2,
            'complaint_percentile': 0.088,
            'sustained_count': 1,
            'rank': 'Police Officer',
            'percentile': {
                'percentile_trr': '0.0000',
                'percentile_allegation_civilian': '77.0000',
                'percentile_allegation_internal': '0.0200',
                'percentile_allegation': '0.0880',
                'year': 2016,
            },
            'important': True,
            'null_position': 2,
            'last_activity': '2002-02-27T18:00:00-06:00',
            'kind': 'single_officer'
        })


class SimpleCardSerializerTestCase(TestCase):
    def test_serialize_simple_card(self):
        officer = OfficerFactory(
            id=123,
            first_name='Alex',
            last_name='Mack',
            race='White',
            gender='M',
            birth_year=1910,
            allegation_count=2,
            honorable_mention_count=1,
            sustained_count=1,
            discipline_count=1,
            civilian_compliment_count=0,
            rank='Police Officer',
            civilian_allegation_percentile='77.000',
            internal_allegation_percentile='0.020',
            trr_percentile='0.000',
            complaint_percentile='0.2300',
        )

        expect(SimpleCardSerializer(officer).data).to.eq({
            'id': 123,
            'full_name': 'Alex Mack',
            'race': 'White',
            'gender': 'Male',
            'birth_year': 1910,
            'rank': 'Police Officer',
            'percentile': {
                'percentile_trr': '0.0000',
                'percentile_allegation_civilian': '77.0000',
                'percentile_allegation_internal': '0.0200',
                'percentile_allegation': '0.2300',
                'year': 2016,
            }
        })


class PairCardSerializerTestCase(TestCase):
    def test_serialize_pair_card(self):
        officer1 = OfficerFactory(
            id=1,
            first_name='Alex',
            last_name='Mack',
            race='White',
            gender='M',
            birth_year=1910,
            allegation_count=2,
            honorable_mention_count=1,
            sustained_count=1,
            discipline_count=1,
            civilian_compliment_count=0,
            rank='Police Officer',
            civilian_allegation_percentile='77.0000',
            internal_allegation_percentile='0.0200',
            trr_percentile='0.0000',
            complaint_percentile='38.7000',
        )
        officer2 = OfficerFactory(
            id=2,
            first_name='German',
            last_name='Mack',
            race='Black',
            gender='F',
            birth_year=1940,
            allegation_count=3,
            honorable_mention_count=1,
            sustained_count=2,
            discipline_count=1,
            civilian_compliment_count=1,
            rank='Officer',
            civilian_allegation_percentile='77.222',
            internal_allegation_percentile='4.020',
            trr_percentile='5.000',
            complaint_percentile='15.6000',
        )
        pair_card = ActivityPairCardFactory(
            officer1=officer1,
            officer2=officer2,
            important=False,
            last_activity=None,
            coaccusal_count=3
        )
        setattr(pair_card, 'null_position', 0)

        expect(PairCardSerializer(pair_card).data).to.eq({
            'officer1': {
                'id': 1,
                'full_name': 'Alex Mack',
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1910,
                'rank': 'Police Officer',
                'percentile': {
                    'percentile_trr': '0.0000',
                    'percentile_allegation_civilian': '77.0000',
                    'percentile_allegation_internal': '0.0200',
                    'percentile_allegation': '38.7000',
                    'year': 2016,
                }
            },
            'officer2': {
                'id': 2,
                'full_name': 'German Mack',
                'race': 'Black',
                'gender': 'Female',
                'birth_year': 1940,
                'rank': 'Officer',
                'percentile': {
                    'percentile_trr': '5.0000',
                    'percentile_allegation_civilian': '77.2220',
                    'percentile_allegation_internal': '4.0200',
                    'percentile_allegation': '15.6000',
                    'year': 2016,
                }
            },
            'important': False,
            'null_position': 0,
            'last_activity': None,
            'coaccusal_count': 3,
            'kind': 'coaccused_pair'
        })
