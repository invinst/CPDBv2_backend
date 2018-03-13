from django.core.management import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('table', nargs='+')

    def handle(self, *args, **kwargs):
        for table in kwargs['table']:
            model = apps.get_model(table)
            model.objects.all().delete()
