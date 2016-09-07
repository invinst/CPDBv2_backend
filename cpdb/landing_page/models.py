from django.db import models

from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel, FieldPanel
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
    vftg_header = models.CharField(max_length=255, blank=True)
    vftg_date = models.DateField(blank=True, null=True)
    vftg_content = models.CharField(max_length=255, blank=True)
    vftg_link = models.URLField(blank=True)
    hero_complaints_text = models.CharField(max_length=255, blank=True)
    hero_use_of_force_text = models.CharField(max_length=255, blank=True)

    # SEO
    page_title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('hero_complaints_text'),
                FieldPanel('hero_use_of_force_text'),
            ],
            heading='Hero Section'),
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
        MultiFieldPanel(
            [
                FieldPanel('vftg_header'),
                FieldPanel('vftg_date'),
                FieldPanel('vftg_content'),
                FieldPanel('vftg_link'),
            ],
            heading='VFTG'),
    ]

    promote_panels = [
        FieldPanel('page_title'),
        FieldPanel('description'),
    ]
