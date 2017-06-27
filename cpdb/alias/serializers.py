from rest_framework.serializers import Serializer, ListField, CharField


class AliasSerializer(Serializer):
    aliases = ListField(child=CharField(max_length=20))
