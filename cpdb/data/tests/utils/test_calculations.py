from datetime import date, datetime

import pytz
from django.test import TestCase
from robber import expect
from mock import patch

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory
from data.utils.calculations import calculate_top_percentile
from trr.factories import TRRFactory


class CalculateTopPercentileTestCase(TestCase):

    @patch('data.models.ALLEGATION_MIN_DATETIME', datetime(2002, 1, 1, tzinfo=pytz.utc))
    @patch('data.models.ALLEGATION_MAX_DATETIME', datetime(2016, 12, 31, tzinfo=pytz.utc))
    @patch('data.models.INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME', datetime(2002, 1, 1, tzinfo=pytz.utc))
    @patch('data.models.INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME', datetime(2016, 12, 31, tzinfo=pytz.utc))
    @patch('data.models.TRR_MIN_DATETIME', datetime(2002, 1, 1, tzinfo=pytz.utc))
    @patch('data.models.TRR_MAX_DATETIME', datetime(2016, 12, 31, tzinfo=pytz.utc))
    def test_calculate_top_percentile(self):
        officer1 = OfficerFactory(appointed_date=date(2001, 1, 1))
        officer2 = OfficerFactory(appointed_date=date(2002, 1, 1))
        officer3 = OfficerFactory(appointed_date=date(2003, 1, 1))

        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc))

        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation3, final_finding='NS', start_date=date(2005, 1, 1)
        )

        TRRFactory(officer=officer2, trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc))
        TRRFactory(officer=officer3, trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc))
        TRRFactory(officer=officer3, trr_datetime=datetime(2006, 1, 1, tzinfo=pytz.utc))

        expect(calculate_top_percentile()).to.eq({
            officer1.id: {
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 0,
                'percentile_trr': 0,
                'percentile_allegation': 0,
            },
            officer2.id: {
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 0,
                'percentile_trr': 33.3333,
                'percentile_allegation': 33.3333,
            },
            officer3.id: {
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 0,
                'percentile_trr': 66.6667,
                'percentile_allegation': 66.6667,
            },
        })
