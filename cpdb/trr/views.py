from copy import deepcopy

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from trr.models import TRR
from trr.serializers.trr_response_serializers import TRRSerializer, AttachmentRequestSerializer
from .doc_types import TRRDocType


class TRRDesktopViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = TRRDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(TRRSerializer(search_result[0].to_dict()).data)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        data = deepcopy(request.data)
        data['trr'] = trr.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Thanks for subscribing', 'trr_id': int(pk)})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'trr_id': int(pk)})

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)


class TRRMobileViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = TRRDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(TRRSerializer(search_result[0].to_dict()).data)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        data = deepcopy(request.data)
        data['trr'] = trr.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Thanks for subscribing', 'trr_id': int(pk)})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'trr_id': int(pk)})

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)
