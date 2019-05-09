from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from data.models import Allegation, Officer
from officers.serializers.response_serializers import OfficerCardSerializer
from pinboard.serializers.pinboard_complaint_serializer import PinboardComplaintSerializer
from pinboard.serializers.pinboard_trr_serializer import PinboardTRRSerializer
from trr.models import TRR
from pinboard.constants import PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD, PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY
from social_graph.queries import GeographyDataQuery
from social_graph.queries import SocialGraphDataQuery
from pinboard.serializers.pinboard_serializer import PinboardSerializer
from pinboard.serializers.officer_card_serializer import OfficerCardSerializer as PinboardOfficerCardSerializer
from pinboard.serializers.allegation_card_serializer import AllegationCardSerializer
from pinboard.serializers.document_card_serializer import DocumentCardSerializer
from .models import Pinboard


@method_decorator(never_cache, name='dispatch')
class PinboardBaseViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Pinboard.objects.all()
    serializer_class = PinboardSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

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

    @detail_route(methods=['GET'], url_path='complaints')
    def complaints(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        crids = set(pinboard.allegations.values_list('crid', flat=True))
        complaints = Allegation.objects.filter(crid__in=crids)
        serializer = PinboardComplaintSerializer(complaints, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET'], url_path='officers')
    def officers(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        officer_ids = set(pinboard.officers.values_list('id', flat=True))
        officers = Officer.objects.filter(id__in=officer_ids)
        serializer = OfficerCardSerializer(officers, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET'], url_path='trrs')
    def trrs(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        trr_ids = set(pinboard.trrs.values_list('id', flat=True))
        trrs = TRR.objects.filter(id__in=trr_ids).prefetch_related('actionresponse_set')
        serializer = PinboardTRRSerializer(trrs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-coaccusals')
    def relevant_coaccusals(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_coaccusals = paginator.paginate_queryset(pinboard.relevant_coaccusals, request, view=self)
        serializer = PinboardOfficerCardSerializer(relevant_coaccusals, many=True)
        return paginator.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-documents')
    def relevant_documents(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_documents = paginator.paginate_queryset(pinboard.relevant_documents, request, view=self)
        serializer = DocumentCardSerializer(relevant_documents, many=True)
        return paginator.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-complaints')
    def relevant_complaints(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_complaints = paginator.paginate_queryset(pinboard.relevant_complaints, request, view=self)
        serializer = AllegationCardSerializer(relevant_complaints, many=True)
        return paginator.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], url_path='geographic-data')
    def geographic_data(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        return Response(GeographyDataQuery(pinboard.all_officers).execute())


class PinboardDesktopViewSet(PinboardBaseViewSet):
    @detail_route(methods=['get'], url_path='social-graph')
    def social_graph(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        social_graph_data_query = SocialGraphDataQuery(
            pinboard.all_officers,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY,
            True
        )
        return Response(social_graph_data_query.graph_data())


class PinboardMobileViewSet(PinboardBaseViewSet):
    @detail_route(methods=['get'], url_path='social-graph')
    def social_graph(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        social_graph_data_query = SocialGraphDataQuery(
            pinboard.all_officers,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD,
            PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY,
        )
        return Response(social_graph_data_query.graph_data())
