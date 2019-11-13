import time
import requests
from urllib3.exceptions import HTTPError

from django.db.models import F
from django.conf import settings

from tqdm import tqdm

from data.constants import AttachmentSourceType
from data.models import AttachmentFile
from document_cloud.constants import REPROCESS_TEXT_MAX_RETRIES


class DocumentCloudSession(requests.Session):
    def __init__(self, logger):
        super(DocumentCloudSession, self).__init__()
        self.logger = logger

        login_response = self.post(
            'https://www.documentcloud.org/login',
            {'email': settings.DOCUMENTCLOUD_USER, 'password': settings.DOCUMENTCLOUD_PASSWORD}
        )
        if login_response.status_code != 200:
            self.logger.error('Cannot login to document cloud to reprocessing text')
            raise requests.exceptions.RequestException(
                f'Cannot login {login_response.status_code}: {login_response.json()}'
            )

    def _request_reprocess_text(self, documentcloud_id):
        try:
            response = self.post(
                f'https://www.documentcloud.org/documents/{documentcloud_id}/reprocess_text',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
        except (requests.exceptions.RequestException, HTTPError) as e:
            self.logger.warn(f'Exception when sending reprocess {documentcloud_id} request: {e}')
            return False
        else:
            if response.status_code != 200:
                self.logger.warn(
                    f'Reprocessing text {documentcloud_id} failed'
                    f' with status code {response.status_code}: {response.json()}'
                )
            else:
                self.logger.info(f'Reprocessing text with id {documentcloud_id} success')
            return True

    def request_reprocess_missing_text_documents_with_delay(self, delay_time=0.01):
        no_text_documents = AttachmentFile.objects.filter(
            file_type='document',
            text_content='',
            source_type__in=AttachmentSourceType.DOCUMENTCLOUD_SOURCE_TYPES,
            reprocess_text_count__lt=REPROCESS_TEXT_MAX_RETRIES,
        )
        no_text_documents_ids = no_text_documents.values_list('external_id', flat=True).distinct()
        requested_ids = []
        for documentcloud_id in tqdm(no_text_documents_ids, desc=f'Reprocessing text on documentcloud'):
            if self._request_reprocess_text(documentcloud_id):
                requested_ids.append(documentcloud_id)
            time.sleep(delay_time)

        no_text_documents.filter(external_id__in=requested_ids).update(
            reprocess_text_count=F('reprocess_text_count') + 1
        )
