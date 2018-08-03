from mock import patch, Mock

from data import officer_percentile
from data.constants import (
    ALLEGATION_MIN_DATETIME, ALLEGATION_MAX_DATETIME,
    INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME, INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME,
    TRR_MIN_DATETIME, TRR_MAX_DATETIME
)


def mock_percentile_map_range(
    allegation_min=ALLEGATION_MIN_DATETIME,
    allegation_max=ALLEGATION_MAX_DATETIME,
    internal_civilian_min=INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME,
    internal_civilian_max=INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME,
    trr_min=TRR_MIN_DATETIME,
    trr_max=TRR_MAX_DATETIME,
    honorable_mention_max=None,
    honorable_mention_min=None,
):
    honorable_mention_range = []
    if honorable_mention_max and honorable_mention_min:
        honorable_mention_range = (honorable_mention_min, honorable_mention_max)

    @patch('data.officer_percentile.ALLEGATION_MIN_DATETIME', allegation_min)
    @patch('data.officer_percentile.ALLEGATION_MAX_DATETIME', allegation_max)
    @patch('data.officer_percentile.INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME', internal_civilian_min)
    @patch('data.officer_percentile.INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME', internal_civilian_max)
    @patch('data.officer_percentile.TRR_MIN_DATETIME', trr_min)
    @patch('data.officer_percentile.TRR_MAX_DATETIME', trr_max)
    @patch('data.officer_percentile._get_award_dataset_range', Mock(return_value=honorable_mention_range))
    def annotation(func):
        new_percentile_map = officer_percentile.create_percentile_map()
        return patch('data.officer_percentile.PERCENTILE_MAP', new_percentile_map)(func)

    return annotation
