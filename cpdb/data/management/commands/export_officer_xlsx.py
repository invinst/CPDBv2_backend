from django.core.management import BaseCommand

from data.models import Officer
from officers.services.export_xlsx.accused import AccusedExcelWriter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('officer_id')

    def export_trrs(self, officer):
        pass

    def export_investigations(self, officer):
        pass

    def handle(self, officer_id, *args, **kwargs):
        officer = Officer.objects.get(id=officer_id)
        AccusedExcelWriter(officer).export_xlsx()
        self.export_trrs(officer)
        self.export_investigations(officer)
