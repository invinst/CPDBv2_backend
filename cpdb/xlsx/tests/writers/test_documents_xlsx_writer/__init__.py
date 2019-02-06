from datetime import datetime

import pytz
from robber.expect import expect

from data.factories import (
    OfficerFactory, AllegationFactory, AttachmentFileFactory, OfficerAllegationFactory, InvestigatorFactory,
    InvestigatorAllegationFactory,
)
from xlsx.tests.writer_base_test_case import WriterBaseTestCase
from xlsx.writers.documents_xlsx_writer import DocumentsXlsxWriter


class DocumentsXlsxWriterTestCase(WriterBaseTestCase):
    def test_file_name(self):
        officer = OfficerFactory(id=1)
        writer = DocumentsXlsxWriter(officer, self.test_output_dir)
        expect(writer.file_name).to.eq('documents.xlsx')

    def test_export_xlsx_empty(self):
        officer = OfficerFactory(id=1)
        writer = DocumentsXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('documents.xlsx')
        self.assert_csv_files_equal('empty', ['Complaint Documents', 'Investigation Documents'])

    def test_export_xlsx(self):
        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            allegation=allegation,
            source_type='DOCUMENTCLOUD',
            title='CRID 1045950 CR Original Case Incident Report 1 of 5',
            url='https://assets.documentcloud.org/documents/5679592/CRID.pdf',
            external_created_at=datetime(2019, 1, 9, 9, 11, 38, 41928, tzinfo=pytz.utc),
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
        )
        AttachmentFileFactory(
            allegation=allegation,
            source_type='COPA_DOCUMENTCLOUD',
            title='CRID 1045950 CR Original Case Incident Report 2 of 5',
            url='https://assets.documentcloud.org/documents/5678901/CRID.pdf',
            external_created_at=datetime(2019, 1, 9, 9, 11, 38, 41929, tzinfo=pytz.utc),
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
        )
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(source_type='DOCUMENTCLOUD')

        officer = OfficerFactory(id=1)
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        allegation456 = AllegationFactory(crid='456')
        AttachmentFileFactory(
            allegation=allegation456,
            source_type='DOCUMENTCLOUD',
            title='CRID 1041253 CR Original Case Incident Report 1 of 5',
            url='https://assets.documentcloud.org/documents/1041253/CRID.pdf',
            external_created_at=datetime(2019, 1, 8, 9, 11, 38, 41928, tzinfo=pytz.utc),
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334111',
        )
        AttachmentFileFactory(
            allegation=allegation456,
            source_type='COPA_DOCUMENTCLOUD',
            title='CRID 1041253 CR Original Case Incident Report 2 of 5',
            url='https://assets.documentcloud.org/documents/1041253/CRID.pdf',
            external_created_at=datetime(2019, 1, 8, 9, 11, 38, 41927, tzinfo=pytz.utc),
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334111',
        )
        AttachmentFileFactory(allegation=allegation456, source_type='COPA')
        AttachmentFileFactory(source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(source_type='COPA_DOCUMENTCLOUD')

        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(allegation=allegation456, investigator=investigator)

        writer = DocumentsXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('documents.xlsx')
        self.assert_csv_files_equal('documents_1', ['Complaint Documents', 'Investigation Documents'])
