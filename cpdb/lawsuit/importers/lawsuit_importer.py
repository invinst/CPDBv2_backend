from datetime import datetime
import pytz

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.contenttypes.models import ContentType

from airtable import Airtable

from lawsuit.models import (
    Lawsuit,
    LawsuitPlaintiff,
    Payment,
)
from data.models import AttachmentFile
from data.constants import MEDIA_TYPE_DOCUMENT

BATCH_SIZE = 1000
LAWSUIT_UPDATE_FIELDS = [
    'case_no',
    'incident_date',
    'primary_cause',
    'summary',
    'location',
    'add1',
    'add2',
    'city',
    'point',
    'airtable_id',
    'airtable_updated_at',
    'outcomes',
    'misconducts',
    'violences',
    'interactions',
    'services',
]
PLAINTIFF_UPDATE_FIELDS = [
    'name',
    'lawsuit_id',
    'airtable_id',
    'airtable_updated_at',
]
PAYMENT_UPDATE_FIELDS = [
    'payee',
    'settlement',
    'legal_fees',
    'paid_date',
    'lawsuit_id',
    'airtable_id',
    'airtable_updated_at',
]
ATTACHMENT_UPDATE_FIELDS = [
    'title',
    'file_type',
    'url',
    'preview_image_url'
]


class LawsuitImporter(object):
    def __init__(self, logger=None, force_update=False):
        self.log_data = []
        self.logger = logger
        self.force_update = force_update
        self.airtable_lawsuits_data = []
        self.airtable_payments_data = []
        self.airtable_plaintiffs_data = []
        self.primary_cause_data_mapping = {}

    def log_info(self, message):
        if self.logger:
            self.logger.info(message)
        self.log_data.append(message)
        print(message)

    @staticmethod
    def parse_datetime(date_string):
        return datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=pytz.utc) if date_string else None

    def load_airtable_data(self):
        self.airtable_lawsuits_data = Airtable(
            settings.AIRTABLE_LAWSUITS_PROJECT_KEY, settings.AIRTABLE_LAWSUITS_TABLE_NAME
        ).get_all()
        self.airtable_payments_data = Airtable(
            settings.AIRTABLE_LAWSUITS_PROJECT_KEY, settings.AIRTABLE_PAYMENTS_TABLE_NAME
        ).get_all()
        self.airtable_plaintiffs_data = Airtable(
            settings.AIRTABLE_LAWSUITS_PROJECT_KEY, settings.AIRTABLE_PLAINTIFFS_TABLE_NAME
        ).get_all()
        self.primary_cause_data_mapping = {}
        for airtable_payment_data in self.airtable_payments_data:
            airtable_payment_fields = airtable_payment_data['fields']
            airtable_case = airtable_payment_fields.get('case')
            lawsuit_airtable_id = airtable_case[0] if airtable_case else None
            primary_cause = airtable_payment_fields.get('primary_cause_edited')
            if lawsuit_airtable_id and primary_cause:
                self.primary_cause_data_mapping[lawsuit_airtable_id] = primary_cause

    def lawsuit_data(self, airtable_lawsuit_data):
        airtable_lawsuit_fields = airtable_lawsuit_data['fields']
        case_no = airtable_lawsuit_fields.get('case_no')

        lon = airtable_lawsuit_fields.get('lon')
        lat = airtable_lawsuit_fields.get('lat')
        point = Point(lon, lat) if lon and lat else None
        address = airtable_lawsuit_fields.get('address', '').strip()
        if ' ' in address:
            add1, add2 = address.split(' ', 1)
        else:
            add1 = address
            add2 = ''
        city = ' '.join(list(filter(None, [airtable_lawsuit_fields.get('city'), airtable_lawsuit_fields.get('state')])))
        lawsuit_airtable_id = airtable_lawsuit_data['id']
        primary_cause = self.primary_cause_data_mapping.get(lawsuit_airtable_id)

        return {
            'airtable_id': lawsuit_airtable_id,
            'airtable_updated_at': airtable_lawsuit_fields.get('Last Modified Time'),
            'primary_cause': primary_cause,
            'case_no': case_no,
            'summary': airtable_lawsuit_fields.get('narrative', ''),
            'point': point,
            'incident_date': self.parse_datetime(airtable_lawsuit_fields.get('incident_date')),
            'location': airtable_lawsuit_fields.get('Location Description', ''),
            'add1': add1,
            'add2': add2,
            'city': city,
            'outcomes': airtable_lawsuit_fields.get('Incident Outcome', []),
            'misconducts': airtable_lawsuit_fields.get('misconduct type', []),
            'violences': airtable_lawsuit_fields.get('weapons', []),
            'interactions': airtable_lawsuit_fields.get('interaction', []),
            'services': airtable_lawsuit_fields.get('Officer Tags', []),
        }

    def update_lawsuits(self):
        new_lawsuits = []
        updated_lawsuits = []

        airtable_lawsuit_data_mapping = {}
        invalid_lawsuit_rows = []
        duplicated_rows = []
        for airtable_lawsuit_data in self.airtable_lawsuits_data:
            airtable_lawsuit_fields = airtable_lawsuit_data['fields']
            case_no = airtable_lawsuit_fields.get('case_no')

            if case_no:
                if case_no not in airtable_lawsuit_data_mapping:
                    airtable_lawsuit_data_mapping[case_no] = airtable_lawsuit_data
                elif len(airtable_lawsuit_data_mapping[case_no]['fields']) < len(airtable_lawsuit_data['fields']):
                    duplicated_rows.append(airtable_lawsuit_data_mapping[case_no])
                    airtable_lawsuit_data_mapping[case_no] = airtable_lawsuit_data
                else:
                    duplicated_rows.append(airtable_lawsuit_data)
            else:
                invalid_lawsuit_rows.append(airtable_lawsuit_data)

        if invalid_lawsuit_rows:
            self.log_info(f'==== LAWSUIT: Invalid rows ({len(invalid_lawsuit_rows)}) ====')
            for invalid_lawsuit_row in invalid_lawsuit_rows:
                self.log_info(invalid_lawsuit_row)
        if duplicated_rows:
            self.log_info(f'==== LAWSUIT: Duplicated rows ({len(duplicated_rows)}) ====')
            for duplicated_row in duplicated_rows:
                self.log_info(duplicated_row)

        all_case_no = airtable_lawsuit_data_mapping.keys()

        for airtable_lawsuit_data in airtable_lawsuit_data_mapping.values():
            airtable_lawsuit_fields = airtable_lawsuit_data['fields']
            airtable_id = airtable_lawsuit_data['id']
            case_no = airtable_lawsuit_fields.get('case_no')
            airtable_updated_at = airtable_lawsuit_fields.get('Last Modified Time')
            lawsuit = Lawsuit.objects.filter(case_no=case_no).first()

            if lawsuit:
                if lawsuit.airtable_id != airtable_id \
                        or lawsuit.airtable_updated_at != airtable_updated_at \
                        or self.force_update:
                    lawsuit_data = self.lawsuit_data(airtable_lawsuit_data)
                    for attr, value in lawsuit_data.items():
                        setattr(lawsuit, attr, value)
                    updated_lawsuits.append(lawsuit)

            else:
                lawsuit_data = self.lawsuit_data(airtable_lawsuit_data)
                new_lawsuits.append(Lawsuit(**lawsuit_data))

        if new_lawsuits:
            self.log_info(f'Creating {len(new_lawsuits)} lawsuits')
            Lawsuit.bulk_objects.bulk_create(new_lawsuits, batch_size=BATCH_SIZE)

        if updated_lawsuits:
            self.log_info(f'Updating {len(updated_lawsuits)} lawsuits')
            Lawsuit.bulk_objects.bulk_update(
                updated_lawsuits,
                update_fields=LAWSUIT_UPDATE_FIELDS,
                batch_size=BATCH_SIZE
            )

        deleted_lawsuits = Lawsuit.objects.exclude(case_no__in=all_case_no)
        self.log_info(f'Deleting {deleted_lawsuits.count()} lawsuits')
        deleted_lawsuits.delete()

    def update_lawsuit_primary_causes(self):
        updated_lawsuits = []
        for lawsuit in Lawsuit.objects.only('id', 'airtable_id', 'primary_cause'):
            primary_cause = self.primary_cause_data_mapping.get(lawsuit.airtable_id)
            if lawsuit.primary_cause != primary_cause:
                lawsuit.primary_cause = primary_cause
                updated_lawsuits.append(lawsuit)
        if updated_lawsuits:
            self.log_info(f'Updating {len(updated_lawsuits)} lawsuit primary causes')
            Lawsuit.bulk_objects.bulk_update(
                updated_lawsuits,
                update_fields=['primary_cause'],
                batch_size=BATCH_SIZE
            )

    def plaintiff_data(self, airtable_plaintiff_data, lawsuit_id):
        airtable_plaintiff_fields = airtable_plaintiff_data['fields']

        return {
            'airtable_id': airtable_plaintiff_data['id'],
            'airtable_updated_at': airtable_plaintiff_fields.get('Last Modified Time'),
            'name': airtable_plaintiff_fields.get('name'),
            'lawsuit_id': lawsuit_id,
        }

    def update_plaintiffs(self, lawsuit_mapping):
        new_plaintiffs = []
        updated_plaintiffs = []
        all_plaintiff_airtable_ids = set()
        invalid_plaintiff_rows = []

        for airtable_plaintiff_data in self.airtable_plaintiffs_data:
            plaintiff_airtable_id = airtable_plaintiff_data['id']
            airtable_plaintiff_fields = airtable_plaintiff_data['fields']
            airtable_case = airtable_plaintiff_fields.get('case')
            lawsuit_airtable_id = airtable_case[0] if airtable_case else None
            airtable_updated_at = airtable_plaintiff_fields.get('Last Modified Time')
            lawsuit_id = lawsuit_mapping.get(lawsuit_airtable_id)

            if lawsuit_id:
                all_plaintiff_airtable_ids.add(plaintiff_airtable_id)
                plaintiff = LawsuitPlaintiff.objects.filter(airtable_id=plaintiff_airtable_id).first()
                if plaintiff:
                    if plaintiff.airtable_updated_at != airtable_updated_at or self.force_update:
                        plaintiff_data = self.plaintiff_data(airtable_plaintiff_data, lawsuit_id)
                        for attr, value in plaintiff_data.items():
                            setattr(plaintiff, attr, value)
                        updated_plaintiffs.append(plaintiff)

                else:
                    plaintiff_data = self.plaintiff_data(airtable_plaintiff_data, lawsuit_id)
                    new_plaintiffs.append(LawsuitPlaintiff(**plaintiff_data))
            else:
                invalid_plaintiff_rows.append(airtable_plaintiff_data)

        if invalid_plaintiff_rows:
            self.log_info(f'==== PLAINTIFF: Invalid rows ({len(invalid_plaintiff_rows)}) ====')
            for invalid_plaintiff_row in invalid_plaintiff_rows:
                self.log_info(invalid_plaintiff_row)

        if new_plaintiffs:
            LawsuitPlaintiff.bulk_objects.bulk_create(new_plaintiffs, batch_size=BATCH_SIZE)

        if updated_plaintiffs:
            LawsuitPlaintiff.bulk_objects.bulk_update(
                updated_plaintiffs,
                update_fields=PLAINTIFF_UPDATE_FIELDS,
                batch_size=BATCH_SIZE
            )

        LawsuitPlaintiff.objects.exclude(airtable_id__in=list(all_plaintiff_airtable_ids)).delete()

    def payment_data(self, airtable_payment_data, lawsuit_id):
        airtable_payment_fields = airtable_payment_data['fields']

        return {
            'airtable_id': airtable_payment_data['id'],
            'airtable_updated_at': airtable_payment_fields.get('Last Modified Time'),
            'lawsuit_id': lawsuit_id,
            'payee': airtable_payment_fields.get('payee'),
            'settlement': airtable_payment_fields.get('payment'),
            'legal_fees': airtable_payment_fields.get('fees_costs'),
            'paid_date': self.parse_datetime(airtable_payment_fields.get('date_paid')),
        }

    def update_payments(self, lawsuit_mapping):
        new_payments = []
        updated_payments = []
        all_payment_airtable_ids = set()
        invalid_payment_rows = []

        for airtable_payment_data in self.airtable_payments_data:
            payment_airtable_id = airtable_payment_data['id']
            airtable_payment_fields = airtable_payment_data['fields']
            airtable_case = airtable_payment_fields.get('case')
            lawsuit_airtable_id = airtable_case[0] if airtable_case else None
            airtable_updated_at = airtable_payment_fields.get('Last Modified Time')
            lawsuit_id = lawsuit_mapping.get(lawsuit_airtable_id)

            if lawsuit_id:
                all_payment_airtable_ids.add(payment_airtable_id)
                payment = Payment.objects.filter(airtable_id=payment_airtable_id).first()
                if payment:
                    if payment.airtable_updated_at != airtable_updated_at or self.force_update:
                        payment_data = self.payment_data(airtable_payment_data, lawsuit_id)
                        for attr, value in payment_data.items():
                            setattr(payment, attr, value)
                        updated_payments.append(payment)

                else:
                    payment_data = self.payment_data(airtable_payment_data, lawsuit_id)
                    new_payments.append(Payment(**payment_data))
            else:
                invalid_payment_rows.append(airtable_payment_data)

        if invalid_payment_rows:
            self.log_info(f'==== PAYMENT: Invalid rows ({len(invalid_payment_rows)}) ====')
            for invalid_payment_row in invalid_payment_rows:
                self.log_info(invalid_payment_row)

        if new_payments:
            Payment.bulk_objects.bulk_create(new_payments, batch_size=BATCH_SIZE)

        if updated_payments:
            Payment.bulk_objects.bulk_update(
                updated_payments,
                update_fields=PAYMENT_UPDATE_FIELDS,
                batch_size=BATCH_SIZE
            )

        Payment.objects.exclude(airtable_id__in=list(all_payment_airtable_ids)).delete()

    def attachment_data(self, case_no, attachment_url):
        return {
            'title': case_no,
            'file_type': MEDIA_TYPE_DOCUMENT,
            # TODO add preview_image_url from documentcloud
            'preview_image_url': '',
            'url': attachment_url,
        }

    def update_attachments(self, lawsuit_mapping, lawsuit_attachment_mapping):
        new_attachments = []
        updated_attachments = []
        deleted_attachments = []

        lawsuit_content_type = ContentType.objects.get(app_label='lawsuit', model='lawsuit')

        for airtable_lawsuit_data in self.airtable_lawsuits_data:
            airtable_lawsuit_fields = airtable_lawsuit_data['fields']
            lawsuit_airtable_id = airtable_lawsuit_data['id']
            attachment = lawsuit_attachment_mapping.get(lawsuit_airtable_id)
            attachment_url = airtable_lawsuit_fields.get('complaint_url')
            case_no = airtable_lawsuit_fields.get('case_no')
            lawsuit_id = lawsuit_mapping.get(lawsuit_airtable_id)

            if lawsuit_id:
                if attachment:
                    if attachment_url:
                        attachment_data = self.attachment_data(case_no, attachment_url)
                        if attachment_url != attachment.url:
                            for attr, value in attachment_data.items():
                                setattr(attachment, attr, value)
                            updated_attachments.append(attachment)
                    else:
                        deleted_attachments.append(attachment)
                else:
                    if attachment_url and lawsuit_id:
                        attachment_data = self.attachment_data(case_no, attachment_url)
                        new_attachments.append(
                            AttachmentFile(
                                **attachment_data,
                                owner_id=lawsuit_id,
                                owner_type=lawsuit_content_type,
                            )
                        )

        if new_attachments:
            AttachmentFile.bulk_objects.bulk_create(new_attachments, batch_size=BATCH_SIZE)

        if updated_attachments:
            AttachmentFile.bulk_objects.bulk_update(
                updated_attachments,
                update_fields=ATTACHMENT_UPDATE_FIELDS,
                batch_size=BATCH_SIZE
            )

        if deleted_attachments:
            deleted_attachment_ids = [attachment.id for attachment in deleted_attachments]
            AttachmentFile.objects.filter(id__in=deleted_attachment_ids).delete()

    def update_data(self):
        self.load_airtable_data()
        self.update_lawsuits()
        self.update_lawsuit_primary_causes()
        lawsuits = Lawsuit.objects.prefetch_related('attachment_files').all()
        lawsuit_mapping = {lawsuit.airtable_id: lawsuit.id for lawsuit in lawsuits}
        self.update_plaintiffs(lawsuit_mapping)
        self.update_payments(lawsuit_mapping)
        lawsuit_attachment_mapping = {lawsuit.airtable_id: lawsuit.attachment for lawsuit in lawsuits}
        self.update_attachments(lawsuit_mapping, lawsuit_attachment_mapping)
