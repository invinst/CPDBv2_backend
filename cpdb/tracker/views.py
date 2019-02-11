from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from data.models import AttachmentFile
from .serializers import AttachmentFileListSerializer


class AttachmentViewSet(viewsets.ViewSet):
    pagination_class = LimitOffsetPagination

    def list(self, request):
        queryset = AttachmentFile.objects.all()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = AttachmentFileListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AttachmentFileListSerializer(queryset, many=True)
        return Response(serializer.data)
