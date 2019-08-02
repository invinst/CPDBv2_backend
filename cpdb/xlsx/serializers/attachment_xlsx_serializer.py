import pytz

from rest_framework.serializers import Serializer, CharField, DateTimeField


class AttachmentXlsxSerializer(Serializer):
    title = CharField(allow_blank=True, allow_null=True)
    url = CharField(allow_blank=True)
    date_discovered = DateTimeField(
        source='external_created_at', allow_null=True, format='%Y-%m-%d', default_timezone=pytz.utc
    )
    text_content = CharField(allow_blank=True)
