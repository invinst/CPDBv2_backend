from django.test import TestCase
from django.core.urlresolvers import reverse

from robber import expect

from popup.factories import PopupFactory


class PopupViewSetTestCase(TestCase):
    def test_list(self):
        PopupFactory(name='some_name', page='some_page', title='some title', text='some text')
        response = self.client.get(reverse('api-v2:popup-list'))
        expect(response.data).to.eq([{
            'name': 'some_name',
            'page': 'some_page',
            'title': 'some title',
            'text': 'some text',
        }])

    def test_list_with_param(self):
        PopupFactory(name='some_name', page='officer', title='some title', text='some text')
        PopupFactory(name='some_name', page='some_page', title='some title', text='some text')
        response = self.client.get(reverse('api-v2:popup-list'), {'page': 'officer'})
        expect(response.data).to.eq([{
            'name': 'some_name',
            'page': 'officer',
            'title': 'some title',
            'text': 'some text'
        }])
