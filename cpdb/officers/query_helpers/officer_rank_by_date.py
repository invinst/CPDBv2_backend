from sortedcontainers import SortedKeyList

from django.conf import settings

from es_index.utils import timing_validate
from data.models import Salary

_rank_dict = None


def _rank_sort_key(obj):
    return obj['spp_date']


@timing_validate('Initializing officer rank by date lookup...')
def _init_rank_dict():
    global _rank_dict
    _rank_dict = dict()
    for rank in Salary.objects.filter(spp_date__isnull=False).values('officer_id', 'spp_date', 'rank'):
        rank_list = _rank_dict.setdefault(
            rank['officer_id'],
            SortedKeyList(key=_rank_sort_key))
        rank_list.add(rank)


def initialize_rank_by_date_helper():
    global _rank_dict
    if settings.TEST or _rank_dict is None:
        _init_rank_dict()


def get_officer_rank_by_date(officer_id, date):
    global _rank_dict
    if officer_id in _rank_dict:
        rank_list = _rank_dict[officer_id]
        ind = rank_list.bisect_key_right(date)
        if ind > 0:
            return rank_list[ind-1]['rank']

    return None
