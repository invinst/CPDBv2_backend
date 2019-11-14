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
    def __init__(self, log_func):
        super(DocumentCloudSession, self).__init__()
        self.log_func = log_func

        login_response = self.post(
            'https://www.documentcloud.org/login',
            {'email': settings.DOCUMENTCLOUD_USER, 'password': settings.DOCUMENTCLOUD_PASSWORD}
        )
        if login_response.status_code != 200:
            self.log_func('ERROR: Cannot login to document cloud to reprocessing text')
            raise requests.exceptions.RequestException(
                f'Cannot login {login_response.status_code}: {login_response.json()}'
            )

    def _request_reprocess_text(self, document):
        try:
            response = self.post(
                f'https://www.documentcloud.org/documents/{document.external_id}/reprocess_text',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
        except (requests.exceptions.RequestException, HTTPError) as e:
            self.log_func(f'Exception when sending reprocess request for {document.url}: {e}')
            sent, success = False, False
        else:
            if response.status_code == 200:
                self.log_func(f'Reprocessing text {document.url} success')
                sent, success = True, True
            else:
                self.log_func(
                    f'Reprocessing text {document.url} failed'
                    f' with status code {response.status_code}: {response.json()}'
                )
                sent, success = True, False
        return sent, success

    def request_reprocess_missing_text_documents_with_delay(self, delay_time=0.01):
        no_text_documents = AttachmentFile.objects.filter(
            file_type='document',
            text_content='',
            source_type__in=AttachmentSourceType.DOCUMENTCLOUD_SOURCE_TYPES,
        )
        reprocess_documents = no_text_documents.filter(reprocess_text_count__lt=REPROCESS_TEXT_MAX_RETRIES).distinct()
        requested_ids = []
        success_count = 0
        for reprocess_document in tqdm(reprocess_documents, desc=f'Reprocessing text on documentcloud'):
            sent, success = self._request_reprocess_text(reprocess_document)
            if sent:
                requested_ids.append(reprocess_document.external_id)
                if success:
                    success_count += 1
            time.sleep(delay_time)

        failure_count = reprocess_documents.count() - success_count
        skipped_documents_count = no_text_documents.filter(reprocess_text_count__gte=REPROCESS_TEXT_MAX_RETRIES).count()
        no_text_documents_count = no_text_documents.count()

        self.log_func(
            'Sent reprocessing text requests: '
            f'{success_count} success, {failure_count} failure, {skipped_documents_count} skipped '
            f'for {no_text_documents_count} no-text documents'
        )

        no_text_documents.filter(external_id__in=requested_ids).update(
            reprocess_text_count=F('reprocess_text_count') + 1
        )
