from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from pinboard.constants import PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD, PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY
from pinboard.queries import GeographyDataQuery
from social_graph.queries import SocialGraphDataQuery
from .models import Pinboard
from .serializers import PinboardSerializer


@method_decorator(never_cache, name='dispatch')
class PinboardViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Pinboard.objects.all()
    serializer_class = PinboardSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        response = super().create(request)
        request.session['pinboard-id'] = response.data['id']
        return response

    def update(self, request, pk):
        if 'pinboard-id' in request.session and \
               str(request.session['pinboard-id']) == str(pk):
            return super().update(request, pk)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk):
        pinboard = self.get_object()
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(pinboard).data)

    @detail_route(methods=['get'], url_path='social-graph')
    def social_graph(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        social_graph_data_query = SocialGraphDataQuery(
            pinboard.all_officers,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY
        )

        return Response(social_graph_data_query.graph_data)

    @detail_route(methods=['get'], url_path='geographic-data')
    def geographic_data(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        return Response(GeographyDataQuery(pinboard.all_officers).execute())
