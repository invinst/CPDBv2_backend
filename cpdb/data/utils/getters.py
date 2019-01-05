from django.db.models import F, Value, Count
from django.db.models.functions import Concat


def get_officers_most_complaints_from_query(query):
    query = query.values('officer').annotate(
        id=F('officer__id'),
        percentile_allegation=F('officer__complaint_percentile'),
        percentile_allegation_civilian=F('officer__civilian_allegation_percentile'),
        percentile_allegation_internal=F('officer__internal_allegation_percentile'),
        percentile_trr=F('officer__trr_percentile'),
        name=Concat('officer__first_name', Value(' '), 'officer__last_name'),
        count=Count('allegation', distinct=True)
    )
    query = query.order_by('-count')[:3]
    return query.values(
        'id',
        'name',
        'count',
        'percentile_allegation',
        'percentile_allegation_civilian',
        'percentile_allegation_internal',
        'percentile_trr'
    )
