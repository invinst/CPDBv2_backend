import json

from django.core.management.base import BaseCommand
from django.conf import settings

from documentcloud import DocumentCloud
from documentcloud.toolbox import DoesNotExistError
from tqdm import tqdm

from data.models import AttachmentFile
from document_cloud.services.documentcloud_service import DocumentcloudService


class Command(BaseCommand):
    help = 'Update linked document\'s meta data on Document Cloud'

    def get_document_id(self, attachment_file, document_service):
        additional_info = attachment_file.additional_info
        if type(additional_info) is unicode:
            additional_info = json.loads(additional_info)

        if 'documentcloud_id' in additional_info:
            return additional_info['documentcloud_id']
        else:
            return document_service.parse_link(attachment_file.url)['documentcloud_id']

    def handle(self, *args, **options):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
        document_service = DocumentcloudService()

        tqdm_list = tqdm(AttachmentFile.cloud_document.all())

        for attachment_file in tqdm_list:
            tqdm_list.set_description('Process %s - %s' % (attachment_file.id, attachment_file.title))

            document_id = self.get_document_id(attachment_file, document_service)
            try:
                document = client.documents.get(document_id)
                document_service.update_document_meta_data(document, attachment_file)
            except DoesNotExistError:
                pass  # Some documents we dont have enough permission to read or edit
