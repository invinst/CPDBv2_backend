import inspect

from django.db import models


def join_expression(table_a_name, table_a_alias, table_a_field, table_b_alias, table_b_field):
    return 'LEFT JOIN %s %s ON %s.%s = %s.%s' % (
        table_a_name,
        table_a_alias,
        table_a_alias,
        table_a_field,
        table_b_alias,
        table_b_field
    )


def field_name_with_alias(base_table_alias, field_name):
    if '.' not in field_name:
        return '%s.%s' % (base_table_alias, field_name)
    return field_name


def is_model_subclass(obj):
    return inspect.isclass(obj) and issubclass(obj, models.Model)
