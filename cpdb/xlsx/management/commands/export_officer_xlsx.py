from django.core.management import BaseCommand

from data.models import Officer
from xlsx.writers.accused_xlsx_writer import AccusedXlsxWriter
from xlsx.writers.investigator_xlsx_writer import InvestigatorXlsxWriter
from xlsx.writers.use_of_force_xlsx_writer import UseOfForceXlsxWriter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('officer_id')

    def export_investigations(self, officer):
        pass

    def handle(self, officer_id, *args, **kwargs):
        officer = Officer.objects.get(id=officer_id)
        AccusedXlsxWriter(officer).export_xlsx()
        UseOfForceXlsxWriter(officer).export_xlsx()
        InvestigatorXlsxWriter(officer).export_xlsx()
