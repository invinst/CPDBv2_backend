from datetime import date
import pytz

from django.test.testcases import TestCase
from django.utils.timezone import datetime

from mock import patch
from robber.expect import expect

from data.constants import (
    PERCENTILE_ALLEGATION_GROUP,
    PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
    PERCENTILE_TRR_GROUP
)
from data.factories import OfficerFactory, OfficerAllegationFactory, AwardFactory
from data.tests.officer_percentile_utils import mock_percentile_map_range
from officers.tests.utils import validate_object
from trr.factories import TRRFactory
from data import officer_percentile


class OfficerPercentileTestCase(TestCase):

    def test_officer_service_year_filter_no_appointed_date(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=None)

        officers = officer_percentile._officer_service_year(date(2015, 2, 1), date(2016, 7, 1))
        expect(officers).to.have.length(1)
        expect(officers[0].id).to.equal(1)

    def test_officer_service_year_filter_service_time_less_than_1_year(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2016, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2015, 12, 31))

        officers = officer_percentile._officer_service_year(date(2015, 2, 1), date(2016, 7, 1))
        expect(officers).to.have.length(1)
        expect(officers[0].id).to.equal(1)

    def test_officer_service_year(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 1))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 1))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 1), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 1), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._officer_service_year(date(2015, 2, 1), date(2016, 7, 1))

        expect(officers).to.have.length(4)

        expected_dict = {
            1: {
                'officer_id': 1,
                'start_date': date(2015, 2, 1),
                'end_date': date(2016, 7, 1),
                'service_year': 1.4137
            },
            2: {
                'officer_id': 2,
                'start_date': date(2015, 3, 1),
                'end_date': date(2016, 7, 1),
                'service_year': 1.337
            },
            3: {
                'officer_id': 3,
                'start_date': date(2015, 2, 1),
                'end_date': date(2016, 2, 1),
                'service_year': 1.0
            },
            4: {
                'officer_id': 4,
                'start_date': date(2015, 2, 1),
                'end_date': date(2016, 7, 1),
                'service_year': 1.4137
            }
        }
        for officer in officers:
            validate_object(officer, expected_dict[officer.id])

    @mock_percentile_map_range(
        trr_min=datetime(2014, 1, 1, tzinfo=pytz.utc),
        trr_max=datetime(2014, 12, 1, tzinfo=pytz.utc)
    )
    def test_compute_trr_metric_return_empty_if_date_range_smaller_than_1_year(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2016, PERCENTILE_TRR_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        trr_min=datetime(2014, 3, 1, tzinfo=pytz.utc),
        trr_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_trr_metric_return_empty_if_not_enough_data(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2014, PERCENTILE_TRR_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        trr_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        trr_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_trr_metric(self):
        officer = OfficerFactory(id=1, appointed_date=date(2010, 3, 14))

        TRRFactory(officer=officer, trr_datetime=datetime(2014, 12, 31, tzinfo=pytz.utc))
        TRRFactory(officer=officer, trr_datetime=datetime(2015, 1, 1, tzinfo=pytz.utc))
        TRRFactory(officer=officer, trr_datetime=datetime(2016, 1, 1, tzinfo=pytz.utc))
        TRRFactory(officer=officer, trr_datetime=datetime(2016, 2, 1, tzinfo=pytz.utc))
        TRRFactory(officer=officer, trr_datetime=datetime(2017, 2, 1, tzinfo=pytz.utc))

        officers = officer_percentile._compute_metric(2016, PERCENTILE_TRR_GROUP)
        expect(officers).to.have.length(1)
        validate_object(officers[0], {
            'officer_id': 1,
            'year': 2016,
            'start_date': date(2015, 1, 1),
            'end_date': date(2016, 7, 1),
            'service_year': 1.4986,
            'num_trr': 3,
            'metric_trr': 2.0019
        })

    @mock_percentile_map_range(
        internal_civilian_min=datetime(2014, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2014, 12, 1, tzinfo=pytz.utc)
    )
    def test_compute_internal_civilian_allegation_metric_date_range_smaller_than_1_year(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2016, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        internal_civilian_min=datetime(2014, 3, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_internal_civilian_allegation_metric_return_empty_if_not_enough_data(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2014, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        internal_civilian_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_internal_civilian_allegation_metric(self):
        officer = OfficerFactory(id=1, appointed_date=date(2010, 3, 14))

        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2014, 12, 31, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer,
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2016, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )

        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2014, 12, 31, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            6,
            officer=officer,
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2016, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )

        officers = officer_percentile._compute_metric(2016, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP)
        expect(officers).to.have.length(1)
        validate_object(officers[0], {
            'officer_id': 1,
            'year': 2016,
            'start_date': date(2015, 1, 1),
            'end_date': date(2016, 7, 1),
            'service_year': 1.4986,
            'num_allegation_civilian': 3,
            'metric_allegation_civilian': 2.0019,
            'num_allegation_internal': 6,
            'metric_allegation_internal': 4.0037
        })

    @mock_percentile_map_range(
        allegation_min=datetime(2014, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2014, 12, 1, tzinfo=pytz.utc)
    )
    def test_compute_allegation_metric_date_range_smaller_than_1_year(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2016, PERCENTILE_ALLEGATION_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        allegation_min=datetime(2014, 3, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_allegation_metric_return_empty_if_not_enough_data(self):
        OfficerFactory(id=1, appointed_date=date(2010, 3, 14))
        OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2010, 3, 14), resignation_date=date(2016, 2, 1))
        OfficerFactory(id=4, appointed_date=date(2010, 3, 14), resignation_date=date(2017, 12, 31))

        officers = officer_percentile._compute_metric(2014, PERCENTILE_ALLEGATION_GROUP)
        expect(officers).to.have.length(0)

    @mock_percentile_map_range(
        allegation_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2016, 7, 1, tzinfo=pytz.utc)
    )
    def test_compute_allegation_metric(self):
        officer = OfficerFactory(id=1, appointed_date=date(2010, 3, 14))

        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2014, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer,
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2016, 7, 2, tzinfo=pytz.utc),
        )

        officers = officer_percentile._compute_metric(2016, PERCENTILE_ALLEGATION_GROUP)
        expect(officers).to.have.length(1)
        validate_object(officers[0], {
            'officer_id': 1,
            'year': 2016,
            'start_date': date(2015, 1, 1),
            'end_date': date(2016, 7, 1),
            'service_year': 1.4986,
            'num_allegation': 3,
            'metric_allegation': 2.0019,
        })

    @mock_percentile_map_range(
        allegation_min=datetime(2013, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2014, 1, 1, tzinfo=pytz.utc),
        internal_civilian_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2016, 1, 1, tzinfo=pytz.utc),
        trr_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        trr_max=datetime(2016, 1, 1, tzinfo=pytz.utc)
    )
    def test_top_percentile(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(1990, 3, 14))
        officer2 = OfficerFactory(id=2, appointed_date=date(1990, 3, 14))
        officer3 = OfficerFactory(id=3, appointed_date=date(1990, 3, 14))

        # officer1 have all data
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer1,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer1,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            4,
            officer=officer1,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            2,
            officer=officer1,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        # officer2 don't have trr
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )

        # officer3 don't have allegation in ALLEGATION_MIN - ALLEGATION_MAX
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer3,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer3,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            3,
            officer=officer3,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        expected_dict = {
            1: {
                'officer_id': 1,
                'year': 2016,
                'metric_allegation': 2,
                'metric_allegation_civilian': 4,
                'metric_allegation_internal': 3,
                'metric_trr': 2,
                'percentile_allegation': 66.6667,
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 66.6667,
                'percentile_trr': 33.3333
            },
            2: {
                'officer_id': 2,
                'year': 2016,
                'metric_allegation': 1,
                'metric_allegation_civilian': 1,
                'metric_allegation_internal': 1,
                'metric_trr': 0.0,
                'percentile_allegation': 33.3333,
                'percentile_allegation_civilian': 0.0000,
                'percentile_allegation_internal': 0.0000,
                'percentile_trr': 0.0
            },
            3: {
                'officer_id': 3,
                'year': 2016,
                'metric_allegation': 0.0,
                'metric_allegation_civilian': 3,
                'metric_allegation_internal': 2,
                'metric_trr': 3,
                'percentile_allegation': 0.0,
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 33.3333,
                'percentile_trr': 66.6667,
            }
        }

        officers = officer_percentile.top_percentile(2016)
        for officer in officers:
            validate_object(officer, expected_dict[officer.id])

    @mock_percentile_map_range(
        allegation_min=datetime(2013, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2014, 1, 1, tzinfo=pytz.utc),
        internal_civilian_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2016, 1, 1, tzinfo=pytz.utc),
        trr_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        trr_max=datetime(2016, 1, 1, tzinfo=pytz.utc)
    )
    def test_top_percentile_with_types(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(1990, 3, 14))
        officer2 = OfficerFactory(id=2, appointed_date=date(1990, 3, 14))
        officer3 = OfficerFactory(id=3, appointed_date=date(1990, 3, 14))
        officer4 = OfficerFactory(id=4, appointed_date=date(1990, 3, 14))

        # officer1 have all data
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer1,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer1,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            4,
            officer=officer1,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            2,
            officer=officer1,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        # officer2 don't have trr
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )

        # officer3 don't have allegation in ALLEGATION_MIN - ALLEGATION_MAX
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer3,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer3,
            allegation__incident_date=datetime(2015, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            3,
            officer=officer3,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        # officer4 don't have allegation in INTERNAL_CIVILIAN_ALLEGATION year range
        OfficerAllegationFactory.create_batch(
            5,
            officer=officer4,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        TRRFactory.create_batch(
            6,
            officer=officer4,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        expected_dict = {
            1: {
                'officer_id': 1,
                'year': 2016,
                'metric_allegation_civilian': 4,
                'metric_allegation_internal': 3,
                'metric_trr': 2,
                'percentile_allegation': None,
                'percentile_allegation_civilian': 75.0,
                'percentile_allegation_internal': 75.0,
                'percentile_trr': 25.0
            },
            2: {
                'officer_id': 2,
                'year': 2016,
                'metric_allegation_civilian': 1,
                'metric_allegation_internal': 1,
                'metric_trr': 0.0,
                'percentile_allegation': None,
                'percentile_allegation_civilian': 25.0,
                'percentile_allegation_internal': 25.0,
                'percentile_trr': 0.0
            },
            3: {
                'officer_id': 3,
                'year': 2016,
                'metric_allegation_civilian': 3,
                'metric_allegation_internal': 2,
                'metric_trr': 3,
                'percentile_allegation': None,
                'percentile_allegation_civilian': 50.0,
                'percentile_allegation_internal': 50.0,
                'percentile_trr': 50.0
            },
            4: {
                'officer_id': 4,
                'year': 2016,
                'metric_allegation_civilian': 0.0,
                'metric_allegation_internal': 0.0,
                'metric_trr': 6,
                'percentile_allegation': None,
                'percentile_allegation_civilian': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_trr': 75.0
            }
        }

        visual_token_percentile_groups = [
            PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
            PERCENTILE_TRR_GROUP
        ]
        officers = officer_percentile.top_percentile(2016, percentile_groups=visual_token_percentile_groups)
        for officer in officers:
            validate_object(officer, expected_dict[officer.id])

    @mock_percentile_map_range(
        allegation_min=datetime(2013, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2014, 1, 1, tzinfo=pytz.utc),
        internal_civilian_min=datetime(2014, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2015, 1, 1, tzinfo=pytz.utc),
        trr_min=datetime(2015, 1, 1, tzinfo=pytz.utc),
        trr_max=datetime(2016, 1, 1, tzinfo=pytz.utc)
    )
    def test_top_percentile_not_enough_service_year(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(1990, 3, 14))
        officer2 = OfficerFactory(id=2, appointed_date=date(1990, 3, 14), resignation_date=date(2014, 5, 1))
        officer3 = OfficerFactory(id=3, appointed_date=date(2013, 3, 14))
        officer4 = OfficerFactory(id=4, appointed_date=date(1990, 3, 14), resignation_date=date(2015, 5, 1))

        # officer1 have all data
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer1,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer1,
            allegation__incident_date=datetime(2014, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            4,
            officer=officer1,
            allegation__incident_date=datetime(2014, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            2,
            officer=officer1,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        # officer2 don't have trr
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2014, 2, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation__incident_date=datetime(2014, 3, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )

        # officer3 don't have allegation in ALLEGATION_MIN - ALLEGATION_MAX
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer3,
            allegation__incident_date=datetime(2014, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory.create_batch(
            3,
            officer=officer3,
            allegation__incident_date=datetime(2014, 7, 2, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        TRRFactory.create_batch(
            3,
            officer=officer3,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        # officer4 don't have allegation in INTERNAL_CIVILIAN_ALLEGATION year range
        OfficerAllegationFactory.create_batch(
            5,
            officer=officer4,
            allegation__incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc),
        )
        TRRFactory.create_batch(
            6,
            officer=officer4,
            trr_datetime=datetime(2015, 2, 1, tzinfo=pytz.utc)
        )

        expected_dict = {
            1: {
                'officer_id': 1,
                'year': 2016,
                'metric_allegation': 2,
                'metric_allegation_civilian': 4,
                'metric_allegation_internal': 3,
                'metric_trr': 2,
                'percentile_allegation': 33.3333,
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 66.6667,
                'percentile_trr': 0.0
            },
            2: {
                'officer_id': 2,
                'year': 2016,
                'metric_allegation': 1,
                'metric_allegation_civilian': None,
                'metric_allegation_internal': None,
                'metric_trr': None,
                'percentile_allegation': 0.0,
                'percentile_allegation_civilian': None,
                'percentile_allegation_internal': None,
                'percentile_trr': None
            },
            3: {
                'officer_id': 3,
                'year': 2016,
                'metric_allegation': None,
                'metric_allegation_civilian': 3,
                'metric_allegation_internal': 2,
                'metric_trr': 3,
                'percentile_allegation': None,
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 33.3333,
                'percentile_trr': 50.0
            },
            4: {
                'officer_id': 4,
                'year': 2016,
                'metric_allegation': 5,
                'metric_allegation_civilian': 0.0,
                'metric_allegation_internal': 0.0,
                'metric_trr': None,
                'percentile_allegation': 66.6667,
                'percentile_allegation_civilian': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_trr': None
            }
        }

        officers = officer_percentile.top_percentile(2016)
        for officer in officers:
            validate_object(officer, expected_dict[officer.id])

    def test_top_percentile_type_not_found(self):
        officer = OfficerFactory(id=1, appointed_date=date(2016, 1, 1))
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2013, 1, 1, tzinfo=pytz.utc),
            start_date=datetime(2014, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        with self.assertRaisesRegex(ValueError, 'type is invalid'):
            officer_percentile.top_percentile(2017, percentile_groups=['not_exist'])

    def test_top_visual_token_percentile(self):
        with patch('data.officer_percentile.top_percentile', return_value=[]) as mock_top_percentile:
            officer_percentile.top_visual_token_percentile(2016)
            visual_token_percentile_groups = [
                PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
                PERCENTILE_TRR_GROUP
            ]
            mock_top_percentile.assert_called_with(2016, percentile_groups=visual_token_percentile_groups)

    def test_top_allegation_percentile(self):
        with patch('data.officer_percentile.top_percentile', return_value=[]) as mock_top_percentile:
            officer_percentile.top_allegation_percentile(2016)
            mock_top_percentile.assert_called_with(2016, percentile_groups=[PERCENTILE_ALLEGATION_GROUP])

    def test_compute_honorable_mention_metric(self):
        self._create_dataset_for_honorable_mention_percentile()

        OfficerFactory(id=3, appointed_date=date(2015, 3, 15))
        OfficerFactory(id=4, appointed_date=date(2015, 1, 1))

        expected_result_yr2017 = [{
            'id': 3,
            'metric_honorable_mention': 0
        }, {
            'id': 4,
            'metric_honorable_mention': 0
        }, {
            'id': 1,
            'metric_honorable_mention': 0.625
        }, {
            'id': 2,
            'metric_honorable_mention': 1.875
        }]
        honorable_mention_metric_2017 = officer_percentile._compute_honorable_mention_metric(2017)

        expect(honorable_mention_metric_2017.count()).to.eq(4)
        validate_object(honorable_mention_metric_2017[0], expected_result_yr2017[0])
        validate_object(honorable_mention_metric_2017[1], expected_result_yr2017[1])
        validate_object(honorable_mention_metric_2017[2], expected_result_yr2017[2])
        validate_object(honorable_mention_metric_2017[3], expected_result_yr2017[3])

        # we have no data of 2018, then percentile metric should return value of 2017 instead
        honorable_mention_metric_2018 = officer_percentile._compute_honorable_mention_metric(2018)

        expect(honorable_mention_metric_2018.count()).to.eq(4)
        validate_object(honorable_mention_metric_2018[0], expected_result_yr2017[0])
        validate_object(honorable_mention_metric_2018[1], expected_result_yr2017[1])
        validate_object(honorable_mention_metric_2018[2], expected_result_yr2017[2])
        validate_object(honorable_mention_metric_2018[3], expected_result_yr2017[3])

        honorable_mention_metric_2015 = officer_percentile._compute_honorable_mention_metric(2015)
        expect(honorable_mention_metric_2015.count()).to.eq(1)
        validate_object(honorable_mention_metric_2015[0], {
            'id': 1,
            'metric_honorable_mention': 0.6673
        })

    def test_honorable_mention_metric_less_than_one_year(self):
        self._create_dataset_for_honorable_mention_percentile()

        # expect officer2 to be excluded cause he service less than 1 year
        honorable_mention_metric_2016 = officer_percentile._compute_honorable_mention_metric(2016)
        expect(honorable_mention_metric_2016.count()).to.eq(1)
        validate_object(honorable_mention_metric_2016[0], {
            'id': 1,
            'metric_honorable_mention': 0.75
        })

        honorable_mention_metric_2017 = officer_percentile._compute_honorable_mention_metric(2017)
        expect(honorable_mention_metric_2017.count()).to.eq(2)
        validate_object(honorable_mention_metric_2017[0], {
            'id': 1,
            'metric_honorable_mention': 0.625
        })
        validate_object(honorable_mention_metric_2017[1], {
            'id': 2,
            'metric_honorable_mention': 1.875
        })

    def _create_dataset_for_honorable_mention_percentile(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
        officer2 = OfficerFactory(id=2, appointed_date=date(2016, 3, 14))
        AwardFactory(officer=officer1, award_type='Complimentary Letter', start_date=datetime(2013, 1, 1))
        AwardFactory(officer=officer1, award_type='Honorable Mention', start_date=datetime(2014, 1, 1))
        AwardFactory(officer=officer1, award_type='Honorable Mention', start_date=date(2015, 1, 1))
        AwardFactory(officer=officer1, award_type='Honorable Mention', start_date=date(2016, 1, 22))
        AwardFactory(officer=officer2, award_type='Honorable Mention', start_date=date(2017, 10, 19))
        AwardFactory(officer=officer2, award_type='Honorable Mention', start_date=date(2017, 10, 19))
        AwardFactory(officer=officer2, award_type='Honorable Mention', start_date=date(2017, 10, 19))

    def test_get_award_dataset_range(self):
        expect(officer_percentile._get_award_dataset_range()).to.be.empty()

        self._create_dataset_for_honorable_mention_percentile()

        expect(officer_percentile._get_award_dataset_range()).to.be.eq([
            date(2013, 1, 1),
            date(2017, 10, 19)
        ])

    def test_annotate_honorable_mention_percentile_officers(self):
        self._create_dataset_for_honorable_mention_percentile()
        OfficerFactory(id=3, appointed_date=date(2015, 3, 15))
        OfficerFactory(id=4, appointed_date=date(2015, 1, 1))

        # current year
        annotated_officers = officer_percentile.annotate_honorable_mention_percentile_officers()
        expect(annotated_officers).to.have.length(4)
        validate_object(annotated_officers[0], {
            'id': 3,
            'metric_honorable_mention': 0,
            'percentile_honorable_mention': 0,
        })
        validate_object(annotated_officers[1], {
            'id': 4,
            'metric_honorable_mention': 0,
            'percentile_honorable_mention': 0,
        })
        validate_object(annotated_officers[2], {
            'id': 1,
            'metric_honorable_mention': 0.625,
            'percentile_honorable_mention': 50.0,
        })
        validate_object(annotated_officers[3], {
            'id': 2,
            'metric_honorable_mention': 1.875,
            'percentile_honorable_mention': 75.0,
        })
