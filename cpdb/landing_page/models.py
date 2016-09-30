from django.db import models
from django.contrib.postgres.fields import JSONField

from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel, FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore import blocks

from story.models import StoryPage
from faq.models import FAQPage
from landing_page.randomizers import RANDOMIZER_STRAT_LAST_N_DAYS, RANDOMIZER_STRAT_LAST_N_ENTRIES, randomize


class LandingPage(Page):
    RANDOMIZER_STRAT_CHOICES = (
        (RANDOMIZER_STRAT_LAST_N_DAYS, 'last n days'),
        (RANDOMIZER_STRAT_LAST_N_ENTRIES, 'last n entries')
    )
    coverage_pool_strategy = models.CharField(
        max_length=255, choices=RANDOMIZER_STRAT_CHOICES, default=RANDOMIZER_STRAT_LAST_N_ENTRIES)
    coverage_strat_n = models.IntegerField(default=10)
    faq_pool_strategy = models.CharField(
        max_length=255, choices=RANDOMIZER_STRAT_CHOICES, default=RANDOMIZER_STRAT_LAST_N_ENTRIES)
    faq_strat_n = models.IntegerField(default=10)

    vftg_header = models.CharField(max_length=255, blank=True)
    vftg_date = models.DateField(blank=True, null=True)
    vftg_content = models.CharField(max_length=255, blank=True)
    vftg_link = models.URLField(blank=True)
    hero_complaints_text = models.CharField(max_length=255, blank=True)
    hero_use_of_force_text = models.CharField(max_length=255, blank=True)
    about_header = models.CharField(max_length=255, blank=True)
    about_content = StreamField([('paragraph', blocks.TextBlock())], blank=True)
    collaborate_header = models.CharField(max_length=255, blank=True)
    collaborate_content = StreamField([('paragraph', blocks.TextBlock())], blank=True)

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
                FieldPanel('coverage_pool_strategy'),
                FieldPanel('coverage_strat_n'),
            ],
            heading='Coverage Randomizer Section'),
        MultiFieldPanel(
            [
                FieldPanel('faq_pool_strategy'),
                FieldPanel('faq_strat_n'),
            ],
            heading='FAQ Randomizer Section'),
        MultiFieldPanel(
            [
                FieldPanel('vftg_header'),
                FieldPanel('vftg_date'),
                FieldPanel('vftg_content'),
                FieldPanel('vftg_link'),
            ],
            heading='VFTG'),
        MultiFieldPanel(
            [
                FieldPanel('about_header'),
                StreamFieldPanel('about_content'),
            ],
            heading='About Section'),
        MultiFieldPanel(
            [
                FieldPanel('collaborate_header'),
                StreamFieldPanel('collaborate_content'),
            ],
            heading='Collaborate Section'),
    ]

    promote_panels = [
        FieldPanel('page_title'),
        FieldPanel('description'),
    ]

    def randomized_coverages(self, sample_size=3):
        return randomize(StoryPage.objects, self.coverage_strat_n, sample_size, self.coverage_pool_strategy)

    def randomized_faqs(self, sample_size=3):
        return randomize(FAQPage.objects, self.faq_strat_n, sample_size, self.faq_pool_strategy)


class LandingPageContent(models.Model):
    collaborate_header = models.CharField(max_length=255, blank=True, null=True)
    collaborate_content = JSONField(null=True)
