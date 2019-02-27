from django.db import models
from django.conf import settings

from data.models.common import TimeStampsModel
from document_cloud.constants import DOCUMENT_CRAWLER_STATUS_CHOICES
from shared.aws import aws


class DocumentCrawler(TimeStampsModel):
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_successful_run = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)
    status = models.CharField(max_length=20, null=True, choices=DOCUMENT_CRAWLER_STATUS_CHOICES)
    log_key = models.CharField(max_length=255, null=True)

    @property
    def log_url(self):
        if self.log_key:
            return aws.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': settings.S3_BUCKET_CRAWLER_LOG,
                    'Key': self.log_key,
                }
            )
        else:
            return None
