import shutil
import filecmp
from decimal import Decimal

import pytz
import os
from subprocess import call
from datetime import datetime, date

from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import (
    OfficerFactory,
    AllegationFactory,
    OfficerAllegationFactory,
    AllegationCategoryFactory,
    VictimFactory,
    PoliceWitnessFactory,
    InvestigatorAllegationFactory,
    InvestigatorFactory,
)
from xlsx.writers.investigator_xlsx_writer import InvestigatorXlsxWriter

test_dir = os.path.dirname(__file__)
test_output_dir = f'{test_dir}/output'


class InvestigatorXlsxWriterTestCase(TestCase):
    def tearDown(self):
        shutil.rmtree(test_output_dir, ignore_errors=True)

    def test_file_name(self):
        officer = OfficerFactory(id=1)
        writer = InvestigatorXlsxWriter(officer, test_output_dir)
        expect(writer.file_name).to.eq('investigator_1.xlsx')

    def test_export_xlsx_empty(self):
        officer = OfficerFactory(id=1)
        writer = InvestigatorXlsxWriter(officer, test_output_dir)
        writer.export_xlsx()

        call([
            'xlsx2csv', f'{test_output_dir}/investigator_1.xlsx', test_output_dir, '-a'
        ])

        expect(
            filecmp.cmp(f'{test_output_dir}/Allegation.csv', f'{test_dir}/csv/empty/Allegation.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Accused Officer.csv', f'{test_dir}/csv/empty/Accused Officer.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Beat.csv', f'{test_dir}/csv/empty/Beat.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Police Witness.csv', f'{test_dir}/csv/empty/Police Witness.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Victim.csv', f'{test_dir}/csv/empty/Victim.csv')
        ).to.be.true()

    def test_export_xlsx(self):
        investigator = InvestigatorFactory(officer__id=1234)
        allegation = AllegationFactory(
            crid='1009678',
            location='Tavern/Liquor Store',
            add1='37XX',
            add2='W 63RD ST',
            city='CHICAGO IL',
            old_complaint_address=None,
            incident_date=datetime(2007, 9, 28, 0, 0, tzinfo=pytz.utc),
            beat__name='0823',
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
            beat__name='2511',
            is_officer_complaint=False,
            coaccused_count=9
        )
        InvestigatorAllegationFactory(investigator=investigator, allegation=allegation)
        InvestigatorAllegationFactory(investigator=investigator, allegation=allegation1)
        officer = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan',
            middle_initial='A',
            middle_initial2=None,
            suffix_name=None,
            gender='M',
            race='White',
            appointed_date=date(1988, 12, 5),
            resignation_date=date(2008, 8, 5),
            rank='Police Officer',
            birth_year=1963,
            active='No',
            complaint_percentile=Decimal('99.9751'),
            civilian_allegation_percentile=Decimal('99.9778'),
            internal_allegation_percentile=Decimal('99.8056'),
            trr_percentile=Decimal('64.3694'),
            honorable_mention_percentile=Decimal('0.0000'),
            allegation_count=175,
            sustained_count=6,
            honorable_mention_count=1,
            unsustained_count=112,
            discipline_count=2,
            civilian_compliment_count=0,
            trr_count=1,
            major_award_count=0,
            current_badge='5167',
            last_unit__unit_name='003',
            current_salary=73116,
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
            last_unit__unit_name='003',
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
            last_unit__unit_name='001',
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
            last_unit__unit_name='003',
            current_salary=101442,
        )
        PoliceWitnessFactory(
            officer=witness,
            allegation=allegation,
        )

        writer = InvestigatorXlsxWriter(investigator.officer, test_output_dir)
        writer.export_xlsx()
        call([
            'xlsx2csv', f'{test_output_dir}/investigator_1234.xlsx', test_output_dir, '-a'
        ])

        expect(
            filecmp.cmp(f'{test_output_dir}/Allegation.csv', f'{test_dir}/csv/investigator_1234/Allegation.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Accused Officer.csv', f'{test_dir}/csv/investigator_1234/Accused Officer.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Beat.csv', f'{test_dir}/csv/investigator_1234/Beat.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Police Witness.csv', f'{test_dir}/csv/investigator_1234/Police Witness.csv')
        ).to.be.true()
        expect(
            filecmp.cmp(f'{test_output_dir}/Victim.csv', f'{test_dir}/csv/investigator_1234/Victim.csv')
        ).to.be.true()
