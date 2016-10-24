from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination

from cms.models import SlugPage, ReportPage
from cms.cms_page_descriptors import get_descriptor, get_descriptors
from cms.serializers import CMSPageSerializer, ReportPageSerializer


class CMSPageViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, pk=None):
        queryset = SlugPage.objects.all()
        cms_page = get_object_or_404(queryset, pk=pk)
        serializer = CMSPageSerializer(get_descriptor(cms_page))
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = SlugPage.objects.all()
        cms_page = get_object_or_404(queryset, pk=pk)
        serializer = CMSPageSerializer(get_descriptor(cms_page), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': serializer.errors}, status_code=status.HTTP_400_BAD_REQUEST)


class ReportPageViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        queryset = ReportPage.objects.all()
        paginator = LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ReportPageSerializer(get_descriptors(paginated_queryset), many=True)
        return paginator.get_paginated_response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = ReportPage.objects.all()
        cms_page = get_object_or_404(queryset, pk=pk)
        serializer = ReportPageSerializer(get_descriptor(cms_page), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': serializer.errors}, status_code=status.HTTP_400_BAD_REQUEST)
