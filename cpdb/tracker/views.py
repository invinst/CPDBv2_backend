from django.shortcuts import get_object_or_404
from django.db.models import OuterRef
from django.views.decorators.cache import never_cache

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action

from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from data.utils.subqueries import SQCount
from document_cloud.models import DocumentCrawler
from es_index.pagination import ESQuerysetPagination
from .doc_types import AttachmentFileDocType
from .serializers import (
    AttachmentFileListSerializer,
    AuthenticatedAttachmentFileListSerializer,
    AttachmentFileSerializer,
    AuthenticatedAttachmentFileSerializer,
    UpdateAttachmentFileSerializer,
    DocumentCrawlerSerializer,
)
from activity_log.models import ActivityLog
from activity_log.constants import ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT
from shared.utils import formatted_errors


class AttachmentViewSet(viewsets.ViewSet):
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
        ))

        serializer_class = AttachmentFileListSerializer if request.auth is None else \
            AuthenticatedAttachmentFileListSerializer

        if 'match' in request.query_params and 'crid' not in request.query_params:
            match = request.query_params['match']

            es_query = AttachmentFileDocType().search().query(
                'multi_match', query=match, operator='and', fields=['crid', 'title', 'text_content']
            )
            if request.auth is None:
                es_query = es_query.filter('term', show=True)

            paginator = ESQuerysetPagination()
            page = paginator.paginate_es_query(es_query, request, queryset)
        else:
            if 'crid' in request.query_params:
                queryset = queryset.filter(allegation_id=request.query_params['crid'])

            if request.auth is None:
                queryset = queryset.filter(show=True)

            queryset = queryset.order_by('-created_at', '-updated_at', 'id')

            paginator = LimitOffsetPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request, pk):
        attachment = get_object_or_404(AttachmentFile, id=pk)
        old_tags = list(attachment.tags.all())

        serializer = UpdateAttachmentFileSerializer(
            instance=attachment,
            data=request.data,
            user=request.user
        )

        try:
            if serializer.is_valid():
                serializer.save()
                attachment.refresh_from_db()
                new_tags = list(attachment.tags.all())
                if new_tags != old_tags:
                    added_tags = list(set(new_tags).difference(set(old_tags)))
                    removed_tags = list(set(old_tags).difference(set(new_tags)))
                    added_logs = [
                        ActivityLog(
                            modified_object=attachment,
                            action_type=ADD_TAG_TO_DOCUMENT,
                            user=request.user,
                            data=tag.name
                        )
                        for tag in added_tags
                    ]
                    removed_logs = [
                        ActivityLog(
                            modified_object=attachment,
                            action_type=REMOVE_TAG_FROM_DOCUMENT,
                            user=request.user,
                            data=tag.name
                        )
                        for tag in removed_tags
                    ]
                    ActivityLog.objects.bulk_create(added_logs + removed_logs)

                return Response(
                    status=status.HTTP_200_OK,
                    data=AuthenticatedAttachmentFileSerializer(attachment).data
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': formatted_errors(serializer.errors)}
            )

    @action(detail=False, methods=['get'], url_path='tags')
    def tags(self, request):
        return Response(list(AttachmentFile.tags.all().order_by('name').values_list('name', flat=True)))


class DocumentCrawlersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = DocumentCrawler.objects.order_by('-created_at')
    serializer_class = DocumentCrawlerSerializer
