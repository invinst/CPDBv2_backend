from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
from mock import patch, Mock

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
    PoliceWitnessFactory
)


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
        investigator_allegations = InvestigatorAllegationFactory.create_batch(2, allegation=allegation)
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        PoliceWitnessFactory(officer=officer_1, allegation=allegation)
        PoliceWitnessFactory(officer=officer_2, allegation=allegation)

        result = CRMobileSerializer(allegation).data
        investigator_allegations_arg = investigator_allegation_serializer_mock.call_args[0][0]
        police_witnesses_arg = police_witness_serializer_mock.call_args[0][0]
        expect(set(investigator_allegations_arg)).to.eq(set(investigator_allegations))
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

        result = InvestigatorMobileSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('German Lauren')

        investigator_allegation.investigator.officer = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan'
        )
        result = InvestigatorMobileSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('Jerome Finnigan')
