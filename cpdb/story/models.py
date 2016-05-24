from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel


class Newspaper(models.Model):
    title = models.CharField(max_length=255)
    canonical_url = models.URLField()

    def __unicode__(self):
        return self.title


class StoryPage(Page):
    newspaper = models.ForeignKey(Newspaper, on_delete=models.SET_NULL, null=True)
    post_date = models.DateField(null=True)
    body = StreamField([
        ('paragraph', blocks.TextBlock())])

    content_panels = Page.content_panels + [
        FieldPanel('newspaper'),
        FieldPanel('post_date'),
        StreamFieldPanel('body')
    ]
