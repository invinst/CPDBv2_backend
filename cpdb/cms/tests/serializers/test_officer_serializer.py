from django.test import SimpleTestCase
from django.core.exceptions import ObjectDoesNotExist

from mock import Mock, patch
from robber import expect

from cms.serializers import OfficerSerializer


class OfficerSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        officer = Mock()
        officer.id = 123
        officer.v1_url = 'http://cpdb.co/officer/alan/123'
        officer.full_name = 'Alan Johnson'
        officer.gender_display = 'Male'
        officer.allegation_count = 3
        officer.race = 'White'

        expect(OfficerSerializer(officer).data).to.eq({
            'id': 123,
            'v1_url': 'http://cpdb.co/officer/alan/123',
            'full_name': 'Alan Johnson',
            'gender': 'Male',
            'allegation_count': 3,
            'race': 'White'
        })

    def test_deserialize(self):
        officer = Mock()
        queryset = Mock()
        queryset.get = Mock(return_value=officer)
        with patch('cms.serializers.Officer.objects.all', return_value=queryset):
            expect(OfficerSerializer().to_internal_value({'id': 123})).to.eq(officer)
            queryset.get.assert_called_with(pk=123)

    def test_deserialize_object_does_not_exist(self):
        queryset = Mock()
        queryset.get = Mock(side_effect=ObjectDoesNotExist)
        serializer = OfficerSerializer(data=[{'id': 123}], many=True)
        serializer.field_name = 'officers'
        with patch('cms.serializers.Officer.objects.all', return_value=queryset):
            serializer.is_valid()
            expect(serializer.errors).to.eq({'officers': 'Officer does not exist'})

    def test_deserialize_with_wrong_type_for_id(self):
        serializer = OfficerSerializer(data=[123], many=True)
        serializer.field_name = 'officers'
        serializer.is_valid()
        expect(serializer.errors).to.eq({'officers': 'Incorrect type. Expected officer pk'})
