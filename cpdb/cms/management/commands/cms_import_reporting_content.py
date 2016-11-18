import csv
import re
from datetime import datetime

from django.core.management.base import BaseCommand

from cms.serializers import ReportPageSerializer
from cms.factories import LinkEntityFactory


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                serializer = ReportPageSerializer(
                    data=ReportPageSerializer().fake_data(
                        title=row['Headline'],
                        excerpt=filter(None, re.split(r'\n\s+', row['Excerpt (two paragraphs)'])),
                        publication=row['Name of the publication'],
                        publish_date=datetime.strptime(row['Date of publication'], '%m/%d/%Y').strftime('%Y-%m-%d'),
                        author=row['Byline(s)'],
                        article_link={
                            'blocks': ['Continue at %s' % row['Name of the publication']],
                            'entities': [
                                LinkEntityFactory(
                                    url=row['Link'],
                                    length=len(row['Name of the publication']),
                                    offset=12,
                                    block_index=0
                                )
                            ]
                        }
                    )
                )
                serializer.is_valid()
                serializer.save()
