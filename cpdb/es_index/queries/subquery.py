from .utils import join_expression


class Subquery(object):
    def __init__(self, query, on):
        self._query = query
        self.on = on

    def field_names(self):
        return self._query.field_aliases()

    @property
    def query_body(self):
        return '( %s )' % self._query.raw_query

    def join_table(self, alias, table, table_alias):
        return join_expression(
            self.query_body,
            alias,
            self.on,
            table_alias,
            table.pk_field.name
        )
