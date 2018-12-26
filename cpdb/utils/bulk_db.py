def build_bulk_update_sql(table_name, id_field, fields, data):
    column_assignment = ', '.join(f'{field} = c.{field}' for field in fields)
    data_columns = [id_field] + fields

    def format_value(value):
        if value is None:
            return 'NULL'
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)

    def format_value_row(row):
        return f"({', '.join(format_value(row[field]) for field in data_columns)})"

    value_rows = ', '.join(map(format_value_row, data))
    defining_types = ', '.join(f'(NULL::{table_name}).{field}' for field in data_columns)
    null_rows_for_defining_types = f'({defining_types}), '

    return f'''
        UPDATE {table_name} AS t SET
          {column_assignment}
        FROM (values
          {null_rows_for_defining_types}
          {value_rows}
        ) AS c({', '.join(data_columns)})
        WHERE c.{id_field} = t.{id_field};
    '''
