from rest_framework.serializers import Serializer, CharField


class AreaXlsxSerializer(Serializer):
    name = CharField()
    area_type = CharField()
    median_income = CharField(allow_null=True)
    commander = CharField(source='commander.full_name', allow_null=True)
    alderman = CharField(allow_null=True)
    police_hq = CharField(source='police_hq.name', allow_null=True)
