from factory import DjangoModelFactory, SubFactory

from activity_grid.models import ActivityCard, ActivityPairCard
from data.factories import OfficerFactory


class ActivityCardFactory(DjangoModelFactory):
    class Meta:
        model = ActivityCard

    officer = SubFactory(OfficerFactory)
    important = False
    last_activity = None


class ActivityPairCardFactory(DjangoModelFactory):
    class Meta:
        model = ActivityPairCard

    officer1 = SubFactory(OfficerFactory)
    officer2 = SubFactory(OfficerFactory)
    important = False
    last_activity = None
