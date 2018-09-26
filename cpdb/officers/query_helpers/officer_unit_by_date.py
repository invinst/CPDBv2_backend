from datetime import datetime

from django.conf import settings

from sortedcontainers import SortedKeyList

from es_index.utils import timing_validate
from data.models import OfficerHistory

_history_dict = None


def _history_sort_key(obj):
    return obj['effective_date']


@timing_validate('Initializing officer unit by date lookup...')
def _init_history_dict():
    global _history_dict
    _history_dict = dict()
    queryset = OfficerHistory.objects.filter(effective_date__isnull=False)\
        .select_related('unit').values(
            'unit_id', 'officer_id', 'unit__unit_name', 'unit__description',
            'end_date', 'effective_date'
        )
    for officer_history in queryset:
        history_list = _history_dict.setdefault(
            officer_history['officer_id'],
            SortedKeyList(key=_history_sort_key))
        history_list.add(officer_history)


def initialize_unit_by_date_helper():
    global _history_dict
    if settings.TEST or _history_dict is None:
        _init_history_dict()


def get_officer_unit_by_date(officer_id, d):
    global _history_dict
    if d is not None and type(d) is datetime:
        d = d.date()
    if officer_id in _history_dict:
        history_list = _history_dict[officer_id]
        ind = history_list.bisect_key_right(d)
        if ind > 0:
            history = history_list[ind-1]
            if history['end_date'] is None or history['end_date'] >= d:
                return (
                    history['unit__unit_name'],
                    history['unit__description']
                )
    return (None, None)
