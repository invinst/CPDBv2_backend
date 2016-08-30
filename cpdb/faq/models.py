from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.wagtailsnippets.models import register_snippet


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
