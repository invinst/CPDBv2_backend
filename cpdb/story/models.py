from django.db import models

from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class CoveragePage(Page):
    subpage_types = ['story.StoryPage']


class StoryPageTag(TaggedItemBase):
    content_object = ParentalKey('story.StoryPage', related_name='tagged_items')


class StoryPage(Page):
    publication_name = models.CharField(max_length=255, blank=True)
    publication_short_name = models.CharField(max_length=255, blank=True)
    author_name = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    post_date = models.DateField(null=True)
    publication_date = models.DateField(null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('paragraph', blocks.TextBlock())])
    tags = ClusterTaggableManager(through=StoryPageTag, blank=True)
    featured = models.BooleanField(default=False)

    parent_page_types = ['story.CoveragePage']

    content_panels = Page.content_panels + [
        FieldPanel('publication_name'),
        FieldPanel('publication_short_name'),
        FieldPanel('author_name'),
        FieldPanel('canonical_url'),
        FieldPanel('post_date'),
        FieldPanel('publication_date'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body')
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
        FieldPanel('featured'),
    ]
