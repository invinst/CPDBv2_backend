import string

from django.core.exceptions import ValidationError


def is_valid_hex_color(value):
    if value[0] == '#' and len(value) == 7 and all([c in string.hexdigits for c in value[1:]]):
        return True
    else:
        raise ValidationError('Value must be a valid hex color')
