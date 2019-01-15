from datetime import datetime, date
from decimal import Decimal

import pytz
from robber.expect import expect

from data.factories import (
    OfficerFactory,
    AllegationFactory,
    OfficerAllegationFactory,
    AllegationCategoryFactory,
    VictimFactory,
    PoliceWitnessFactory,
    AreaFactory,
    PoliceUnitFactory,
)
from xlsx.tests.writer_base_test_case import WriterBaseTestCase
from xlsx.writers.accused_xlsx_writer import AccusedXlsxWriter


class AccusedXlsxWriterTestCase(WriterBaseTestCase):
    def test_file_name(self):
        officer = OfficerFactory(id=1)
        writer = AccusedXlsxWriter(officer, self.test_output_dir)
        expect(writer.file_name).to.eq('accused.xlsx')

    def test_export_xlsx_empty(self):
        officer = OfficerFactory(id=1)
        writer = AccusedXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('accused.xlsx')
        self.assert_csv_files_equal('empty', ['Allegation', 'Coaccused Officer', 'Beat', 'Police Witness', 'Victim'])

    def test_export_xlsx(self):
        allegation = AllegationFactory(
            crid='1009678',
            location='Tavern/Liquor Store',
            add1='37XX',
            add2='W 63RD ST',
            city='CHICAGO IL',
            old_complaint_address=None,
            incident_date=datetime(2007, 9, 28, 0, 0, tzinfo=pytz.utc),
            beat=AreaFactory(name='0823'),
            is_officer_complaint=True,
            coaccused_count=19
        )
        allegation1 = AllegationFactory(
            crid='1012803',
            location='Public Way - Other',
            add1='31XX',
            add2='N NEWCASTLE AVE',
            city='CHICAGO IL',
            old_complaint_address=None,
            incident_date=datetime(2005, 11, 1, 0, 0, tzinfo=pytz.utc),
            beat=AreaFactory(name='2511'),
            is_officer_complaint=False,
            coaccused_count=9
        )
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            middle_initial='A',
            middle_initial2=None,
            suffix_name=None,
        )
        officer1 = OfficerFactory(
            first_name='Jeffery',
            last_name='Aaron',
            middle_initial='M',
            middle_initial2=None,
            suffix_name=None,
            gender='M',
            race='White',
            appointed_date=date(2005, 9, 26),
            resignation_date=None,
            rank='Sergeant of Police',
            birth_year=1971,
            active='Yes',
            complaint_percentile=Decimal('61.2357'),
            civilian_allegation_percentile=Decimal('61.2069'),
            internal_allegation_percentile=Decimal('76.9384'),
            trr_percentile=Decimal('79.8763'),
            honorable_mention_percentile=Decimal('94.8669'),
            allegation_count=6,
            sustained_count=0,
            honorable_mention_count=61,
            unsustained_count=0,
            discipline_count=0,
            civilian_compliment_count=4,
            trr_count=7,
            major_award_count=0,
            current_badge='1424',
            last_unit=PoliceUnitFactory(unit_name='003'),
            current_salary=101442,
        )
        officer2 = OfficerFactory(
            first_name='Karina',
            last_name='Aaron',
            middle_initial=None,
            middle_initial2=None,
            suffix_name=None,
            gender='F',
            race='Hispanic',
            appointed_date=date(2005, 9, 26),
            resignation_date=None,
            rank='Police Officer',
            birth_year=1980,
            active='Yes',
            complaint_percentile=Decimal('72.0378'),
            civilian_allegation_percentile=Decimal('76.4252'),
            internal_allegation_percentile=Decimal('0.0000'),
            trr_percentile=Decimal('67.4458'),
            honorable_mention_percentile=Decimal('96.0992'),
            allegation_count=8,
            sustained_count=0,
            honorable_mention_count=71,
            unsustained_count=2,
            discipline_count=0,
            civilian_compliment_count=2,
            trr_count=4,
            major_award_count=0,
            current_badge='20373',
            last_unit=PoliceUnitFactory(unit_name='001'),
            current_salary=94122,
        )
        allegation_category = AllegationCategoryFactory(
            category='Illegal Search',
            allegation_name='Improper Search Of Person',
        )
        allegation_category1 = AllegationCategoryFactory(
            category='False Arrest',
            allegation_name='Illegal Arrest / False Arrest',
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            allegation_category=allegation_category,
            start_date=date(2007, 9, 28),
            end_date=None,
            recc_finding='',
            recc_outcome='Unknown',
            final_finding='',
            final_outcome='Unknown',
            disciplined=None,
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation1,
            allegation_category=allegation_category1,
            start_date=date(2007, 12, 21),
            end_date=date(2008, 5, 29),
            recc_finding='',
            recc_outcome='Unknown',
            final_finding='',
            final_outcome='Unknown',
            disciplined=None,
        )
        OfficerAllegationFactory(
            officer=officer1,
            allegation=allegation,
            allegation_category=allegation_category,
            start_date=date(1967, 10, 21),
            end_date=date(1980, 8, 1),
            recc_finding='',
            recc_outcome='Unknown',
            final_finding='SU',
            final_outcome='30 Day Suspension',
            disciplined=True,
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation=allegation,
            allegation_category=allegation_category,
            start_date=date(1970, 8, 13),
            end_date=date(1973, 9, 15),
            recc_finding='',
            recc_outcome='Unknown',
            final_finding='SU',
            final_outcome='Suspended Over 30 Days',
            final_outcome_class='',
            disciplined=True,
        )
        VictimFactory(
            allegation=allegation,
            gender='M',
            race='Hispanic',
            birth_year=1973,
        )
        VictimFactory(
            allegation=allegation1,
            gender='',
            race='',
            birth_year=None,
        )
        witness = OfficerFactory(
            first_name='Jeffery',
            last_name='Aaron',
            middle_initial='M',
            middle_initial2=None,
            suffix_name=None,
            gender='M',
            race='White',
            appointed_date=date(2005, 9, 26),
            resignation_date=None,
            rank='Sergeant of Police',
            birth_year=1971,
            active='Yes',
            complaint_percentile=Decimal('61.2357'),
            civilian_allegation_percentile=Decimal('61.2069'),
            internal_allegation_percentile=Decimal('76.9384'),
            trr_percentile=Decimal('79.8763'),
            honorable_mention_percentile=Decimal('94.8669'),
            allegation_count=6,
            sustained_count=0,
            honorable_mention_count=61,
            unsustained_count=0,
            discipline_count=0,
            civilian_compliment_count=4,
            trr_count=7,
            major_award_count=0,
            current_badge='1424',
            last_unit=PoliceUnitFactory(unit_name='003'),
            current_salary=101442,
        )
        PoliceWitnessFactory(
            officer=witness,
            allegation=allegation,
        )

        writer = AccusedXlsxWriter(officer, self.test_output_dir)
        writer.export_xlsx()

        self.covert_xlsx_to_csv('accused.xlsx')
        self.assert_csv_files_equal(
            'accused_8562',
            ['Allegation', 'Coaccused Officer', 'Beat', 'Police Witness', 'Victim']
        )
