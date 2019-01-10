import shutil
import filecmp
import pytz
import os
from subprocess import call
from datetime import datetime

from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import OfficerFactory
from trr.factories import TRRFactory
from xlsx.writers.use_of_force_xlsx_writer import UseOfForceXlsxWriter

test_dir = os.path.dirname(__file__)
test_output_dir = f'{test_dir}/output'


class UseOfForceXlsxWriterTestCase(TestCase):
    def tearDown(self):
        shutil.rmtree(test_output_dir, ignore_errors=True)

    def test_file_name(self):
        officer = OfficerFactory(id=1)
        writer = UseOfForceXlsxWriter(officer, test_output_dir)
        expect(writer.file_name).to.eq('use_of_force_1.xlsx')

    def test_export_xlsx_empty(self):
        officer = OfficerFactory(id=1)
        writer = UseOfForceXlsxWriter(officer, test_output_dir)
        writer.export_xlsx()

        call(['xlsx2csv', f'{test_output_dir}/use_of_force_1.xlsx', f'{test_output_dir}/use_of_force_1.csv'])

        expect(
            filecmp.cmp(f'{test_output_dir}/use_of_force_1.csv', f'{test_dir}/csv/use_of_force_empty.csv')
        ).to.be.true()

    def test_export_xlsx(self):
        officer = OfficerFactory(id=1)
        TRRFactory(
            officer=officer,
            id='4',
            beat=1322,
            block='17XX',
            direction='West',
            street='Division St',
            location='Parking Lot/Garage(Non.Resid.)',
            trr_datetime=datetime(2004, 1, 17, 14, 47, tzinfo=pytz.utc),
            indoor_or_outdoor='Outdoor',
            lighting_condition='DAYLIGHT',
            weather_condition='OTHER',
            notify_OEMC=False,
            notify_district_sergeant=False,
            notify_OP_command=False,
            notify_DET_division=False,
            number_of_weapons_discharged=None,
            party_fired_first=None,
            location_recode='Parking Lot/Garage (Non-Residential)',
            taser=False,
            total_number_of_shots=0,
            firearm_used=False,
            number_of_officers_using_firearm=0,
            officer_assigned_beat='1368A',
            officer_unit__unit_name='1234',
            officer_unit_detail=None,
            officer_on_duty=True,
            officer_in_uniform=False,
            officer_injured=False,
            officer_rank='Police Officer',
            subject_id=1,
            subject_armed=False,
            subject_injured=True,
            subject_alleged_injury=True,
            subject_age=38,
            subject_birth_year=1965,
            subject_gender='M',
            subject_race='HISPANIC',
        )
        writer = UseOfForceXlsxWriter(officer, test_output_dir)
        writer.export_xlsx()

        call(['xlsx2csv', f'{test_output_dir}/use_of_force_1.xlsx', f'{test_output_dir}/use_of_force_1.csv'])

        expect(
            filecmp.cmp(f'{test_output_dir}/use_of_force_1.csv', f'{test_dir}/csv/use_of_force_1.csv')
        ).to.be.true()
