from datetime import date, timedelta
import random


RANDOMIZER_STRAT_LAST_N_DAYS = 'LAST_N_DAYS'
RANDOMIZER_STRAT_LAST_N_ENTRIES = 'LAST_N_ENTRIES'


def last_n_days(objects, n, sample_size):
    pool = objects.filter(created__gte=date.today() - timedelta(days=n))
    try:
        return random.sample(pool, sample_size)
    except ValueError:
        return pool


def last_n_entries(objects, n, sample_size):
    pool = objects.order_by('-created')[:n]
    try:
        return random.sample(pool, sample_size)
    except ValueError:
        return pool


RANDOMIZER_FUNCS = {
    RANDOMIZER_STRAT_LAST_N_DAYS: last_n_days,
    RANDOMIZER_STRAT_LAST_N_ENTRIES: last_n_entries
}


def randomize(objects, n, sample_size, strategy):
    return RANDOMIZER_FUNCS[strategy](objects, n, sample_size)
