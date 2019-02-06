from xlsx.writers.accused_xlsx_writer import AccusedXlsxWriter
from xlsx.writers.investigator_xlsx_writer import InvestigatorXlsxWriter
from xlsx.writers.use_of_force_xlsx_writer import UseOfForceXlsxWriter
from xlsx.writers.documents_xlsx_writer import DocumentsXlsxWriter

XlsxWriters = [AccusedXlsxWriter, UseOfForceXlsxWriter, InvestigatorXlsxWriter, DocumentsXlsxWriter]


def export_officer_xlsx(officer, out_dir):
    for writer_class in XlsxWriters:
        writer_class(officer, out_dir).export_xlsx()
    return [writer_class.file_name for writer_class in XlsxWriters]
