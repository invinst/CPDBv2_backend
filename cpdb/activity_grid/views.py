from operator import itemgetter

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard, ActivityPairCard
from activity_grid.serializers import OfficerCardSerializer, SimpleCardSerializer
from officers.doc_types import OfficerInfoDocType
from twitterbot.constants import RESPONSE_TYPE_SINGLE_OFFICER, RESPONSE_TYPE_COACCUSED_PAIR


class ActivityGridViewSet(viewsets.ViewSet):
    def get_activity_cards(self):
        # Get cards from database
        cards = ActivityCard.objects.all()
        cards = cards.annotate(null_position=Count('last_activity'))
        cards = cards.order_by('-important', '-null_position', '-last_activity')[:40]

        # Get cards' officer ids
        ids = list(cards.values_list('officer_id', flat=True))

        # Sort the cards by ids
        cards = list(cards)
        cards.sort(key=lambda x: x.officer.id)

        # Get officers' info from ES, and sort them by ids
        officers = OfficerInfoDocType.search().query('terms', id=ids)[:40].sort('id').execute()

        # This loop is possible as 1 card is linked to 1 officer with the same id
        results = []
        for card, officer in zip(cards, officers):
            result = OfficerCardSerializer(officer).data
            result['important'] = card.important
            result['null_position'] = card.null_position
            result['last_activity'] = card.last_activity
            result['type'] = RESPONSE_TYPE_SINGLE_OFFICER
            results.append(result)
        return results

    def get_activity_pair_cards(self):
        # Get cards from database
        pair_cards = ActivityPairCard.objects.all()
        pair_cards = pair_cards.annotate(null_position=Count('last_activity'))
        pair_cards = pair_cards.order_by('-important', '-null_position', '-last_activity')[:40]

        # Get all the ids without duplicates
        officer1_ids = list(pair_cards.values_list('officer1__id', flat=True))
        officer1_ids = list(set(officer1_ids))
        officer2_ids = list(pair_cards.values_list('officer2__id', flat=True))
        officer2_ids = list(set(officer2_ids))
        ids = officer1_ids + list(set(officer2_ids) - set(officer1_ids))

        # Get the officers from ES
        officers = OfficerInfoDocType.search().query('terms', id=ids)[:80].execute()

        results = []

        for pair in pair_cards:
            officer1 = [o for o in officers if o.id == pair.officer1.id][0]
            officer2 = [o for o in officers if o.id == pair.officer2.id][0]
            try:
                coaccusals = [c for c in officer1.coaccusals if c['id'] == officer2.id]
                coaccusal_count = coaccusals[0]['coaccusal_count']
            except (IndexError, AttributeError):
                coaccusal_count = 0

            results.append({
                'officer1': SimpleCardSerializer(officer1).data,
                'officer2': SimpleCardSerializer(officer2).data,
                'coaccusal_count': coaccusal_count,
                'important': pair.important,
                'null_position': pair.null_position,
                'last_activity': pair.last_activity,
                'type': RESPONSE_TYPE_COACCUSED_PAIR
            })
        return results

    def list(self, request):
        results = self.get_activity_cards() + self.get_activity_pair_cards()
        results.sort(key=itemgetter('important', 'null_position', 'last_activity'), reverse=True)

        for result in results:
            result.pop('important')
            result.pop('null_position')
            result.pop('last_activity')

        return Response(results)
