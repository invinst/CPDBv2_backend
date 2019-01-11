import filecmp
import os
import shutil
from subprocess import call

from django.test import TestCase
from rest_framework.serializers import Serializer, CharField

from robber import expect

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from data.models import Officer, Allegation
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter

test_dir = os.path.dirname(__file__)
test_output_dir = f'{test_dir}/output'


class OfficerTestSerializer(Serializer):
    name = CharField(source='full_name')
    gender = CharField(source='gender_display', allow_blank=True)


class AllegationTestSerializer(Serializer):
    crid = CharField()
    summary = CharField(allow_blank=True)


class OfficerTestWriter(OfficerXlsxWriter):
    @property
    def file_name(self):
        return f'officer_{self.officer.id}.xlsx'

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


class OfficerXlsxWriterTestCase(TestCase):
    def setUp(self):
        shutil.rmtree(test_output_dir, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(test_output_dir, ignore_errors=True)

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

        writer = OfficerTestWriter(officer=officer, out_dir=test_output_dir)
        writer.export_xlsx()

        sheetnames = writer.wb.sheetnames
        expect(sheetnames).to.have.length(2)
        expect(sheetnames[0]).to.eq('Officer')
        expect(sheetnames[1]).to.eq('Allegation')

        call([
            'xlsx2csv', f'{test_output_dir}/officer_8562.xlsx', test_output_dir, '-a'
        ])

        expect(
            filecmp.cmp(f'{test_output_dir}/Officer.csv', f'{test_dir}/csv/officer.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Allegation.csv', f'{test_dir}/csv/Allegation.csv')
        ).to.be.true()
