from django.test import TestCase

from robber import expect
from mock import patch, Mock

from data.utils.calculations import calculate_top_percentile
from officers.tests.utils import create_object


class CalculateTopPercentileTestCase(TestCase):

    @patch(
        'data.officer_percentile.top_percentile',
        Mock(return_value=[
            create_object({
                'officer_id': 1,
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 2.2222,
            }),
            create_object({
                'officer_id': 2,
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 33.3333,
                'percentile_trr': 33.3333,
                'percentile_allegation': 33.3333,
            }),
        ])
    )
    def test_calculate_top_percentile(self):
        expect(calculate_top_percentile()).to.eq({
            1: {
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 2.2222,
                'percentile_trr': None,
                'percentile_allegation': None,
            },
            2: {
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 33.3333,
                'percentile_trr': 33.3333,
                'percentile_allegation': 33.3333,
            },
        })
