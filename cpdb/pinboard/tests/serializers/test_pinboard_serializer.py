from django.test import TestCase

from robber import expect

from pinboard.serializers.pinboard_serializer import PinboardSerializer
from data.factories import OfficerFactory, AllegationFactory
from pinboard.factories import PinboardFactory


class PinboardSerializerTestCase(TestCase):
    def test_serialization_without_data(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='1')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        expect(PinboardSerializer(pinboard).data).to.eq({
            'id': '66ef1560',
            'title': 'Test pinboard',
            'description': 'Test description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        })

    def test_serialization_with_data(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='1')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        pinboard_data = {
            'id': '123abc',
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        }

        serializer = PinboardSerializer(data=pinboard_data)
        expect(serializer.is_valid()).to.be.true()
        expect(serializer.data).to.eq({
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        })

    def test_serialization_with_non_existing_pinned_item_ids(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='123abc')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        pinboard_data = {
            'id': '123abc',
            'title': 'title',
            'description': 'description',
            'officer_ids': [1, 2, 4, 5],
            'crids': ['xyz789', '123abc', '456def'],
            'trr_ids': [0, 3, 1],
        }

        serializer = PinboardSerializer(data=pinboard_data)
        expect(serializer.is_valid()).to.be.true()
        expect(serializer.data).to.eq({
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['123abc'],
            'trr_ids': [],
            'not_found_items': {
                'officer_ids': [2, 4, 5],
                'crids':  ['xyz789', '456def'],
                'trr_ids': [0, 3, 1],
            }
        })
