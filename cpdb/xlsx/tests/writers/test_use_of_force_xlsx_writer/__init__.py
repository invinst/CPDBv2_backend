from datetime import datetime

import pytz
from robber.expect import expect

from data.factories import OfficerFactory, PoliceUnitFactory
from trr.factories import TRRFactory
from xlsx.tests.writer_base_test_case import WriterBaseTestCase
from xlsx.writers.use_of_force_xlsx_writer import UseOfForceXlsxWriter


class UseOfForceXlsxWriterTestCase(WriterBaseTestCase):
    def test_file_name(self):
        officer = OfficerFactory(id=1)
        writer = UseOfForceXlsxWriter(officer, self.test_output_dir)
        expect(writer.file_name).to.eq('use_of_force_1.xlsx')

    def test_export_xlsx_empty(self):
        officer = OfficerFactory(id=1)
        writer = UseOfForceXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('use_of_force_1.xlsx')
        self.assert_csv_files_equal('empty', ['Use Of Force'])

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
            officer_unit=PoliceUnitFactory(unit_name='1234'),
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
        writer = UseOfForceXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('use_of_force_1.xlsx')
        self.assert_csv_files_equal('use_of_force_1', ['Use Of Force'])
