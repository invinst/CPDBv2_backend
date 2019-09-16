from datetime import date

from django.test import TestCase

from robber import expect

from pinboard.serializers.mobile.relevant.officer_serializer import OfficerMobileSerializer
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    OfficerAllegationFactory,
    PoliceUnitFactory,
    OfficerHistoryFactory,
)
from pinboard.factories import PinboardFactory


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='1')
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004'
        )
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        officer_coaccusal = OfficerFactory(
            id=11,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=2,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Police Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )

        allegation = AllegationFactory(crid='11')
        OfficerAllegationFactory(allegation=allegation, officer=pinned_officer)
        OfficerAllegationFactory(allegation=allegation, officer=officer_coaccusal)
        OfficerHistoryFactory(officer=officer_coaccusal, unit=unit, effective_date=date(2004, 1, 2))

        pinboard_relevant_coaccusals = [c for c in pinboard.relevant_coaccusals]
        expect(pinboard_relevant_coaccusals).to.have.length(1)

        coaccusal = pinboard_relevant_coaccusals[0]

        expect(OfficerMobileSerializer(coaccusal).data).to.eq({
            'id': 11,
            'full_name': 'Jerome Finnigan',
            'rank': 'Police Officer',
            'percentile': {
                'year': 2010,
                'percentile_trr': '11.1100',
                'percentile_allegation_civilian': '33.3300',
                'percentile_allegation_internal': '44.4400',
                'percentile_allegation': '22.2200',
            },
            'coaccusal_count': 1,
            'allegation_count': 2,
        })
