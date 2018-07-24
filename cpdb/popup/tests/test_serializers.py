from django.test import TestCase
from mock import Mock, PropertyMock
from robber import expect

from popup.serializers import PopupSerializer


class PopupSerializerTestCase(TestCase):
    def test_get_data(self):
        popup = Mock(**{
            'page': 'some page',
            'title': 'some title',
            'text': 'some text',
        })
        type(popup).name = PropertyMock(return_value='some name')

        expect(PopupSerializer(popup).data).to.eq({
            'name': 'some name',
            'page': 'some page',
            'title': 'some title',
            'text': 'some text',
        })
