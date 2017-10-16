import factory

from activity_grid.models import ActivityCard
from data.factories import OfficerFactory


class ActivityCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityCard


class OfficerActivityCardFactory(ActivityCardFactory):
    officer = factory.SubFactory(OfficerFactory)
