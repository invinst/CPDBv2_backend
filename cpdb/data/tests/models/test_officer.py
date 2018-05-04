from datetime import date

import pytz
from django.test.testcases import TestCase, override_settings
from django.utils.timezone import datetime
from robber.expect import expect

from data.constants import PERCENTILE_ALLEGATION
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory,
    OfficerAllegationFactory, AwardFactory,
    AllegationFactory, ComplainantFactory, AllegationCategoryFactory
)
from data.models import Officer
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

    def test_compute_metric_pecentile(self):
        self._create_dataset_for_percentile()
        OfficerFactory(id=3, appointed_date=date(2015, 3, 15))
        OfficerFactory(id=4, appointed_date=date(2015, 1, 1))

        expeced_result_yr2017 = [
            {
                'year': 2017,
                'officer_id': 3,
                'service_year': 2.6,
                'metric_allegation': 0,
                'metric_allegation_internal': 0,
                'metric_allegation_civilian': 0,
                'metric_trr': 0
            }, {
                'year': 2017,
                'officer_id': 4,
                'service_year': 2.8,
                'metric_allegation': 0,
                'metric_allegation_civilian': 0,
                'metric_allegation_internal': 0,
                'metric_trr': 0
            }, {
                'year': 2017,
                'officer_id': 1,
                'service_year': 4.8,
                'metric_allegation': 0.625,
                'metric_allegation_civilian': 0.625,
                'metric_allegation_internal': 0,
                'metric_trr': 0
            }, {
                'year': 2017,
                'officer_id': 2,
                'service_year': 1.6,
                'metric_allegation': 1.875,
                'metric_allegation_civilian': 1.25,
                'metric_allegation_internal': 0.625,
                'metric_trr': 0.625
            }]
        expect(list(Officer.compute_metric_percentile(2017))).to.eq(expeced_result_yr2017)

        # we have no data of 2018, then percentile metric should return value of 2017 instead
        expect(list(Officer.compute_metric_percentile(2018))).to.eq(expeced_result_yr2017)

        expect(list(Officer.compute_metric_percentile(2015))).to.eq([
            {
                'year': 2015,
                'officer_id': 1,
                'service_year': 2.9973,  # ~1094 days / 365.0
                'metric_allegation_internal': 0.0,
                'metric_allegation_civilian': 0.6673,  # ceils(2 / 2.9973),
                'metric_allegation': 0.6673,
                'metric_trr': 0.0
            }
        ])

    def test_compute_metric_pecentile_less_one_year(self):
        self._create_dataset_for_percentile()

        # expect officer2 to be excluded cause he service less than 1 year
        expect(list(Officer.compute_metric_percentile(2016))).to.eq([
            {
                'year': 2016,
                'officer_id': 1,
                'service_year': 4.0,  # ~ 1460.0 / 365.0,
                'metric_allegation': 0.75,  # 3.0 / (1116.0 / 365.0),
                'metric_allegation_civilian': 0.75,
                'metric_allegation_internal': 0.0,
                'metric_trr': 0.0
            }])

        expect(list(Officer.compute_metric_percentile(2017))).to.eq([
            {
                'year': 2017,
                'officer_id': 1,
                'service_year': 4.8,
                'metric_allegation': 0.625,
                'metric_allegation_civilian': 0.625,
                'metric_allegation_internal': 0.0,
                'metric_trr': 0.0
            }, {
                'year': 2017,
                'officer_id': 2,
                'service_year': 1.6,
                'metric_allegation': 1.875,
                'metric_allegation_civilian': 1.25,
                'metric_allegation_internal': 0.625,
                'metric_trr': 0.625
            }
        ])

    def test_get_dataset_range(self):
        expect(Officer.get_dataset_range()).to.be.empty()

        OfficerAllegationFactory(
            allegation__incident_date=datetime(2013, 1, 1),
            start_date=date(2014, 1, 1))
        OfficerAllegationFactory(
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2014, 1, 1))
        OfficerAllegationFactory(
            start_date=date(2016, 1, 22),
            allegation__incident_date=datetime(2016, 1, 1))
        expect(Officer.get_dataset_range()).to.be.eq([
            date(2013, 1, 1),
            date(2016, 1, 22)
        ])

        OfficerAllegationFactory(
            start_date=date(2000, 1, 3),
            allegation__incident_date=datetime(2014, 2, 1),
        )
        TRRFactory(
            trr_datetime=datetime(2016, 2, 29)
        )
        expect(Officer.get_dataset_range()).to.be.eq([
            date(2000, 1, 3),
            date(2016, 2, 29),
        ])

    def _create_dataset_for_percentile(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
        officer2 = OfficerFactory(id=2, appointed_date=date(2016, 3, 14))

        OfficerAllegationFactory(
            officer=officer1,
            allegation__incident_date=datetime(2013, 1, 1, tzinfo=pytz.utc),
            start_date=datetime(2014, 1, 1),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2014, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2016, 1, 22),
            allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory.create_batch(
            2, officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        OfficerAllegationFactory(
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 3, 15, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        TRRFactory(officer=officer2, trr_datetime=datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(Officer.get_dataset_range()).to.be.eq([
            date(2013, 1, 1),
            date(2017, 10, 19)
        ])

    def test_top_complaint_officers(self):
        self._create_dataset_for_percentile()
        OfficerFactory(id=3, appointed_date=date(2015, 3, 15))
        OfficerFactory(id=4, appointed_date=date(2015, 1, 1))

        # current year
        expect(Officer.top_complaint_officers(100)).to.eq([
            {
                'year': 2017,
                'officer_id': 3,
                'service_year': 2.6,
                'metric_allegation': 0,
                'metric_allegation_internal': 0,
                'metric_allegation_civilian': 0,
                'metric_trr': 0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0,
                'percentile_allegation_civilian': 0,
                'percentile_trr': 0
            }, {
                'year': 2017,
                'officer_id': 4,
                'service_year': 2.8,
                'metric_allegation': 0,
                'metric_allegation_civilian': 0,
                'metric_allegation_internal': 0,
                'metric_trr': 0,
                'percentile_allegation': 0,
                'percentile_allegation_internal': 0,
                'percentile_allegation_civilian': 0,
                'percentile_trr': 0
            }, {
                'year': 2017,
                'officer_id': 1,
                'service_year': 4.8,
                'metric_allegation': 0.625,
                'metric_allegation_civilian': 0.625,
                'metric_allegation_internal': 0,
                'metric_trr': 0,
                'percentile_allegation': 50.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 50.0,
                'percentile_trr': 0
            }, {
                'year': 2017,
                'officer_id': 2,
                'service_year': 1.6,
                'metric_allegation': 1.875,
                'metric_allegation_civilian': 1.25,
                'metric_allegation_internal': 0.625,
                'metric_trr': 0.625,
                'percentile_allegation': 75.0,
                'percentile_allegation_internal': 75.0,
                'percentile_allegation_civilian': 75.0,
                'percentile_trr': 75.0
            }])

        expect(Officer.top_complaint_officers(100, year=2015)).to.eq([
            {
                'year': 2015,
                'officer_id': 1,
                'service_year': 2.9973,  # ~1094 days / 365.0
                'metric_allegation_internal': 0.0,
                'metric_allegation_civilian': 0.6673,  # ceils(2 / 2.9973),
                'metric_allegation': 0.6673,
                'metric_trr': 0.0,
                'percentile_allegation': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 0.0,
                'percentile_trr': 0.0
            }
        ])

    def test_top_complaint_officers_type_not_found(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2016, 1, 1))
        OfficerAllegationFactory(officer=officer1,
                                 allegation__incident_date=date(2013, 1, 1),
                                 start_date=datetime(2014, 1, 1, tzinfo=pytz.utc),
                                 allegation__is_officer_complaint=False)
        with self.assertRaisesRegex(ValueError, 'type is invalid'):
            Officer.top_complaint_officers(100, year=2017, percentile_types=['not_exist'])

    def test_top_complaint_officers_with_type(self):
        self._create_dataset_for_percentile()
        OfficerFactory(id=3, appointed_date=date(2015, 3, 15))
        OfficerFactory(id=4, appointed_date=date(2015, 1, 1))

        # expect calculate percentile_allegation only
        expect(Officer.top_complaint_officers(100, year=2015, percentile_types=[PERCENTILE_ALLEGATION])).to.eq([
            {
                'year': 2015,
                'officer_id': 1,
                'service_year': 2.9973,  # ~1094 days / 365.0
                'metric_allegation_internal': 0.0,
                'metric_allegation_civilian': 0.6673,  # ceils(2 / 2.9973),
                'metric_allegation': 0.6673,
                'metric_trr': 0.0,
                'percentile_allegation': 0.0,
            }
        ])

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
