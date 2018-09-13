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
        )
    )
