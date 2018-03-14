from datetime import date, datetime
from django.test.testcases import TestCase, override_settings
from django.utils.timezone import now
from robber.expect import expect

from data.models import Officer
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory,
    OfficerAllegationFactory, AwardFactory
)
from trr.factories import TRRFactory


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

    def test_current_badge_not_found(self):
        officer = OfficerFactory()
        expect(officer.current_badge).to.equal('')
        OfficerBadgeNumberFactory(officer=officer, current=False)
        expect(officer.current_badge).to.equal('')

    def test_current_badge(self):
        officer = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer, star='123', current=True)
        expect(officer.current_badge).to.eq('123')

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
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        expect(officer.last_unit).to.eq('CAND')

    def test_abbr_name(self):
        officer = OfficerFactory(first_name='Michel', last_name='Foo')
        expect(officer.abbr_name).to.eq('M. Foo')

    def test_discipline_count(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(officer=officer, final_outcome='100')
        OfficerAllegationFactory(officer=officer, final_outcome='600')
        OfficerAllegationFactory(officer=officer, final_outcome='')
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

    def test_compute_num_allegation_trr(self):
        # ========================= #     # ========================= #
        # year  |   # Allegation    |     # year  |   # Percentile    |
        #       | o1 | o2 | o3 | o4 |     #       | o1 | o2 | o3 | o4 |
        # 2014  | 1  |    |    |    |  => # 2014  | 75 | 0  | 0  | 0  |
        # 2015  | 1  | 3  |    |    |     # 2015  | 50 | 75 | 0  | 0  |
        # 2016  | 1  |    |    |    |     # 2016  | 50 | 50 | 0  | 0  |
        # ========================= #     # ========================= #

        appointed_date = datetime(2013, 1, 1)
        officer1 = OfficerFactory(id=1, appointed_date=appointed_date)
        officer2 = OfficerFactory(id=2, appointed_date=appointed_date)
        OfficerFactory(id=3, appointed_date=appointed_date)
        OfficerFactory(id=4, appointed_date=appointed_date)
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=datetime(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2015, 1, 1),
                                 allegation__incident_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2016, 1, 22),
                                 allegation__incident_date=datetime(2016, 1, 1),
                                 allegation__is_officer_complaint=False)
        TRRFactory(
            officer=officer2,
            trr_datetime=datetime(2016, 1, 1)
        )

        OfficerAllegationFactory.create_batch(
            3,
            officer=officer2,
            start_date=date(2015, 10, 12),
            allegation__is_officer_complaint=False
        )

        expected_service_time = datetime(2017, 12, 31) - appointed_date

        expect(list(Officer.compute_num_allegation_trr(2017))).to.eq([
            {
                'service_time': expected_service_time,
                'num_allegation': 0,
                'num_allegation_civilian': 0,
                'officer_id': 3,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 0,
                'num_allegation_civilian': 0,
                'officer_id': 4,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 1,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'num_trr': 1
            }])

        expected_service_time = datetime(2015, 12, 31) - appointed_date
        expect(list(Officer.compute_num_allegation_trr(2015))).to.eq([
            {
                'service_time': expected_service_time,
                'num_allegation': 0,
                'num_allegation_civilian': 0,
                'officer_id': 3,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 0,
                'num_allegation_civilian': 0,
                'officer_id': 4,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 2,
                'num_allegation_civilian': 2,
                'officer_id': 1,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': expected_service_time,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'num_trr': 0
            }])

    def test_compute_num_allegation_trr_less_one_year(self):
        appointed_date1 = datetime(2013, 1, 1)
        appointed_date2 = datetime(2016, 1, 1)
        officer1 = OfficerFactory(id=1, appointed_date=appointed_date1)
        officer2 = OfficerFactory(id=2, appointed_date=appointed_date2)
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=datetime(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2015, 1, 1),
                                 allegation__incident_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2016, 1, 22),
                                 allegation__incident_date=datetime(2016, 1, 1),
                                 allegation__is_officer_complaint=False)

        OfficerAllegationFactory.create_batch(
            3,
            officer=officer2,
            start_date=date(2015, 10, 12),
            allegation__is_officer_complaint=False
        )

        expect(list(Officer.compute_num_allegation_trr(2016))).to.eq([
            {
                'service_time': datetime(2016, 12, 31) - appointed_date1,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 1,
                'num_allegation_internal': 0,
                'num_trr': 0
            }])

        expect(list(Officer.compute_num_allegation_trr(2017))).to.eq([
            {
                'service_time': datetime(2017, 12, 31) - appointed_date1,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 1,
                'num_allegation_internal': 0,
                'num_trr': 0
            }, {
                'service_time': datetime(2017, 12, 31) - appointed_date2,
                'num_allegation': 3,
                'num_allegation_civilian': 3,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'num_trr': 0
            }
        ])

    def test_top_complaint_officers(self):
        appointed_date = datetime(2013, 1, 1)
        officer1 = OfficerFactory(id=1, appointed_date=appointed_date)
        officer2 = OfficerFactory(id=2, appointed_date=appointed_date)
        OfficerFactory(id=3, appointed_date=appointed_date)
        OfficerFactory(id=4, appointed_date=appointed_date)
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=datetime(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2015, 1, 1),
                                 allegation__incident_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2016, 1, 22),
                                 allegation__incident_date=datetime(2016, 1, 1),
                                 allegation__is_officer_complaint=False)
        TRRFactory(
            officer=officer2,
            trr_datetime=datetime(2016, 1, 1)
        )

        expected_service_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        expected_service_time -= appointed_date
        current_year = now().year
        expect(Officer.top_complaint_officers(100)).to.eq([
            {
                'percentile_trr': 0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': current_year,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 3,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0},
            {
                'percentile_trr': 0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': current_year,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 4,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0
            },
            {
                'percentile_trr': 0,
                'num_allegation_civilian': 3,
                'percentile_allegation_civilian': 75.0,
                'service_time': expected_service_time,
                'year': current_year,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 3,
                'allegation': 3 / (expected_service_time.days / 365.0),
                'allegation_civilian': 3 / (expected_service_time.days / 365.0),
                'officer_id': 1,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 75.0,
                'percentile_allegation_internal': 0
            },
            {
                'percentile_trr': 75.0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': current_year,
                'allegation_internal': 0.0,
                'num_trr': 1,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'trr': 1 / (expected_service_time.days / 365.0),
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0
            }
        ])

        expected_service_time = datetime(2017, 12, 31) - appointed_date
        expect(expected_service_time.days / 365.0).to.eq(5)
        expect(Officer.top_complaint_officers(100, year=2017)).to.eq([
            {
                'percentile_trr': 0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 3,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0
            }, {
                'percentile_trr': 0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 4,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0
            }, {
                'percentile_trr': 0,
                'num_allegation_civilian': 3,
                'percentile_allegation_civilian': 75.0,
                'service_time': expected_service_time,
                'year': 2017,
                'allegation_internal': 0.0,
                'num_trr': 0,
                'num_allegation': 3,
                'allegation': 0.6,
                'allegation_civilian': 0.6,
                'officer_id': 1,
                'num_allegation_internal': 0,
                'trr': 0.0,
                'percentile_allegation': 75.0,
                'percentile_allegation_internal': 0
            }, {
                'percentile_trr': 75.0,
                'num_allegation_civilian': 0,
                'percentile_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'allegation_internal': 0.0,
                'num_trr': 1,
                'num_allegation': 0,
                'allegation': 0.0,
                'allegation_civilian': 0.0,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'trr': 0.2,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0
            }
        ])

    def test_top_complaint_officers_type_not_found(self):
        officer1 = OfficerFactory(id=1, appointed_date=datetime(2016, 1, 1))
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=datetime(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        with self.assertRaisesRegex(ValueError, 'type is invalid'):
            Officer.top_complaint_officers(100, year=2017, type=['not_exist'])

    def test_top_complaint_officers_with_type(self):
        appointed_date = datetime(2013, 1, 1)
        officer1 = OfficerFactory(id=1, appointed_date=appointed_date)
        officer2 = OfficerFactory(id=2, appointed_date=appointed_date)
        OfficerFactory(id=3, appointed_date=appointed_date)
        OfficerFactory(id=4, appointed_date=appointed_date)
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=datetime(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2015, 1, 1),
                                 allegation__incident_date=datetime(2014, 1, 1),
                                 allegation__is_officer_complaint=False)
        OfficerAllegationFactory(officer=officer1, start_date=date(2016, 1, 22),
                                 allegation__incident_date=datetime(2016, 1, 1),
                                 allegation__is_officer_complaint=False)
        TRRFactory(
            officer=officer2,
            trr_datetime=datetime(2016, 1, 1)
        )

        expected_service_time = datetime(2017, 12, 31) - appointed_date
        expect(expected_service_time.days / 365.0).to.eq(5)
        expect(Officer.top_complaint_officers(100, year=2017, type=['allegation'])).to.eq([
            {
                'num_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'num_trr': 0,
                'num_allegation': 0,
                'officer_id': 3,
                'num_allegation_internal': 0,
                'allegation': 0.0,
                'percentile_allegation': 0,
            }, {
                'num_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'num_trr': 0,
                'num_allegation': 0,
                'officer_id': 4,
                'num_allegation_internal': 0,
                'allegation': 0.0,
                'percentile_allegation': 0,
            }, {
                'num_allegation_civilian': 0,
                'service_time': expected_service_time,
                'year': 2017,
                'num_trr': 1,
                'num_allegation': 0,
                'officer_id': 2,
                'num_allegation_internal': 0,
                'allegation': 0.0,
                'percentile_allegation': 0,
            }, {
                'num_allegation_civilian': 3,
                'service_time': expected_service_time,
                'year': 2017,
                'num_trr': 0,
                'num_allegation': 3,
                'officer_id': 1,
                'allegation': 0.6,
                'num_allegation_internal': 0,
                'percentile_allegation': 75.0
            }
        ])
