from datetime import date, timedelta

# import pytz
# from django.test import override_settings
from django.test.testcases import TestCase

from mock import patch, Mock
from robber import expect
from decimal import Decimal

from data.factories import (
    OfficerFactory,
    OfficerBadgeNumberFactory,
    AwardFactory,
    OfficerHistoryFactory,
    PoliceUnitFactory,
    OfficerAllegationFactory,
    SalaryFactory
)
from data.cache_managers import officer_cache_manager
from data.models import Officer
from shared.tests.utils import create_object
from trr.factories import TRRFactory


class OfficerCacheManagerTestCase(TestCase):
    def test_allegation_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, final_finding='NS', officer=officer_1)
        OfficerAllegationFactory(final_finding='SU', officer=officer_1)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.allegation_count).to.eq(3)
        expect(officer_2.allegation_count).to.eq(0)

    def test_sustained_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, final_finding='SU', officer=officer_1)
        OfficerAllegationFactory(final_finding='NS', officer=officer_1)
        OfficerAllegationFactory(final_finding='NS', officer=officer_2)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.sustained_count).to.eq(2)
        expect(officer_2.sustained_count).to.eq(0)

    def test_unsustained_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, final_finding='NS', officer=officer_1)
        OfficerAllegationFactory(final_finding='SU', officer=officer_1)
        OfficerAllegationFactory(final_finding='SU', officer=officer_2)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.unsustained_count).to.eq(2)
        expect(officer_2.unsustained_count).to.eq(0)

    def test_discipline_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, officer=officer_1, disciplined=True)
        OfficerAllegationFactory(officer=officer_1, disciplined=False)
        OfficerAllegationFactory(officer=officer_2, disciplined=False)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.discipline_count).to.eq(2)
        expect(officer_2.discipline_count).to.eq(0)

    def test_honorable_mention_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        AwardFactory(officer=officer_1, award_type='Other')
        AwardFactory(officer=officer_1, award_type='Complimentary Letter')
        AwardFactory(officer=officer_1, award_type='Complimentary Letter')
        AwardFactory(officer=officer_1, award_type='Honorable Mention')
        AwardFactory(officer=officer_1, award_type='ABC Honorable Mention')
        AwardFactory(officer=officer_2, award_type='Complimentary Letter')
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.honorable_mention_count).to.eq(2)
        expect(officer_2.honorable_mention_count).to.eq(0)

    def test_civilian_compliment_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        AwardFactory(officer=officer_1, award_type='Other')
        AwardFactory(officer=officer_1, award_type='Complimentary Letter')
        AwardFactory(officer=officer_1, award_type='Complimentary Letter')
        AwardFactory(officer=officer_1, award_type='Honorable Mention')
        AwardFactory(officer=officer_1, award_type='ABC Honorable Mention')
        AwardFactory(officer=officer_2, award_type='Honorable Mention')
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.civilian_compliment_count).to.eq(2)
        expect(officer_2.civilian_compliment_count).to.eq(0)

    def test_major_award_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        AwardFactory(officer=officer_1, award_type='HONORED POLICE STAR')
        AwardFactory(officer=officer_1, award_type='POLICE MEDAL')
        AwardFactory(officer=officer_1, award_type='PIPE BAND AWARD')
        AwardFactory(officer=officer_1, award_type='LIFE SAVING AWARD')
        AwardFactory(officer=officer_2, award_type='LIFE SAVING AWARD')
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.major_award_count).to.eq(2)
        expect(officer_2.major_award_count).to.eq(0)

    def test_trr_count(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        TRRFactory.create_batch(2, officer=officer_1)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.trr_count).to.eq(2)
        expect(officer_2.trr_count).to.eq(0)

    def test_current_badge(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer_1, star='123', current=True)
        OfficerBadgeNumberFactory(officer=officer_2, current=False)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()

        expect(officer_1.current_badge).to.eq('123')
        expect(officer_2.current_badge).to.eq(None)

    def test_last_unit(self):
        officer = OfficerFactory()
        expect(officer.last_unit).to.equal(None)

        last_unit = PoliceUnitFactory(unit_name='BDCH')

        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'), end_date=date(2000, 1, 1))
        OfficerHistoryFactory(officer=officer, unit=last_unit, end_date=date(2002, 1, 1))
        officer_cache_manager.build_cached_columns()
        officer.refresh_from_db()

        expect(officer.last_unit).to.eq(last_unit)

    def test_current_salary(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        expect(officer_1.current_salary).to.be.none()

        SalaryFactory(officer=officer_1, year=2010, salary=5000)
        SalaryFactory(officer=officer_1, year=2012, salary=10000)
        SalaryFactory(officer=officer_1, year=2015, salary=15000)
        SalaryFactory(officer=officer_1, year=2017, salary=20000)
        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()

        expect(officer_1.current_salary).to.eq(20000)
        expect(officer_2.current_salary).to.be.none()

    def test_has_unique_name(self):
        officer_1 = OfficerFactory(first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(first_name='Jerome', last_name='Finnigan')
        officer_3 = OfficerFactory(first_name='German', last_name='Finnigan')
        officer_4 = OfficerFactory(first_name='Jerome', last_name='Piwinicki')
        officer_5 = OfficerFactory(first_name='German', last_name='Piwinicki')
        expect(officer_1.has_unique_name).to.be.false()
        expect(officer_2.has_unique_name).to.be.false()
        expect(officer_3.has_unique_name).to.be.false()
        expect(officer_4.has_unique_name).to.be.false()
        expect(officer_5.has_unique_name).to.be.false()

        officer_cache_manager.build_cached_columns()
        officer_1.refresh_from_db()
        officer_2.refresh_from_db()
        officer_3.refresh_from_db()
        officer_4.refresh_from_db()
        officer_5.refresh_from_db()

        expect(officer_1.has_unique_name).to.be.false()
        expect(officer_2.has_unique_name).to.be.false()
        expect(officer_3.has_unique_name).to.be.true()
        expect(officer_4.has_unique_name).to.be.true()
        expect(officer_5.has_unique_name).to.be.true()

    @patch(
        'data.cache_managers.officer_cache_manager.officer_percentile.latest_year_percentile',
        Mock(return_value=[
            create_object({
                'officer_id': 2,
                'year': 2014,
                'percentile_allegation': '66.6667',
                'percentile_trr': '0.0000',
                'percentile_honorable_mention': 66.6667
            }),
            create_object({
                'officer_id': 1,
                'year': 2017,
                'percentile_allegation_civilian': '66.6667',
                'percentile_allegation_internal': '66.6667',
                'percentile_trr': '33.3333',
                'percentile_honorable_mention': 33.3333,
            }),
            create_object({
                'officer_id': 3,
                'year': 2017,
                'percentile_allegation': '0.0000',
                'percentile_allegation_civilian': '0.0000',
                'percentile_allegation_internal': '0.0000',
                'percentile_honorable_mention': 0.0
            }),
            create_object({
                'officer_id': 4,
                'year': 2017,
                'percentile_allegation': '0.0000',
                'percentile_allegation_civilian': '0.0000',
                'percentile_allegation_internal': '0.0000',
                'percentile_trr': '66.6667',
            })
        ])
    )
    def test_build_cached_percentiles(self):
        OfficerFactory(id=1, appointed_date=date.today() - timedelta(days=60), resignation_date=None)
        OfficerFactory(id=2, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerFactory(id=3, appointed_date=date(1980, 1, 1), resignation_date=None)
        OfficerFactory(id=4, appointed_date=date(1980, 1, 1), resignation_date=None)

        officer_cache_manager.build_cached_percentiles()

        officer_1 = Officer.objects.get(id=1)
        officer_2 = Officer.objects.get(id=2)
        officer_3 = Officer.objects.get(id=3)
        officer_4 = Officer.objects.get(id=4)

        expect(officer_1.complaint_percentile).to.be.none()
        expect(officer_1.civilian_allegation_percentile).to.eq(Decimal('66.6667'))
        expect(officer_1.internal_allegation_percentile).to.eq(Decimal('66.6667'))
        expect(officer_1.trr_percentile).to.eq(Decimal('33.3333'))
        expect(officer_1.honorable_mention_percentile).to.eq(Decimal('33.3333'))

        expect(officer_2.complaint_percentile).to.eq(Decimal('66.6667'))
        expect(officer_2.civilian_allegation_percentile).to.be.none()
        expect(officer_2.internal_allegation_percentile).to.be.none()
        expect(officer_2.trr_percentile).to.eq(Decimal('0.0'))
        expect(officer_2.honorable_mention_percentile).to.eq(Decimal('66.6667'))

        expect(officer_3.complaint_percentile).to.eq(Decimal('0.0000'))
        expect(officer_3.civilian_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer_3.internal_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer_3.trr_percentile).to.be.none()
        expect(officer_3.honorable_mention_percentile).to.eq(Decimal('0.0000'))

        expect(officer_4.complaint_percentile).to.eq(Decimal('0.0000'))
        expect(officer_4.civilian_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer_4.internal_allegation_percentile).to.eq(Decimal('0.0000'))
        expect(officer_4.trr_percentile).to.eq(Decimal('66.6667'))
        expect(officer_4.honorable_mention_percentile).to.be.none()

    # @override_settings(
    #     ALLEGATION_MIN='1988-01-01',
    #     ALLEGATION_MAX='2016-07-01',
    #     INTERNAL_CIVILIAN_ALLEGATION_MIN='2000-01-01',
    #     INTERNAL_CIVILIAN_ALLEGATION_MAX='2016-07-01',
    #     TRR_MIN='2004-01-08',
    #     TRR_MAX='2016-04-12')
    # def test_build_cached_yearly_percentiles(self):
    #     officer_1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
    #     officer_2 = OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
    #     officer_3 = OfficerFactory(id=3, appointed_date=date(2014, 3, 1), resignation_date=date(2015, 4, 14))

    #     OfficerAllegationFactory(
    #         officer=officer_1,
    #         allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
    #         start_date=datetime(2015, 1, 1),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory(
    #         officer=officer_1,
    #         start_date=date(2015, 1, 1),
    #         allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory(
    #         officer=officer_1,
    #         start_date=date(2016, 1, 22),
    #         allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory.create_batch(
    #         2,
    #         officer=officer_2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False
    #     )
    #     OfficerAllegationFactory(
    #         officer=officer_2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2016, 3, 15, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=True
    #     )
    #     OfficerAllegationFactory(
    #         officer=officer_2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2017, 3, 15, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=True
    #     )
    #     TRRFactory(
    #         officer=officer_1,
    #         trr_datetime=datetime(2017, 3, 15, tzinfo=pytz.utc),
    #     )
    #     TRRFactory(
    #         officer=officer_1,
    #         trr_datetime=datetime(2016, 3, 15, tzinfo=pytz.utc),
    #     )
    #     officer_cache_manager.build_cached_yearly_percentiles()

    #     expected_officer_yearly_percentiles = {
    #         officer_1.id: {
    #             2014: {
    #                 'percentile_allegation': Decimal(0.0),
    #                 'percentile_allegation_civilian': Decimal(0.0),
    #                 'percentile_allegation_internal': Decimal(0.0),
    #                 'percentile_trr': Decimal(0.0),
    #             },
    #             2015: {
    #                 'percentile_allegation': Decimal(50.0),
    #                 'percentile_allegation_civilian': Decimal(50.0),
    #                 'percentile_allegation_internal': Decimal(0.0),
    #                 'percentile_trr': Decimal(0.0),
    #             },
    #             2016: {
    #                 'percentile_allegation': Decimal(33.3333),
    #                 'percentile_allegation_civilian': Decimal(33.3333),
    #                 'percentile_allegation_internal': Decimal(0.0),
    #                 'percentile_trr': Decimal(66.6667),
    #             }
    #         },
    #         officer_2.id: {
    #             2016: {
    #                 'percentile_allegation': Decimal(66.6667),
    #                 'percentile_allegation_civilian': Decimal(66.6667),
    #                 'percentile_allegation_internal': Decimal(66.6667),
    #                 'percentile_trr': Decimal(0.0),
    #             }
    #         },
    #         officer_3.id: {
    #             2015: {
    #                 'percentile_allegation': Decimal(0.0),
    #                 'percentile_allegation_civilian': Decimal(0.0),
    #                 'percentile_allegation_internal': Decimal(0.0),
    #                 'percentile_trr': Decimal(0.0),
    #             }
    #         }
    #     }
    #     for officer_id, expected_yearly_percentiles in expected_officer_yearly_percentiles.items():
    #         yearly_percentiles = OfficerYearlyPercentile.objects.filter(officer_id=officer_id)
    #         expect(yearly_percentiles.count()).to.eq(len(expected_yearly_percentiles.keys()))
    #         for year, expected_percentile in expected_yearly_percentiles.items():
    #             percentile = yearly_percentiles.get(year=year)
    #             for attr, value in expected_percentile.items():
    #                 expect(f'{getattr(percentile, attr):.2f}').to.eq(f'{value:.2f}')
