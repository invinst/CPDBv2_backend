from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from data.models.common import TimeStampsModel
from app_config.validators import is_valid_hex_color


class VisualTokenColor(TimeStampsModel):
    color = models.CharField(max_length=7, validators=[is_valid_hex_color])
    text_color = models.CharField(max_length=7, validators=[is_valid_hex_color])
    lower_range = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    upper_range = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return f'[{self.lower_range} - {self.upper_range}]: { self.color}'
