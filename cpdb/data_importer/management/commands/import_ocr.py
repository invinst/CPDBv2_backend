import csv
from io import StringIO

from urllib.request import urlopen
from tqdm import tqdm

from django.core.management import BaseCommand
from django.db.models import Prefetch

from data.models import AttachmentFile, AttachmentOCR


BATCH_SIZE = 1000


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--ocr-url', help='URL of the OCR csv file')

    def read_csv_from_url(self, url):
        ftp_stream = urlopen(url)
        text = ftp_stream.read().decode('utf-8')
        csv_file = csv.DictReader(StringIO(text), delimiter=',')
        return list(csv_file)

    def create_attachment_ocr_pages(self, sorted_ocr_csv_file):
        found_ocr_pages = 0
        missing_ocr_pages = []
        attachment_ocrs = []
        attachment_ids = set()
        LOG_KEYS = ['cr_id', 'filename', 'doccloud_url']

        for row in tqdm(sorted_ocr_csv_file):
            attachment = AttachmentFile.objects.for_allegation().filter(owner_id=row['cr_id'], url=row['doccloud_url']).first()
            log_values = [row[key] for key in LOG_KEYS]
            if attachment:
                attachment_ocrs.append(
                    AttachmentOCR(attachment=attachment, page_num=row['page_num'], ocr_text=row['ocr_text'])
                )
                found_ocr_pages += 1
                attachment_ids.add(attachment.id)
            else:
                missing_ocr_pages.append(log_values)

        AttachmentOCR.objects.bulk_create(attachment_ocrs, batch_size=BATCH_SIZE)

        print(f'Found OCR pages: {found_ocr_pages}')
        print(f'Missing OCR pages: {len(missing_ocr_pages)}')
        print('=== START Missing OCR pages ===')
        print(missing_ocr_pages)
        print('=== END Missing OCR pages ===')

        return attachment_ids

    def update_attachment_ocrs(self, attachment_ids):
        attachments = AttachmentFile.objects.filter(id__in=attachment_ids).prefetch_related(
            Prefetch('attachment_ocrs', queryset=AttachmentOCR.objects.order_by('page_num')))

        for attachment in tqdm(attachments):
            attachment.text_content = '\n'.join(
                [attachment_ocr.ocr_text for attachment_ocr in attachment.attachment_ocrs.all()])
            attachment.is_external_ocr = True

        AttachmentFile.bulk_objects.bulk_update(
            attachments, update_fields=['is_external_ocr', 'text_content'], batch_size=BATCH_SIZE
        )
        print(f'Updated attachment OCRs: {len(attachment_ids)}')

    def handle(self, *args, **options):
        ocr_csv_file = self.read_csv_from_url(options['ocr_url'])
        sorted_ocr_csv_file = list(sorted(ocr_csv_file, key=lambda row: row['filename'] + '_' + row['page_num']))
        found_attachment_ids = self.create_attachment_ocr_pages(sorted_ocr_csv_file)
        self.update_attachment_ocrs(found_attachment_ids)
