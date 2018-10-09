from rest_framework import serializers


class CherryPickSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            key: val for key, val in obj.items() if key in self.Meta.fields
        }
