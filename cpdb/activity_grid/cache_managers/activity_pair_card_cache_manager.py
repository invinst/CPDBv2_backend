from django.db.models import OuterRef

from activity_grid.models import ActivityPairCard
from data.models import Allegation
from data.utils.subqueries import SQCount


def cache_data():
    allegations = Allegation.objects.filter(
        officerallegation__officer=OuterRef('officer1')
    ).filter(
        officerallegation__officer=OuterRef('officer2')
    )
    ActivityPairCard.objects.update(coaccusal_count=SQCount(allegations.values('crid')))
