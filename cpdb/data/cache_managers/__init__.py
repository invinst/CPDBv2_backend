from activity_grid.cache_managers import activity_pair_card_cache_manager
from . import allegation_cache_manager, officer_cache_manager, salary_cache_manager


managers = [
    allegation_cache_manager,
    officer_cache_manager,
    salary_cache_manager,
    activity_pair_card_cache_manager
]


def cache_all():
    for manager in managers:
        manager.cache_data()
