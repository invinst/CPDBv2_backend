from datetime import datetime
import dateutil.parser
import json

from django.contrib.gis.geos import Point

from .table import Table
from .utils import is_model_subclass
from .postgres_array_parser import parse_postgres_row_array


class QueryField(object):
    def __init__(self, field):
        if '.' in field:
            [self._source_table_name, self._name] = field.split('.')
        else:
            self._name = field

    def initialize(self, table_alias, table, alias, joins):
        self._table_alias = table_alias
        self._table = table
        if is_model_subclass(self._table):
            self._table = Table(table)
        self._alias = alias
        self._joins = joins
        for k, v in self._joins.iteritems():
            if is_model_subclass(v):
                self._joins[k] = Table(v)
        if not hasattr(self, '_source_table_name'):
            self._source_table_name = table_alias
        if self._source_table_name == table_alias:
            self._source_table = self._table
        else:
            self._source_table = self._joins[self._source_table_name]
        try:
            self.kind = self._source_table.get_kind(self._name)
        except AttributeError:
            pass

    def render(self):
        return '%s.%s AS %s' % (self._source_table_name, self._name, self._alias)

    def belong_to(self, table_alias):
        return self._source_table_name == table_alias

    def name_to_group(self):
        return '%s.%s' % (self._source_table_name, self._name)

    def alias(self):
        return self._alias

    def serialize(self, val):
        return val


class GeometryQueryField(QueryField):
    def render(self):
        return 'ST_AsGML(%s.%s) AS %s' % (self._source_table_name, self._name, self._alias)

    def serialize(self, val):
        if val is None:
            return None
        return Point.from_gml(val)


class CountQueryField(QueryField):
    kind = 'integer'

    def __init__(self, from_table, related_to, where=None):
        self._related_to = related_to
        if is_model_subclass(from_table):
            self._from_table = Table(from_table)
        else:
            self._from_table = from_table
        if where is None:
            self._where = {}
        else:
            self._where = where

    def initialize(self, **kwargs):
        super(CountQueryField, self).initialize(**kwargs)
        if self._related_to == self._table_alias:
            self._join_table = self._table
        else:
            self._join_table = self._joins[self._related_to]

    def render(self):
        return ' '.join([
            '(',
            'SELECT COUNT(*)',
            'FROM %s' % self._from_table.name,
            'WHERE',
            ' AND '.join(
                ['%s = %s.%s' % (
                    self._from_table.find_foreign_key_to(self._join_table).name,
                    self._related_to,
                    self._join_table.pk_field.name
                )] +
                ["%s = '%s'" % (k, v) for k, v in self._where.items()]
            ),
            ')',
            'AS',
            self._alias
        ])

    def belong_to(self, table_name):
        return False

    def name_to_group(self):
        return '%s.%s' % (self._related_to, self._join_table.pk_field.name)


class ForeignQueryField(QueryField):
    def __init__(self, relation, field_name):
        self._relation = relation
        self._relation_field_name = field_name

    def initialize(self, **kwargs):
        super(ForeignQueryField, self).initialize(**kwargs)
        self._relation_table = Table(
            self._table.find_foreign_key_with_name(self._relation).related_table
        )
        self.kind = self._relation_table.get_kind(self._relation_field_name)

    def render(self):
        return ' '.join([
            '(',
            'SELECT %s' % self._relation_field_name,
            'FROM %s' % self._relation_table.name,
            'WHERE %s = %s.%s' % (
                self._relation_table.pk_field.name,
                self._table_alias,
                self._relation
            ),
            ') AS',
            self._alias
        ])

    def belong_to(self, table_name):
        return False

    def name_to_group(self):
        return '%s.%s' % (self._table_alias, self._relation)


class RowArrayQueryField(QueryField):
    kind = None

    def __init__(self, relation):
        self._source_table_name = relation

    def initialize(self, **kwargs):
        super(RowArrayQueryField, self).initialize(**kwargs)
        relation = self._joins[self._source_table_name]
        self._relation_field_names = relation.field_names
        self._relation_field_kinds = relation.field_kinds

    def render(self):
        return ' '.join([
            'array_agg(DISTINCT ROW(',
            ', '.join([
                '%s.%s' % (self._source_table_name, field_name)
                for field_name in self._relation_field_names
            ]),
            ')) AS',
            self._alias
        ])

    def belong_to(self, table_name):
        return False

    def name_to_group(self):
        return None

    def serialize_subfield(self, kind, string):
        if string is None:
            return None

        if kind == 'smallint':
            return int(string)
        elif kind == 'varchar':
            return string
        elif kind == 'geometry':
            return Point.from_gml(string)
        elif kind == 'text':
            return string
        elif kind == 'numeric':
            return float(string)
        elif kind == 'boolean':
            if string in ['t', 'Yes']:
                return True
            elif string in ['f', 'No']:
                return False
            else:
                return None
        elif kind == 'date':
            return datetime.strptime(string, '%Y-%m-%d').date()
        elif kind == 'integer':
            return int(string)
        elif kind == 'serial':
            return int(string)
        elif kind is None:
            return None
        elif kind == 'jsonb':
            string = string.replace('\\"\\"', '"')
            return json.loads(string)
        elif kind == 'timestamp with time zone':
            return dateutil.parser.parse(string)
        else:
            raise NotImplementedError(
                'Cannot yet serialize subfield of kind "%s", value was "%s"' % (
                    kind,
                    string
                )
            )

    def serialize(self, val):
        val_tuples = parse_postgres_row_array(val)
        result = []
        for row in val_tuples:
            result.append(
                {
                    self._relation_field_names[i]:
                    self.serialize_subfield(self._relation_field_kinds[i], v)
                    for i, v in enumerate(row)
                }
            )
        return result
