import os
import json
import shutil

from datetime import date

from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.wagtailimages.tests.utils import get_test_image_file

from story.factories import StoryFactory, NewspaperFactory, ImageFactory


class StoryAPITests(APITestCase):
    maxDiff = None

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            # TODO: for multiple tests that create default image `test.png` this command causes SourceImageIOError
            # while serializing story
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_list_stories(self):
        story_1 = StoryFactory(
            title='title a',
            image=ImageFactory(file=get_test_image_file(filename='a-image.png')),
            canonical_url='http://domain.com/title_a',
            post_date=date(2015, 11, 3),
            newspaper=NewspaperFactory(
                id=11,
                name='a paper',
                short_name='ap'),
            body='[{"type": "paragraph", "value": "a a a a"}]',
            )

        story_2 = StoryFactory(
            title='title b',
            image=None,
            canonical_url='http://domain.com/title_b',
            post_date=date(2015, 11, 4),
            newspaper=NewspaperFactory(
                id=12,
                name='b paper',
                short_name='bp'),
            body='[{"type": "paragraph", "value": "b b b b"}]',
            )

        StoryFactory(
            title='title c',
            image=None,
            canonical_url='http://domain.com/title_c',
            post_date=date(2015, 11, 5),
            newspaper=NewspaperFactory(
                id=13,
                name='c paper',
                short_name='cp'),
            body='[{"type": "paragraph", "value": "c c c c"}]',
            )

        url = reverse('api:story-list')
        response = self.client.get(url, {'limit': 2})
        actual_content = json.loads(response.content)

        expected_results = [
            {
                'id': story_1.id,
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
                'id': story_2.id,
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
