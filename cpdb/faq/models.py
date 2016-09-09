from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


@register_snippet
class FAQ(models.Model):
    title = models.CharField(max_length=255, blank=True)
    body = StreamField([
        ('paragraph', blocks.TextBlock())])

    content_panels = Page.content_panels + [
        FieldPanel('title'),
        StreamFieldPanel('body')
    ]

    def __unicode__(self):
        return self.title


class FAQsPage(Page):
    subpage_types = ['faq.FAQPage']


class FAQPageTag(TaggedItemBase):
    content_object = ParentalKey('faq.FAQPage', related_name='tagged_items')


class FAQPage(Page):
    parent_page_types = ['faq.FAQsPage']
    body = StreamField([
        ('paragraph', blocks.TextBlock())])
    created = models.DateTimeField(auto_now_add=True)
    tags = ClusterTaggableManager(through=FAQPageTag, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]
