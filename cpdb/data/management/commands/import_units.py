from csv import DictReader

from django.core.management import BaseCommand

from tqdm import tqdm

from data.models import PoliceUnit


class DescriptionMatcher(object):
    def __init__(self, context):
        self.context = context

    def perform(self, unit_name):
        candidates = [entry for entry in self.context if entry['Unit No.'] == unit_name]
        active_candidates = [candidate for candidate in candidates if candidate['Status'] == 'Y']

        if len(active_candidates) >= 1:
            return active_candidates[0]['Unit Description']

        return candidates[0]['Unit Description']


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path) as f:
            reader = DictReader(f)
            context = [row for row in reader]
            matcher = DescriptionMatcher(context=context)

            for unit in tqdm(PoliceUnit.objects.all(), 'Adding description for unit'):
                unit.description = matcher.perform(unit.unit_name).title()
                unit.save()
