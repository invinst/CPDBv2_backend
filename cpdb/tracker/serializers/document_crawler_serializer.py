import pytz

from rest_framework import serializers
from shared.serializer import NoNullSerializer


class DocumentCrawlerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    crawler_name = serializers.CharField(source='source_type')
    status = serializers.CharField()
    num_documents = serializers.IntegerField()
    num_new_documents = serializers.IntegerField()
    recent_run_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d', default_timezone=pytz.utc)
    num_successful_run = serializers.IntegerField()
    log_url = serializers.CharField()
