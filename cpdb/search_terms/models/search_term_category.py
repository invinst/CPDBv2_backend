from adminsortable.models import SortableMixin
from django.db import models

from data.models.common import TimeStampsModel


class SearchTermCategory(TimeStampsModel, SortableMixin):
    name = models.CharField(max_length=60)
    order_number = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['order_number']
        verbose_name_plural = 'Search term categories'

    def __str__(self):
        return self.name
