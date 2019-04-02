from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from pinboard.constants import PINBOARD_SOCIAL_GRAPH_DEFAULT_THRESHOLD, PINBOARD_SOCIAL_GRAPH_DEFAULT_SHOW_CILVIL_ONLY
from social_graph.queries import SocialGraphDataQuery
from pinboard.serializers.pinboard_serializer import PinboardSerializer
from pinboard.serializers.officer_card_serializer import OfficerCardSerializer
from pinboard.serializers.allegation_card_serializer import AllegationCardSerializer
from pinboard.serializers.document_card_serializer import DocumentCardSerializer
from .models import Pinboard


class PinboardViewSet(
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

    @detail_route(methods=['get'], url_path='relevant-coaccusals')
    def relevant_coaccusals(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_coaccusals = paginator.paginate_queryset(pinboard.relevant_coaccusals, request, view=self)
        serializer = OfficerCardSerializer(relevant_coaccusals, many=True)
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
