from django.db.models import Subquery, OuterRef, Sum, F

from lawsuit.models import Lawsuit


def cache_data():
    Lawsuit.objects.update(
        total_settlement=Subquery(
            Lawsuit.objects.filter(
                id=OuterRef('id')
            ).annotate(
                total=Sum('payments__settlement')
            ).values('total')[:1]
        ),
        total_legal_fees=Subquery(
            Lawsuit.objects.filter(
                id=OuterRef('id')
            ).annotate(
                total=Sum('payments__legal_fees')
            ).values('total')[:1]
        )
    )

    Lawsuit.objects.update(
        total_payments=F('total_settlement') + F('total_legal_fees')
    )
