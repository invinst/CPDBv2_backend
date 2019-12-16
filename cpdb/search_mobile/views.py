from search.workers import (
    OfficerWorker,
    TRRWorker,
    CRWorker,
    DateCRWorker,
    DateTRRWorker,
    DateOfficerWorker,
    InvestigatorCRWorker
)
from search.views import SearchViewSet
from .queries import OfficerMobileQuery, CrMobileQuery, TrrMobileQuery
from .formatters import OfficerV2Formatter, CRFormatter, TRRFormatter
from .serializers import OfficerSerializer, AllegationSerializer, TRRSerializer


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'DATE > CR': CRFormatter,
        'DATE > TRR': TRRFormatter,
        'DATE > OFFICERS': OfficerV2Formatter,
        'OFFICER': OfficerV2Formatter,
        'CR': CRFormatter,
        'TRR': TRRFormatter,
        'INVESTIGATOR > CR': CRFormatter,
    }

    workers = {
        'DATE > CR': DateCRWorker(),
        'DATE > TRR': DateTRRWorker(),
        'OFFICER': OfficerWorker(),
        'CR': CRWorker(),
        'TRR': TRRWorker(),
        'DATE > OFFICERS': DateOfficerWorker(),
        'INVESTIGATOR > CR': InvestigatorCRWorker(),
    }

    recent_items_queries = [
        {
            'query_param': 'officer_ids',
            'query': OfficerMobileQuery,
            'serializer': OfficerSerializer,
        },
        {
            'query_param': 'crids',
            'query': CrMobileQuery,
            'serializer': AllegationSerializer,
        },
        {
            'query_param': 'trr_ids',
            'query': TrrMobileQuery,
            'serializer': TRRSerializer,
        },
    ]
