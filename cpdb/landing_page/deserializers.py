from rest_framework import serializers

from landing_page.models import LandingPageContent


class LandingPageContentDeserializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageContent
        fields = (
            'id', 'collaborate_header', 'collaborate_content'
            )

    def update(self, instance, validated_data):
        instance.collaborate_header = validated_data.get('collaborate_header', instance.collaborate_header)
        instance.collaborate_content = validated_data.get('collaborate_content', instance.collaborate_content)
        instance.save()
        return instance
