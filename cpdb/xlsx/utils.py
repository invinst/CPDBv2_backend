
from data.models import Officer
from xlsx.writers.accused_xlsx_writer import AccusedXlsxWriter
from xlsx.writers.investigator_xlsx_writer import InvestigatorXlsxWriter
from xlsx.writers.use_of_force_xlsx_writer import UseOfForceXlsxWriter


def export_officer_xlsx(officer_id, out_dir):
    officer = Officer.objects.get(id=officer_id)
    AccusedXlsxWriter(officer, out_dir).export_xlsx()
    UseOfForceXlsxWriter(officer, out_dir).export_xlsx()
    InvestigatorXlsxWriter(officer, out_dir).export_xlsx()

    return [AccusedXlsxWriter.file_name, UseOfForceXlsxWriter.file_name, InvestigatorXlsxWriter.file_name]
