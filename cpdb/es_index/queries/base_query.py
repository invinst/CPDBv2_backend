from django.db import connection

from .utils import is_model_subclass
from .query_fields import QueryField
from .table import Table


class BaseQuery(object):
    base_table_alias = 'base_table'
    joins = {}

    def __init__(self):
        self.base_table = Table(self.base_table)
        self._wheres = []
        self._process_joins()
        self._process_fields()

    def field_aliases(self):
        return [field.alias() for field in self._fields]

    @property
    def field_names_to_group(self):
        return [field.name_to_group() for field in self._fields]

    def execute(self):
        with connection.cursor() as cursor:
            cursor.execute(self.raw_query + ';')
            rows = cursor.fetchall()
        for row in rows:
            yield {
                self._fields[ind].alias(): self._fields[ind].serialize(val)
                for ind, val in enumerate(row)
            }

    def _process_fields(self):
        self._fields = []
        for field_alias, val in self.fields.iteritems():
            if isinstance(val, str):
                field = QueryField(val)
            else:
                field = val
            field.initialize(
                table_alias=self.base_table_alias,
                table=self.base_table,
                alias=field_alias,
                joins=self.joins
            )
            self._fields.append(field)

    def _process_joins(self):
        self._joins = []
        for alias, relation in self.joins.iteritems():
            if is_model_subclass(relation):
                relation = Table(relation)
                self.joins[alias] = relation
            self._joins.append(relation.join_table(
                alias, self.base_table, self.base_table_alias
            ))

    def fields_with_alias(self):
        return ', '.join([
            field.render() for field in self._fields
        ])

    def value_str(self, value):
        value_type = type(value)

        if value_type is int:
            return str(value)
        if value_type is str:
            return '\'%s\'' % value
        if value_type is unicode:
            return '\'%s\'' % value

        raise NotImplementedError('lookup value of type %s is not supported yet.' % value_type.__name__)

    def in_operator(self, values):
        if values is None or len(values) == 0:
            raise ValueError('Cant do "in" lookup for empty list.')

        return '= ANY(ARRAY[%s])' % ','.join([self.value_str(v) for v in values])

    def equal_operator(self, value):
        return '=%s' % self.value_str(value)

    def operate_str(self, operator, value):
        operator_map = {
            'in': self.in_operator,
            'equal': self.equal_operator
        }
        return operator_map[operator](value)

    def where(self, **kwargs):
        self._wheres = []
        for k, v in kwargs.iteritems():
            if '__' not in k:
                field, operator = k, 'equal'
            else:
                field, operator = k.split('__')
            try:
                self._wheres.append('%s %s' % (field, self.operate_str(operator, v)))
            except KeyError:
                raise NotImplementedError('%s lookup is not supported yet.' % operator)
        return self

    def where_str(self):
        if len(self._wheres) == 0:
            return None
        return 'WHERE %s' % (', '.join(self._wheres))
