from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from data.constants import MAX_VISUAL_TOKEN_YEAR


class NoNullSerializer(serializers.Serializer):
    def to_representation(self, instance):
        representation = super(NoNullSerializer, self).to_representation(instance)
        return OrderedDict((key, value) for (key, value) in representation.items() if value is not None)


class LightweightOfficerPercentileSerializer(NoNullSerializer):
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class OfficerPercentileSerializer(LightweightOfficerPercentileSerializer):
    percentile_allegation = serializers.DecimalField(
        source='complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    year = serializers.SerializerMethodField()

    def get_year(self, obj):
        return min(obj.resignation_date.year, MAX_VISUAL_TOKEN_YEAR) if obj.resignation_date else MAX_VISUAL_TOKEN_YEAR


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def __init__(self, field_name, max_length, *args, **kwargs):
        self.field_name = field_name
        self.max_length = max_length
        super(CreatableSlugRelatedField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if self.max_length:
            if len(data) > self.max_length:
                raise ValidationError(
                    {self.field_name: [f'Ensure this field has no more than {self.max_length} characters.']}
                )
        obj, _ = self.get_queryset().get_or_create(**{self.slug_field: data})
        return obj
