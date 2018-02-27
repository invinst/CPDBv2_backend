from django.db import models

from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey


class SearchTermCategory(SortableMixin):
    name = models.CharField(max_length=60)
    order_number = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['order_number']
        verbose_name_plural = 'Search term categories'

    def __unicode__(self):
        return self.name


VIEW_ALL_CTA_TYPE = 'view_all'
PLAIN_TEXT_CTA_TYPE = 'plain_text'
LINK_CTA_TYPE = 'link'
SEARCH_TERM_CTA_TYPES = (
    (VIEW_ALL_CTA_TYPE, 'View All'),
    (PLAIN_TEXT_CTA_TYPE, 'Plain text'),
    (LINK_CTA_TYPE, 'Link')
)


class SearchTermItem(SortableMixin):
    category = SortableForeignKey(SearchTermCategory)
    slug = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=60)
    description = models.TextField(null=True, blank=True)
    call_to_action_type = models.CharField(
        choices=SEARCH_TERM_CTA_TYPES, default=PLAIN_TEXT_CTA_TYPE, max_length=20
    )
    call_to_action_text = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    order_number = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ['order_number']

    def __unicode__(self):
        return self.name
