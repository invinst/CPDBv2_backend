from django_filters import BaseInFilter, CharFilter, FilterSet

from .models import SearchTracking


class CharInFilter(BaseInFilter, CharFilter):
    pass


class SearchTrackingFilterSet(FilterSet):
    query_types = CharInFilter(name='query_type', lookup_expr='in')

    class Meta:
        model = SearchTracking
        fields = ('query_types', )
