from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from data.models import Officer
from .doc_types import OfficerSummaryDocType, OfficerTimelineEventDocType, OfficerTimelineMinimapDocType
from .serializers import TimelineSerializer
from .pagination import TimelinePagination


class OfficersViewSet(viewsets.ViewSet):

    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = OfficerSummaryDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='timeline-items')
    def timeline_items(self, request, pk):
        if Officer.objects.filter(pk=pk).exists():
            if request.GET.get('sort') == 'asc':
                sort_order = ['year_sort', 'date_sort', 'priority_sort']
            else:
                sort_order = ['-year_sort', '-date_sort', '-priority_sort']
            query = OfficerTimelineEventDocType().search().sort(*sort_order).query('term', officer_id=pk)
            paginator = TimelinePagination(int(pk))
            paginated_query = paginator.paginate_es_query(query, request)
            serializer = TimelineSerializer(paginated_query, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='timeline-minimap')
    def timeline_minimap(self, request, pk):
        query = OfficerTimelineMinimapDocType().search().query('term', officer_id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict()['items'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
