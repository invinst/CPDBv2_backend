from datetime import date

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from story.factories import StoryPageFactory, NewspaperFactory


class StoryAPITests(APITestCase):
    def test_list_stories(self):
        StoryPageFactory(
            id=11,
            title='title a',
            canonical_url='http://domain.com/title_a',
            post_date=date(2015, 11, 3),
            newspaper=NewspaperFactory(
                id=11,
                name='a paper',
                short_name='ap'),
            image__filename='a-image',
            body='[{"type": "paragraph", "value": "a a a a"}]')
        StoryPageFactory(
            id=12,
            title='title b',
            canonical_url='http://domain.com/title_b',
            post_date=date(2015, 11, 4),
            newspaper=NewspaperFactory(
                id=12,
                name='b paper',
                short_name='bp'),
            image__filename='b-image',
            body='[{"type": "paragraph", "value": "b b b b"}]')
        StoryPageFactory(
            id=13,
            title='title c',
            canonical_url='http://domain.com/title_c',
            post_date=date(2015, 11, 5),
            newspaper=NewspaperFactory(
                id=13,
                name='c paper',
                short_name='cp'),
            image__filename='c-image',
            body='[{"type": "paragraph", "value": "c c c c"}]')

        url = reverse('story-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'id': 11,
                'title': 'title a',
                'canonical_url': 'http://domain.com/title_a',
                'post_date': '2015-11-03',
                'newspaper': {
                    'id': 11,
                    'name': 'a paper',
                    'short_name': 'ap'
                },
                'image_url': {
                    '480_320': '/media/images/a-image.min-480x320.jpg'
                },
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'a a a a'
                    }
                ]
            },
            {
                'id': 12,
                'title': 'title b',
                'canonical_url': 'http://domain.com/title_b',
                'post_date': '2015-11-04',
                'newspaper': {
                    'id': 12,
                    'name': 'b paper',
                    'short_name': 'bp'
                },
                'image_url': {
                    '480_320': '/media/images/b-image.min-480x320.jpg'
                },
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'b b b b'
                    }
                ]
            },
            {
                'id': 13,
                'title': 'title c',
                'canonical_url': 'http://domain.com/title_c',
                'post_date': '2015-11-05',
                'newspaper': {
                    'id': 13,
                    'name': 'c paper',
                    'short_name': 'cp'
                },
                'image_url': {
                    '480_320': '/media/images/c-image.min-480x320.jpg'
                },
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'c c c c'
                    }
                ]
            }
        ])
