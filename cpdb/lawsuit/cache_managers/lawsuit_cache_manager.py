from django.db.models import Subquery, OuterRef, Sum, F
from django.db.models.functions import Coalesce

from lawsuit.models import Lawsuit


def cache_data():
    Lawsuit.objects.update(
        total_settlement=Subquery(
            Lawsuit.objects.filter(
                id=OuterRef('id')
            ).annotate(
                total=Coalesce(Sum('payments__settlement'), 0)
            ).values('total')[:1]
        ),
        total_legal_fees=Subquery(
            Lawsuit.objects.filter(
                id=OuterRef('id')
            ).annotate(
                total=Coalesce(Sum('payments__legal_fees'), 0)
            ).values('total')[:1]
        )
    )

    Lawsuit.objects.update(
        total_payments=F('total_settlement') + F('total_legal_fees')
    )
