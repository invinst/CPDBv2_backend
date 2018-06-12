from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from activity_grid.models import ActivityCard, ActivityPairCard
from twitterbot.models import TYPE_SINGLE_OFFICER, TYPE_COACCUSED_PAIR


class ActivityGridUpdater():
    def process(self, response):
        if response['type'] == TYPE_SINGLE_OFFICER:
            officer = response['entity']
            activity_card, _ = ActivityCard.objects.get_or_create(officer=officer)
            activity_card.last_activity = timezone.now()
            activity_card.save()

        elif response['type'] == TYPE_COACCUSED_PAIR:
            officer1 = response['officer1']
            officer2 = response['officer2']

            try:
                activity_pair_card, _ = ActivityPairCard.objects.get(officer1=officer2, officer2=officer1)
            except ObjectDoesNotExist:
                activity_pair_card, _ = ActivityPairCard.objects.get_or_create(officer1=officer1, officer2=officer2)

            activity_pair_card.last_activity = timezone.now()
            activity_pair_card.save()
