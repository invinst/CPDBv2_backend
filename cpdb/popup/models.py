from django.db.models import Model, CharField, TextField


class Popup(Model):
    name = CharField(max_length=64)
    page = CharField(max_length=32)
    title = CharField(max_length=255)
    text = TextField()

    def __str__(self):
        return self.name
