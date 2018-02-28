from copy import deepcopy

from elasticsearch_dsl import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404

from .doc_types import CRDocType
from data.models import Allegation
from cr.serializers import AttachmentRequestSerializer, CRSummarySerializer, AllegationWithNewDocumentsSerializer


class CRViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = CRDocType().search().query('term', crid=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)
        data = deepcopy(request.data)
        data['allegation'] = allegation.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Thanks for subscribing', 'crid': pk})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'crid': pk})

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'], url_path='list-by-new-document')
    def allegations_with_new_documents(self, request):
        limit = request.GET.get('limit', 40)
        results = Allegation.get_cr_with_new_documents(limit)
        serializer = AllegationWithNewDocumentsSerializer(results, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], url_path='complaint-summaries')
    def complaint_summaries(self, request):
        query = CRDocType().search().filter('bool', filter=[
            Q('exists', field='summary'),
            ~Q('term', summary__keyword='')
        ])
        query = query.sort('-incident_date', '-crid')
        results = query[0:40].execute()
        return Response(CRSummarySerializer(results, many=True).data, status=status.HTTP_200_OK)
