from django.test import TestCase
from rest_framework import serializers

from robber import expect

from shared.serializer import NoNullSerializer
from shared.tests.utils import create_object


class NoNullSerializerTestCase(TestCase):
    def test_serialization_remove_None_attr(self):

        class ObjectSerializer(NoNullSerializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
        objects = [
            create_object({'id': 1, 'name': 'Alex', 'value': 3}),
            create_object({'id': 2, 'name': None, 'value': 4})
        ]

        data = ObjectSerializer(objects, many=True).data
        expect(data).to.eq([
            {'id': 1, 'name': 'Alex'},
            {'id': 2}
        ])
