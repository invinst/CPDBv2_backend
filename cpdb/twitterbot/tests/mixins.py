from twitterbot.index_aliases import twitterbot_index_alias
from twitterbot.indexers import OfficerIndexer


class RebuildIndexMixin:
    def setUp(self):
        twitterbot_index_alias.write_index.delete(ignore=404)
        twitterbot_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with twitterbot_index_alias.indexing():
            OfficerIndexer().reindex()
        twitterbot_index_alias.write_index.refresh()
