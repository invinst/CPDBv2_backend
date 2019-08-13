import random

import factory
import pytz
from faker import Faker

from activity_log.constants import ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT
from activity_log.models import ActivityLog
from data.factories import UserFactory

fake = Faker()


class ActivityLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityLog

    created_at = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    updated_at = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    user = factory.SubFactory(UserFactory)
    action_type = factory.LazyFunction(lambda: random.choice([ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT]))
    data = factory.LazyFunction(lambda: fake.text(10))
