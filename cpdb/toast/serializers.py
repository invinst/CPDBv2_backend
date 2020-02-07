from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class ToastSerializer(Serializer):
    name = CharField(max_length=25)
    template = CharField(max_length=255)
