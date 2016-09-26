import os
import json
import shutil
from datetime import date

from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.tests.utils import get_test_image_file

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
        story_1 = coverage_page.add_child(instance=StoryPageFactory.build(
            title='title a',
            image=ImageFactory(file=get_test_image_file(filename='a-image.png')),
            publication_date=date(2015, 11, 3),
            canonical_url='http://domain.com/title_a',
            publication_name='a paper',
            publication_short_name='ap',
            body='[{"type": "paragraph", "value": "a a a a"}]',
            ))

        story_2 = coverage_page.add_child(instance=StoryPageFactory.build(
            title='title b',
            image=None,
            publication_date=date(2015, 11, 4),
            canonical_url='http://domain.com/title_b',
            publication_name='b paper',
            publication_short_name='bp',
            body='[{"type": "paragraph", "value": "b b b b"}]',
            ))

        coverage_page.add_child(instance=StoryPageFactory.build(
            title='title c',
            image=None,
            publication_date=date(2015, 11, 5),
            canonical_url='http://domain.com/title_c',
            publication_name='c paper',
            publication_short_name='cp',
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
                'publication_date': '2015-11-03',
                'publication_name': 'a paper',
                'publication_short_name': 'ap',
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
                'publication_date': '2015-11-04',
                'publication_name': 'b paper',
                'publication_short_name': 'bp',
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
