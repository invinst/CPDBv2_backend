from rest_framework import viewsets, mixins

from .models import SearchTermCategory, SearchTermItem
from .serializers import SearchTermCategorySerializer, SearchTermItemWithTermsSerializer


class SearchTermCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SearchTermCategory.objects.all()
    serializer_class = SearchTermCategorySerializer
    pagination_class = None


class SearchTermItemViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SearchTermItem.objects.all()
    serializer_class = SearchTermItemWithTermsSerializer
