from django.shortcuts import get_object_or_404
from django.db.models import Q, OuterRef
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from data.utils.subqueries import SQCount
from document_cloud.models import DocumentCrawler
from .serializers import (
    AttachmentFileListSerializer,
    AuthenticatedAttachmentFileListSerializer,
    AttachmentFileSerializer,
    AuthenticatedAttachmentFileSerializer,
    UpdateAttachmentFileSerializer,
    DocumentCrawlerSerializer,
)


class AttachmentViewSet(viewsets.ViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @never_cache
    def retrieve(self, request, pk):
        if request.user.is_authenticated:
            queryset = AttachmentFile.objects.filter(file_type=MEDIA_TYPE_DOCUMENT)
            document = get_object_or_404(queryset, pk=pk)
            return Response(AuthenticatedAttachmentFileSerializer(document).data)
        else:
            queryset = AttachmentFile.showing.filter(file_type=MEDIA_TYPE_DOCUMENT)
            document = get_object_or_404(queryset, pk=pk)
            return Response(AttachmentFileSerializer(document).data)

    def list(self, request):
        queryset = AttachmentFile.objects.annotate(documents_count=SQCount(
            AttachmentFile.showing.filter(allegation=OuterRef('allegation')).values('allegation')
        )).order_by('-created_at', '-updated_at', 'id')

        if 'crid' in request.query_params:
            queryset = queryset.filter(allegation_id=request.query_params['crid'])
        elif 'match' in request.query_params:
            match = request.query_params['match']
            queryset = queryset.filter(Q(title__icontains=match) | Q(allegation__crid__icontains=match))

        serializer_class = AuthenticatedAttachmentFileListSerializer
        if request.auth is None:
            serializer_class = AttachmentFileListSerializer
            queryset = queryset.filter(show=True)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request, pk):
        attachment = get_object_or_404(AttachmentFile, id=pk)

        serializer = UpdateAttachmentFileSerializer(
            instance=attachment,
            data=request.data,
            user=request.user
        )

        if serializer.is_valid():
            serializer.save()
            attachment.refresh_from_db()
            return Response(
                status=status.HTTP_200_OK,
                data=AuthenticatedAttachmentFileSerializer(attachment).data
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)


class DocumentCrawlersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = DocumentCrawler.objects.order_by('-created_at')
    serializer_class = DocumentCrawlerSerializer
