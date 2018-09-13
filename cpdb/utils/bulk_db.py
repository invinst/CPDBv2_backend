def build_bulk_update_sql(table_name, id_field, fields, data):
    update_template = '''
        UPDATE {table_name} AS t SET
          {column_assignment}
        FROM (values
          {type_row}
          {value_rows}
        ) AS c({data_columns}) 
        WHERE c.{id_field} = t.{id_field};
    '''

    column_assignment = ', '.join('{field} = c.{field}'.format(field=field) for field in fields)
    data_columns = [id_field] + fields

    def format_value(value):
        if value is None:
            return 'NULL'
        elif isinstance(value, str):
            return "'{}'".format(value)
        else:
            return str(value)

    def format_value_row(row):
        return '({})'.format(
            ', '.join(format_value(row[field]) for field in data_columns)
        )

    value_rows = ', '.join(map(format_value_row, data))
    null_rows_for_defining_types = '({}), '.format(
        ', '.join('(NULL::{}).{}'.format(table_name, field) for field in data_columns)
    )

    return update_template.format(
        table_name=table_name,
        column_assignment=column_assignment,
        data_columns=', '.join(data_columns),
        type_row=null_rows_for_defining_types,
        value_rows=value_rows,
        id_field=id_field)
