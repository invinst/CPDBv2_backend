from datetime import date, timedelta
import random

RANDOMIZER_STRATEGIES = [{
    'id': 1,
    'name': 'Last entries'
}, {
    'id': 2,
    'name': 'Last days'
}]


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
    RANDOMIZER_STRATEGIES[0]['id']: last_n_entries,
    RANDOMIZER_STRATEGIES[1]['id']: last_n_days
}


def randomize(objects, n, sample_size, strategy):
    return RANDOMIZER_FUNCS[strategy](objects, n, sample_size)
