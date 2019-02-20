from rest_framework import viewsets, mixins

from document_cloud.models import DocumentCrawler
from document_crawlers.serializers import DocumentCrawlerSerializer


class DocumentCrawlersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = DocumentCrawler.objects.order_by('-created_at')
    serializer_class = DocumentCrawlerSerializer
