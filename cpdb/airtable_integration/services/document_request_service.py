import time

from django.conf import settings

from airtable import Airtable
from requests.exceptions import HTTPError
from tqdm import tqdm

from data.models import AttachmentRequest
from trr.models import TRRAttachmentRequest


class AirTableUploader(object):
    API_LIMIT = 1.0 / 5
    _lazy_airtable = None

    @classmethod
    def _build_data(cls, raw_object):
        raise NotImplementedError

    @classmethod
    def _get_foia_airtable(cls):
        if cls._lazy_airtable is None:
            cls._lazy_airtable = Airtable(settings.AIRTABLE_PROJECT_KEY, settings.AIRTABLE_TABLE_NAME)
        return cls._lazy_airtable

    @classmethod
    def _build_record(cls, raw_object):
        explanation, requested_for, agencies = cls._build_data(raw_object)
        return {
            'Explanation': explanation,
            'Project': [
                'CPDP'
            ],
            'Agency': agencies,
            'Requested For': requested_for,
            'Requestor': [
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
    def _build_data(cls, document_request):
        allegation = document_request.allegation
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
        requested_for = "CR {crid}".format(crid=allegation.crid)
        agencies = [
            settings.AIRTABLE_CPD_AGENCY_ID
            if allegation.incident_date.year < 2006 or document_request.investigated_by_cpd()
            else settings.AIRTABLE_COPA_AGENCY_ID
        ]
        return explanation, requested_for, agencies

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
    def _build_data(cls, document_request):
        officer = document_request.trr.officer
        explanation = "Officer: {officer_name}(ID {officer_id})".format(
            officer_id=officer.id,
            officer_name=officer.full_name
        ) if officer else ''

        requested_for = "TRR {trrid}".format(trrid=document_request.trr_id)
        return explanation, requested_for, []

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
