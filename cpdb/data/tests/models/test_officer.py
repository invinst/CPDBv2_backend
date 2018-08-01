from datetime import date

import pytz
from django.test.testcases import TestCase, override_settings
from django.utils.timezone import datetime

from freezegun import freeze_time
from robber.expect import expect

from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory,
    OfficerAllegationFactory, AwardFactory,
    AllegationFactory, ComplainantFactory, AllegationCategoryFactory, SalaryFactory,
)
from data.models import Officer, Salary


class OfficerTestCase(TestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        first = 'first'
        last = 'last'
        url = 'domain/officer/first-last/1'
        expect(Officer(first_name=first, last_name=last, pk=1).v1_url).to.eq(url)

    def test_v2_to(self):
        expect(Officer(pk=1).v2_to).to.eq('/officer/1/')

    def test_get_absolute_url(self):
        expect(Officer(pk=1).get_absolute_url()).to.eq('/officer/1/')

    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_current_age(self):
        expect(OfficerFactory(birth_year=1968).current_age).to.eq(49)

    def test_current_badge_not_found(self):
        officer = OfficerFactory()
        expect(officer.current_badge).to.equal('')
        OfficerBadgeNumberFactory(officer=officer, current=False)
        expect(officer.current_badge).to.equal('')

    def test_current_badge(self):
        officer = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer, star='123', current=True)
        expect(officer.current_badge).to.eq('123')

    def test_historic_units(self):
        officer = OfficerFactory()
        unithistory1 = OfficerHistoryFactory(officer=officer, unit__unit_name='1',
                                             unit__description='Unit 1', effective_date=date(2000, 1, 1))
        unithistory2 = OfficerHistoryFactory(officer=officer, unit__unit_name='2',
                                             unit__description='Unit 2', effective_date=date(2000, 1, 2))
        expect(officer.historic_units).to.eq([unithistory2.unit, unithistory1.unit])

    def test_historic_badges(self):
        officer = OfficerFactory()
        expect(officer.historic_badges).to.be.empty()
        OfficerBadgeNumberFactory(officer=officer, star='000', current=True)
        OfficerBadgeNumberFactory(officer=officer, star='123', current=False)
        OfficerBadgeNumberFactory(officer=officer, star='456', current=False)
        expect(list(officer.historic_badges)).to.eq(['123', '456'])

    def test_gender_display(self):
        expect(OfficerFactory(gender='M').gender_display).to.equal('Male')
        expect(OfficerFactory(gender='F').gender_display).to.equal('Female')
        expect(OfficerFactory(gender='X').gender_display).to.equal('X')

    def test_gender_display_keyerror(self):
        expect(OfficerFactory(gender='').gender_display).to.equal('')

    def test_honorable_mention_count(self):
        officer = OfficerFactory()
        AwardFactory(officer=officer, award_type='Other')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        AwardFactory(officer=officer, award_type='ABC Honorable Mention')

        expect(officer.honorable_mention_count).to.eq(2)

    def test_civilian_compliment_count(self):
        officer = OfficerFactory()
        AwardFactory(officer=officer, award_type='Other')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        AwardFactory(officer=officer, award_type='ABC Honorable Mention')

        expect(officer.civilian_compliment_count).to.eq(2)

    def test_last_unit(self):
        officer = OfficerFactory()
        expect(officer.last_unit).to.equal(None)

        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'), end_date=date(2000, 1, 1))
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='BDCH'), end_date=date(2002, 1, 1))
        expect(officer.last_unit.unit_name).to.eq('BDCH')

    def test_abbr_name(self):
        officer = OfficerFactory(first_name='Michel', last_name='Foo')
        expect(officer.abbr_name).to.eq('M. Foo')

    def test_discipline_count(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(officer=officer, disciplined=True)
        OfficerAllegationFactory(officer=officer, disciplined=False)
        expect(officer.discipline_count).to.eq(1)

    def test_visual_token_background_color(self):
        crs_colors = [
            (0, '#f5f4f4'),
            (3, '#edf0fa'),
            (7, '#d4e2f4'),
            (20, '#c6d4ec'),
            (30, '#aec9e8'),
            (45, '#90b1f5')
        ]
        for cr, color in crs_colors:
            officer = OfficerFactory()
            OfficerAllegationFactory.create_batch(cr, officer=officer)
            expect(officer.visual_token_background_color).to.eq(color)

    @override_settings(VISUAL_TOKEN_STORAGEACCOUNTNAME='cpdbdev')
    def test_visual_token_png_url(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_url).to.eq('https://cpdbdev.blob.core.windows.net/visual-token/officer_90.png')

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='media_folder')
    def test_visual_token_png_path(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_path).to.eq('media_folder/officer_90.png')

    def test_get_unit_by_date(self):
        officer = OfficerFactory()
        unit_100 = PoliceUnitFactory()
        unit_101 = PoliceUnitFactory()
        OfficerHistoryFactory(
            officer=officer,
            unit=unit_100,
            effective_date=date(2000, 1, 1),
            end_date=date(2005, 12, 31),
        )
        OfficerHistoryFactory(
            officer=officer,
            unit=unit_101,
            effective_date=date(2006, 1, 1),
            end_date=date(2010, 12, 31),
        )
        expect(officer.get_unit_by_date(date(1999, 1, 1))).to.be.none()
        expect(officer.get_unit_by_date(date(2001, 1, 1))).to.eq(unit_100)
        expect(officer.get_unit_by_date(date(2007, 1, 1))).to.eq(unit_101)
        expect(officer.get_unit_by_date(date(2011, 1, 1))).to.be.none()

    def test_complaint_category_aggregation(self):
        officer = OfficerFactory()

        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=None,
            final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=date(
                2010, 1, 1),
            final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=date(
                2011, 1, 1),
            final_finding='SU'
        )

        expect(officer.complaint_category_aggregation).to.eq([
            {
                'name': 'Use of Force',
                'count': 3,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Use of Force'
                    }, {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'Use of Force'
                    }
                ]
            }
        ])

    def test_complainant_race_aggregation(self):
        officer = OfficerFactory()

        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        allegation3 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation3, start_date=None, final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, race='White')
        ComplainantFactory(allegation=allegation2, race='')
        ComplainantFactory(allegation=allegation3, race='White')

        expect(officer.complainant_race_aggregation).to.eq([
            {
                'name': 'White',
                'count': 2,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'White'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_race_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_race_aggregation).to.eq([])

    def test_complainant_age_aggregation(self):
        officer = OfficerFactory()

        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, age=23)
        ComplainantFactory(allegation=allegation2, age=None)

        expect(officer.complainant_age_aggregation).to.eq([
            {
                'name': '21-30',
                'count': 1,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': '21-30'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_gender_aggregation(self):
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, gender='F')
        ComplainantFactory(allegation=allegation2, gender='')
        expect(officer.complainant_gender_aggregation).to.eq([
            {
                'name': 'Female',
                'count': 1,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'Female'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_gender_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_gender_aggregation).to.eq([])

    def test_major_award_count(self):
        officer = OfficerFactory()
        AwardFactory(officer=officer, award_type='HONORED POLICE STAR')
        AwardFactory(officer=officer, award_type='POLICE MEDAL')
        AwardFactory(officer=officer, award_type='PIPE BAND AWARD')
        AwardFactory(officer=officer, award_type='LIFE SAVING AWARD')
        expect(officer.major_award_count).to.eq(2)

    def test_coaccusals(self):
        officer0 = OfficerFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation0 = AllegationFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer0, allegation=allegation0)
        OfficerAllegationFactory(officer=officer0, allegation=allegation1)
        OfficerAllegationFactory(officer=officer0, allegation=allegation2)
        OfficerAllegationFactory(officer=officer1, allegation=allegation0)
        OfficerAllegationFactory(officer=officer1, allegation=allegation1)
        OfficerAllegationFactory(officer=officer2, allegation=allegation2)

        coaccusals = list(officer0.coaccusals)
        expect(coaccusals).to.have.length(2)
        expect(coaccusals).to.contain(officer1)
        expect(coaccusals).to.contain(officer2)

        expect(coaccusals[coaccusals.index(officer1)].coaccusal_count).to.eq(2)
        expect(coaccusals[coaccusals.index(officer2)].coaccusal_count).to.eq(1)

    def test_current_salary(self):
        officer = OfficerFactory()
        expect(officer.current_salary).to.be.none()

        SalaryFactory(officer=officer, year=2010, salary=5000)
        SalaryFactory(officer=officer, year=2012, salary=10000)
        SalaryFactory(officer=officer, year=2015, salary=15000)
        SalaryFactory(officer=officer, year=2017, salary=20000)

        expect(officer.current_salary).to.eq(20000)

    def test_unsustained_count(self):
        allegation = AllegationFactory()
        officer = OfficerFactory()
        OfficerAllegationFactory(allegation=allegation, final_finding='NS', officer=officer)
        OfficerAllegationFactory(allegation=allegation, final_finding='NS', officer=officer)
        expect(officer.unsustained_count).to.eq(2)

    def test_sustained_count(self):
        allegation = AllegationFactory()
        officer = OfficerFactory()
        OfficerAllegationFactory(allegation=allegation, final_finding='SU', officer=officer)
        OfficerAllegationFactory(allegation=allegation, final_finding='SU', officer=officer)
        expect(officer.sustained_count).to.eq(2)

    def test_rank_histories(self):
        officer = OfficerFactory()
        SalaryFactory(
            officer=officer, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=None,
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=15000, year=2007, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=20000, year=2008, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=25000, year=2009, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(officer.rank_histories).to.eq([{
            'date': date(2005, 1, 1),
            'rank': 'Police Officer'
        }, {
            'date': date(2008, 1, 1),
            'rank': 'Sergeant'
        }])

    def test_rank_histories_with_no_salary(self):
        officer = OfficerFactory()
        expect(officer.rank_histories).to.eq([])

    def test_get_rank_by_date(self):
        officer = OfficerFactory()
        SalaryFactory(
            officer=officer, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=15000, year=2007, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=20000, year=2008, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=25000, year=2009, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(officer.get_rank_by_date(None)).to.eq(None)
        expect(officer.get_rank_by_date(date(2007, 1, 1))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(datetime(2007, 1, 1, tzinfo=pytz.utc))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(date(2005, 1, 1))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(date(2009, 1, 1))).to.eq('Sergeant')
        expect(officer.get_rank_by_date(date(2004, 1, 1))).to.be.none()

    def test_get_rank_by_date_with_empty_rank_histories(self):
        officer = OfficerFactory()
        expect(officer.get_rank_by_date(date(2007, 1, 1))).to.be.none()


class SalaryManagerTestCase(TestCase):
    def test_rank_histories_without_joined(self):
        officer1 = OfficerFactory(appointed_date=date(2005, 1, 1))
        officer2 = OfficerFactory(appointed_date=date(2005, 1, 1))
        SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=None,
            start_date=date(2005, 1, 1)
        )
        salary1 = SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary2 = SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(Salary.objects.rank_histories_without_joined()).to.eq([salary1, salary2])
