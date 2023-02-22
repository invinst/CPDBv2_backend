import time

import requests
from data.constants import AttachmentSourceType
from data.models import AttachmentFile
from django.conf import settings
from django.db.models import F
from document_cloud.constants import REPROCESS_TEXT_MAX_RETRIES
from tqdm import tqdm
from urllib3.exceptions import HTTPError


class DocumentCloudSession(requests.Session):
    def __init__(self, log_func):
        super(DocumentCloudSession, self).__init__()
        self.log_func = log_func

        login_response = self.post(
            'https://accounts.muckrock.com/api/token',
            {'username': settings.DOCUMENTCLOUD_USER, 'password': settings.DOCUMENTCLOUD_PASSWORD}
        )
        if login_response.status_code != 200:
            self.log_func('[ERROR] Cannot login to document cloud to reprocessing text')
            self.log_func(f'[ERROR DETAIL]: : {login_response.json()}')
            raise requests.exceptions.RequestException(
                f'Cannot login {login_response.status_code}: {login_response.json()}'
            )

    def _request_reprocess_text(self, document):
        try:
            response = self.post(
                f'https://accounts.muckrock.com/api/documents/{document.external_id}/process',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
        except (requests.exceptions.RequestException, HTTPError) as e:
            self.log_func(f'[ERROR] when sending reprocess request for {document.url}: {e}')
            sent, success = False, False
        else:
            sent = True
            success = response.status_code == 200
            if success:
                self.log_func(f'[SUCCESS] Reprocessing text {document.url}')
            else:
                self.log_func(
                    f'[FAIL] Reprocessing text {document.url} failed'
                    f' with status code {response.status_code}: {response.json()}'
                )
        return sent, success

    def _request_reprocess_with_delay(self, reprocess_documents, delay_time=0.01):
        requested_ids = []
        success_count = 0
        for reprocess_document in tqdm(
            reprocess_documents.order_by('external_id'),
            desc=f'Reprocessing text on documentcloud'
        ):
            sent, success = self._request_reprocess_text(reprocess_document)
            if sent:
                requested_ids.append(reprocess_document.external_id)
            if success:
                success_count += 1
            time.sleep(delay_time)

        reprocess_documents.filter(external_id__in=requested_ids).update(
            reprocess_text_count=F('reprocess_text_count') + 1
        )
        return success_count

    def request_reprocess_missing_text_documents(self, ):
        no_text_documents = AttachmentFile.objects.filter(
            file_type='document',
            text_content='',
            source_type__in=AttachmentSourceType.DOCUMENTCLOUD_SOURCE_TYPES,
        )
        reprocess_documents = no_text_documents.filter(reprocess_text_count__lt=REPROCESS_TEXT_MAX_RETRIES)

        no_text_documents_count = no_text_documents.count()
        reprocess_documents_count = reprocess_documents.count()
        skipped_documents_count = no_text_documents_count - reprocess_documents_count

        success_count = self._request_reprocess_with_delay(reprocess_documents)
        failure_count = reprocess_documents_count - success_count

        self.log_func(
            'Sent reprocessing text requests: '
            f'{success_count} success, {failure_count} failure, {skipped_documents_count} skipped '
            f'for {no_text_documents_count} no-text documents'
        )
