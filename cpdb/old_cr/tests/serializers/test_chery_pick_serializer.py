from django.test import SimpleTestCase

from robber import expect

from old_cr.serializers.base import CherryPickSerializer


class CherryPickSerializerTestCase(SimpleTestCase):
    def test_serializer(self):
        class Serializer(CherryPickSerializer):
            class Meta(object):
                fields = ('a', 'b')

        expect(Serializer({'a': 'a', 'c': 'c'}).data).to.eq({'a': 'a'})
