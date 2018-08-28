from .field import Field
from .utils import join_expression
from .exceptions import ForeignKeyNotFoundException


class Table(object):
    def __init__(self, model_class):
        self.fields = [
            Field(field) for field in model_class._meta.fields
        ]
        self._model_class = model_class
        self.pk_field = Field(model_class._meta.pk)

    @property
    def name(self):
        return self._model_class._meta.db_table

    def field_names(self):
        return [field.name for field in self.fields]

    def find_foreign_key_to(self, relation):
        for field in self.fields:
            if field.is_foreign_key_to(relation):
                return field

        raise ForeignKeyNotFoundException(
            'Cannot find foreign key field from %s to %s.' % (
                self.name,
                relation.name
            ))

    def find_foreign_key_with_name(self, name):
        for field in self.fields:
            if field.is_foreign_key() and field.name == name:
                return field
        raise ForeignKeyNotFoundException(
            'Cannot find foreign key with name %s.' % name
        )

    def join_table(self, alias, table, table_alias):
        try:
            field = table.find_foreign_key_to(self)
            join = join_expression(
                self.name,
                alias,
                self.pk_field.name,
                table_alias,
                field.name
            )
        except ForeignKeyNotFoundException:
            field = self.find_foreign_key_to(table)
            join = join_expression(
                self.name,
                alias,
                field.name,
                table_alias,
                table.pk_field.name
            )
        return join
