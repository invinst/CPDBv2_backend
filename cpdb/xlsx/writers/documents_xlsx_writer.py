from xlsx.constants import DOCUMENTS_XLSX
from xlsx.serializers.attachment_xlsx_serializer import AttachmentXlsxSerializer
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class DocumentsXlsxWriter(OfficerXlsxWriter):
    file_name = DOCUMENTS_XLSX

    def write_complaint_documents_sheet(self):
        ws = self.wb.create_sheet('Complaint Documents', 0)
        self.write_sheet(ws, self.officer.allegation_attachments, AttachmentXlsxSerializer)

    def write_investigation_documents_sheet(self):
        ws = self.wb.create_sheet('Investigation Documents', 1)
        self.write_sheet(ws, self.officer.investigator_attachments, AttachmentXlsxSerializer)

    def export_xlsx(self):
        self.write_complaint_documents_sheet()
        self.write_investigation_documents_sheet()
        self.save()
