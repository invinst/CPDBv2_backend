import time

from airtable import Airtable
from requests.exceptions import HTTPError
from tqdm import tqdm

from config.settings.common import AIRTABLE_PROJECT_KEY, AIRTABLE_TABLE_NAME
from data.models import AttachmentRequest
from trr.models import TRRAttachmentRequest


class AirTableUploader(object):
    API_LIMIT = 1.0 / 5
    _lazy_airtable = None

    @classmethod
    def _build_explanation_and_request_desc(cls, raw_object):
        raise NotImplementedError

    @classmethod
    def _get_foia_airtable(cls):
        if cls._lazy_airtable is None:
            cls._lazy_airtable = Airtable(AIRTABLE_PROJECT_KEY, AIRTABLE_TABLE_NAME)
        return cls._lazy_airtable

    @classmethod
    def _build_record(cls, raw_object):
        explanation, request_desc = cls._build_explanation_and_request_desc(raw_object)
        return {
            'Explanation': explanation,
            'Project': [
                'CPDP'
            ],
            'Request Desc': request_desc,
            'Requestor': [
                {
                    'id': 'usrVdJCqxgnDTNRFW',
                    'email': 'andrew@invisibleinstitute.com',
                    'name': 'Andrew Fan'
                },
                {
                    'id': 'usrGiZFcyZ6wHTYWd',
                    'email': 'rajiv@invisibleinstitute.com',
                    'name': 'Rajiv Sinclair'
                }
            ]
        }

    @classmethod
    def _delay_upload(cls, raw_object):
        record = cls._build_record(raw_object)
        try:
            cls._get_foia_airtable().insert(record)
            time.sleep(cls.API_LIMIT)
        except HTTPError:
            return False
        return True

    @classmethod
    def _get_uploaded_objects(cls):
        raise NotImplementedError

    @classmethod
    def _post_handle(cls, upload_results):
        raise NotImplementedError

    @classmethod
    def upload(cls):
        raw_objects = cls._get_uploaded_objects()

        uploaded_results = [
            (raw_object, cls._delay_upload(raw_object))
            for raw_object in raw_objects
        ]
        cls._post_handle(uploaded_results)


class CRRequestAirTableUploader(AirTableUploader):
    @classmethod
    def _build_explanation_and_request_desc(cls, document_requests):
        allegation = document_requests.allegation
        officer_allegations = allegation.officerallegation_set.select_related('officer')\
            .order_by('officer__first_name', 'officer__last_name')
        officers_info = [
            "{officer_name}(ID {officer_id})".format(
                officer_id=officer_allegation.officer.id,
                officer_name=officer_allegation.officer.full_name
            )
            for officer_allegation in officer_allegations if officer_allegation.officer
        ]
        explanation = "Officers: {}".format(', '.join(officers_info)) if officers_info else ''
        request_desc = "CR {crid}(investigated by {investigator_name})".format(
            crid=allegation.crid,
            investigator_name=('CPD' if document_requests.investigated_by_cpd() else 'COPA')
        )
        return explanation, request_desc

    @classmethod
    def _get_uploaded_objects(cls):
        return AttachmentRequest.objects.filter(added_to_foia_airtable=False)

    @classmethod
    def _post_handle(cls, uploaded_results):
        uploaded_success = [document_request.id for document_request, success in uploaded_results if success]

        batch_size = 1000
        for i in tqdm(range(0, len(uploaded_success), batch_size)):
            batch_ids = uploaded_success[i:i + batch_size]
            AttachmentRequest.objects.filter(id__in=batch_ids).update(added_to_foia_airtable=True)


class TRRRequestAirTableUploader(AirTableUploader):
    @classmethod
    def _build_explanation_and_request_desc(cls, document_requests):
        officer = document_requests.trr.officer
        explanation = "Officer: {officer_name}(ID {officer_id})".format(
            officer_id=officer.id,
            officer_name=officer.full_name
        ) if officer else ''

        request_desc = "TRR {trrid}".format(trrid=document_requests.trr_id)
        return explanation, request_desc

    @classmethod
    def _get_uploaded_objects(cls):
        return TRRAttachmentRequest.objects.filter(added_to_foia_airtable=False)

    @classmethod
    def _post_handle(cls, uploaded_results):
        uploaded_success = [document_request.id for document_request, success in uploaded_results if success]

        batch_size = 1000
        for i in tqdm(range(0, len(uploaded_success), batch_size)):
            batch_ids = uploaded_success[i:i + batch_size]
            TRRAttachmentRequest.objects.filter(id__in=batch_ids).update(added_to_foia_airtable=True)
