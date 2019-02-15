from django.contrib.postgres.fields import JSONField
from django.db import models

from data.models.common import TimeStampsModel
from analytics import constants


class EventManager(models.Manager):
    def create_attachment_download_events(self, attachment_ids):
        return self.bulk_create([
            Event(name=constants.EVT_ATTACHMENT_DOWNLOAD, data={'id': attachment_id})
            for attachment_id in attachment_ids
        ])

    def get_attachment_download_events(self, attachment_ids=list()):
        queryset = self.filter(name=constants.EVT_ATTACHMENT_DOWNLOAD)
        if len(attachment_ids) > 0:
            queryset = queryset.filter(data__id__in=attachment_ids)
        return queryset

    def create_attachment_view_events(self, attachment_ids):
        return self.bulk_create([
            Event(name=constants.EVT_ATTACHMENT_VIEW, data={'id': attachment_id})
            for attachment_id in attachment_ids
        ])

    def get_attachment_view_events(self, attachment_ids=list()):
        queryset = self.filter(name=constants.EVT_ATTACHMENT_VIEW)
        if len(attachment_ids) > 0:
            queryset = queryset.filter(data__id__in=attachment_ids)
        return queryset


class Event(TimeStampsModel):
    name = models.CharField(max_length=255)
    data = JSONField()

    objects = EventManager()

    @property
    def attachment_id(self):
        if self.name not in [constants.EVT_ATTACHMENT_VIEW, constants.EVT_ATTACHMENT_DOWNLOAD]:
            return None
        try:
            return self.data['id']
        except KeyError:
            return None
