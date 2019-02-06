from rest_framework.serializers import Serializer, CharField
from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from data.models import Officer, Allegation
from xlsx.tests.writer_base_test_case import WriterBaseTestCase
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class OfficerTestSerializer(Serializer):
    name = CharField(source='full_name')
    gender = CharField(source='gender_display', allow_blank=True)


class AllegationTestSerializer(Serializer):
    crid = CharField()
    summary = CharField(allow_blank=True)


class OfficerTestWriter(OfficerXlsxWriter):
    @property
    def file_name(self):
        return f'officer.xlsx'

    def write_officer_sheet(self):
        ws = self.wb.create_sheet('Officer', 0)
        self.write_sheet(ws, Officer.objects.all(), OfficerTestSerializer)

    def write_allegation_sheet(self):
        ws = self.wb.create_sheet('Allegation', 1)
        self.write_sheet(
            ws, Allegation.objects.filter(officerallegation__officer=self.officer), AllegationTestSerializer
        )

    def export_xlsx(self):
        self.write_officer_sheet()
        self.write_allegation_sheet()
        self.save()


class OfficerXlsxWriterTestCase(WriterBaseTestCase):
    def test_export_xlsx_file_successfully(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            gender='M',
        )
        allegation = AllegationFactory(
            crid='123456',
            summary='Heaven'
        )
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        writer = OfficerTestWriter(officer=officer, out_dir=self.test_output_dir)
        writer.export_xlsx()

        sheetnames = writer.wb.sheetnames
        expect(sheetnames).to.have.length(2)
        expect(sheetnames[0]).to.eq('Officer')
        expect(sheetnames[1]).to.eq('Allegation')

        self.covert_xlsx_to_csv('officer.xlsx')
        self.assert_csv_files_equal('', ['Officer', 'Allegation'])

    def test_raise_NotImplementedError(self):
        officer = OfficerFactory()
        writer = OfficerXlsxWriter(officer=officer, out_dir=self.test_output_dir)
        expect(writer.export_xlsx).to.throw(NotImplementedError)
