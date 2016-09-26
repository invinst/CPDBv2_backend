import shutil

from django.test.testcases import TestCase
from django.conf import settings
from wagtail.wagtailimages.tests.utils import get_test_image_file

from story.factories import StoryPageFactory, ImageFactory
from story.serializers import StoryPageSerializer


class StoryPageSerializersTestCase(TestCase):
    def test_get_image_url(self):
        story = StoryPageFactory.build(image=ImageFactory(file=get_test_image_file(filename='file.png')))

        expected_title = 'file.min-480x320.png'
        serialized_story = StoryPageSerializer(story)
        self.assertTrue(expected_title in serialized_story.data['image_url']['480_320'])

        shutil.rmtree(settings.MEDIA_ROOT)

    def test_get_image_url_on_no_image(self):
        story = StoryPageFactory.build(image=None)

        serialized_story = StoryPageSerializer(story)
        self.assertEqual(serialized_story.data['image_url'], {})
