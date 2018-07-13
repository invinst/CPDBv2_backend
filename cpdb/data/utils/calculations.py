from data.models import Officer


def calculate_top_percentile():
    top_percentile = Officer.top_percentile()

    return {
        data.officer_id: {
            'percentile_allegation': getattr(data, 'percentile_allegation', None),
            'percentile_allegation_civilian': getattr(data, 'percentile_allegation_civilian', None),
            'percentile_allegation_internal': getattr(data, 'percentile_allegation_internal', None),
            'percentile_trr': getattr(data, 'percentile_trr', None)
        }
        for data in top_percentile
    }
