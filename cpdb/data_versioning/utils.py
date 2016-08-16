
def _get_relation_fields(klass, content, many_to_many=False, pop=False):
    if many_to_many:
        prop_to_check = 'many_to_many'
    else:
        prop_to_check = 'many_to_one'
    result = dict()
    for field in klass._meta.get_fields():
        if getattr(field, prop_to_check):
            try:
                if pop:
                    value = content.pop(field.name)
                else:
                    value = content[field.name]
                if many_to_many:
                    if not isinstance(value, list):
                        value = [value]
                result[field.name] = value
            except KeyError:
                pass
    return result


def get_many_to_many_fields(klass, content, pop=False):
    return _get_relation_fields(klass, content, many_to_many=True, pop=pop)


def get_foreign_key_fields(klass, content, pop=False):
    return _get_relation_fields(klass, content, many_to_many=False, pop=pop)
