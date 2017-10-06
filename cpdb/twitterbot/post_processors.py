from django.utils import timezone

from activity_grid.models import ActivityCard
from twitterbot.models import TYPE_SINGLE_OFFICER


class ActivityGridUpdater():
    def process(self, response):
        if response['type'] == TYPE_SINGLE_OFFICER:
            officer = response['entity']
            activity_card, _ = ActivityCard.objects.get_or_create(officer=officer)
            activity_card.last_activity = timezone.now()
            activity_card.save()
