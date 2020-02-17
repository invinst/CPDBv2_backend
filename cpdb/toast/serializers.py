from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import Serializer


class ToastBaseSerializer(Serializer):
    template = CharField(max_length=255)


class ToastDesktopSerializer(ToastBaseSerializer):
    name = CharField(max_length=25)


class ToastMobileSerializer(ToastBaseSerializer):
    name = SerializerMethodField()

    def get_name(self, obj):
        return obj.name.replace('MOBILE ', '')
