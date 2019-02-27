from django.conf import settings
from datetime import datetime
import pytz

from data.models import AttachmentFile
from document_cloud.constants import DOCUMENT_CRAWLER_SUCCESS, DOCUMENT_CRAWLER_FAILED
from document_cloud.models import DocumentCrawler
from shared.aws import aws


class BaseAttachmentImporter(object):
    source_type = None
    all_source_types = None

    def __init__(self, logger):
        self.log_data = []
        self.logger = logger

    def log_info(self, message):
        self.logger.info(message)
        self.log_data.append(message)

    def generate_s3_log_file(self):
        filename = datetime.now(pytz.utc).strftime(format='%Y-%m-%d-%H%M%S.txt')
        log_key = f'{self.source_type.lower()}/{filename}'
        aws.s3.put_object(
            Body='\n'.join(self.log_data).encode(),
            Bucket=settings.S3_BUCKET_CRAWLER_LOG,
            Key=log_key
        )
        return log_key

    def get_current_num_successful_run(self):
        return DocumentCrawler.objects.filter(source_type=self.source_type, status='Success').count()

    def record_success_crawler_result(self, num_new_attachments, num_updated_attachments):
        num_documents = AttachmentFile.objects.filter(
            source_type__in=self.all_source_types
        ).count()

        self.log_info(f'Creating {num_new_attachments} attachments')
        self.log_info(f'Updating {num_updated_attachments} attachments')
        self.log_info(f'Total {self.source_type.lower()} attachments: {num_documents}')
        self.log_info('Done importing!')

        log_key = self.generate_s3_log_file()

        DocumentCrawler.objects.create(
            source_type=self.source_type,
            status=DOCUMENT_CRAWLER_SUCCESS,
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=num_updated_attachments,
            num_successful_run=self.get_current_num_successful_run() + 1,
            log_key=log_key
        )

    def record_failed_crawler_result(self):
        self.log_info(
            f'Error occurred! Cannot update documents.'
        )
        log_key = self.generate_s3_log_file()

        DocumentCrawler.objects.create(
            source_type=self.source_type,
            status=DOCUMENT_CRAWLER_FAILED,
            num_successful_run=self.get_current_num_successful_run(),
            log_key=log_key
        )
