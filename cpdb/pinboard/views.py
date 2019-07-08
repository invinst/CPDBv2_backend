from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from pinboard.serializers.pinboard_serializer import (
    PinboardSerializer,
    OrderedPinboardSerializer
)
from pinboard.serializers.desktop.pinned import (
    PinnedOfficerSerializer,
    PinnedAllegationSerializer,
    PinnedTRRSerializer
)
from pinboard.serializers.desktop.relevant import (
    RelevantOfficerSerializer,
    RelevantAllegationSerializer,
    RelevantDocumentSerializer
)

from .models import Pinboard, ProxyAllegation as Allegation


@method_decorator(never_cache, name='dispatch')
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
        self.update_owned_pinboards(request, response.data['id'])
        self.update_latest_retrieved_pinboard(request, response.data['id'])
        return response

    def update(self, request, pk):
        if str(pk) in request.session.get('owned_pinboards', []):
            return super().update(request, pk)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk):
        pinboard = self.get_object()
        owned_pinboards = request.session.get('owned_pinboards', [])

        if pk not in owned_pinboards:
            pinboard = pinboard.clone()
            self.update_owned_pinboards(request, pinboard.id)
        self.update_latest_retrieved_pinboard(request, pinboard.id)

        return Response(OrderedPinboardSerializer(pinboard).data)

    def update_owned_pinboards(self, request, pinboard_id):
        owned_pinboards = request.session.get('owned_pinboards', [])
        owned_pinboards.append(pinboard_id)
        request.session['owned_pinboards'] = owned_pinboards
        request.session['modified'] = True

    def update_latest_retrieved_pinboard(self, request, pinboard_id):
        request.session['latest_retrieved_pinboard'] = pinboard_id
        request.session['modified'] = True

    @list_route(methods=['GET'], url_path='latest-retrieved-pinboard')
    def latest_retrieved_pinboard(self, request):
        if ('latest_retrieved_pinboard' in request.session) and \
                (request.session['latest_retrieved_pinboard']
                    in request.session.get('owned_pinboards', [])):
            pinboard = get_object_or_404(Pinboard, id=request.session['latest_retrieved_pinboard'])
            return Response(self.serializer_class(pinboard).data)

        return Response({})

    @detail_route(methods=['GET'], url_path='complaints')
    def complaints(self, request, pk):
        allegations = Allegation.objects.get_complaints_in_pinboard(pk)

        serializer = PinnedAllegationSerializer(allegations, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET'], url_path='officers')
    def officers(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        serializer = PinnedOfficerSerializer(pinboard.officers, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET'], url_path='trrs')
    def trrs(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        serializer = PinnedTRRSerializer(pinboard.trrs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-coaccusals')
    def relevant_coaccusals(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_coaccusals = paginator.paginate_queryset(pinboard.relevant_coaccusals, request, view=self)
        serializer = RelevantOfficerSerializer(relevant_coaccusals, many=True)
        return paginator.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-documents')
    def relevant_documents(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_documents = paginator.paginate_queryset(pinboard.relevant_documents, request, view=self)
        serializer = RelevantDocumentSerializer(relevant_documents, many=True)
        return paginator.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], url_path='relevant-complaints')
    def relevant_complaints(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_complaints = paginator.paginate_queryset(pinboard.relevant_complaints, request, view=self)
        serializer = RelevantAllegationSerializer(relevant_complaints, many=True)
        return paginator.get_paginated_response(serializer.data)
