from rest_framework import viewsets, mixins

from .models import SearchTermCategory
from .serializers import SearchTermCategorySerializer


class SearchTermCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SearchTermCategory.objects.all()
    serializer_class = SearchTermCategorySerializer
    pagination_class = None
