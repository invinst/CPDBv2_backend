import logging
from csv import DictReader

from django.core.management import BaseCommand

from tqdm import tqdm

from data.models import Allegation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path) as f:
            reader = DictReader(f)

            for row in tqdm(reader, desc='Updating summary'):
                try:
                    cr = Allegation.objects.get(crid=row['crid'])
                    summary = row['summary']
                    if cr and cr.summary != summary:
                        cr.summary = summary
                        cr.save()
                except Allegation.DoesNotExist:
                    # TODO: since it is not enough data, we not yet import to real db
                    logger.warning(f"cr {row['crid']} does not exist")
