from django.db import models

from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailcore.models import Page

from story.models import Story
from faq.models import FAQ


class LandingPage(Page):
    report1 = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page1')
    report2 = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page2')
    report3 = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page3')
    faq1 = models.ForeignKey(FAQ, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page1')
    faq2 = models.ForeignKey(FAQ, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page2')
    faq3 = models.ForeignKey(FAQ, null=True, blank=True, on_delete=models.SET_NULL, related_name='landing_page3')

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                SnippetChooserPanel('report1'),
                SnippetChooserPanel('report2'),
                SnippetChooserPanel('report3'),
            ],
            heading='Reporting Section'),
        MultiFieldPanel(
            [
                SnippetChooserPanel('faq1'),
                SnippetChooserPanel('faq2'),
                SnippetChooserPanel('faq3'),
            ],
            heading='FAQ Section'),
    ]
