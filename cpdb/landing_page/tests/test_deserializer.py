from django.test import TestCase

from landing_page.deserializers import LandingPageContentDeserializer
from landing_page.factories import LandingPageContentFactory


class LandingPageContentDeserializerTestCase(TestCase):
    def setUp(self):
        self.landing_page_content = LandingPageContentFactory()

    def test_deserializer_update(self):
        collaborate_header = 'a'
        serializer = LandingPageContentDeserializer(self.landing_page_content, data={
            'collaborate_header': collaborate_header,
            })
        serializer.is_valid()
        serializer.save()
        self.landing_page_content.refresh_from_db()
        self.assertEqual(self.landing_page_content.collaborate_header, collaborate_header)
