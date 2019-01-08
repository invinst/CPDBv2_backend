from rest_framework.serializers import Serializer, CharField, IntegerField


class VictimExcelSerializer(Serializer):
    crid = CharField(source='allegation.crid')
    gender = CharField(source='gender_display', allow_blank=True)
    race = CharField()
    birth_year = IntegerField(allow_null=True)
