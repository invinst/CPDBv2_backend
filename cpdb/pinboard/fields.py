from django.db import models
from django.utils.translation import gettext_lazy as _

from pinboard.utils import int_to_zero_padded_hex, zero_padded_hex_to_int, generate_hex_from_uuid


class HexFieldError(Exception):
    pass


class HexFieldTooManyCollisionError(HexFieldError):
    pass


# Never rename or change this field as long as there are still migrations depend on it.
# If you want to make change, create another field.
class HexField(models.BigIntegerField):
    description = _("Hex encoded big (8 byte) integer")

    def __init__(self, hex_length=8, auto_gen_add=True, collision_retry=10, *args, **kwargs):
        self.hex_length = hex_length
        self.auto_gen_add = auto_gen_add
        self.collision_retry = collision_retry
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.hex_length != 8:
            kwargs['hex_length'] = self.hex_length
        if not self.auto_gen_add:
            kwargs['auto_gen_add'] = self.auto_gen_add
        if self.collision_retry != 10:
            kwargs['collision_retry'] = self.collision_retry
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return int_to_zero_padded_hex(value, self.hex_length)

    def to_python(self, value):
        if type(value) is str:
            return value
        if value is None:
            return value
        return int_to_zero_padded_hex(value, self.hex_length)

    def get_prep_value(self, value):
        if value is None:
            return value
        return zero_padded_hex_to_int(value)

    def pre_save(self, model_instance, add):
        if self.auto_gen_add and add and getattr(model_instance, self.attname, None) is None:
            model = type(model_instance)
            value = generate_hex_from_uuid(self.hex_length)

            retry = 0
            while model.objects.filter(**{self.attname: value}).exists():
                retry += 1
                if retry > self.collision_retry:
                    raise HexFieldTooManyCollisionError(
                        "Can't generate hex field value, %d consecutive collision. Consider increase hex_length." %
                        self.collision_retry
                    )
                value = generate_hex_from_uuid(self.hex_length)

            setattr(model_instance, self.attname, value)
            return value

        else:
            return super().pre_save(model_instance, add)
