import os
import json
import shutil

from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.tests.utils import get_test_image_file
from freezegun import freeze_time

from story.factories import StoryPageFactory, ImageFactory, CoveragePageFactory
from data.factories import RootPageFactory


class StoryAPITests(APITestCase):
    maxDiff = None

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            # TODO: for multiple tests that create default image `test.png` this command causes SourceImageIOError
            # while serializing story
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_list_stories(self):
        root = Page.add_root(instance=RootPageFactory.build())
        coverage_page = root.add_child(instance=CoveragePageFactory.build())
        with freeze_time('2015-11-03'):
            story_1 = coverage_page.add_child(instance=StoryPageFactory.build(
                title='title a',
                image=ImageFactory(file=get_test_image_file(filename='a-image.png')),
                canonical_url='http://domain.com/title_a',
                publication_name='a paper',
                publication_short_url='ap',
                body='[{"type": "paragraph", "value": "a a a a"}]',
                ))

        with freeze_time('2015-11-04'):
            story_2 = coverage_page.add_child(instance=StoryPageFactory.build(
                title='title b',
                image=None,
                canonical_url='http://domain.com/title_b',
                publication_name='b paper',
                publication_short_url='bp',
                body='[{"type": "paragraph", "value": "b b b b"}]',
                ))

        with freeze_time('2015-11-05'):
            coverage_page.add_child(instance=StoryPageFactory.build(
                title='title c',
                image=None,
                canonical_url='http://domain.com/title_c',
                publication_name='c paper',
                publication_short_url='cp',
                body='[{"type": "paragraph", "value": "c c c c"}]',
                ))

        url = reverse('api:story-list')
        response = self.client.get(url, {'limit': 2})
        actual_content = json.loads(response.content)

        expected_results = [
            {
                'id': story_1.id,
                'title': 'title a',
                'canonical_url': 'http://domain.com/title_a',
                'post_date': '2015-11-03',
                'publication_name': 'a paper',
                'publication_short_url': 'ap',
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
                'publication_name': 'b paper',
                'publication_short_url': 'bp',
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
