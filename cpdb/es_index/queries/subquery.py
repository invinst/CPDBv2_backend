from .utils import join_expression, is_model_subclass
from .table import Table


class Subquery(object):
    def __init__(self, query, on, left_on=None):
        if is_model_subclass(query):
            table = Table(query)
            self.field_names = table.field_names
            self.field_kinds = table.field_kinds
            self._query_body = table.name
        else:
            query_fields = query.query_fields()
            self.field_names = [field.alias() for field in query_fields]
            self.field_kinds = [field.kind for field in query_fields]
            self._query_body = '( %s )' % query.raw_query
        self._on = on
        self._left_on = left_on
        self._field_kind_dict = {
            self.field_names[ind]: kind for ind, kind in enumerate(self.field_kinds)
        }

    def _left_field_name(self, table):
        if self._left_on is not None:
            return self._left_on
        return table.pk_field.name

    def get_kind(self, name):
        return self._field_kind_dict[name]

    def join_table(self, alias, table, table_alias):
        return join_expression(
            self._query_body,
            alias,
            self._on,
            table_alias,
            self._left_field_name(table)
        )
