from django.db.models import OuterRef, Subquery, Count

from data.models import OfficerAllegation, Allegation


def cache_data():
    Allegation.objects.update(
        most_common_category=Subquery(
            OfficerAllegation.objects.filter(
                allegation_id=OuterRef('id')
            ).values('allegation_id').annotate(
                cat_count=Count('allegation_category__id')
            ).order_by('-cat_count').values('allegation_category__id')[:1]
        ),
        first_start_date=Subquery(
            OfficerAllegation.objects.filter(
                allegation_id=OuterRef('id'),
                start_date__isnull=False
            ).values('start_date')[:1]
        ),
        first_end_date=Subquery(
            OfficerAllegation.objects.filter(
                allegation_id=OuterRef('id'),
                end_date__isnull=False
            ).values('end_date')[:1]
        ),
        coaccused_count=Subquery(
            OfficerAllegation.objects.filter(
                allegation_id=OuterRef('id'),
            ).values('allegation_id').annotate(
                count=Count('id')
            ).values('count')[:1]
        )
    )

    count_columns = [
        'coaccused_count',
    ]

    for column in count_columns:
        Allegation.objects.filter(**{'{}__isnull'.format(column): True}).update(**{column: 0})
