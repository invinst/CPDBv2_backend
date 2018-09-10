from .base_query import BaseQuery


class DistinctQuery(BaseQuery):
    @property
    def raw_query(self):
        return ' '.join(filter(None, [
            'SELECT DISTINCT ON (%s.id)' % self.base_table_alias,
            self.fields_with_alias(),
            'FROM %s %s' % (self.base_table.name, self.base_table_alias),
            ' '.join([join for join in self._joins]),
            self.where_str()
        ]))
