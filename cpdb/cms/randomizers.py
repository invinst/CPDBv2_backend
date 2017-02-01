from datetime import date, timedelta
import random


STRATEGY_LAST_N_ENTRIES = {
    'id': 1,
    'name': 'Last entries'
}
STRATEGY_LAST_N_DAYS = {
    'id': 2,
    'name': 'Last days'
}
STRATEGY_STARRED_ONLY = {
    'id': 3,
    'name': 'Starred only'
}


def last_n_days(queryset, n):
    return queryset.filter(created__gte=date.today() - timedelta(days=n))


def last_n_entries(queryset, n):
    return queryset.order_by('-created')[:n]


def starred_only(queryset, n):
    return queryset.filter(starred=True).order_by('-created')[:n]


RANDOMIZER_FUNCS = {
    1: last_n_entries,
    2: last_n_days,
    3: starred_only
}


def randomize(queryset, n, sample_size, strategy):
    pool = RANDOMIZER_FUNCS[strategy](queryset, n)
    try:
        return random.sample(pool, sample_size)
    except ValueError:
        return pool
