from datetime import datetime
from operator import itemgetter

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
from mock import patch, Mock
import pytz

from cr.serializers.cr_response_serializers import (
    CRSerializer,
    InvestigatorAllegationSerializer,
    CRSummarySerializer,
    CRRelatedComplaintSerializer
)
from data.factories import (
    AllegationFactory,
    AreaFactory,
    InvestigatorAllegationFactory,
    OfficerFactory,
    OfficerAllegationFactory,
    PoliceWitnessFactory,
    OfficerBadgeNumberFactory,
    InvestigatorFactory,
    ComplainantFactory
)


class CRSerializerTestCase(TestCase):
    def test_get_point(self):
        allegation = AllegationFactory(point=None)
        result = CRSerializer(allegation).data
        expect(result).to.exclude('point')

        allegation = AllegationFactory(point=Point(1.0, 1.0))
        result = CRSerializer(allegation).data
        expect(result['point']).to.eq({'lon': 1.0, 'lat': 1.0})

    def test_get_beat(self):
        allegation = AllegationFactory(beat=None)
        result = CRSerializer(allegation).data
        expect(result).to.exclude('beat')

        allegation = AllegationFactory(beat=AreaFactory(name='23'))
        result = CRSerializer(allegation).data
        expect(result['beat']).to.eq('23')

    @patch(
        'cr.serializers.cr_response_serializers.CoaccusedSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_get_coaccused(self, coaccused_serializer_mock):
        allegation = AllegationFactory()
        officer_allegations = OfficerAllegationFactory.create_batch(2, allegation=allegation)

        result = CRSerializer(allegation).data
        officer_allegations_arg = coaccused_serializer_mock.call_args[0][0]
        expect(set(officer_allegations_arg)).to.eq(set(officer_allegations))
        expect(result['coaccused']).to.eq([{'id': 1}, {'id': 2}])

    @patch(
        'cr.serializers.cr_response_serializers.InvestigatorAllegationSerializer',
        return_value=Mock(data=[{'officer_id': 1}, {'officer_id': 2}])
    )
    @patch(
        'cr.serializers.cr_response_serializers.PoliceWitnessSerializer',
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

        result = CRSerializer(allegation).data
        investigator_allegations_arg = investigator_allegation_serializer_mock.call_args[0][0]
        police_witnesses_arg = police_witness_serializer_mock.call_args[0][0]
        expect(set(investigator_allegations_arg)).to.eq(set(investigator_allegations))
        for obj in investigator_allegations_arg:
            expect(obj.has_badge_number).to.eq(expected_has_badge_numbers[obj.id])
        expect(set(police_witnesses_arg)).to.eq(set([officer_1, officer_2]))
        expect(result['involvements']).to.eq(
            [{'officer_id': 1}, {'officer_id': 2}, {'officer_id': 4}, {'officer_id': 3}]
        )


class InvestigatorAllegationSerializerTestCase(TestCase):
    def test_get_full_name(self):
        investigator_allegation = InvestigatorAllegationFactory(
            investigator__officer=None,
            investigator__first_name='German',
            investigator__last_name='Lauren'
        )
        setattr(investigator_allegation, 'has_badge_number', False)
        result = InvestigatorAllegationSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('German Lauren')

        investigator_allegation.investigator.officer = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan'
        )
        result = InvestigatorAllegationSerializer(investigator_allegation).data
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

        expect(InvestigatorAllegationSerializer(investigator_allegation_1).data['badge']).to.eq('CPD')
        expect(InvestigatorAllegationSerializer(investigator_allegation_2).data['badge']).to.eq('CPD')
        expect(InvestigatorAllegationSerializer(investigator_allegation_3).data['badge']).to.eq('CPD')
        expect(InvestigatorAllegationSerializer(investigator_allegation_4).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorAllegationSerializer(investigator_allegation_5).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorAllegationSerializer(investigator_allegation_6).data['badge']).to.eq('COPA/IPRA')
        expect(InvestigatorAllegationSerializer(investigator_allegation_7).data['badge']).to.eq('CPD')
        expect(InvestigatorAllegationSerializer(investigator_allegation_8).data['badge']).to.eq('CPD')


class CRSummarySerializerTestCase(TestCase):
    def test_get_category_names(self):
        allegation = AllegationFactory()

        setattr(allegation, 'categories', ['Z Category', 'A Category', 'Z Category', 'B Category', None])
        result = CRSummarySerializer(allegation).data
        expect(result['category_names']).to.eq(['A Category', 'B Category', 'Unknown', 'Z Category'])

        setattr(allegation, 'categories', [])
        result = CRSummarySerializer(allegation).data
        expect(result['category_names']).to.eq(['Unknown'])


class CRRelatedComplaintSerializerTestCase(TestCase):
    def test_serializer(self):
        officer_1 = OfficerFactory(first_name='Jos', last_name='Parker')
        officer_2 = OfficerFactory(first_name='John', last_name='Hurley')
        allegation = AllegationFactory(
            point=Point([0.01, 0.01]),
            incident_date=datetime(2016, 2, 23, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            allegation=allegation,
            officer=officer_1,
            allegation_category__category='False Arrest'
        )
        OfficerAllegationFactory(
            allegation=allegation,
            officer=officer_2,
            allegation_category__category='Use of Force'
        )
        ComplainantFactory(allegation=allegation, gender='M', race='Black', age='18')
        ComplainantFactory(allegation=allegation, gender='F', race='Black', age='19')

        expected_data = {
            'crid': allegation.crid,
            'coaccused': [
                'J. Hurley',
                'J. Parker'
            ],
            'category_names': [
                'False Arrest', 'Use of Force'
            ],
            'complainants': [
                {
                    'race': 'Black',
                    'gender': 'Female',
                    'age': 19
                },
                {
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 18
                }
            ],
            'point': {
                'lat': 0.01,
                'lon': 0.01
            },
            'incident_date': '2016-02-23',
        }
        serializer_data = CRRelatedComplaintSerializer(allegation).data
        serializer_data['coaccused'] = sorted(serializer_data['coaccused'])
        serializer_data['complainants'] = sorted(serializer_data['complainants'], key=itemgetter('gender'))
        expect(serializer_data).to.eq(expected_data)
