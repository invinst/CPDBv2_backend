from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication

from data.models import AttachmentFile
from .serializers import AttachmentFileListSerializer


class AttachmentViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        queryset = AttachmentFile.objects.all().order_by('-created_at', '-updated_at', 'id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AttachmentFileListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request, pk):
        attachment = get_object_or_404(AttachmentFile, id=pk)
        if 'show' in request.data:
            attachment.show = request.data['show']
            attachment.save()
            return Response({'show': attachment.show})
        return Response(status=status.HTTP_400_BAD_REQUEST)
