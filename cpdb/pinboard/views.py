from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch, Count
from django.db.models import Q

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from pinboard.serializers.pinboard_serializer import (
    PinboardSerializer,
    PinboardDetailSerializer,
    ListPinboardDetailSerializer,
    OrderedPinboardSerializer
)
from pinboard.serializers.desktop.admin.pinboard_serializer import PinboardSerializer as PinboardAdminSerializer
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
from pinboard.serializers.mobile.pinned import (
    PinnedAllegationMobileSerializer,
    PinnedOfficerMobileSerializer,
    PinnedTRRMobileSerializer,
)
from pinboard.serializers.mobile.relevant import (
    RelevantOfficerMobileSerializer,
    RelevantAllegationMobileSerializer,
    RelevantDocumentMobileSerializer,
)
from trr.models import ActionResponse
from .models import Pinboard, ProxyAllegation as Allegation


@method_decorator(never_cache, name='dispatch')
class PinboardViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Pinboard.objects.all()
    serializer_class = PinboardDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def list(self, request):
        owned_pinboards = request.session.get('owned_pinboards', [])
        pinboards = Pinboard.objects.filter(id__in=owned_pinboards).order_by('-updated_at')
        detail = self.request.query_params.get('detail', None)
        if detail:
            pinboards = pinboards.prefetch_related('officers', 'allegations', 'trrs')
        serializer = ListPinboardDetailSerializer if detail else PinboardSerializer
        return Response(serializer(pinboards, many=True).data)

    def create(self, request):
        source_pinboard = self._source_pinboard
        if source_pinboard:
            pinboard = source_pinboard.clone()
            self.update_owned_pinboards(request, pinboard.id)
            self.update_latest_retrieved_pinboard(request, pinboard.id)
            return Response(OrderedPinboardSerializer(pinboard).data)
        else:
            response = super().create(request)
            self.update_owned_pinboards(request, response.data['id'])
            self.update_latest_retrieved_pinboard(request, response.data['id'])
            return response

    def update(self, request, pk):
        if str(pk) in request.session.get('owned_pinboards', []):
            source_pinboard = self._source_pinboard

            if source_pinboard:
                data = PinboardDetailSerializer(source_pinboard).data
                pinboard = get_object_or_404(Pinboard, id=pk)
                pinboard_serializer = PinboardDetailSerializer(pinboard, data=data)
                pinboard_serializer.is_valid(raise_exception=True)
                pinboard_serializer.save()
                return Response(pinboard_serializer.data)
            else:
                return super().update(request, pk)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk):
        try:
            pinboard = self.get_object()
        except Http404:
            pinboard = Pinboard.objects.create()
            self.update_owned_pinboards(request, pinboard.id)
        owned_pinboards = request.session.get('owned_pinboards', [])

        if pinboard.id not in owned_pinboards:
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

    def delete(self, request, pk):
        owned_pinboards = request.session.get('owned_pinboards', [])
        if pk in owned_pinboards:
            request.session['owned_pinboards'] = [pinboard for pinboard in owned_pinboards if pinboard != pk]
            request.session['modified'] = True
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='latest-retrieved-pinboard')
    def latest_retrieved_pinboard(self, request):
        if ('latest_retrieved_pinboard' in request.session) and \
                (request.session['latest_retrieved_pinboard']
                    in request.session.get('owned_pinboards', [])):
            pinboard = get_object_or_404(Pinboard, id=request.session['latest_retrieved_pinboard'])
            return Response(self.serializer_class(pinboard).data)
        elif 'create' in request.query_params and request.query_params['create'] == 'true':
            pinboard = Pinboard.objects.create()
            self.update_owned_pinboards(request, pinboard.id)
            self.update_latest_retrieved_pinboard(request, pinboard.id)
            return Response(self.serializer_class(pinboard).data)
        else:
            return Response({})

    @action(detail=True, methods=['GET'], url_path='complaints')
    def complaints(self, request, pk):
        allegations = Allegation.objects.get_complaints_in_pinboard(pk)

        serializer = self.pinned_complaint_serializer_class(allegations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='officers')
    def officers(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        serializer = self.pinned_officer_serializer_class(pinboard.officers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='trrs')
    def trrs(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        serializer = self.pinned_trr_serializer_class(pinboard.trrs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='relevant-coaccusals')
    def relevant_coaccusals(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_coaccusals = paginator.paginate_queryset(pinboard.relevant_coaccusals, request, view=self)
        serializer = self.relevant_coaccusal_serializer_class(relevant_coaccusals, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='relevant-documents')
    def relevant_documents(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_documents = paginator.paginate_queryset(pinboard.relevant_documents, request, view=self)
        serializer = self.relevant_document_serializer_class(relevant_documents, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='relevant-complaints')
    def relevant_complaints(self, request, pk):
        queryset = Pinboard.objects.all()
        pinboard = get_object_or_404(queryset, id=pk)

        paginator = self.pagination_class()
        relevant_complaints = paginator.paginate_queryset(pinboard.relevant_complaints, request, view=self)
        serializer = self.relevant_complaint_serializer_class(relevant_complaints, many=True)
        return paginator.get_paginated_response(serializer.data)

    @property
    def _source_pinboard(self):
        from_pinboard_id = self.request.data.get('source_pinboard_id', None)
        if from_pinboard_id:
            return Pinboard.objects.get(id=from_pinboard_id)


class PinboardDesktopViewSet(PinboardViewSet):
    pinned_officer_serializer_class = PinnedOfficerSerializer
    pinned_complaint_serializer_class = PinnedAllegationSerializer
    pinned_trr_serializer_class = PinnedTRRSerializer
    relevant_document_serializer_class = RelevantDocumentSerializer
    relevant_coaccusal_serializer_class = RelevantOfficerSerializer
    relevant_complaint_serializer_class = RelevantAllegationSerializer
    pinboard_admin_serializer_class = PinboardAdminSerializer

    @action(detail=False, methods=['get'])
    def all(self, request):
        match = request.query_params.get('match', '')

        if request.user.is_authenticated:
            pinboards = Pinboard.objects.order_by('-created_at').annotate(
                child_pinboard_count=Count('child_pinboards', distinct=True)
            ).prefetch_related(
                'officers', 'allegations', 'trrs', 'allegations__most_common_category',
            ).prefetch_related(
                Prefetch(
                    'trrs__actionresponse_set',
                    queryset=ActionResponse.objects.filter(
                        person='Member Action'
                    ).order_by('-action_sub_category', 'force_type')
                )
            )
            if match != '':
                pinboards = pinboards.filter(Q(title__icontains=match) | Q(description__icontains=match))
        else:
            pinboards = []

        paginator = self.pagination_class()
        paginated_pinboards = paginator.paginate_queryset(pinboards, request, view=self)
        return paginator.get_paginated_response(
            self.pinboard_admin_serializer_class(paginated_pinboards, many=True).data
        )


class PinboardMobileViewSet(PinboardViewSet):
    pinned_officer_serializer_class = PinnedOfficerMobileSerializer
    pinned_complaint_serializer_class = PinnedAllegationMobileSerializer
    pinned_trr_serializer_class = PinnedTRRMobileSerializer
    relevant_document_serializer_class = RelevantDocumentMobileSerializer
    relevant_coaccusal_serializer_class = RelevantOfficerMobileSerializer
    relevant_complaint_serializer_class = RelevantAllegationMobileSerializer
