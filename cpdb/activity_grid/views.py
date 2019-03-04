from operator import itemgetter

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard, ActivityPairCard
from activity_grid.serializers import OfficerCardSerializer, PairCardSerializer


class ActivityGridViewSet(viewsets.ViewSet):
    def get_activity_cards(self):
        cards = ActivityCard.objects.annotate(
            null_position=Count('last_activity')
        ).select_related('officer').order_by(
            '-important', '-null_position', '-last_activity'
        )[:40]
        return OfficerCardSerializer(cards, many=True).data

    def get_activity_pair_cards(self):
        pair_cards = ActivityPairCard.objects.annotate(
            null_position=Count('last_activity')
        ).select_related(
            'officer1', 'officer2'
        ).order_by('-important', '-null_position', '-last_activity')[:40]

        return PairCardSerializer(pair_cards, many=True).data

    def list(self, request):
        results = self.get_activity_cards() + self.get_activity_pair_cards()
        results.sort(key=itemgetter('important', 'null_position', 'last_activity'), reverse=True)

        for result in results:
            result.pop('important')
            result.pop('null_position')
            result.pop('last_activity')

        return Response(results)
