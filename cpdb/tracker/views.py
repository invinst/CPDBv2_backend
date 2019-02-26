from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication

from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from tracker.serializers.attachmentfile_serializer import UpdateAttachmentFileSerializer
from .serializers import AttachmentFileListSerializer, AttachmentFileSerializer, AuthenticatedAttachmentFileSerializer


class AttachmentViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, pk):
        queryset = AttachmentFile.showing.filter(file_type=MEDIA_TYPE_DOCUMENT)
        document = get_object_or_404(queryset, pk=pk)
        if request.user.is_authenticated:
            return Response(AuthenticatedAttachmentFileSerializer(document).data)
        else:
            return Response(AttachmentFileSerializer(document).data)

    def list(self, request):
        queryset = AttachmentFile.objects.all().order_by('-created_at', '-updated_at', 'id')
        if 'crid' in request.query_params:
            queryset = queryset.filter(allegation=str(request.query_params['crid']))

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AttachmentFileListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request, pk):
        attachment = get_object_or_404(AttachmentFile, id=pk)

        data = request.data
        if request.user.is_authenticated:
            data['last_updated_by'] = request.user.id

        serializer = UpdateAttachmentFileSerializer(attachment, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
