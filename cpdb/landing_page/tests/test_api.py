import json
from datetime import date

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.wagtailcore.models import Page

from faq.factories import FAQFactory
from story.factories import StoryFactory
from landing_page.factories import LandingPageFactory


class LandingPageAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.add_root(instance=Page(title='Root'))
        cls.landing_page = cls.root.add_child(instance=LandingPageFactory.build(
            report1=StoryFactory(),
            report2=StoryFactory(),
            report3=StoryFactory(),
            faq1=FAQFactory(),
            faq2=FAQFactory(),
            faq3=FAQFactory(),
            vftg_header='CPDP weekly',
            vftg_date=date(2016, 9, 23),
            vftg_content='allegation rarely result in discipline',
            vftg_link='http://nyt.com/articles/123',
            hero_complaints_text='complaints',
            hero_use_of_force_text='use of force',
            page_title='CPDP',
            description='Chicago Police Data Project'
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

        reports = actual_content['reports']
        faqs = actual_content['faqs']

        self.assertEqual(len(reports), 3)
        self.assertEqual(len(faqs), 3)

        report_ids = [report['id'] for report in reports]
        faq_ids = [faq['id'] for faq in faqs]

        self.assertListEqual(report_ids, [
            self.landing_page.report1.pk, self.landing_page.report2.pk, self.landing_page.report3.pk
            ])
        self.assertListEqual(faq_ids, [
            self.landing_page.faq1.pk, self.landing_page.faq2.pk, self.landing_page.faq3.pk
            ])
