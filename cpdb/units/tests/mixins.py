from units.index_aliases import units_index_alias
from units.indexers import UnitIndexer


class UnitSummaryTestCaseMixin(object):
    def setUp(self):
        units_index_alias.write_index.delete(ignore=404)
        units_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with units_index_alias.indexing():
            UnitIndexer().reindex()
        units_index_alias.write_index.refresh()
