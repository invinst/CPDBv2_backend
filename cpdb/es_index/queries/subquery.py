from .utils import join_expression


class Subquery(object):
    def __init__(self, query, on, left_on=None):
        self._query = query
        self._on = on
        self._left_on = left_on
        self._query_fields = query.query_fields()
        self.field_names = [field.alias() for field in self._query_fields]
        self.field_kinds = [field.kind for field in self._query_fields]

    @property
    def query_body(self):
        return '( %s )' % self._query.raw_query

    def _left_field_name(self, table):
        if self._left_on is not None:
            return self._left_on
        return table.pk_field.name

    def join_table(self, alias, table, table_alias):
        return join_expression(
            self.query_body,
            alias,
            self._on,
            table_alias,
            self._left_field_name(table)
        )
