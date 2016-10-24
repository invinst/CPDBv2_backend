from rest_framework import serializers


class CMSPageSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'fields': [
                field.to_representation(obj)
                for field in obj.get_fields()
            ]
        }

    def to_internal_value(self, data):
        return data

    def update(self, instance, validated_data):
        instance.update(validated_data)
        return instance


class ReportPageSerializer(CMSPageSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.get_id(),
            'fields': [
                field.to_representation(obj)
                for field in obj.get_fields()
            ]
        }
