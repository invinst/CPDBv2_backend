from data.constants import PERCENTILE_TYPES
from data.models import Officer


def calculate_top_percentile():
    top_percentile = Officer.top_complaint_officers(100, percentile_types=PERCENTILE_TYPES)

    return {
        data.officer_id: {
            'percentile_allegation': data.percentile_allegation,
            'percentile_allegation_civilian': data.percentile_allegation_civilian,
            'percentile_allegation_internal': data.percentile_allegation_internal,
            'percentile_trr': data.percentile_trr,
        }
        for data in top_percentile
    }
