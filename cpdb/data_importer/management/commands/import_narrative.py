import csv
from io import StringIO

from urllib.request import urlopen
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import AttachmentFile, AttachmentNarrative


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--narrative-url', help='URL of the narrative csv file')

    def read_csv_from_url(self, url):
        ftp_stream = urlopen(url)
        text = ftp_stream.read().decode('utf-8')
        csv_file = csv.DictReader(StringIO(text), delimiter=',')
        return list(csv_file)

    def create_attachment_narratives(self, sorted_narrative_csv_file):
        found_narratives = 0
        missing_narratives = []
        attachment_narratives = []
        LOG_KEYS = ['cr_id', 'pdf_name', 'doccloud_url']

        for row in tqdm(sorted_narrative_csv_file):
            attachment = AttachmentFile.objects.filter(allegation_id=row['cr_id'], url=row['doccloud_url']).first()
            log_values = [row[key] for key in LOG_KEYS]
            if attachment:
                attachment_narratives.append(
                    AttachmentNarrative(
                        attachment=attachment,
                        page_num=row['page_num'],
                        section_name=row['section_name'],
                        column_name=row['column_name'],
                        text_content=row['text']
                    )
                )
                found_narratives += 1
            else:
                missing_narratives.append(log_values)

        AttachmentNarrative.objects.bulk_create(attachment_narratives)

        print(f'Found narratives: {found_narratives}')
        print(f'Missing narratives: {len(missing_narratives)}')
        print('=== START Missing Narratives ===')
        print(missing_narratives)
        print('=== END Missing Narratives ===')

    def handle(self, *args, **options):
        narrative_csv_file = self.read_csv_from_url(options['narrative_url'])
        sorted_narrative_csv_file = list(
            sorted(narrative_csv_file, key=lambda row: row['pdf_name'] + '_' + row['page_num'])
        )
        self.create_attachment_narratives(sorted_narrative_csv_file)
