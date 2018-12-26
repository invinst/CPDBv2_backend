from django.db.models import Case, Value, When, CharField


def get_num_range_case(field, ranges):
    """
    Return Case expression that encapsulate range of number.

    ex: get_num_range_case('age', [10, 20])
     => Case(
            When(age__gte=10, age__lte=20, then=Value('10-20')),
            When(age__lte=21, then=Value('21+')),
            default=Value('Unknown'), output_field=CharField())
    """
    len_ranges = len(ranges)
    whens = []
    for ind, val in enumerate(ranges):
        if ind > 0:
            val += 1
        kwargs = dict()

        if ind == 0 and val == 0:
            kwargs[f'{field}__lte'] = ranges[ind + 1]
            then = f'<{ranges[ind + 1]}'
        elif ind < len_ranges-1:
            kwargs[f'{field}__gte'] = val
            kwargs[f'{field}__lte'] = ranges[ind + 1]
            then = f'{val}-{ranges[ind + 1]}'
        else:
            kwargs[f'{field}__gte'] = val
            then = f'{val}+'
        kwargs['then'] = Value(then)

        whens.append(When(**kwargs))
    return Case(default=Value('Unknown'), output_field=CharField(), *whens)
