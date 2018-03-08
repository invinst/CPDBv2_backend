import inspect
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from rest_framework import serializers
from rest_framework.fields import SkipField

from data.models import Officer
from cms.fields import (
    DateField, StringField, RichTextField, BaseCMSField
)
from cms.models import ReportPage, SlugPage, FAQPage


class BaseCMSPageSerializer(serializers.Serializer):
    def to_representation(self, obj, use_fake=False):
        def _transform_field_value(_fields):
            for field in _fields:
                if field.write_only:
                    continue
                attribute = field.get_attribute(obj)
                value = field.to_representation(attribute)
                if value is not None:
                    yield (value, field)
                elif use_fake:
                    yield (field.fake_data(), field)

        fields = []
        for value, _ in _transform_field_value(self._non_meta_fields):
            fields.append(value)

        meta_fields = dict()
        for value, field in _transform_field_value(self._meta_fields):
            meta_fields[field.field_name] = value

        return {'fields': fields, 'meta': meta_fields}

    @property
    def _non_meta_fields(self):
        return [
            field for field in self.fields.values()
            if not hasattr(self.Meta, 'fields') or field.field_name in self.Meta.fields]

    @property
    def _meta_fields(self):
        return [
            field for field in self.fields.values()
            if field.field_name in getattr(self.Meta, 'meta_fields', [])]

    def fake_data(self, **kwargs):
        fields = []
        for field in self._non_meta_fields:
            if field.read_only:
                continue
            if hasattr(field, 'fake_data'):
                fields.append(field.fake_data(kwargs.get(field.field_name, None)))
            elif field.field_name in kwargs:
                fields.append(kwargs[field.field_name])

        meta = {}
        for field in self._meta_fields:
            if field.read_only:
                continue
            if hasattr(field, 'fake_data'):
                meta[field.field_name] = field.fake_data(kwargs.get(field.field_name, None))
            elif field.field_name in kwargs:
                meta[field.field_name] = kwargs[field.field_name]

        return {'fields': fields, 'meta': meta}

    def to_internal_value(self, data):
        result = dict()
        field_values = []
        for field in self._non_meta_fields:
            if 'fields' not in data:
                break
            if field.read_only:
                continue
            try:
                field_data = [
                    obj['value'] for obj in data['fields']
                    if obj['name'] == field.field_name
                ][0]
                internal_value = field.to_internal_value(field_data)
            except (IndexError, NotImplementedError):
                continue
            field_values.append((field, internal_value))

        for field in self._meta_fields:
            if 'meta' not in data:
                break
            if field.read_only:
                continue
            try:
                internal_value = field.to_internal_value(data['meta'][field.field_name])
            except (KeyError, NotImplementedError):
                continue
            field_values.append((field, internal_value))

        supplied_fields = [field for field, _ in field_values]
        for field in self._writable_fields:
            if field in supplied_fields:
                continue
            try:
                field_values.append((field, field.get_default()))
            except SkipField:
                continue

        for field, value in field_values:
            if isinstance(field, BaseCMSField):
                result.setdefault(field.source, dict()).update(value)
            else:
                result[field.source] = value

        if 'id' in data:
            result['id'] = data['id']

        return result

    def update(self, instance, validated_data):
        validated_data.pop('id', None)
        for key, val in validated_data.iteritems():
            if isinstance(val, dict):
                getattr(instance, key).update(val)
            elif isinstance(instance._meta.get_field(key), models.ManyToManyField):
                getattr(instance, key).set(val)
            else:
                setattr(instance, key, val)
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data.pop('id', None)

        relation_fields = []
        for field in self.fields.values():
            if hasattr(field, 'child') and isinstance(field.child, serializers.ModelSerializer):
                value = validated_data.pop(field.source, None)
                if value is not None:
                    relation_fields.append((field.source, value))

        instance = self.Meta.model.objects.create(**validated_data)

        for key, value in relation_fields:
            attr = getattr(instance, key)
            attr.add(*value)

        return instance


class SlugPageSerializer(BaseCMSPageSerializer):
    def to_internal_value(self, data):
        validated_data = super(SlugPageSerializer, self).to_internal_value(data)
        validated_data['slug'] = self.Meta.slug
        validated_data['serializer_class'] = self.__class__.__name__
        return validated_data


class IdPageSerializer(BaseCMSPageSerializer):
    def to_representation(self, obj, *args, **kwargs):
        representation = super(IdPageSerializer, self).to_representation(obj, *args, **kwargs)
        representation['id'] = obj.id
        return representation


class OfficerListSerializer(serializers.ListSerializer):
    _type = 'officers_list'

    def to_representation(self, obj):
        value = super(OfficerListSerializer, self).to_representation(obj)
        return {
            'name': self.field_name,
            'type': self._type,
            'value': value
        }

    def to_internal_value(self, data):
        try:
            return super(OfficerListSerializer, self).to_internal_value(data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({self.field_name: 'Officer does not exist'})
        except (TypeError, ValueError):
            raise serializers.ValidationError({self.field_name: 'Incorrect type. Expected officer pk'})


class OfficerSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source='gender_display')

    class Meta:
        model = Officer
        fields = ('id', 'allegation_count', 'full_name', 'v1_url', 'race', 'gender')
        list_serializer_class = OfficerListSerializer

    def get_queryset(self):
        return Officer.objects.all()

    def to_internal_value(self, data):
        return self.get_queryset().get(pk=data['id'])


class ReportPageSerializer(IdPageSerializer):
    title = RichTextField(source='fields')
    excerpt = RichTextField(source='fields')
    publication = StringField(source='fields')
    publish_date = DateField(source='fields')
    author = StringField(source='fields')
    article_link = RichTextField(source='fields')
    officers = OfficerSerializer(many=True)

    class Meta:
        model = ReportPage


class FAQPageListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        data_mapping = {item['id']: item for item in validated_data}
        result = []
        for faq in instance:
            if faq.id in data_mapping:
                result.append(self.child.update(faq, data_mapping[faq.id]))

        return result


class FAQPageSerializer(IdPageSerializer):
    question = RichTextField(source='fields')
    answer = RichTextField(source='fields')
    order = serializers.IntegerField()
    starred = serializers.BooleanField()

    class Meta:
        model = FAQPage
        fields = ('question', 'answer')
        meta_fields = ('order', 'starred')
        list_serializer_class = FAQPageListSerializer


class CreateFAQPageSerializer(IdPageSerializer):
    question = RichTextField(source='fields')
    answer = RichTextField(source='fields')
    order = serializers.IntegerField(default=lambda: FAQPage.objects.count())
    starred = serializers.BooleanField()

    class Meta:
        model = FAQPage
        fields = ('question', 'answer')
        meta_fields = ('order', 'starred')

    def validate(self, data):
        if 'answer_value' in data['fields'] and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Unauthorized user cannot add answer.")
        return data


class LandingPageSerializer(SlugPageSerializer):
    navbar_title = RichTextField(
        fake_value=['Citizens Police Data Project'],
        source='fields'
    )
    navbar_subtitle = RichTextField(
        fake_value=[
            'collects and information',
            'about police misconduct in Chicago.'
        ],
        source='fields'
    )
    carousel_complaint_title = RichTextField(
        fake_value=['Complaint Summaries'],
        source='fields'
    )
    carousel_complaint_desc = RichTextField(
        fake_value=['These records contain summary information of the incident of the alleged complaint.'],
        source='fields'
    )
    carousel_allegation_title = RichTextField(
        fake_value=['Officers by Allegation'],
        source='fields'
    )
    carousel_allegation_desc = RichTextField(
        fake_value=['These are the officers with the most allegations of misconduct in Chicago.'],
        source='fields'
    )
    carousel_document_title = RichTextField(
        fake_value=['New Document'],
        source='fields'
    )
    carousel_document_desc = RichTextField(
        fake_value=['We often update our complaint records as we recieve more information from the City.',
                    'Here are some of the recent updates.'],
        source='fields'
    )
    carousel_activity_title = RichTextField(
        fake_value=['Recent Activity'],
        source='fields'
    )
    carousel_activity_desc = RichTextField(
        fake_value=['The officers, pairings, and units we display here are based on what other guests are searching '
                    'on cpdp in addition to officers who are mentioned in conversation with our twitter bot,@cpdpbot'],
        source='fields'
    )

    class Meta:
        slug = 'landing-page'
        model = SlugPage


def get_slug_page_serializer(cms_page):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if cms_page.serializer_class == name:
            return obj
