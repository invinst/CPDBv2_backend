from django.test import SimpleTestCase

from faq.models import FAQ


class FAQModelTestCase(SimpleTestCase):
    def test_unicode(self):
        title = 'abc'
        self.assertEqual(unicode(FAQ(title=title)), title)
