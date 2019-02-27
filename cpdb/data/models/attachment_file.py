import json
import logging
from urllib.error import HTTPError

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django_bulk_update.manager import BulkUpdateManager
from django.conf import settings
from documentcloud import DocumentCloud, DoesNotExistError

from data.constants import MEDIA_TYPE_CHOICES, MEDIA_TYPE_DOCUMENT, AttachmentSourceType
from shared.aws import aws
from .common import TimeStampsModel

logger = logging.getLogger(__name__)


class ShownAttachmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(show=True)


class AttachmentFile(TimeStampsModel):
    external_id = models.CharField(max_length=255, db_index=True)
    file_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, db_index=True)
    additional_info = JSONField(null=True)
    tag = models.CharField(max_length=50)
    original_url = models.CharField(max_length=255, db_index=True)
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE, related_name='attachment_files')
    source_type = models.CharField(max_length=255, db_index=True)
    views_count = models.IntegerField(default=0)
    downloads_count = models.IntegerField(default=0)
    notifications_count = models.IntegerField(default=0)
    show = models.BooleanField(default=True)
    manually_updated = models.BooleanField(default=False)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    # Document cloud information
    preview_image_url = models.CharField(max_length=255, null=True)
    external_created_at = models.DateTimeField(null=True)
    external_last_updated = models.DateTimeField(null=True)
    text_content = models.TextField(blank=True)
    pages = models.IntegerField(default=0)

    objects = BulkUpdateManager()
    showing = ShownAttachmentManager()

    class Meta:
        unique_together = (('allegation', 'external_id', 'source_type'),)

    @property
    def s3_key(self):
        return f'{settings.S3_BUCKET_PDF_DIRECTORY}/{self.external_id}'

    def upload_to_s3(self):
        aws.lambda_client.invoke_async(
            FunctionName=settings.LAMBDA_FUNCTION_UPLOAD_PDF,
            InvokeArgs=json.dumps({
                'url': self.url,
                'bucket': settings.S3_BUCKET_OFFICER_CONTENT,
                'key': self.s3_key
            })
        )

    @property
    def linked_documents(self):
        return AttachmentFile.showing.filter(
            allegation_id=self.allegation_id,
            file_type=MEDIA_TYPE_DOCUMENT,
        ).exclude(id=self.id)

    def update_to_documentcloud(self, field, value):
        if self.source_type not in [AttachmentSourceType.DOCUMENTCLOUD, AttachmentSourceType.COPA_DOCUMENTCLOUD]:
            return

        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        try:
            doc = client.documents.get(self.external_id)
        except DoesNotExistError:
            logger.error(f'Cannot find document with external id {self.external_id} on DocumentCloud')
            return

        setattr(doc, field, value)

        try:
            doc.save()
        except HTTPError:
            logger.error(f'Cannot save document with external id {self.external_id} on DocumentCloud')
