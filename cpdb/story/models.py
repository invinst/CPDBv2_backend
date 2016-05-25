from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class Newspaper(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.title


class StoryPage(Page):
    newspaper = models.ForeignKey(Newspaper, on_delete=models.SET_NULL, null=True)
    canonical_url = models.URLField(null=True)
    post_date = models.DateField(null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('paragraph', blocks.TextBlock())])

    content_panels = Page.content_panels + [
        FieldPanel('newspaper'),
        FieldPanel('canonical_url'),
        FieldPanel('post_date'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body')
    ]
