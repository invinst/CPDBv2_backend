from django.core.exceptions import ValidationError

from data.constants import RACE_UNKNOWN_STRINGS


def validate_race(value):
    # The only way to indicate an unknown race should be by saving it as 'Unknown' string in database
    if value.lower() in RACE_UNKNOWN_STRINGS:
        raise ValidationError(f'Value cannot be "{value}"')
