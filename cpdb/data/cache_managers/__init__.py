from . import allegation_cache_manager
from . import officer_cache_manager
from . import salary_cache_manager


managers = [allegation_cache_manager, officer_cache_manager, salary_cache_manager]


def cache_all():
    for manager in managers:
        manager.cache_data()
