from .base_query import BaseQuery


class AggregateQuery(BaseQuery):
    @property
    def raw_query(self):
        return ' '.join(filter(None, [
            'SELECT',
            self.fields_with_alias(),
            'FROM %s %s' % (self.base_table.name, self.base_table_alias),
            ' '.join([join for join in self._joins]),
            self.where_str(),
            'GROUP BY',
            ', '.join([
                name for name in self.field_names_to_group
                if name is not None and name.startswith(self.base_table_alias)
            ])
        ]))
