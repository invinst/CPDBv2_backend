from search.workers import (
    OfficerWorker,
    TRRWorker,
    CRWorker,
    DateCRWorker,
    DateTRRWorker,
    DateOfficerWorker,
    InvestigatorCRWorker,
    LawsuitWorker
)
from search.views import SearchViewSet
from .queries import OfficerMobileQuery, CrMobileQuery, TrrMobileQuery, LawsuitMobileQuery
from .formatters import OfficerV2Formatter, CRFormatter, TRRFormatter, LawsuitFormatter
from .serializers import (
    OfficerRecentSerializer, AllegationRecentSerializer, TRRRecentSerializer, LawsuitRecentSerializer
)


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
        'LAWSUIT': LawsuitFormatter,
    }

    workers = {
        'DATE > CR': DateCRWorker(),
        'DATE > TRR': DateTRRWorker(),
        'OFFICER': OfficerWorker(),
        'CR': CRWorker(),
        'TRR': TRRWorker(),
        'DATE > OFFICERS': DateOfficerWorker(),
        'INVESTIGATOR > CR': InvestigatorCRWorker(),
        'LAWSUIT': LawsuitWorker(),
    }

    recent_items_queries = [
        {
            'query_param': 'officer_ids',
            'query': OfficerMobileQuery,
            'serializer': OfficerRecentSerializer,
        },
        {
            'query_param': 'crids',
            'query': CrMobileQuery,
            'serializer': AllegationRecentSerializer,
        },
        {
            'query_param': 'trr_ids',
            'query': TrrMobileQuery,
            'serializer': TRRRecentSerializer,
        },
        {
            'query_param': 'lawsuit_ids',
            'query': LawsuitMobileQuery,
            'serializer': LawsuitRecentSerializer,
        },
    ]
