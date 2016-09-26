import json
from datetime import date

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.wagtailcore.models import Page

from faq.factories import FAQPageFactory, FAQsPageFactory
from story.factories import StoryPageFactory, CoveragePageFactory
from landing_page.factories import LandingPageFactory


class LandingPageAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.add_root(instance=Page(title='Root'))
        coverage_page = cls.root.add_child(instance=CoveragePageFactory.build())
        faqs_page = cls.root.add_child(instance=FAQsPageFactory.build())
        for i in xrange(3):
            coverage_page.add_child(instance=StoryPageFactory.build())
            faqs_page.add_child(instance=FAQPageFactory.build())

        cls.landing_page = cls.root.add_child(instance=LandingPageFactory.build(
            vftg_header='CPDP weekly',
            vftg_date=date(2016, 9, 23),
            vftg_content='allegation rarely result in discipline',
            vftg_link='http://nyt.com/articles/123',
            hero_complaints_text='complaints',
            hero_use_of_force_text='use of force',
            page_title='CPDP',
            description='Chicago Police Data Project',
            about_header='About',
            about_content='[{"type": "paragraph", "value": "a a a a"}]',
            collaborate_header='Collaborate with us',
            collaborate_content='[{"type": "paragraph", "value": "b b b b"}]'
            ))

    def test_get_landing_page(self):
        url = reverse('api:landing-page-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_content = json.loads(response.content)

        self.assertEqual(actual_content['vftg_header'], 'CPDP weekly')
        self.assertEqual(actual_content['vftg_date'], '2016-09-23',)
        self.assertEqual(actual_content['vftg_content'], 'allegation rarely result in discipline',)
        self.assertEqual(actual_content['vftg_link'], 'http://nyt.com/articles/123',)
        self.assertEqual(actual_content['hero_complaints_text'], 'complaints',)
        self.assertEqual(actual_content['hero_use_of_force_text'], 'use of force',)
        self.assertEqual(actual_content['page_title'], 'CPDP',)
        self.assertEqual(actual_content['description'], 'Chicago Police Data Project')
        self.assertEqual(actual_content['about_header'], 'About')
        self.assertEqual(actual_content['about_content'], [{
            'type': 'paragraph',
            'value': 'a a a a'
            }])
        self.assertEqual(actual_content['collaborate_header'], 'Collaborate with us')
        self.assertEqual(actual_content['collaborate_content'], [{
            'type': 'paragraph',
            'value': 'b b b b'
            }])

        reports = actual_content['reports']
        faqs = actual_content['faqs']

        self.assertEqual(len(reports), 3)
        self.assertEqual(len(faqs), 3)

        for report in reports:
            self.assertEqual(
                set(['id', 'title', 'publication_name', 'publication_short_name', 'canonical_url',
                     'publication_date', 'image_url', 'body']),
                set(report.keys()))

        for faq in faqs:
            self.assertEqual(
                set(['id', 'title', 'body']),
                set(faq.keys()))
