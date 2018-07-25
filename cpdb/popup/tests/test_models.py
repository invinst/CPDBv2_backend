from django.test.testcases import TestCase
from robber.expect import expect

from popup.factories import PopupFactory


class PopupTestCase(TestCase):
    def test_str_method(self):
        expect(str(PopupFactory(name='some name'))).to.eq('some name')
