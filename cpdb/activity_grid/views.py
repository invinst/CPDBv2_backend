from operator import itemgetter

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard, ActivityPairCard
from activity_grid.serializers import OfficerCardSerializer, SimpleCardSerializer
from officers.doc_types import OfficerInfoDocType
from twitterbot.models import TYPE_SINGLE_OFFICER, TYPE_COACCUSED_PAIR


class ActivityGridViewSet(viewsets.ViewSet):
    def get_activity_cards(self):
        queryset = ActivityCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset[:40]

        results = []

        for card in queryset:
            officer = OfficerInfoDocType.search().query('terms', id=[card.officer.id]).execute()[0]
            result = OfficerCardSerializer(officer).data
            result['important'] = card.important
            result['null_position'] = card.null_position
            result['last_activity'] = card.last_activity
            result['type'] = TYPE_SINGLE_OFFICER
            results.append(result)

        return results

    def get_activity_pair_cards(self):
        queryset = ActivityPairCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset[:40]

        results = []

        for pair in queryset:
            officer1 = OfficerInfoDocType.search().query('terms', id=[pair.officer1.id]).execute()[0]
            officer2 = OfficerInfoDocType.search().query('terms', id=[pair.officer2.id]).execute()[0]
            results.append({
                'officer1': SimpleCardSerializer(officer1).data,
                'officer2': SimpleCardSerializer(officer2).data,
                'id': pair.id,
                'important': pair.important,
                'null_position': pair.null_position,
                'last_activity': pair.last_activity,
                'type': TYPE_COACCUSED_PAIR
            })

        return results

    def list(self, request):
        results = self.get_activity_cards() + self.get_activity_pair_cards()
        results.sort(key=itemgetter('important', 'null_position', 'last_activity'), reverse=True)

        for result in results:
            if result['type'] == TYPE_COACCUSED_PAIR:
                result.pop('id')
            result.pop('important')
            result.pop('null_position')
            result.pop('last_activity')

        return Response(results)
