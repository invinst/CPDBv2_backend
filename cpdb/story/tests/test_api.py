import json
import shutil

from datetime import date

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.tests.utils import get_test_image_file

from story.factories import StoryPageFactory, NewspaperFactory, ImageFactory
from story.models import StoryPage


class StoryAPITests(APITestCase):
    def setUp(self):
        StoryPage.get_tree().all().delete()

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_list_stories(self):
        root = StoryPage.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

        story_page_1 = root.add_child(
            instance=StoryPageFactory.build(
                title='title a',
                image=ImageFactory(file=get_test_image_file(filename='a-image.png')),
                canonical_url='http://domain.com/title_a',
                post_date=date(2015, 11, 3),
                newspaper=NewspaperFactory(
                    id=11,
                    name='a paper',
                    short_name='ap'),
                body='[{"type": "paragraph", "value": "a a a a"}]'))

        story_page_2 = root.add_child(
            instance=StoryPageFactory.build(
                title='title b',
                image=None,
                canonical_url='http://domain.com/title_b',
                post_date=date(2015, 11, 4),
                newspaper=NewspaperFactory(
                    id=12,
                    name='b paper',
                    short_name='bp'),
                body='[{"type": "paragraph", "value": "b b b b"}]'))

        root.add_child(
            instance=StoryPageFactory.build(
                title='title c',
                image=None,
                canonical_url='http://domain.com/title_c',
                post_date=date(2015, 11, 5),
                newspaper=NewspaperFactory(
                    id=13,
                    name='c paper',
                    short_name='cp'),
                body='[{"type": "paragraph", "value": "c c c c"}]'))

        url = reverse('api:story-list')
        response = self.client.get(url, {'limit': 2})
        actual_content = json.loads(response.content)

        expected_results = [
            {
                'id': story_page_1.id,
                'title': 'title a',
                'canonical_url': 'http://domain.com/title_a',
                'post_date': '2015-11-03',
                'newspaper': {
                    'id': 11,
                    'name': 'a paper',
                    'short_name': 'ap'
                },
                'image_url': {
                    '480_320': '/media/images/a-image.min-480x320.png'
                },
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'a a a a'
                    }
                ]
            },
            {
                'id': story_page_2.id,
                'title': 'title b',
                'canonical_url': 'http://domain.com/title_b',
                'post_date': '2015-11-04',
                'newspaper': {
                    'id': 12,
                    'name': 'b paper',
                    'short_name': 'bp'
                },
                'image_url': {},
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'b b b b'
                    }
                ]
            }
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(actual_content.get('results'), expected_results)
        self.assertEqual(actual_content.get('count'), 3)
        self.assertTrue('{url}?limit=2&offset=2'.format(url=str(url)) in actual_content.get('next'))
