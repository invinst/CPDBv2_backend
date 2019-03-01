from django.contrib.gis.db import models

from analytics import constants


class AttachmentTrackingManager(models.Manager):
    def create_attachment_download_events(self, attachments):
        self.bulk_create([
            AttachmentTracking(
                attachment_file=attachment,
                kind=constants.DOWNLOAD_EVENT_TYPE
            )
            for attachment in attachments
        ])


class AttachmentTracking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    attachment_file = models.ForeignKey('data.AttachmentFile', on_delete=models.CASCADE, null=False)
    accessed_from_page = models.CharField(max_length=50, blank=True, default='')
    app = models.CharField(max_length=50, blank=True, default='')
    kind = models.CharField(
        max_length=50,
        choices=constants.ATTACHMENT_FILE_TRACKING_EVENT_TYPE,
        default=constants.VIEW_EVENT_TYPE)

    objects = AttachmentTrackingManager()
