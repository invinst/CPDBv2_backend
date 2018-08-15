from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from activity_grid.models import ActivityCard, ActivityPairCard
from twitterbot.models import TYPE_SINGLE_OFFICER, TYPE_COACCUSED_PAIR


class ActivityGridUpdater():
    def process(self, response):
        if response['type'] == TYPE_SINGLE_OFFICER:
            officer = response['entity']
            activity_card, _ = ActivityCard.objects.get_or_create(officer_id=officer['id'])
            activity_card.last_activity = timezone.now()
            activity_card.save()

        elif response['type'] == TYPE_COACCUSED_PAIR:
            officer1 = response['officer1']
            officer2 = response['officer2']

            # Make sure we don't create duplicated pair card with the same members
            try:
                activity_pair_card = ActivityPairCard.objects.get(
                    officer1_id=officer2['id'], officer2_id=officer1['id']
                )
            except ObjectDoesNotExist:
                activity_pair_card, _ = ActivityPairCard.objects.get_or_create(
                    officer1_id=officer1['id'], officer2_id=officer2['id']
                )

            activity_pair_card.last_activity = timezone.now()
            activity_pair_card.save()
