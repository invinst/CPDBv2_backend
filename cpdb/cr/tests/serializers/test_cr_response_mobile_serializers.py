from datetime import datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
from mock import patch, Mock
import pytz

from cr.serializers.cr_response_mobile_serializers import (
    CRMobileSerializer,
    InvestigatorMobileSerializer
)
from data.factories import (
    AllegationFactory,
    AreaFactory,
    InvestigatorAllegationFactory,
    OfficerFactory,
    OfficerAllegationFactory,
    PoliceWitnessFactory,
    OfficerBadgeNumberFactory, InvestigatorFactory)


class CRMobileSerializerTestCase(TestCase):
    def test_get_point(self):
        allegation = AllegationFactory(point=None)
        result = CRMobileSerializer(allegation).data
        expect(result).to.exclude('point')

        allegation = AllegationFactory(point=Point(1.0, 1.0))
        result = CRMobileSerializer(allegation).data
        expect(result['point']).to.eq({'lon': 1.0, 'lat': 1.0})

    def test_get_beat(self):
        allegation = AllegationFactory(beat=None)
        result = CRMobileSerializer(allegation).data
        expect(result).to.exclude('beat')

        allegation = AllegationFactory(beat=AreaFactory(name='23'))
        result = CRMobileSerializer(allegation).data
        expect(result['beat']).to.eq('23')

    @patch(
        'cr.serializers.cr_response_mobile_serializers.CoaccusedMobileSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_get_coaccused(self, coaccused_serializer_mock):
        allegation = AllegationFactory()
        officer_allegations = OfficerAllegationFactory.create_batch(2, allegation=allegation)

        result = CRMobileSerializer(allegation).data
        officer_allegations_arg = coaccused_serializer_mock.call_args[0][0]
        expect(set(officer_allegations_arg)).to.eq(set(officer_allegations))
        expect(result['coaccused']).to.eq([{'id': 1}, {'id': 2}])

    @patch(
        'cr.serializers.cr_response_mobile_serializers.InvestigatorMobileSerializer',
        return_value=Mock(data=[{'officer_id': 1}, {'officer_id': 2}])
    )
    @patch(
        'cr.serializers.cr_response_mobile_serializers.PoliceWitnessMobileSerializer',
        return_value=Mock(data=[{'officer_id': 4}, {'officer_id': 3}])
    )
    def test_get_involvements(self, police_witness_serializer_mock, investigator_allegation_serializer_mock):
        allegation = AllegationFactory()
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        PoliceWitnessFactory(officer=officer_1, allegation=allegation)
        PoliceWitnessFactory(officer=officer_2, allegation=allegation)
        OfficerBadgeNumberFactory(officer=officer_1, star='456789')
        investigator_1 = InvestigatorFactory(officer=officer_1)
        investigator_2 = InvestigatorFactory(officer=officer_2)
        investigator_3 = InvestigatorFactory()
        investigator_allegation_1 = InvestigatorAllegationFactory(allegation=allegation, investigator=investigator_1)
        investigator_allegation_2 = InvestigatorAllegationFactory(allegation=allegation, investigator=investigator_2)
        investigator_allegation_3 = InvestigatorAllegationFactory(allegation=allegation, investigator=investigator_3)
        investigator_allegations = [investigator_allegation_1, investigator_allegation_2, investigator_allegation_3]
        expected_has_badge_numbers = {
            investigator_allegation_1.id: True,
            investigator_allegation_2.id: False,
            investigator_allegation_3.id: False,
        }

        result = CRMobileSerializer(allegation).data
        investigator_allegations_arg = investigator_allegation_serializer_mock.call_args[0][0]
        police_witnesses_arg = police_witness_serializer_mock.call_args[0][0]
        expect(set(investigator_allegations_arg)).to.eq(set(investigator_allegations))
        for obj in investigator_allegations_arg:
            expect(obj.has_badge_number).to.eq(expected_has_badge_numbers[obj.id])
        expect(set(police_witnesses_arg)).to.eq(set([officer_1, officer_2]))
        expect(result['involvements']).to.eq(
            [{'officer_id': 1}, {'officer_id': 2}, {'officer_id': 4}, {'officer_id': 3}]
        )


class InvestigatorAllegationMobileSerializerTestCase(TestCase):
    def test_get_full_name(self):
        investigator_allegation = InvestigatorAllegationFactory(
            investigator__officer=None,
            investigator__first_name='German',
            investigator__last_name='Lauren'
        )
        setattr(investigator_allegation, 'has_badge_number', True)

        result = InvestigatorMobileSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('German Lauren')

        investigator_allegation.investigator.officer = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan'
        )
        result = InvestigatorMobileSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('Jerome Finnigan')

    def test_get_badge(self):
        allegation_1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 1, 1, tzinfo=pytz.utc))
        allegation_3 = AllegationFactory(incident_date=None)

        investigator_allegation_1 = InvestigatorAllegationFactory(allegation=allegation_1)
        investigator_allegation_2 = InvestigatorAllegationFactory(allegation=allegation_2, current_star='123456')
        investigator_allegation_3 = InvestigatorAllegationFactory(
            allegation=allegation_2,
            current_star=None,
        )
        setattr(investigator_allegation_3, 'has_badge_number', True)
        investigator_allegation_4 = InvestigatorAllegationFactory(allegation=allegation_2, current_star=None)
        setattr(investigator_allegation_4, 'has_badge_number', False)
        investigator_allegation_5 = InvestigatorAllegationFactory(
            allegation=allegation_2,
            current_star=None,
        )
        setattr(investigator_allegation_5, 'has_badge_number', False)
        investigator_allegation_6 = InvestigatorAllegationFactory(
            allegation=allegation_3,
            current_star=None,
        )
        setattr(investigator_allegation_6, 'has_badge_number', False)
        investigator_allegation_7 = InvestigatorAllegationFactory(
            allegation=allegation_3,
            current_star='123456',
        )
        investigator_allegation_8 = InvestigatorAllegationFactory(
            allegation=allegation_3,
            current_star=None,
        )
        setattr(investigator_allegation_8, 'has_badge_number', True)

        expect(InvestigatorMobileSerializer(investigator_allegation_1).data['badge']).to.eq('CPD')
        expect(InvestigatorMobileSerializer(investigator_allegation_2).data['badge']).to.eq('CPD')
        expect(InvestigatorMobileSerializer(investigator_allegation_3).data['badge']).to.eq('CPD')
        expect(InvestigatorMobileSerializer(investigator_allegation_4).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorMobileSerializer(investigator_allegation_5).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorMobileSerializer(investigator_allegation_6).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorMobileSerializer(investigator_allegation_7).data['badge']).to.eq('CPD')
        expect(InvestigatorMobileSerializer(investigator_allegation_8).data['badge']).to.eq('CPD')
