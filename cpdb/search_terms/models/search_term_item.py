import uuid

from django.conf import settings
from django.db import models

from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey
from data.models.common import TimeStampsModel


VIEW_ALL_CTA_TYPE = 'view_all'
PLAIN_TEXT_CTA_TYPE = 'plain_text'
LINK_CTA_TYPE = 'link'
SEARCH_TERM_CTA_TYPES = (
    (VIEW_ALL_CTA_TYPE, 'View All'),
    (PLAIN_TEXT_CTA_TYPE, 'Plain text'),
    (LINK_CTA_TYPE, 'Link')
)


class SearchTermItem(TimeStampsModel, SortableMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = SortableForeignKey('search_terms.SearchTermCategory', on_delete=models.CASCADE)
    slug = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=60)
    description = models.TextField(null=True, blank=True)
    call_to_action_type = models.CharField(
        choices=SEARCH_TERM_CTA_TYPES, default=PLAIN_TEXT_CTA_TYPE, max_length=20
    )
    call_to_action_text = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=200, null=True, blank=True)
    order_number = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ['order_number']

    def __str__(self):
        return self.name

    @property
    def v1_url(self):
        return f'{settings.V1_URL}{self.link}'
