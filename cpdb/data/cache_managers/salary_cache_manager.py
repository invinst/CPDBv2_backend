from itertools import groupby
from operator import attrgetter

from tqdm import tqdm
from data.models import Salary


def cache_data():
    build_cached_rank_changes()


def build_cached_rank_changes():
    salaries = Salary.objects.exclude(spp_date__isnull=True).order_by('officer_id', 'year')
    rank_change_ids = [
        grouped_salaries.next().id
        for _, grouped_salaries in groupby(salaries, key=attrgetter('officer_id', 'rank'))
    ]

    Salary.objects.update(rank_changed=False)

    batch_size = 100
    for i in tqdm(range(0, len(rank_change_ids), batch_size)):
        batch_ids = rank_change_ids[i:i + batch_size]
        Salary.objects.filter(id__in=batch_ids).update(rank_changed=True)
