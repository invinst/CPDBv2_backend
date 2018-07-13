from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class PopupSerializer(Serializer):
    name = CharField(max_length=64)
    page = CharField(max_length=255)
    title = CharField(max_length=255)
    text = CharField()

