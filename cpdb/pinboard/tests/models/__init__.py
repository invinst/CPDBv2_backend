from django.db import models

from pinboard.fields import HexField


class HexModel(models.Model):
    id = HexField(primary_key=True)
    nonauto_hex = HexField(auto_gen_add=False, null=True)
