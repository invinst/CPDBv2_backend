from django.db import models


class Field(object):
    def __init__(self, model_field):
        self._model_field = model_field

    def is_foreign_key_to(self, table):
        return (
            self.is_foreign_key() and
            self._model_field.related_model._meta.db_table == table.name
        )

    def is_foreign_key(self):
        return isinstance(self._model_field, models.ForeignKey)

    @property
    def name(self):
        return self._model_field.column

    @property
    def related_table(self):
        return self._model_field.related_model
